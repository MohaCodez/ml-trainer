import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import xgboost as xgb
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.inspection import permutation_importance

class ModelTrainer:
    def __init__(self, dataset_path, target_column, model_type, hyperparameters):
        self.dataset_path = dataset_path
        self.target_column = target_column
        self.model_type = model_type
        if model_type == 'linear_regression':
            self.hyperparameters = {k: v for k, v in hyperparameters.items() 
                                  if k not in ['normalize']}
        else:
            self.hyperparameters = hyperparameters
        
    def train_and_evaluate(self):
        # Load data
        df = pd.read_csv(self.dataset_path)
        
        # Print data info for debugging
        print("\nDataset Info:")
        print(df.info())
        print("\nMissing Values:")
        print(df.isnull().sum())

        # Drop rows where target column is null
        df_clean = df.dropna(subset=[self.target_column])
        print(f"\nRows after dropping missing target values: {len(df_clean)} (dropped {len(df) - len(df_clean)} rows)")

        if len(df_clean) < 50:  # You can adjust this threshold
            raise ValueError(f"Insufficient data after cleaning. Only {len(df_clean)} samples available.")
        
        # Prepare features and target
        X = df_clean.drop(columns=[self.target_column])
        y = df_clean[self.target_column]
        
        # Identify numeric and categorical columns
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = X.select_dtypes(include=['object', 'category']).columns
        
        print("\nNumeric features:", numeric_features.tolist())
        print("Categorical features:", categorical_features.tolist())
        
        # Create preprocessing pipelines for both numeric and categorical data
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
        ])
        
        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print(f"\nTraining set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Create and train model based on type
        if self.model_type == 'linear_regression':
            model = LinearRegression(**self.hyperparameters)
        elif self.model_type == 'random_forest':
            model = RandomForestRegressor(**self.hyperparameters)
        elif self.model_type == 'knn':
            model = KNeighborsRegressor(**self.hyperparameters)
        elif self.model_type == 'svr':
            model = SVR(**self.hyperparameters)
        elif self.model_type == 'xgboost':
            model = xgb.XGBRegressor(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        # Create a pipeline with preprocessing and model
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Make predictions
        y_pred = pipeline.predict(X_test)
        
        # Calculate metrics
        metrics = {
            'r2_score': float(r2_score(y_test, y_pred)),
            'mse': float(mean_squared_error(y_test, y_pred)),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred)))
        }
        
        print("\nModel Performance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
        
        # Create model info first
        model_info = {
            'n_features': X.shape[1],
            'n_samples_train': X_train.shape[0],
            'n_samples_test': X_test.shape[0],
            'feature_names': X.columns.tolist(),
            'numeric_features': numeric_features.tolist(),
            'categorical_features': categorical_features.tolist(),
            'missing_values': df.isnull().sum().to_dict(),
            'total_samples': len(df),
            'samples_after_cleaning': len(df_clean),
            'dropped_samples': len(df) - len(df_clean),
            'missing_values_before_cleaning': df.isnull().sum().to_dict(),
            'missing_values_after_cleaning': df_clean.isnull().sum().to_dict(),
            'feature_importance_method': 'feature_importances_' if hasattr(model, 'feature_importances_') 
                                      else 'coefficients' if hasattr(pipeline.named_steps['regressor'], 'coef_')
                                      else 'permutation' if hasattr(model, 'predict')
                                      else 'none'
        }

        # Get feature importance for models that support it
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            try:
                # Get feature names after preprocessing
                feature_names = (numeric_features.tolist() + 
                               [f"{feature}_{val}" for feature, vals in 
                                zip(categorical_features,
                                    pipeline.named_steps['preprocessor']
                                    .named_transformers_['cat']
                                    .named_steps['onehot'].categories_)
                                for val in vals[1:]])
                
                # Get feature importances
                importances = model.feature_importances_
                if len(importances) == len(feature_names):
                    feature_importance = dict(zip(feature_names, importances))
                print("\nUsing feature_importances_ method")
            except Exception as e:
                print(f"Error calculating feature importance from feature_importances_: {str(e)}")
                feature_importance = {}
        
        # For Linear Regression, calculate feature importance from coefficients
        elif hasattr(pipeline.named_steps['regressor'], 'coef_'):
            try:
                # Get feature names after preprocessing
                feature_names = (numeric_features.tolist() + 
                               [f"{feature}_{val}" for feature, vals in 
                                zip(categorical_features,
                                    pipeline.named_steps['preprocessor']
                                    .named_transformers_['cat']
                                    .named_steps['onehot'].categories_)
                                for val in vals[1:]])
                
                # Get coefficients and normalize them
                coefficients = np.abs(pipeline.named_steps['regressor'].coef_)
                normalized_coefficients = coefficients / np.sum(coefficients)
                
                if len(normalized_coefficients) == len(feature_names):
                    feature_importance = dict(zip(feature_names, normalized_coefficients))
                    
                    # Add intercept if it exists
                    if hasattr(pipeline.named_steps['regressor'], 'intercept_'):
                        feature_importance['intercept'] = float(abs(pipeline.named_steps['regressor'].intercept_))
                print("\nUsing coefficients method")
            except Exception as e:
                print(f"Error calculating feature importance from coefficients: {str(e)}")
                print(f"Coefficients shape: {coefficients.shape}")
                print(f"Feature names length: {len(feature_names)}")
                feature_importance = {}

        # For models that support permutation importance
        elif hasattr(model, 'predict'):
            try:
                # Calculate permutation importance
                r = permutation_importance(
                    pipeline, X_test, y_test,
                    n_repeats=10,
                    random_state=42
                )
                
                # Get feature names (use original feature names for permutation importance)
                feature_names = X.columns.tolist()
                
                # Normalize importance scores
                importances = np.abs(r.importances_mean)
                normalized_importances = importances / np.sum(importances)
                
                feature_importance = dict(zip(feature_names, normalized_importances))
                print("\nUsing permutation importance method")
            except Exception as e:
                print(f"Error calculating permutation importance: {str(e)}")
                feature_importance = {}

        # Add debug information
        print("\nFeature Importance Method:", model_info['feature_importance_method'])
        print("Feature Importance Values:", feature_importance)
        if not feature_importance:
            print("Warning: No feature importance calculated")
            if hasattr(pipeline.named_steps['regressor'], 'coef_'):
                print("Model has coefficients but calculation failed")
                print("Coefficients:", pipeline.named_steps['regressor'].coef_)
            if hasattr(model, 'feature_importances_'):
                print("Model has feature_importances_ but calculation failed")
                print("Feature importances:", model.feature_importances_)

        # Add additional debug info to model_info
        model_info.update({
            'has_coef': hasattr(pipeline.named_steps['regressor'], 'coef_'),
            'has_feature_importances': hasattr(model, 'feature_importances_'),
            'has_predict': hasattr(model, 'predict'),
            'model_type': self.model_type
        })

        # Prepare scatter data
        scatter_data = {
            'actual': y_test.tolist(),
            'predicted': y_pred.tolist()
        }
        
        return pipeline, metrics, feature_importance, scatter_data, model_info