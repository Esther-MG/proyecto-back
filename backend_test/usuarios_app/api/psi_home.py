from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import User
from usuarios_app.api.admin_home_stats import puede_ver_home_admin
from usuarios_app.api.hspq_report import HspqReportJWTAuthentication
from usuarios_app.models import respuesta1, respuesta2, respuesta3

# Mismo contrato de grupos que el Home del administrador: 2 = Estudiante.
GRUPO_ESTUDIANTE = 2

# Cantidad exacta de filas que cuenta como test terminado.
REFERENCIAS = (
    ('dat', respuesta1, 1, 370),
    ('ipp', respuesta2, 2, 204),
    ('hspq', respuesta3, 3, 140),
)

CRITERIO_COMPLETO = (
    'Un estudiante termina un test cuando tiene exactamente la cantidad de respuestas '
    'de referencia: DAT 370, IPP 204 y HSPQ 140. Si tiene menos, o cualquier otra '
    'cantidad, queda pendiente.'
)


def _conteo_por_estudiante(modelo, test_id, estudiantes):
    """Cuenta filas del test indicado, solo de los estudiantes del grupo 2."""
    filas = (
        modelo.objects.filter(id_test=test_id, usuario_id__in=estudiantes)
        .values('usuario_id')
        .annotate(total=Count('id'))
    )
    return {fila['usuario_id']: fila['total'] for fila in filas}


def _bloque(conteos, estudiantes, esperado):
    terminados = {
        usuario_id for usuario_id in estudiantes
        if conteos.get(usuario_id, 0) == esperado
    }
    return terminados, {
        'terminados': len(terminados),
        'pendientes': len(estudiantes) - len(terminados),
        'respuestas_esperadas': esperado,
    }


def build_psicologo_home_stats():
    estudiantes = set(
        User.objects.filter(groups__id=GRUPO_ESTUDIANTE).values_list('id', flat=True).distinct()
    )
    completos = {}
    bloques = {}
    for nombre, modelo, test_id, esperado in REFERENCIAS:
        terminados, bloque = _bloque(
            _conteo_por_estudiante(modelo, test_id, estudiantes),
            estudiantes,
            esperado,
        )
        completos[nombre] = terminados
        bloques[nombre] = bloque

    tres_total = len(completos['dat'] & completos['ipp'] & completos['hspq'])
    pendiente_total = len(estudiantes) - tres_total
    return {
        'total_estudiantes': len(estudiantes),
        'evaluaciones_completas': tres_total,
        'evaluaciones_pendientes': pendiente_total,
        'estudiantes_tres_tests_terminados': tres_total,
        'estudiantes_con_pendiente': pendiente_total,
        'finalizacion_disponible': True,
        'criterio': CRITERIO_COMPLETO,
        'motivo': None,
        'instrumentos': bloques,
        'tests': bloques,
    }


class PsicologoHomeStatsView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not puede_ver_home_admin(request.user):
            return Response({'detail': 'No autorizado.'}, status=403)
        return Response(build_psicologo_home_stats())
