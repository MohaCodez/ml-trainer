from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TrainingRequest, TrainingResponse, TrainedModel, ModelMetrics
from .database import db
from .ml_utils import train_model
import pandas as pd
import uuid
from datetime import datetime
import json
from typing import List

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_database("mongodb://localhost:27017")

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_database_connection()

@app.post("/train/", response_model=TrainingResponse)
async def train_models(file: UploadFile = File(...), data: str = File(...)):
    try:
        # Parse the training request
        training_data = json.loads(data)
        training_request = TrainingRequest(**training_data)
        
        # Read CSV file
        df = pd.read_csv(file.file)
        
        # Generate training ID
        training_id = str(uuid.uuid4())
        
        # Train models and save results
        for model_config in training_request.models:
            # Train the model
            metrics = await train_model(
                data=df,
                target_column=training_request.target_column,
                model_type=model_config.model_type,
                hyperparameters=model_config.hyperparameters
            )
            
            # Create and save trained model record
            trained_model = TrainedModel(
                id=str(uuid.uuid4()),
                trainId=training_id,
                feature=training_request.target_column,
                modelType=model_config.model_type,
                metrics=ModelMetrics(**metrics),
                timestamp=datetime.now()
            )
            
            await db.save_model(trained_model)
        
        return TrainingResponse(
            training_id=training_id,
            status="success",
            message=f"Successfully trained {len(training_request.models)} models"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=List[TrainedModel])
async def get_trained_models():
    try:
        models = await db.get_all_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/train/{training_id}/status", response_model=TrainingResponse)
async def get_training_status(training_id: str):
    try:
        # In a real application, you would check the actual training status
        # For now, we'll just return a dummy response
        return TrainingResponse(
            training_id=training_id,
            status="completed",
            message="Training completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{model_id}", response_model=TrainedModel)
async def get_model_details(model_id: str):
    try:
        model = await db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 