from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import json
from .models import Dataset, MLModel, TrainingResult
from .serializers import DatasetSerializer, MLModelSerializer, TrainingResultSerializer
from .ml_utils import ModelTrainer
import logging

logger = logging.getLogger(__name__)

class BaseViewSet(viewsets.ModelViewSet):
    def get_success_headers(self):
        """Add CORS headers to all responses"""
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, DELETE',
            'Access-Control-Allow-Headers': '*',
        }
        return headers

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        for key, value in self.get_success_headers().items():
            response[key] = value
        return response

    def options(self, request, *args, **kwargs):
        """Handle preflight requests"""
        return Response(
            {},
            status=status.HTTP_200_OK,
            headers=self.get_success_headers()
        )

class DatasetViewSet(BaseViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    
    @action(detail=False, methods=['POST'])
    def upload(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Validate file format
        if not file_obj.name.endswith('.csv'):
            return Response({'error': 'Only CSV files are supported'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read CSV file
            df = pd.read_csv(file_obj)
            
            # Create dataset instance
            dataset = Dataset.objects.create(
                name=file_obj.name,
                file=file_obj,
                columns=df.columns.tolist(),
                row_count=len(df)
            )
            
            serializer = self.get_serializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MLModelViewSet(BaseViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    
    @action(detail=True, methods=['POST'])
    def train(self, request, pk=None):
        model = self.get_object()
        dataset_id = request.data.get('dataset_id')
        target_column = request.data.get('target_column')
        
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            trainer = ModelTrainer(
                dataset_path=dataset.file.path,
                target_column=target_column,
                model_type=model.model_type,
                hyperparameters=model.hyperparameters
            )
            
            # Train and evaluate the model
            trained_model, metrics, feature_importance, scatter_data, model_info = trainer.train_and_evaluate()
            
            # Save the trained model
            model_filename = f'trained_models/{model.name}_{dataset.name}.pkl'
            os.makedirs('trained_models', exist_ok=True)
            with open(model_filename, 'wb') as f:
                pickle.dump(trained_model, f)
            
            # Create training result
            result = TrainingResult.objects.create(
                dataset=dataset,
                model=model,
                metrics=metrics,
                feature_importance=feature_importance,
                model_file=model_filename
            )
            
            # Prepare response data
            response_data = {
                'metrics': metrics,
                'feature_importance': feature_importance,
                'scatter_data': scatter_data,
                'model_info': model_info
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TrainingResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainingResult.objects.all().order_by('-created_at')
    serializer_class = TrainingResultSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            logger.info(f"Found {queryset.count()} training results")
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data
            logger.info(f"Sending response with {len(response_data)} results")
            
            # Add CORS headers
            response = Response(response_data)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "*"
            return response
        except Exception as e:
            logger.error(f"Error in list view: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        try:
            result = self.get_object()
            logger.info(f"Fetching details for model {pk}")
            serializer = self.get_serializer(result)
            response = Response(serializer.data)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "*"
            return response
        except Exception as e:
            logger.error(f"Error fetching model {pk}: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST', 'OPTIONS'])
def train_multiple_models(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': '*',
        }
        return Response({}, status=status.HTTP_200_OK, headers=headers)

    try:
        # Handle file upload
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file is CSV
        if not file.name.endswith('.csv'):
            return Response({'error': 'Only CSV files are supported'}, status=status.HTTP_400_BAD_REQUEST)

        # Save file temporarily
        path = default_storage.save('tmp/dataset.csv', ContentFile(file.read()))
        
        try:
            # Read the dataset first to validate
            df = pd.read_csv(default_storage.path(path))
            
            # Validate target columns exist in dataset
            target_columns = json.loads(request.POST.get('target_columns', '[]'))
            missing_columns = [col for col in target_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'Target columns not found in dataset: {missing_columns}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if target columns have enough non-null values
            for col in target_columns:
                non_null_count = df[col].count()
                if non_null_count < 50:  # You can adjust this threshold
                    return Response(
                        {'error': f'Insufficient data for target column {col}. Only {non_null_count} non-null values available.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Read the models and target columns from the request
            models = json.loads(request.POST.get('models', '[]'))
            target_columns = json.loads(request.POST.get('target_columns', '[]'))
            
            print("Models config:", models)
            
            # Read the dataset
            df = pd.read_csv(default_storage.path(path))
            
            results = []
            # Create dataset record
            dataset = Dataset.objects.create(
                name=file.name,
                file=file,
                columns=df.columns.tolist(),
                row_count=len(df)
            )
            print(f"Dataset created: {dataset.id}")

            for model_config in models:
                # Validate hyperparameters before creating model
                serializer = MLModelSerializer(data={
                    'name': model_config['name'],
                    'model_type': model_config['model_type'],
                    'hyperparameters': model_config['hyperparameters']
                })
                
                if not serializer.is_valid():
                    return Response(
                        {'error': f"Invalid model configuration: {serializer.errors}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                ml_model = serializer.save()
                print(f"ML Model created: {ml_model.id} ({ml_model.name})")

                for target in target_columns:
                    print(f"Training for target: {target}")
                    trainer = ModelTrainer(
                        dataset_path=default_storage.path(path),
                        target_column=target,
                        model_type=model_config['model_type'],
                        hyperparameters=model_config['hyperparameters']
                    )
                    
                    model, metrics, feature_importance, scatter_data, model_info = trainer.train_and_evaluate()
                    
                    result = TrainingResult.objects.create(
                        dataset=dataset,
                        model=ml_model,
                        metrics=metrics,
                        feature_importance=feature_importance
                    )
                    print(f"Training result created: {result.id}")
                    
                    results.append({
                        'id': str(result.id),
                        'dataset': dataset.name,
                        'model': ml_model.name,
                        'metrics': metrics,
                        'feature_importance': feature_importance,
                        'model_info': model_info
                    })
            
            print(f"Total results created: {len(results)}")
            response = Response(results, status=status.HTTP_201_CREATED)
            response['Access-Control-Allow-Origin'] = '*'
            return response
            
        finally:
            # Clean up temporary file
            default_storage.delete(path)
            
    except Exception as e:
        print(f"Error in train_multiple_models: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET', 'OPTIONS'])
def debug_database(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': '*',
        }
        return Response({}, status=status.HTTP_200_OK, headers=headers)

    try:
        datasets = Dataset.objects.all()
        models = MLModel.objects.all()
        results = TrainingResult.objects.all()
        
        return Response({
            'datasets': [
                {
                    'id': str(d.id),
                    'name': d.name,
                    'row_count': d.row_count
                } for d in datasets
            ],
            'models': [
                {
                    'id': str(m.id),
                    'name': m.name,
                    'type': m.model_type
                } for m in models
            ],
            'results': [
                {
                    'id': str(r.id),
                    'dataset': r.dataset.name,
                    'model': r.model.name,
                    'metrics': r.metrics
                } for r in results
            ]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)