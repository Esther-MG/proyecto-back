from django.apps import apps
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import User
from usuarios_app.models import test
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
        'total_tests_configurados': test.objects.count(),
    }


def puede_ver_home_admin(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_staff or user.is_superuser:
        return True

    nombres = {nombre.lower() for nombre in user.groups.values_list('name', flat=True)}
    return {'administrador', 'psicologo'} & nombres


class AdminHomeStatsView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not puede_ver_home_admin(request.user):
            return Response({'detail': 'No autorizado.'}, status=403)
        return Response(build_admin_home_stats())


MESES = (
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
)


def anios_disponibles():
    filas = (
        User.objects.annotate(anio=ExtractYear('date_joined'))
        .values('anio')
        .annotate(total=Count('id'))
        .order_by('anio')
    )
    return [fila['anio'] for fila in filas if fila['anio'] is not None]


def registros_por_mes(year):
    filas = (
        User.objects.filter(date_joined__year=year)
        .annotate(mes=ExtractMonth('date_joined'))
        .values('mes')
        .annotate(total=Count('id'))
    )
    totales = {fila['mes']: fila['total'] for fila in filas}
    return [
        {
            'month': mes,
            'month_name': MESES[mes - 1],
            'total': totales.get(mes, 0),
        }
        for mes in range(1, 13)
    ]


class AdminHomeRegistrationsView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not puede_ver_home_admin(request.user):
            return Response({'detail': 'No autorizado.'}, status=403)

        bruto = request.query_params.get('year')
        if bruto in (None, ''):
            year = timezone.now().year
        else:
            try:
                year = int(bruto)
            except (TypeError, ValueError):
                return Response({'detail': 'El año no es válido.'}, status=400)
            if year < 1:
                return Response({'detail': 'El año no es válido.'}, status=400)

        return Response({
            'year': year,
            'available_years': anios_disponibles(),
            'monthly_registrations': registros_por_mes(year),
        })
