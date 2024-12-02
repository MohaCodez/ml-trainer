import os
from django.db import models
from django.conf import settings

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    columns = models.JSONField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class MLModel(models.Model):
    MODEL_CHOICES = [
        ('linear_regression', 'Linear Regression'),
        ('random_forest', 'Random Forest'),
        ('knn', 'K-Nearest Neighbors'),
        ('svr', 'Support Vector Regression'),
        ('xgboost', 'XGBoost'),
    ]
    
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=50, choices=MODEL_CHOICES)
    hyperparameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.model_type})"

    class Meta:
        ordering = ['-created_at']

class TrainingResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    metrics = models.JSONField(default=dict)
    feature_importance = models.JSONField(null=True, blank=True)
    model_file = models.FileField(upload_to='trained_models/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.model.name} on {self.dataset.name}" 