from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np
import pandas as pd
from typing import Dict, Any

MODEL_CLASSES = {
    'linear_regression': LinearRegression,
    'svr': SVR,
    'random_forest': RandomForestRegressor,
    'xgboost': XGBRegressor,
    'knn': KNeighborsRegressor
}

def train_model(
    data: pd.DataFrame,
    target_column: str,
    model_type: str,
    hyperparameters: Dict[str, Any]
) -> Dict[str, float]:
    # Prepare data
    X = data.drop(columns=[target_column])
    y = data[target_column]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Get model class and instantiate with hyperparameters
    model_class = MODEL_CLASSES[model_type]
    model = model_class(**hyperparameters)
    
    # Train model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'r2_score': float(r2_score(y_test, y_pred)),
        'mse': float(mean_squared_error(y_test, y_pred)),
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred)))
    }
    
    return metrics 