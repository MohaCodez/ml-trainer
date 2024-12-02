# ML Model Comparator Backend

A Django-based backend system for comparing different machine learning models.

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Datasets
- `GET /api/datasets/` - List all datasets
- `POST /api/datasets/upload/` - Upload a new dataset
- `GET /api/datasets/{id}/` - Retrieve dataset details

### Models
- `GET /api/models/` - List all ML models
- `POST /api/models/` - Create a new ML model
- `POST /api/models/{id}/train/` - Train a model on a dataset

### Results
- `GET /api/results/` - List all training results
- `GET /api/results/{id}/` - Retrieve specific training result

## Directory Structure 