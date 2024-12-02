import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TrainDataService, TrainedModel } from '../../services/train-data.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  trainedModels: TrainedModel[] = [];
  filteredModels: TrainedModel[] = [];
  searchTerm: string = '';
  selectedSort: string = '';
  sortOptions: any[] = [
    { label: 'Model ID', value: 'id' },
    { label: 'Dataset', value: 'dataset' },
    { label: 'Model', value: 'model' },
    { label: 'Created At', value: 'created_at' }
  ];
  loading: boolean = false;
  error: string | null = null;

  constructor(
    private router: Router,
    private trainDataService: TrainDataService
  ) {}

  ngOnInit(): void {
    this.loadTrainedModels();
  }

  loadTrainedModels(): void {
    this.loading = true;
    this.error = null;
    
    console.log('Starting to load trained models...');
    
    this.trainDataService.getTrainingResults().subscribe({
      next: (models: TrainedModel[]) => {
        console.log('Received models:', models);
        this.trainedModels = models;
        this.filteredModels = models;
        this.loading = false;
      },
      error: (error: Error) => {
        console.error('Error loading models:', error);
        this.error = error.message;
        this.loading = false;
      },
      complete: () => {
        console.log('Loading completed');
        console.log('Current models:', this.trainedModels);
      }
    });
  }

  filterModels(): void {
    this.filteredModels = this.trainedModels.filter(model => 
      model.model.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      model.dataset.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
    this.sortModels();
  }

  sortModels(): void {
    if (this.selectedSort) {
      this.filteredModels.sort((a: TrainedModel, b: TrainedModel) => {
        const valueA = a[this.selectedSort as keyof TrainedModel];
        const valueB = b[this.selectedSort as keyof TrainedModel];
        if (valueA < valueB) return -1;
        if (valueA > valueB) return 1;
        return 0;
      });
    }
  }

  viewModelDetails(modelId: string): void {
    this.router.navigate(['/model-details', modelId]);
  }

  navigateToTrainForm(): void {
    this.router.navigate(['/train-form']);
  }
}