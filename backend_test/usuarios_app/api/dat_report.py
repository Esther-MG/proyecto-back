from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import User
from usuarios_app.api.dat_report_config import (
    BAREMO_FUENTE, BAREMO_NOTA_SEXO, DAT_TEST_ID, NO_CONVERSION_NOTE,
    REPORT_VIEWER_GROUPS, SUBTESTS, lookup_centil,
)
from usuarios_app.api.dat_report_pdf import generate_dat_pdf
from usuarios_app.api.hspq_report import HspqReportJWTAuthentication
from usuarios_app.models import pregunta_sa, respuesta1, seccion, test


def _can_view(requester, target):
    if requester.pk == target.pk or requester.is_staff or requester.is_superuser:
        return True
    return requester.groups.filter(name__in=REPORT_VIEWER_GROUPS).exists()


def _join_items(items):
    return '; '.join(
        f"{item['codigo']} ({item['nombre']}): centil {item['centil']}" for item in items
    )


def _profile_text(subtests):
    """Comparación de centiles del propio perfil. Sin niveles, carreras ni diagnóstico."""
    with_centile = [item for item in subtests if item.get('centil') is not None]
    missing = [item for item in subtests if item.get('centil') is None]
    if not with_centile:
        empty = 'No hay centiles disponibles en la Tabla 42 para este perfil.'
        return {
            'interpretacion': empty,
            'fortalezas': 'No consta.',
            'areas_menores': 'No consta.',
            'sintesis': empty,
            'recomendaciones': 'La Tabla 42 no incluye recomendaciones y aquí no hay centiles que comparar.',
        }

    highest = max(item['centil'] for item in with_centile)
    lowest = min(item['centil'] for item in with_centile)
    high_items = [item for item in with_centile if item['centil'] == highest]
    low_items = [item for item in with_centile if item['centil'] == lowest]
    ordered = ', '.join(
        f"{item['codigo']} {item['centil']}"
        for item in sorted(with_centile, key=lambda item: (-item['centil'], item['codigo']))
    )
    lines = [
        f"{item['codigo']} ({item['nombre']}): puntaje directo {item['puntaje_directo']}, centil {item['centil']}."
        for item in subtests if item.get('centil') is not None
    ]
    if missing:
        lines.append('Sin centil en la Tabla 42: ' + ', '.join(item['codigo'] for item in missing) + '.')
    lines.append('La tabla informa el centil. No define categorías bajo, medio o alto.')
    if highest == lowest:
        relative = f'Todos los centiles disponibles son {highest}. No hay diferencia relativa dentro del perfil.'
        strengths = relative
        lower = relative
        synthesis = f'Perfil sin diferencia relativa de centil. Orden: {ordered}.'
    else:
        strengths = 'Centil más alto de este perfil, no una categoría de la tabla: ' + _join_items(high_items)
        lower = 'Centil más bajo de este perfil, no una categoría de la tabla: ' + _join_items(low_items)
        synthesis = (
            f'En este perfil el centil más alto es {highest} y el más bajo es {lowest}. '
            f'Orden de centiles: {ordered}.'
        )
    return {
        'interpretacion': ' '.join(lines),
        'fortalezas': strengths,
        'areas_menores': lower,
        'sintesis': synthesis,
        'recomendaciones': (
            'La Tabla 42 no recomienda carreras ni intervenciones. '
            'Solo respalda la comparación de centiles de este perfil. '
            f'{strengths} {lower} '
            'Intereses, rendimiento y otros antecedentes no constan en la tabla.'
        ),
    }


def build_dat_report(user):
    """Arma el informe DAT. El puntaje directo es la suma de respuesta1.valor."""
    test_row = test.objects.filter(pk=DAT_TEST_ID).first()
    sections = list(seccion.objects.filter(test_id=DAT_TEST_ID).order_by('id'))
    answers = list(
        respuesta1.objects.filter(usuario_id=user.pk, id_test=DAT_TEST_ID)
        .select_related('opcion_id')
        .order_by('id')
    )
    other_tests = sorted({
        row.id_test for row in respuesta1.objects.filter(usuario_id=user.pk).exclude(id_test=DAT_TEST_ID)
    })
    warnings = []
    grado = (user.grado_escolar or '').lower()
    if 'bachillerato' not in grado:
        warnings.append({
            'tipo': 'grado_distinto_del_baremo',
            'detalle': (
                f'El grado registrado es "{user.grado_escolar or "no consta"}". '
                'La Tabla 42 usada es solo de 2.º Bachillerato; no hay otra norma en la fuente.'
            ),
        })
    if other_tests:
        warnings.append({
            'tipo': 'otras_respuestas',
            'detalle': f'Hay respuestas DAT con otro id_test y no entran en este informe: {other_tests}.',
        })

    expected_by_section = {
        row['seccion_id']: row['total']
        for row in pregunta_sa.objects.filter(seccion_id__test_id=DAT_TEST_ID)
        .values('seccion_id')
        .annotate(total=Count('id'))
    }

    code_by_id = dict(SUBTESTS)
    subtests = []
    for section in sections:
        rows = [row for row in answers if row.id_apartado == section.id]
        aciertos = sum(1 for row in rows if row.opcion_id_id and row.opcion_id.valor)
        puntaje_directo = sum(row.valor for row in rows) if rows else None
        preguntas = sorted({row.id_pregunta for row in rows})
        duplicadas = sorted(
            pregunta for pregunta in preguntas
            if sum(1 for row in rows if row.id_pregunta == pregunta) > 1
        )
        code = code_by_id.get(section.id)
        if code is None:
            centil, observacion = None, 'La Tabla 42 no incluye este apartado.'
        else:
            centil, observacion = lookup_centil(code, puntaje_directo)

        if duplicadas:
            warnings.append({
                'tipo': 'respuestas_duplicadas',
                'apartado': section.id,
                'detalle': f'Preguntas con más de una respuesta en {section.nombre}: {duplicadas}.',
            })
        if puntaje_directo is not None and aciertos != puntaje_directo:
            warnings.append({
                'tipo': 'aciertos_distintos_de_puntaje',
                'apartado': section.id,
                'detalle': (
                    f'{section.nombre}: aciertos por clave={aciertos}, '
                    f'puntaje directo={puntaje_directo}. El centil usa el puntaje directo.'
                ),
            })
        if not rows:
            warnings.append({
                'tipo': 'apartado_sin_respuestas',
                'apartado': section.id,
                'detalle': f'No hay respuestas para {section.nombre}.',
            })

        subtests.append({
            'id': section.id,
            'codigo': code or '—',
            'nombre': section.nombre,
            'aciertos': aciertos,
            'puntaje_directo': puntaje_directo,
            'centil': centil,
            'observacion': observacion,
            'preguntas_respondidas': len(preguntas),
            'preguntas_esperadas': expected_by_section.get(section.id),
            'registros_totales': len(rows),
        })

    return {
        'estudiante': {
            'id': user.pk,
            'nombre': user.first_name,
            'apellido': user.last_name,
            'ci_username': user.username,
            'edad': user.edad,
            'sexo': user.sexo,
            'colegio': user.colegio,
            'grado_escolar': user.grado_escolar,
        },
        'test': {
            'nombre': test_row.nombre if test_row else None,
            'id_test': DAT_TEST_ID,
            'baremo': BAREMO_FUENTE,
            'fecha_aplicacion': None,
            'total_respuestas': len(answers),
        },
        'subtests': subtests,
        'perfil': _profile_text(subtests),
        'advertencias': warnings,
        'notas': [BAREMO_NOTA_SEXO, NO_CONVERSION_NOTE],
    }


class DatReportPdfView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if not _can_view(request.user, user):
            return Response({'detail': 'No autorizado.'}, status=403)
        pdf = generate_dat_pdf(build_dat_report(user))
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="DAT_{user_id}.pdf"'
        return response
