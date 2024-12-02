from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import json
from .models import TrainingJob, TrainedModel
from .serializers import TrainingJobSerializer, TrainedModelSerializer
from .ml_utils import train_model

class TrainingJobViewSet(viewsets.ModelViewSet):
    queryset = TrainingJob.objects.all()
    serializer_class = TrainingJobSerializer

    @action(detail=False, methods=['post'])
    def train(self, request):
        try:
            # Handle file upload
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Save file temporarily
            path = default_storage.save('tmp/dataset.csv', ContentFile(file.read()))
            
            # Parse training configuration
            training_data = json.loads(request.POST.get('data', '{}'))
            
            # Create training job
            training_job = TrainingJob.objects.create(
                name=training_data['name'],
                target_column=training_data['target_column'],
                status='processing'
            )

            # Read dataset
            df = pd.read_csv(default_storage.path(path))
            
            # Train models
            for model_config in training_data['models']:
                metrics = train_model(
                    data=df,
                    target_column=training_data['target_column'],
                    model_type=model_config['model_type'],
                    hyperparameters=model_config['hyperparameters']
                )
                
                TrainedModel.objects.create(
                    training_job=training_job,
                    model_type=model_config['model_type'],
                    feature=training_data['target_column'],
                    hyperparameters=model_config['hyperparameters'],
                    metrics=metrics
                )
            
            # Update job status
            training_job.status = 'completed'
            training_job.save()
            
            # Clean up
            default_storage.delete(path)
            
            return Response({
                'training_id': str(training_job.id),
                'status': 'success',
                'message': f"Successfully trained {len(training_data['models'])} models"
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True)
    def status(self, request, pk=None):
        try:
            training_job = self.get_object()
            return Response({
                'training_id': str(training_job.id),
                'status': training_job.status,
                'message': f"Training job {training_job.status}"
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrainedModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainedModel.objects.all()
    serializer_class = TrainedModelSerializer

    def get_queryset(self):
        queryset = TrainedModel.objects.all()
        
        # Filter by feature
        feature = self.request.query_params.get('feature', None)
        if feature:
            queryset = queryset.filter(feature=feature)
        
        # Filter by training job
        training_job = self.request.query_params.get('training_job', None)
        if training_job:
            queryset = queryset.filter(training_job=training_job)
        
        # Filter by model type
        model_type = self.request.query_params.get('model_type', None)
        if model_type:
            queryset = queryset.filter(model_type=model_type)
        
        return queryset

    @action(detail=True)
    def metrics(self, request, pk=None):
        model = self.get_object()
        return Response(model.metrics)

    @action(detail=False)
    def features(self, request):
        features = TrainedModel.objects.values_list('feature', flat=True).distinct()
        return Response(list(features))

    @action(detail=False)
    def model_types(self, request):
        model_types = TrainedModel.objects.values_list('model_type', flat=True).distinct()
        return Response(list(model_types)) 