from django.apps import apps
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import User
from usuarios_app.api.hspq_report import HspqReportJWTAuthentication
from usuarios_app.api.hspq_report_config import REPORT_VIEWER_GROUPS

# DAT, IPP y HSPQ. No se cuentan las filas de la tabla actual `test`.
TESTS_FIJOS = 3
# Cuando exista el modelo, el contador suma sus registros sin tocar las tablas actuales.
MODELO_TEST_GENERICO = ('usuarios_app', 'TestGenerico')

GRUPO_ADMINISTRADOR = 1
GRUPO_ESTUDIANTE = 2
GRUPO_PSICOLOGO = 3


def contar_tests_genericos():
    try:
        modelo = apps.get_model(*MODELO_TEST_GENERICO)
    except LookupError:
        return 0
    return modelo.objects.count()


def contar_usuarios_en_grupo(group_id):
    return User.objects.filter(groups__id=group_id).distinct().count()


def build_admin_home_stats():
    return {
        'total_usuarios': User.objects.count(),
        'total_estudiantes': contar_usuarios_en_grupo(GRUPO_ESTUDIANTE),
        'total_administradores': contar_usuarios_en_grupo(GRUPO_ADMINISTRADOR),
        'total_psicologos': contar_usuarios_en_grupo(GRUPO_PSICOLOGO),
        'total_tests_configurados': TESTS_FIJOS + contar_tests_genericos(),
    }


def puede_ver_home_admin(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.filter(name__in=REPORT_VIEWER_GROUPS).exists()


class AdminHomeStatsView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not puede_ver_home_admin(request.user):
            return Response({'detail': 'No autorizado.'}, status=403)
        return Response(build_admin_home_stats())
