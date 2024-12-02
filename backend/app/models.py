from django.db import models
import uuid

class TrainingJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    target_column = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class TrainedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    training_job = models.ForeignKey(TrainingJob, on_delete=models.CASCADE, related_name='models')
    model_type = models.CharField(max_length=100)
    feature = models.CharField(max_length=255)
    hyperparameters = models.JSONField()
    metrics = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_type} for {self.feature}"

    class Meta:
        ordering = ['-created_at'] 