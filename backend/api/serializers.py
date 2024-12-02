from rest_framework import serializers
from .models import Dataset, MLModel, TrainingResult

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'

class MLModelSerializer(serializers.ModelSerializer):
    hyperparameters = serializers.JSONField()

    class Meta:
        model = MLModel
        fields = ['id', 'name', 'model_type', 'hyperparameters', 'created_at']

    def validate_hyperparameters(self, value):
        """
        Validate hyperparameters based on model type
        """
        model_type = self.initial_data.get('model_type')
        
        # Define valid hyperparameters for each model type
        valid_hyperparameters = {
            'linear_regression': [
                'fit_intercept',
                'normalize',
                'n_jobs'
            ],
            'random_forest': [
                'n_estimators',
                'max_depth',
                'min_samples_split',
                'min_samples_leaf',
                'max_features',
                'random_state',
                'n_jobs'
            ],
            'knn': [
                'n_neighbors',
                'weights',
                'algorithm',
                'leaf_size'
            ],
            'svr': [
                'kernel',
                'C',
                'epsilon',
                'gamma'
            ],
            'xgboost': [
                'n_estimators',
                'max_depth',
                'learning_rate',
                'subsample',
                'colsample_bytree'
            ]
        }

        if model_type not in valid_hyperparameters:
            raise serializers.ValidationError(f"Invalid model type: {model_type}")

        # Check if all provided hyperparameters are valid for the model type
        for param in value.keys():
            if param not in valid_hyperparameters[model_type]:
                raise serializers.ValidationError(
                    f"Invalid hyperparameter '{param}' for model type '{model_type}'"
                )

        return value

class TrainingResultSerializer(serializers.ModelSerializer):
    dataset_name = serializers.CharField(source='dataset.name')
    model_name = serializers.CharField(source='model.name')
    model_type = serializers.CharField(source='model.model_type')

    class Meta:
        model = TrainingResult
        fields = [
            'id',
            'dataset_name',
            'model_name',
            'model_type',
            'metrics',
            'feature_importance',
            'created_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format the data to match frontend expectations
        return {
            'id': str(data['id']),
            'dataset': data['dataset_name'],
            'model': data['model_name'],
            'metrics': data['metrics'],
            'feature_importance': data['feature_importance'],
            'created_at': data['created_at']
        } 