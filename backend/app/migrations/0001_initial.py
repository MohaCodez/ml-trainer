from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('target_column', models.CharField(max_length=255)),
                ('status', models.CharField(default='pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrainedModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('model_type', models.CharField(max_length=100)),
                ('feature', models.CharField(max_length=255)),
                ('hyperparameters', models.JSONField()),
                ('metrics', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('training_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='app.trainingjob')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ] 