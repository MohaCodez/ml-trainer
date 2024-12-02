import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface ModelMetrics {
  r2_score: number;
  mse: number;
  mae: number;
  rmse: number;
}

export interface TrainedModel {
  id: string;
  dataset: string;
  model: string;
  metrics: ModelMetrics;
  feature_importance: { [key: string]: number };
  created_at: string;
}

export interface MLModel {
  id: string;
  name: string;
  model_type: string;
  hyperparameters: { [key: string]: any };
  created_at: string;
}

export interface Dataset {
  id: string;
  name: string;
  columns: string[];
  row_count: number;
  uploaded_at: string;
}

export interface TrainingResponse {
  metrics: ModelMetrics;
  feature_importance: { [key: string]: number };
  scatter_data: {
    actual: number[];
    predicted: number[];
  };
  model_info: {
    n_features: number;
    n_samples_train: number;
    n_samples_test: number;
    feature_names: string[];
  };
}

interface ModelConfig {
  name: string;
  model_type: 'linear_regression' | 'random_forest' | 'knn' | 'svr' | 'xgboost';
  hyperparameters: LinearRegressionHyperparameters | RandomForestHyperparameters | KNNHyperparameters | SVRHyperparameters | XGBoostHyperparameters;
}

interface LinearRegressionHyperparameters {
  fit_intercept?: boolean;
  normalize?: boolean;
  n_jobs?: number;
}

interface RandomForestHyperparameters {
  n_estimators?: number;
  max_depth?: number | null;
  min_samples_split?: number;
  min_samples_leaf?: number;
  max_features?: 'auto' | 'sqrt' | 'log2' | number;
  random_state?: number;
  n_jobs?: number;
}

interface KNNHyperparameters {
  n_neighbors?: number;
  weights?: 'uniform' | 'distance';
  algorithm?: 'auto' | 'ball_tree' | 'kd_tree' | 'brute';
  leaf_size?: number;
}

interface SVRHyperparameters {
  kernel?: 'linear' | 'poly' | 'rbf' | 'sigmoid';
  C?: number;
  epsilon?: number;
  gamma?: 'scale' | 'auto' | number;
}

interface XGBoostHyperparameters {
  n_estimators?: number;
  max_depth?: number;
  learning_rate?: number;
  subsample?: number;
  colsample_bytree?: number;
}

@Injectable({
  providedIn: 'root'
})
export class TrainDataService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // Dataset endpoints
  uploadDataset(file: File): Observable<Dataset> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<Dataset>(`${this.apiUrl}/datasets/upload/`, formData).pipe(
      catchError(this.handleError('upload dataset'))
    );
  }

  getDatasets(): Observable<Dataset[]> {
    return this.http.get<Dataset[]>(`${this.apiUrl}/datasets/`).pipe(
      catchError(this.handleError('fetch datasets'))
    );
  }

  // Model endpoints
  getModels(): Observable<MLModel[]> {
    return this.http.get<MLModel[]>(`${this.apiUrl}/models/`).pipe(
      catchError(this.handleError('fetch models'))
    );
  }

  // Results endpoints
  getTrainingResults(): Observable<TrainedModel[]> {
    console.log('Fetching training results from:', `${this.apiUrl}/results/`);
    return this.http.get<TrainedModel[]>(`${this.apiUrl}/results/`).pipe(
      tap(results => console.log('Received results:', results)),
      catchError(error => {
        console.error('Error details:', {
          status: error.status,
          statusText: error.statusText,
          message: error.message,
          error: error.error
        });
        return throwError(() => new Error(this.getErrorMessage(error)));
      })
    );
  }

  getResultDetails(resultId: string): Observable<TrainedModel> {
    console.log('Fetching details for model:', resultId);
    return this.http.get<TrainedModel>(`${this.apiUrl}/results/${resultId}/`).pipe(
      tap(result => console.log('Received model details:', result)),
      catchError(this.handleError('fetch model details'))
    );
  }

  // Multi-model training endpoint
  trainMultipleModels(file: File, models: ModelConfig[], targetColumns: string[]): Observable<any> {
    console.log('Training models with:', { file, models, targetColumns });
    const formData = new FormData();
    formData.append('file', file);
    formData.append('models', JSON.stringify(models));
    formData.append('target_columns', JSON.stringify(targetColumns));

    return this.http.post(`${this.apiUrl}/train/`, formData).pipe(
      tap(response => console.log('Training response:', response)),
      catchError(error => {
        console.error('Training error details:', error);
        return throwError(() => new Error(this.getErrorMessage(error)));
      })
    );
  }

  private handleError(operation: string) {
    return (error: any): Observable<never> => {
      console.error(`Error during ${operation}:`, error);
      if (error.status === 0) {
        return throwError(() => new Error('Connection refused. Is the server running?'));
      } else if (error.status === 404) {
        return throwError(() => new Error(`Resource not found`));
      }
      return throwError(() => new Error(error.error?.error || `Failed to ${operation}`));
    };
  }

  private getErrorMessage(error: any): string {
    if (error.status === 0) {
      return 'Server is not responding. Please check if it is running.';
    }
    if (error.status === 404) {
      return 'Resource not found.';
    }
    return error.error?.message || error.message || 'An unknown error occurred';
  }
}
