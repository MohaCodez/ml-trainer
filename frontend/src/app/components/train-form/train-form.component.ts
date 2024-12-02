import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { TrainDataService } from '../../services/train-data.service';
import { MessageService } from 'primeng/api';

type ModelType = 'linear_regression' | 'random_forest' | 'knn' | 'svr' | 'xgboost';

interface HyperParameter {
  name: string;
  type: string;
  default: any;
  min?: number;
  max?: number;
  step?: number;
  options?: DropdownOption[];
}

interface DropdownOption {
  label: string;
  value: any;
}

@Component({
  selector: 'app-train-form',
  templateUrl: './train-form.component.html',
  styleUrls: ['./train-form.component.scss'],
  providers: [MessageService]
})
export class TrainFormComponent implements OnInit {
  trainForm!: FormGroup;
  selectedFile: File | null = null;
  availableColumns: { label: string; value: string }[] = [];
  loading = false;

  modelTypes = [
    { label: 'Linear Regression', value: 'linear_regression' },
    { label: 'Random Forest', value: 'random_forest' },
    { label: 'K-Nearest Neighbors', value: 'knn' },
    { label: 'Support Vector Regression', value: 'svr' },
    { label: 'XGBoost', value: 'xgboost' }
  ];

  maxFeaturesOptions: DropdownOption[] = [
    { label: 'Auto', value: 'auto' },
    { label: 'Sqrt', value: 'sqrt' },
    { label: 'Log2', value: 'log2' }
  ];

  weightsOptions: DropdownOption[] = [
    { label: 'Uniform', value: 'uniform' },
    { label: 'Distance', value: 'distance' }
  ];

  algorithmOptions: DropdownOption[] = [
    { label: 'Auto', value: 'auto' },
    { label: 'Ball Tree', value: 'ball_tree' },
    { label: 'KD Tree', value: 'kd_tree' },
    { label: 'Brute Force', value: 'brute' }
  ];

  kernelOptions: DropdownOption[] = [
    { label: 'RBF', value: 'rbf' },
    { label: 'Linear', value: 'linear' },
    { label: 'Polynomial', value: 'poly' },
    { label: 'Sigmoid', value: 'sigmoid' }
  ];

  hyperparameterOptions: { [key in ModelType]: HyperParameter[] } = {
    linear_regression: [
      { name: 'fit_intercept', type: 'boolean', default: true },
      { name: 'n_jobs', type: 'number', default: -1, min: -1, max: 8 }
    ],
    random_forest: [
      { name: 'n_estimators', type: 'number', default: 100, min: 10, max: 1000 },
      { name: 'max_depth', type: 'number', default: 20, min: 1, max: 100 },
      { name: 'min_samples_split', type: 'number', default: 2, min: 2, max: 20 },
      { name: 'min_samples_leaf', type: 'number', default: 1, min: 1, max: 10 },
      { name: 'max_features', type: 'select', default: 'sqrt', options: this.maxFeaturesOptions },
      { name: 'random_state', type: 'number', default: 42, min: 0, max: 100 }
    ],
    knn: [
      { name: 'n_neighbors', type: 'number', default: 5, min: 1, max: 20 },
      { name: 'weights', type: 'select', default: 'uniform', options: this.weightsOptions },
      { name: 'algorithm', type: 'select', default: 'auto', options: this.algorithmOptions },
      { name: 'leaf_size', type: 'number', default: 30, min: 1, max: 100 }
    ],
    svr: [
      { name: 'kernel', type: 'select', default: 'rbf', options: this.kernelOptions },
      { name: 'C', type: 'number', default: 1.0, min: 0.1, max: 10.0, step: 0.1 },
      { name: 'epsilon', type: 'number', default: 0.1, min: 0.01, max: 1.0, step: 0.01 },
      { name: 'gamma', type: 'string', default: 'scale' }
    ],
    xgboost: [
      { name: 'n_estimators', type: 'number', default: 100, min: 10, max: 1000 },
      { name: 'max_depth', type: 'number', default: 6, min: 1, max: 20 },
      { name: 'learning_rate', type: 'number', default: 0.3, min: 0.01, max: 1.0, step: 0.01 },
      { name: 'subsample', type: 'number', default: 1.0, min: 0.1, max: 1.0, step: 0.1 },
      { name: 'colsample_bytree', type: 'number', default: 1.0, min: 0.1, max: 1.0, step: 0.1 }
    ]
  };

  constructor(
    private fb: FormBuilder,
    private trainDataService: TrainDataService,
    private messageService: MessageService
  ) {
    this.trainForm = this.fb.group({
      models: this.fb.array([]),
      target_columns: [[]],
      file: [null]
    });
  }

  ngOnInit(): void {
    this.addModel();
  }

  get models(): FormArray {
    return this.trainForm.get('models') as FormArray;
  }

  addModel(): void {
    const modelForm = this.fb.group({
      name: [''],
      model_type: [''],
      hyperparameters: this.fb.group({})
    });

    modelForm.get('model_type')?.valueChanges.subscribe((type: string | null) => {
      if (type && Object.keys(this.hyperparameterOptions).includes(type)) {
        this.updateHyperparameters(modelForm, type as ModelType);
      }
    });

    this.models.push(modelForm);
  }

  removeModel(index: number): void {
    this.models.removeAt(index);
  }

  updateHyperparameters(modelForm: FormGroup, modelType: ModelType): void {
    const hyperParams = this.fb.group({});
    
    this.getHyperparameters(modelType).forEach(param => {
      hyperParams.addControl(param.name, this.fb.control(param.default));
    });

    modelForm.setControl('hyperparameters', hyperParams);
    modelForm.patchValue({
      name: `${modelType} Model`
    });
  }

  getHyperparameters(modelType: ModelType): HyperParameter[] {
    return this.hyperparameterOptions[modelType] || [];
  }

  onFileSelect(event: any): void {
    const file = event.files[0];
    if (file) {
      this.selectedFile = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const headers = text.split('\n')[0].split(',');
        this.availableColumns = headers.map(h => ({
          label: h.trim(),
          value: h.trim()
        }));
      };
      reader.readAsText(file);
    }
  }

  onSubmit(): void {
    if (!this.selectedFile) {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Please select a file'
      });
      return;
    }

    const formValue = this.trainForm.value;
    if (!formValue.target_columns || formValue.target_columns.length === 0) {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Please select at least one target column'
      });
      return;
    }

    this.loading = true;
    console.log('Submitting form with values:', formValue);

    this.trainDataService.trainMultipleModels(
      this.selectedFile,
      formValue.models,
      formValue.target_columns
    ).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Models trained successfully'
        });
        console.log('Training response:', response);
      },
      error: (error: any) => {
        this.loading = false;
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.message || 'Failed to train models'
        });
        console.error('Training error:', error);
      }
    });
  }

  getParamMin(param: HyperParameter): number {
    return param.min ?? 0;
  }

  getParamMax(param: HyperParameter): number {
    return param.max ?? 100;
  }

  getParamStep(param: HyperParameter): number {
    return param.step ?? 1;
  }

  getParamOptions(param: HyperParameter): DropdownOption[] {
    return param.options ?? [];
  }
}