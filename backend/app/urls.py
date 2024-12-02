from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingJobViewSet, TrainedModelViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'training', TrainingJobViewSet, basename='training')
router.register(r'models', TrainedModelViewSet, basename='models')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
] 