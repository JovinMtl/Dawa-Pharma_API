from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView, \
                                            TokenRefreshView,\
                                                  TokenVerifyView)



urlpatterns = [
    path("admin/", admin.site.urls),
]