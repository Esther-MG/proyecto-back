#from django.shortcuts import render
#from usuarios_app.models import usuario, tipo_usuario
#from django.http import JsonResponse

# Create your views here.
#def usuariolist(request):
#    usuarios = usuario.objects.all()
#    data = {
#        'usuario': list(usuarios.values())
#    }
    
#    return JsonResponse(data)

#def usuario_detail(request, pk):
#    usuarios = usuario.objects.get(pk=pk)
#    data = {
#        'nombre': usuarios.nombre,
#        'apellido': usuarios.apellido,
#        'ci': usuarios.ci,
#    }
    
#    return JsonResponse(data)