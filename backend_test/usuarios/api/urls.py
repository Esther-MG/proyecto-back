from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from usuarios.api.views import registration_view, logout_view, login_view, registration_admin_view, session_view, update_test_fields_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', registration_view , name='register'),
    path('registeradmin/', registration_admin_view, name='registeradmin'),
    path('logout/', logout_view, name='logout'),
    path('session/', session_view, name='session'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('update_test/<int:usuario_id>/', update_test_fields_view, name='update_test'),

]
