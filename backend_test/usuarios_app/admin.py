from django.contrib import admin
from usuarios_app.models import tutor, test, seccion, pregunta_sa, opcion_sa, encuesta, respuesta1, pregunta_ipp, opcion_ipp, respuesta2, pregunta_hspq, opcion_hspq, respuesta3
# Register your models here.
admin.site.register(test)
admin.site.register(seccion)
admin.site.register(pregunta_sa)
admin.site.register(opcion_sa)
admin.site.register(tutor)
admin.site.register(encuesta)
admin.site.register(respuesta1)
admin.site.register(pregunta_ipp)
admin.site.register(opcion_ipp)
admin.site.register(respuesta2)
admin.site.register(pregunta_hspq)
admin.site.register(opcion_hspq)
admin.site.register(respuesta3)
