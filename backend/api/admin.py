from django.contrib import admin
from .models import Dataset, MLModel, TrainingResult

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at', 'row_count')
    search_fields = ('name',)

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'created_at')
    list_filter = ('model_type',)
    search_fields = ('name',)

@admin.register(TrainingResult)
class TrainingResultAdmin(admin.ModelAdmin):
    list_display = ('model', 'dataset', 'created_at')
    list_filter = ('model__model_type',)
    search_fields = ('model__name', 'dataset__name') 