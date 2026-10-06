from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import User
from usuarios_app.api.hspq_report import HspqReportJWTAuthentication
from usuarios_app.api.ipp_report_config import (
    CAMPOS, IPP_TEST_ID, NOTA_ESCALA, NOTA_PUNTAJE, REPORT_VIEWER_GROUPS,
    TRANSFORMED_LABEL,
)
from usuarios_app.api.ipp_report_pdf import generate_ipp_pdf
from usuarios_app.api.views import convert_score
from usuarios_app.models import pregunta_ipp, respuesta2, test


def _can_view(requester, target):
    if requester.pk == target.pk or requester.is_staff or requester.is_superuser:
        return True
    return requester.groups.filter(name__in=REPORT_VIEWER_GROUPS).exists()


def _join(labels):
    labels = [label for label in labels if label]
    if not labels:
        return 'No consta.'
    if len(labels) == 1:
        return labels[0]
    return ', '.join(labels[:-1]) + ' y ' + labels[-1]


def _field_label(item):
    return f"{item['id']}. {item['nombre']}"


def _pair(item):
    return f"{_field_label(item)} (AC {item['pt_ac']}, PR {item['pt_pr']})"


def _extreme(fields, key, highest):
    values = [item[key] for item in fields if item[key] is not None]
    if not values:
        return []
    target = max(values) if highest else min(values)
    return [item for item in fields if item[key] == target]


def _profile_text(fields):
    scored = [
        item for item in fields
        if item['pt_ac'] is not None and item['pt_pr'] is not None
    ]
    if not scored:
        empty = 'No hay puntuaciones transformadas para describir el perfil.'
        return {
            'interpretacion': empty,
            'altos_bajos': empty,
            'relacion': empty,
            'sintesis': empty,
        }

    all_scores = [item[key] for item in scored for key in ('pt_ac', 'pt_pr')]
    highest = max(all_scores)
    lowest = min(all_scores)
    amplitude = highest - lowest
    if amplitude >= 30:
        forma = 'el perfil muestra contrastes marcados entre campos'
    elif amplitude <= 15:
        forma = 'el perfil es relativamente plano'
    else:
        forma = 'el perfil muestra contrastes moderados'

    ac_high = _extreme(scored, 'pt_ac', True)
    ac_low = _extreme(scored, 'pt_ac', False)
    pr_high = _extreme(scored, 'pt_pr', True)
    pr_low = _extreme(scored, 'pt_pr', False)
    peak_value = max(max(item['pt_ac'], item['pt_pr']) for item in scored)
    floor_value = min(min(item['pt_ac'], item['pt_pr']) for item in scored)
    peaks = [item for item in scored if max(item['pt_ac'], item['pt_pr']) == peak_value]
    floors = [item for item in scored if min(item['pt_ac'], item['pt_pr']) == floor_value]

    intro = (
        'Las cifras comparadas son puntuaciones transformadas del sistema, no percentiles verificados '
        'ni niveles del baremo. La lectura solo contrasta este perfil. No es un diagnóstico ni una '
        'afirmación de capacidad. '
        f'La puntuación transformada más alta es {highest} y la más baja es {lowest} '
        f'(amplitud {amplitude}); {forma}.'
    )

    highs = (
        f'Interés relativamente mayor en actividades: {_join(_field_label(item) for item in ac_high)} '
        f'(AC {ac_high[0]["pt_ac"]}). '
        f'Interés relativamente mayor en profesiones: {_join(_field_label(item) for item in pr_high)} '
        f'(PR {pr_high[0]["pt_pr"]}). '
        f'El valor más alto del perfil ({peak_value}) aparece en {_join(_pair(item) for item in peaks)}.'
    )
    lows = (
        f'Interés relativamente menor en actividades: {_join(_field_label(item) for item in ac_low)} '
        f'(AC {ac_low[0]["pt_ac"]}). '
        f'Interés relativamente menor en profesiones: {_join(_field_label(item) for item in pr_low)} '
        f'(PR {pr_low[0]["pt_pr"]}). '
        f'El valor más bajo del perfil ({floor_value}) aparece en {_join(_pair(item) for item in floors)}.'
    )
    unknown = [
        item for item in floors
        if item['desconocidas_ac'] or item['desconocidas_pr']
    ]
    if unknown:
        lows += (
            ' En '
            + _join(_field_label(item) for item in unknown)
            + ' hay respuestas D. Esas respuestas puntúan 0, igual que el rechazo, '
            'así que el puntaje bajo no distingue desconocimiento de desagrado.'
        )

    gaps = sorted(
        ((abs(item['pt_ac'] - item['pt_pr']), item['pt_ac'] - item['pt_pr'], item) for item in scored),
        key=lambda row: row[0],
        reverse=True,
    )
    gap_cut = amplitude / 2
    discrepant = [row for row in gaps if row[0] >= gap_cut and row[0] > 0]
    if not discrepant and gaps and gaps[0][0] > 0:
        discrepant = [gaps[0]]
    close = [row for row in gaps if row[0] == gaps[-1][0]]

    def _direction(delta):
        if delta > 0:
            return 'el interés por actividades queda por encima del interés por profesiones'
        if delta < 0:
            return 'el interés por profesiones queda por encima del interés por actividades'
        return 'actividades y profesiones coinciden'

    if discrepant:
        relation = (
            'Se destaca como discrepancia relativa del perfil toda diferencia AC–PR igual o mayor '
            f'que la mitad de la amplitud de este informe ({gap_cut:g} puntos). '
            'Ese margen solo ordena la lectura; no es un punto de corte del manual. '
            + ' '.join(
                f'{_field_label(item)}: AC {item["pt_ac"]} y PR {item["pt_pr"]}; {_direction(delta)}.'
                for _gap, delta, item in discrepant
            )
        )
    else:
        relation = (
            'No se observa una separación AC–PR que alcance la mitad de la amplitud de este perfil. '
            'Actividades y profesiones quedan relativamente próximas en los 17 campos.'
        )
    relation += (
        ' La coincidencia más estrecha está en '
        + _join(
            f'{_field_label(item)} (diferencia {gap})'
            for gap, _delta, item in close
        )
        + '.'
    )
    if discrepant:
        relation += (
            ' Conviene ampliar la información profesional sobre '
            + _join(_field_label(item) for _gap, _delta, item in discrepant)
            + ' antes de interpretar esa diferencia. Esto no recomienda una opción vocacional.'
        )

    synthesis = (
        f'{forma[:1].upper()}{forma[1:]}. '
        f'El interés relativamente más alto se observa en {_join(_field_label(item) for item in peaks)}. '
        f'El interés relativamente más bajo se observa en {_join(_field_label(item) for item in floors)}. '
        + (
            'La relación AC–PR más separada está en '
            + _join(_field_label(item) for _gap, _delta, item in discrepant)
            + '. '
            if discrepant else
            'No hay una discrepancia AC–PR marcada dentro de este perfil. '
        )
        + 'Esta síntesis no diagnostica ni recomienda opciones vocacionales.'
    )
    return {
        'interpretacion': intro,
        'altos_bajos': highs + ' ' + lows,
        'relacion': relation,
        'sintesis': synthesis,
    }


def build_ipp_report(user):
    """Arma el informe IPP. El puntaje directo es la suma usada por el cálculo existente."""
    test_row = test.objects.filter(pk=IPP_TEST_ID).first()
    answers = list(
        respuesta2.objects.filter(usuario_id=user.pk)
        .select_related('opcion_id', 'pregunta_id')
        .order_by('id')
    )
    warnings = []
    other_tests = sorted({row.id_test for row in answers if row.id_test != IPP_TEST_ID})
    if other_tests:
        warnings.append({
            'tipo': 'otro_id_test',
            'detalle': (
                f'Hay respuestas con otro id_test ({other_tests}). '
                'El cálculo existente no las excluye; este informe tampoco.'
            ),
        })
    duplicated = (
        respuesta2.objects.filter(usuario_id=user.pk)
        .values('pregunta_id')
        .annotate(n=Count('id'))
        .filter(n__gt=1)
    )
    if duplicated:
        warnings.append({
            'tipo': 'respuestas_duplicadas',
            'detalle': 'Hay preguntas con más de una respuesta. La suma las incluye, como el cálculo existente.',
        })

    fields = []
    for section_id, name, code in CAMPOS:
        rows = [row for row in answers if row.pregunta_id.seccion == section_id]
        ac_rows = [row for row in rows if row.categoria == 'AC']
        pr_rows = [row for row in rows if row.categoria == 'PR']
        pd_ac = sum(row.valor for row in ac_rows) if ac_rows else None
        pd_pr = sum(row.valor for row in pr_rows) if pr_rows else None
        pt_ac = convert_score(pd_ac, 'AC', section_id) if pd_ac is not None else None
        pt_pr = convert_score(pd_pr, 'PR', section_id) if pd_pr is not None else None
        questions = pregunta_ipp.objects.filter(seccion=section_id)
        ac_items = questions.filter(categoria='AC').count()
        pr_items = questions.filter(categoria='PR').count()
        if ac_items != 6 or pr_items != 6:
            warnings.append({
                'tipo': 'clasificacion_distinta',
                'detalle': (
                    f'{section_id}. {name}: hay {ac_items} ítems AC y {pr_items} ítems PR. '
                    'El informe respeta esa clasificación guardada y no reasigna ítems.'
                ),
            })
        fields.append({
            'id': section_id,
            'nombre': name,
            'codigo': code,
            'pd_ac': pd_ac,
            'pd_pr': pd_pr,
            'pt_ac': pt_ac,
            'pt_pr': pt_pr,
            'desconocidas_ac': sum(1 for row in ac_rows if (row.opcion_id.inciso or '').upper() == 'D'),
            'desconocidas_pr': sum(1 for row in pr_rows if (row.opcion_id.inciso or '').upper() == 'D'),
        })

    return {
        'estudiante': {
            'nombre': user.first_name,
            'apellido': user.last_name,
            'ci_username': user.username,
            'edad': user.edad,
            'sexo': user.sexo,
            'colegio': user.colegio,
            'grado_escolar': user.grado_escolar,
        },
        'test': {
            'nombre': test_row.nombre if test_row else 'Inventario de intereses y preferencias profesionales',
            'items': pregunta_ipp.objects.filter(test_id=IPP_TEST_ID).count(),
            'campos': len(CAMPOS),
            'escala': TRANSFORMED_LABEL,
            'fecha_aplicacion': None,
        },
        'campos': fields,
        'perfil': _profile_text(fields),
        'advertencias': warnings,
        'notas': [NOTA_PUNTAJE, NOTA_ESCALA],
    }


class IppReportPdfView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if not _can_view(request.user, user):
            return Response({'detail': 'No autorizado.'}, status=403)
        pdf = generate_ipp_pdf(build_ipp_report(user))
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="IPP_{user_id}.pdf"'
        return response
