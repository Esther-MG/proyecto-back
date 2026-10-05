from django.urls import path,include
#from usuarios_app.api.views import usuario_list, usuario_detail
from usuarios_app.api.views import (UsuarioDetailAV, TipoUsuarioAV,
TutorDetailAV, TutorListAV,TutorCreate, TestDetailAV,
SeccionDetailAV, PreguntaSADetailAV, OpcionSADetailAV, UserListAV, GroupUsuarioAV, UserGroupView,
EncuestaAV, Respuesta1AV, Respuesta1View, TestView, SeccionView, PreguntaView, OpcionView, TestResultsView,
UserSectionResponsesView, PreguntaIppView, PreguntaIPPDetails, OpcionIppView, Respuesta2AV, Respuesta2View,
UserSectionSumView, PreguntaHSPQList, PreguntaHSPQDetails, OpcionHspqView, OpcionHspqDetailAV, Respuesta3AV, Respuesta3View, UserSectionSumViewHspq,
UserTestResultsTotal,Conversion, ResultSegundoOrden)
from usuarios_app.api.hspq_report import HspqReportDataView, HspqReportPdfView
from usuarios_app.api.dat_report import DatReportPdfView
from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
#router.register('usuarios', UsuarioListVS, basename='usuarios' )

urlpatterns = [
    path('usuarios/', UserListAV.as_view(), name='usuarios-list'),
    path('user/<int:pk>', UsuarioDetailAV.as_view(), name='usuarios-detail'),

    path('tipousuario/', GroupUsuarioAV.as_view(), name='tiposuarios-detail'),
    
    path('tutor/<int:pk>', TutorListAV.as_view(), name='tutor-list'),
    path('usuario/<int:pk>/tutor-create/', TutorCreate.as_view(), name='tutor-create'),
    path('usuario/<int:pk>/tutor/', TutorDetailAV.as_view(), name='tutor-detail'),

    path('test/', TestView.as_view(), name='test-list'),
    path('seccion/', SeccionView.as_view(), name='seccion-list'),
    path('preguntasa/', PreguntaView.as_view(), name='pregunta-list'),
    path('opcionsa/', OpcionView.as_view(), name='opcion-list'),
    path('test/<int:pk>/', TestDetailAV.as_view(), name='test-detail'),
    path('test/seccion/<int:pk>/', SeccionDetailAV.as_view(), name='test-seccion-detail'),
    path('test/seccion/pregunta/<int:pk>/', PreguntaSADetailAV.as_view(), name='test-pregunta-detail'),
    path('test/seccion/pregunta/opcion/<int:pk>/', OpcionSADetailAV.as_view(), name='pregunta-opcion-detail'),
    
    path('user_group/<int:user_id>/', UserGroupView.as_view(), name='user-group'),
    #Test vocacionales
    path('encuesta/<int:pk>', EncuestaAV.as_view(), name='encuesta'),
    path('respuestaSa/<int:opcion_pk>', Respuesta1AV.as_view(), name='respuesta1-details'),
    path('viewSa/<int:pk>', Respuesta1View.as_view(), name='respuesta1-list'),
    path('user/<int:user_id>/test-results/', UserTestResultsTotal.as_view(), name='user-test-results-total'),
    path('user/<int:user_id>/conversion/', Conversion.as_view(), name='user-test-results-conversion'),

    path('test_results/<int:user_id>/<int:apartado_id>/', TestResultsView.as_view(), name='total-verbal'),
    path('list_answers/<int:user_id>/<int:section_id>/', UserSectionResponsesView.as_view(), name='section-answers'),

    path('test/preguntaIpp/<int:pk>/', PreguntaIPPDetails.as_view(), name='test-preguntaIPP-detail'),
    path('opcionIpp/', OpcionIppView.as_view(), name='opcionIPP-detail'),
    path('respuestaIpp/<int:pregunta_pk>/<int:opcion_pk>', Respuesta2AV.as_view(), name='respuesta2-create'),
    path('viewIpp/<int:pk>', Respuesta2View.as_view(), name='respuesta2-list'),
    path('user/<int:user_id>/section_sum/', UserSectionSumView.as_view(), name='user-section-sum'),

    path('test/preguntaHspq/', PreguntaHSPQList.as_view(), name='test-preguntaHSPQ-list'),
    path('test/preguntaHspq/<int:pk>/', PreguntaHSPQDetails.as_view(), name='test-preguntaHSPQ-detail'),
    path('opcionHspq/', OpcionHspqView.as_view(), name='opcionHSPQ-detail'),
    path('opcionHspq/<int:pk>/', OpcionHspqDetailAV.as_view(), name='opcionHSPQ-detail'),
    path('respuestaHspq/<int:opcion_pk>', Respuesta3AV.as_view(), name='respuesta3-create'),
    path('viewHspq/<int:pk>', Respuesta3View.as_view(), name='respuesta3-list'),
    path('user/<int:user_id>/section_sumHspq/', UserSectionSumViewHspq.as_view(), name='user-section-sumHspq'),
    path('resultSegundo/<int:user_id>/', ResultSegundoOrden.as_view(), name='resultSegundo'),
    path('hspq/report/<int:user_id>/', HspqReportDataView.as_view(), name='hspq-report-data'),
    path('hspq/report/<int:user_id>/pdf/', HspqReportPdfView.as_view(), name='hspq-report-pdf'),
    path('dat/report/<int:user_id>/pdf/', DatReportPdfView.as_view(), name='dat-report-pdf'),

]
