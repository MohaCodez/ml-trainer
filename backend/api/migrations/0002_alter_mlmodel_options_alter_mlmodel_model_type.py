# Generated by Django 5.0.2 on 2024-11-29 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mlmodel',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='mlmodel',
            name='model_type',
            field=models.CharField(choices=[('linear_regression', 'Linear Regression'), ('random_forest', 'Random Forest'), ('knn', 'K-Nearest Neighbors'), ('svr', 'Support Vector Regression'), ('xgboost', 'XGBoost')], max_length=50),
        ),
    ]
