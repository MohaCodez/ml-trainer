from django.test import TestCase
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Dataset, MLModel, TrainingResult
import os

class DatasetTests(APITestCase):
    def test_upload_dataset(self):
        # Create a simple CSV file
        csv_content = b"feature1,feature2,target\n1,2,3\n4,5,6"
        file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        
        # Make the upload request
        response = self.client.post('/api/datasets/upload/', {'file': file}, format='multipart')
        
        # Check if the upload was successful
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Dataset.objects.filter(name="test.csv").exists())

class MLModelTests(TestCase):
    def test_create_model(self):
        model = MLModel.objects.create(
            name="Test Model",
            model_type="linear_regression",
            hyperparameters={"fit_intercept": True}
        )
        self.assertEqual(model.name, "Test Model")
        self.assertEqual(model.model_type, "linear_regression")

class TrainingResultTests(TestCase):
    def setUp(self):
        # Create test dataset and model
        self.dataset = Dataset.objects.create(
            name="test.csv",
            file="path/to/test.csv"
        )
        self.model = MLModel.objects.create(
            name="Test Model",
            model_type="linear_regression"
        )
    
    def test_create_training_result(self):
        result = TrainingResult.objects.create(
            dataset=self.dataset,
            model=self.model,
            metrics={"r2_score": 0.95}
        )
        self.assertEqual(result.metrics["r2_score"], 0.95) 