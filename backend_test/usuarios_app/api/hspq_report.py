from collections import Counter, defaultdict

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from usuarios.models import User
from usuarios_app.api.hspq_report_pdf import generate_hspq_pdf
from usuarios_app.models import pregunta_hspq, respuesta3
from usuarios_app.api.hspq_report_config import (
    FACTOR_ORDER, REPORT_VIEWER_GROUPS, DECATIPO_SOURCE_NOTE,
    SECONDARY_SOURCE_FACTORS, SECONDARY_FACTOR_NAMES, SECONDARY_FACTOR_COEFFICIENTS,
    SECONDARY_FACTORS_SOURCE_NOTE, SEXO_ALIASES,
    NIVEL_BAJO_MAX, NIVEL_PROMEDIO_MAX, INTERPRETACION_PENDIENTE, FACTOR_POLE_DESCRIPTIONS,
)
from usuarios_app.api.views import (
    convert_section_a, convert_section_b, convert_section_c, convert_section_d,
    convert_section_e, convert_section_f, convert_section_g, convert_section_h,
    convert_section_i, convert_section_j, convert_section_o, convert_section_q2,
    convert_section_q3, convert_section_q4,
)

class HspqReportJWTAuthentication(JWTAuthentication):
    """El frontend envia el access JWT como 'Authorization: Token <access>', no 'Bearer'."""

    def get_raw_token(self, header):
        parts = header.split()
        if parts and parts[0].lower() == b'token':
            if len(parts) != 2:
                raise AuthenticationFailed(
                    'Authorization header must contain two space-delimited values',
                    code='bad_authorization_header',
                )
            return parts[1]
        return super().get_raw_token(header)


DECATIPO_CONVERTERS = {
    'A': convert_section_a, 'B': convert_section_b, 'C': convert_section_c,
    'D': convert_section_d, 'E': convert_section_e, 'F': convert_section_f,
    'G': convert_section_g, 'H': convert_section_h, 'I': convert_section_i,
    'J': convert_section_j, 'O': convert_section_o, 'Q2': convert_section_q2,
    'Q3': convert_section_q3, 'Q4': convert_section_q4,
}


def _normalize_factor(raw):
    return (raw or '').strip().upper()


def _can_view(requester, target):
    if requester.pk == target.pk or requester.is_staff or requester.is_superuser:
        return True
    return requester.groups.filter(name__in=REPORT_VIEWER_GROUPS).exists()


def _normalize_sexo(raw):
    return SEXO_ALIASES.get((raw or '').strip().lower())


def _nivel_decatipo(decatipo):
    if decatipo is None:
        return None
    if decatipo <= NIVEL_BAJO_MAX:
        return 'bajo'
    if decatipo <= NIVEL_PROMEDIO_MAX:
        return 'promedio'
    return 'alto'


def _descripcion_primario(factor, nivel):
    # Descriptores de polos del Cuadro B (manual HSPQ, adaptacion espanola).
    polos = FACTOR_POLE_DESCRIPTIONS.get(factor)
    if nivel is None or polos is None:
        return INTERPRETACION_PENDIENTE
    if nivel in ('bajo', 'alto'):
        return polos[nivel]
    return f"Nivel promedio, entre '{polos['bajo']}' y '{polos['alto']}'."


def _build_interpretacion(factors, factores_secundarios):
    # Descriptiva y neutral: solo clasifica el decatipo obtenido. Sin texto clinico inventado.
    primarios = [{
        'factor': f['factor'],
        'puntuacion_directa': f['puntuacion_directa'],
        'decatipo': f['decatipo'],
        'nivel': _nivel_decatipo(f['decatipo']),
        'descripcion': _descripcion_primario(f['factor'], _nivel_decatipo(f['decatipo'])),
    } for f in factors]

    secundarios = [{
        'clave': clave,
        'nombre': datos['nombre'],
        'decatipo': datos['decatipo'],
        'nivel': _nivel_decatipo(datos['decatipo']),
        'descripcion': INTERPRETACION_PENDIENTE,
    } for clave, datos in factores_secundarios.items()]

    return {'factores_primarios': primarios, 'factores_secundarios': secundarios}


def _compute_secondary_factors(decatipos, sexo_raw, warnings):
    # QI-QIV = sum(Ki * decatipo_i) + a, Tabla 4 (manual HSPQ, adaptacion espanola). B excluido.
    sexo = _normalize_sexo(sexo_raw)
    if sexo is None:
        warnings.append({
            'tipo': 'sexo_no_reconocido',
            'detalle': (
                f"sexo '{sexo_raw}' no coincide con los coeficientes (masculino/femenino) "
                "de la Tabla 4; no se calcularon los factores secundarios."
            ),
        })

    missing_factors = [f for f in SECONDARY_SOURCE_FACTORS if decatipos.get(f) is None]
    if missing_factors:
        warnings.append({
            'tipo': 'secundarios_no_calculados',
            'detalle': f'Factores primarios sin decatipo valido para QI-QIV: {missing_factors}.',
        })

    result = {}
    for key, nombre in SECONDARY_FACTOR_NAMES.items():
        if sexo is None or missing_factors:
            result[key] = {'nombre': nombre, 'decatipo': None}
            continue
        coeffs = SECONDARY_FACTOR_COEFFICIENTS[sexo][key]
        valor = sum(coeffs[f] * decatipos[f] for f in SECONDARY_SOURCE_FACTORS) + coeffs['constante']
        result[key] = {'nombre': nombre, 'decatipo': round(valor, 2)}
    return result


def build_hspq_report(user):
    responses = list(respuesta3.objects.filter(usuario_id=user.pk).order_by('id'))
    warnings = []

    test_ids = sorted({r.id_test for r in responses})
    if len(test_ids) > 1:
        warnings.append({
            'tipo': 'multiples_tests',
            'detalle': f'Existen respuestas con distintos id_test: {test_ids}.',
        })

    # factor -> id_pregunta -> respuestas (orden por id ascendente)
    by_factor = defaultdict(lambda: defaultdict(list))
    unknown_factors = Counter()
    for r in responses:
        factor = _normalize_factor(r.seccion)
        if factor != r.seccion:
            warnings.append({
                'tipo': 'factor_normalizado',
                'detalle': f"respuesta {r.id}: seccion '{r.seccion}' interpretada como '{factor}'.",
            })
        if factor not in DECATIPO_CONVERTERS:
            unknown_factors[r.seccion] += 1
            continue
        by_factor[factor][r.id_pregunta].append(r)

    for raw, count in unknown_factors.items():
        warnings.append({
            'tipo': 'factor_desconocido',
            'detalle': f"{count} respuesta(s) con seccion '{raw}' ignoradas en el calculo.",
        })

    expected = Counter()
    if test_ids:
        for p in pregunta_hspq.objects.filter(test_id__in=test_ids):
            expected[_normalize_factor(p.seccion)] += 1

    factors = []
    for factor in FACTOR_ORDER:
        questions = by_factor.get(factor, {})
        answered = len(questions)
        total_records = sum(len(v) for v in questions.values())
        duplicated_ids = sorted(q for q, v in questions.items() if len(v) > 1)
        expected_count = expected.get(factor) if test_ids else None

        # Con duplicados se usa la respuesta mas reciente por pregunta; no se borra nada.
        pd = sum(v[-1].valor for v in questions.values()) if questions else None

        if answered == 0:
            status = 'sin_respuestas'
        elif expected_count and answered < expected_count:
            status = 'incompleto'
        else:
            status = 'completo'

        if status == 'sin_respuestas':
            warnings.append({'tipo': 'factor_sin_respuestas', 'factor': factor,
                             'detalle': f'No hay respuestas para el factor {factor}.'})
        elif status == 'incompleto':
            warnings.append({'tipo': 'factor_incompleto', 'factor': factor,
                             'detalle': f'{answered} de {expected_count} preguntas respondidas.'})
        if expected_count is not None and expected_count == 0 and answered:
            warnings.append({'tipo': 'sin_preguntas_esperadas', 'factor': factor,
                             'detalle': f'No hay preguntas {factor} registradas para validar completitud.'})
        if duplicated_ids:
            warnings.append({'tipo': 'respuestas_duplicadas', 'factor': factor,
                             'detalle': f'Preguntas con mas de una respuesta: {duplicated_ids}.'})

        factors.append({
            'factor': factor,
            'puntuacion_directa': pd,
            'decatipo': DECATIPO_CONVERTERS[factor](pd) if pd is not None else None,
            'preguntas_respondidas': answered,
            'preguntas_esperadas': expected_count,
            'registros_totales': total_records,
            'preguntas_duplicadas': duplicated_ids,
            'estado': status,
        })

    decatipos = {f['factor']: f['decatipo'] for f in factors}
    factores_secundarios = _compute_secondary_factors(decatipos, user.sexo, warnings)
    interpretacion = _build_interpretacion(factors, factores_secundarios)

    # Datos listos para graficar el perfil HSPQ: las 13 escalas de personalidad, sin B.
    perfil_grafico = [
        {'factor': factor, 'decatipo': decatipos.get(factor)}
        for factor in SECONDARY_SOURCE_FACTORS
    ]

    completitud = [{
        'factor': f['factor'],
        'estado': f['estado'],
        'preguntas_respondidas': f['preguntas_respondidas'],
        'preguntas_esperadas': f['preguntas_esperadas'],
        'registros_totales': f['registros_totales'],
        'preguntas_duplicadas': f['preguntas_duplicadas'],
    } for f in factors]

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
            'nombre': 'HSPQ',
            'id_test': test_ids[0] if len(test_ids) == 1 else (test_ids or None),
            'total_respuestas': len(responses),
            'completitud': completitud,
        },
        'factores_primarios': interpretacion['factores_primarios'],
        'factores_secundarios': interpretacion['factores_secundarios'],
        'perfil_grafico': perfil_grafico,
        'advertencias': warnings,
        'interpretacion': interpretacion,
        'notas': [DECATIPO_SOURCE_NOTE, SECONDARY_FACTORS_SOURCE_NOTE],
    }


class HspqReportDataView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if not _can_view(request.user, user):
            return Response({'detail': 'No autorizado.'}, status=403)
        return Response(build_hspq_report(user))


class HspqReportPdfView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if not _can_view(request.user, user):
            return Response({'detail': 'No autorizado.'}, status=403)
        pdf = generate_hspq_pdf(build_hspq_report(user))
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="HSPQ_{user_id}.pdf"'
        return response
