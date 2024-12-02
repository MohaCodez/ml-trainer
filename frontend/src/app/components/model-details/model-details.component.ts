import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TrainDataService, TrainedModel } from '../../services/train-data.service';
import { Chart } from 'chart.js/auto';
import { MessageService } from 'primeng/api';

@Component({
    selector: 'app-model-details',
    templateUrl: './model-details.component.html',
    styleUrls: ['./model-details.component.scss'],
    providers: [MessageService]
})
export class ModelDetailsComponent implements OnInit {
    model: TrainedModel | null = null;
    loading: boolean = true;
    error: string | null = null;
    featureImportanceChart: any;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private trainDataService: TrainDataService,
        private messageService: MessageService
    ) {}

    ngOnInit(): void {
        const modelId = this.route.snapshot.paramMap.get('id');
        console.log('Model ID from route:', modelId);  // Debug log
        if (modelId) {
            this.loadModelDetails(modelId);
        } else {
            this.error = 'No model ID provided';
            this.loading = false;
        }
    }

    loadModelDetails(modelId: string): void {
        this.loading = true;
        this.error = null;

        this.trainDataService.getResultDetails(modelId).subscribe({
            next: (model: TrainedModel) => {
                console.log('Loaded model details:', model);
                this.model = model;
                this.loading = false;
                setTimeout(() => this.createFeatureImportanceChart(), 0);
            },
            error: (error: Error) => {
                console.error('Error loading model details:', error);
                this.error = 'Failed to load model details';
                this.loading = false;
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to load model details'
                });
            }
        });
    }

    createFeatureImportanceChart(): void {
        if (!this.model?.feature_importance) {
            console.warn('No feature importance data available');  // Debug log
            return;
        }

        const ctx = document.getElementById('featureImportanceChart') as HTMLCanvasElement;
        if (!ctx) {
            console.error('Could not find chart canvas element');  // Debug log
            return;
        }

        if (this.featureImportanceChart) {
            this.featureImportanceChart.destroy();
        }

        const features = Object.keys(this.model.feature_importance);
        const importance = Object.values(this.model.feature_importance);

        console.log('Creating chart with data:', { features, importance });  // Debug log

        this.featureImportanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: features,
                datasets: [{
                    label: 'Feature Importance',
                    data: importance,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    title: {
                        display: true,
                        text: 'Feature Importance'
                    }
                }
            }
        });
    }

    goBack(): void {
        this.router.navigate(['/']);
    }
} 