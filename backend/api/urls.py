from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DatasetViewSet, 
    MLModelViewSet, 
    TrainingResultViewSet,
    train_multiple_models,
    debug_database
)

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet)
router.register(r'models', MLModelViewSet)
router.register(r'results', TrainingResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('train/', train_multiple_models, name='train-multiple-models'),
    path('debug/', debug_database, name='debug-database'),
] 