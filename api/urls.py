from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView, \
                                            TokenRefreshView,\
                                                  TokenVerifyView)


from .views import EntrantImiti, ImitiOut


router = DefaultRouter()
router.register(r'in', EntrantImiti, basename='entrants' )
router.register(r'out', ImitiOut, basename='sortant')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view()),
    path('check/', TokenVerifyView.as_view()),
]