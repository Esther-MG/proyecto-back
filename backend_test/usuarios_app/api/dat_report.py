from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import User
from usuarios_app.api.dat_report_config import (
    APTITUD_SIGNIFICADO, BAREMO_FUENTE, BAREMO_NOTA_SEXO, DAT_TEST_ID,
    NO_CONVERSION_NOTE, REPORT_VIEWER_GROUPS, SUBTESTS, lookup_centil,
)
from usuarios_app.api.dat_report_pdf import generate_dat_pdf
from usuarios_app.api.hspq_report import HspqReportJWTAuthentication
from usuarios_app.models import pregunta_sa, respuesta1, seccion, test


def _can_view(requester, target):
    if requester.pk == target.pk or requester.is_staff or requester.is_superuser:
        return True
    return requester.groups.filter(name__in=REPORT_VIEWER_GROUPS).exists()


def _label(item):
    meaning = APTITUD_SIGNIFICADO.get(item['codigo'], item['nombre'])
    return f"{item['codigo']} ({item['nombre']}: {meaning}; centil {item['centil']})"


def _codes(items):
    codes = [item['codigo'] for item in items]
    if len(codes) < 2:
        return ', '.join(codes)
    return ', '.join(codes[:-1]) + ' y ' + codes[-1]


def _profile_text(subtests):
    """Contraste dentro del perfil. No asigna niveles con nombre, carreras ni diagnóstico."""
    with_centile = [item for item in subtests if item.get('centil') is not None]
    missing = [item for item in subtests if item.get('centil') is None]
    if not with_centile:
        empty = 'No hay centiles disponibles en la plantilla para este perfil.'
        return {
            'interpretacion': empty,
            'fortalezas': 'No consta.',
            'areas_menores': 'No consta.',
            'sintesis': empty,
            'lectura': empty,
        }

    highest = max(item['centil'] for item in with_centile)
    lowest = min(item['centil'] for item in with_centile)
    peak = [item for item in with_centile if item['centil'] == highest]
    floor = [item for item in with_centile if item['centil'] == lowest and item not in peak]
    middle = [item for item in with_centile if item not in peak and item not in floor]
    anchor = max((item['centil'] for item in middle), default=None)
    superior = []
    intermedios = []
    if anchor is not None:
        for item in middle:
            closer_to_anchor = (anchor - item['centil']) < (item['centil'] - lowest)
            (superior if closer_to_anchor or item['centil'] == anchor else intermedios).append(item)

    intro = (
        'Los centiles provienen de la Plantilla de Baremos escolares y ubican el puntaje directo. '
        'No describen una capacidad absoluta ni una categoría normativa con nombre, porque la plantilla '
        'no define niveles bajo, medio o alto. Lo que sigue es el contraste dentro de este perfil, '
        'para integrarlo después con IPP y HSPQ. No es un diagnóstico.'
    )
    parts = [intro]
    if missing:
        parts.append('Sin centil en la plantilla: ' + _codes(missing) + '.')
    if highest == lowest:
        parts.append(
            f'Todos los centiles disponibles son {highest}. No se observa una aptitud relativamente '
            'más alta ni más baja dentro del perfil.'
        )
        relative = parts[-1]
        return {
            'interpretacion': ' '.join(parts),
            'fortalezas': relative,
            'areas_menores': relative,
            'sintesis': relative,
            'lectura': (
                'Esta lectura no recomienda opciones vocacionales. Solo deja el perfil DAT '
                'para integrarlo después con IPP y HSPQ. ' + relative
            ),
        }

    peak_text = (
        f"{_codes(peak)} es claramente el resultado más alto del perfil"
        if len(peak) == 1 else
        f"{_codes(peak)} son los resultados más altos del perfil"
    )
    parts.append(
        f'{peak_text}: ' + '; '.join(_label(item) for item in peak) + '. '
        'Esa posición es una fortaleza relativa dentro del perfil. El centil informa la ubicación '
        'en la plantilla; no se le asigna una clasificación normativa con nombre.'
    )
    if superior:
        parts.append(
            'Se observa un desempeño relativamente mayor que en las demás aptitudes, aunque por debajo '
            f'de {_codes(peak)}, en ' + '; '.join(_label(item) for item in superior) + '.'
        )
    if intermedios:
        above = _codes(peak + superior)
        verb = 'Queda' if len(intermedios) == 1 else 'Quedan'
        parts.append(
            f'{verb} en una posición intermedia, pero baja respecto de las aptitudes superiores del perfil '
            f'({above}): ' + '; '.join(_label(item) for item in intermedios) + '.'
        )
    if floor:
        parts.append(
            f'{_codes(floor)} '
            f'{"es el resultado más bajo" if len(floor) == 1 else "son los resultados más bajos"} '
            'del perfil: ' + '; '.join(_label(item) for item in floor) + '. '
            'Se observa un desempeño relativamente menor dentro del perfil. '
            'No se afirma una incapacidad absoluta.'
        )

    strengths = (
        'Fortaleza relativa del perfil, no clasificación normativa: '
        + '; '.join(_label(item) for item in peak) + '.'
    )
    if superior:
        strengths += (
            ' También se observa un desempeño relativamente mayor que en el resto, sin alcanzar '
            f'el resultado más alto, en {_codes(superior)}.'
        )
    lower = (
        'Desempeño relativamente menor dentro del perfil, no clasificación normativa: '
        + ('; '.join(_label(item) for item in floor) if floor else 'No consta.')
    )
    if intermedios:
        if len(intermedios) == 1:
            lower += (
                f' {_codes(intermedios)} no está entre los resultados más bajos, pero se observa bajo '
                f'respecto de {_codes(peak + superior)}.'
            )
        else:
            lower += (
                f' {_codes(intermedios)} no están entre los resultados más bajos, pero se observan bajos '
                f'respecto de {_codes(peak + superior)}.'
            )
    synthesis = (
        f'{peak_text}. '
        + (
            f'{_codes(superior)} se observan relativamente superiores a las demás aptitudes del perfil. '
            if superior else ''
        )
        + (
            (
                f'{_codes(intermedios)} queda en una posición intermedia, baja respecto de las aptitudes superiores. '
                if len(intermedios) == 1 else
                f'{_codes(intermedios)} quedan en una posición intermedia, baja respecto de las aptitudes superiores. '
            )
            if intermedios else ''
        )
        + (
            f'{_codes(floor)} '
            f'{"es el resultado más bajo" if len(floor) == 1 else "son los resultados más bajos"} del perfil.'
            if floor else ''
        )
    )
    lectura = (
        'Esta sección no recomienda opciones vocacionales. La orientación vocacional final se hará '
        'después, integrando DAT, IPP y HSPQ. Aquí solo se interpreta el perfil DAT: ' + synthesis
    )
    return {
        'interpretacion': ' '.join(parts),
        'fortalezas': strengths,
        'areas_menores': lower,
        'sintesis': synthesis,
        'lectura': lectura,
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
            centil, observacion = None, 'La plantilla no incluye este apartado.'
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
