from rest_framework import serializers
from .models import TrainingJob, TrainedModel

class TrainedModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainedModel
        fields = ['id', 'training_job', 'model_type', 'feature', 'hyperparameters', 'metrics', 'created_at']

class TrainingJobSerializer(serializers.ModelSerializer):
    models = TrainedModelSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingJob
        fields = ['id', 'name', 'target_column', 'status', 'models', 'created_at', 'updated_at'] 