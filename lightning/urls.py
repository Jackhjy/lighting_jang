from django.urls import include, path
from rest_framework import routers
from lightning import views

#router = routers.DefaultRouter()
#router.register(r'api', views.UserViewSet)
#router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', views.DataPostAPI.as_view()),
]