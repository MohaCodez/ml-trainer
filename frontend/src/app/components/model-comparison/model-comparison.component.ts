import { Component, OnInit } from '@angular/core';
import { Chart, ChartConfiguration, RadialLinearScale, LineElement, PointElement, RadarController } from 'chart.js';
import { TrainDataService, TrainedModel } from '../../services/train-data.service';

Chart.register(RadarController, RadialLinearScale, LineElement, PointElement);

@Component({
  selector: 'app-model-comparison',
  templateUrl: './model-comparison.component.html',
  styleUrls: ['./model-comparison.component.scss']
})
export class ModelComparisonComponent implements OnInit {
  metrics: string[] = ['R² Score', 'MSE', 'MAE', 'RMSE'];
  selectedMetric: string = 'R² Score';
  barChart: any;
  radarChart: any;
  results: TrainedModel[] = [];
  filteredResults: TrainedModel[] = [];
  uniqueDatasets: string[] = [];
  uniqueModelTypes: string[] = [];
  selectedDataset: string = '';
  selectedModelType: string = '';

  constructor(private trainDataService: TrainDataService) {}

  ngOnInit(): void {
    this.loadModels();
  }

  loadModels(): void {
    this.trainDataService.getTrainingResults().subscribe({
      next: (models: TrainedModel[]) => {
        this.results = models;
        this.filteredResults = models;
        this.updateFilters();
        this.createCharts();
      },
      error: (error: Error) => {
        console.error('Error loading models:', error);
      }
    });
  }

  updateFilters(): void {
    this.uniqueDatasets = [...new Set(this.results.map(model => model.dataset))];
    this.uniqueModelTypes = [...new Set(this.results.map(model => model.model))];
  }

  filterModels(): void {
    this.filteredResults = this.results.filter(model => {
      const datasetMatch = !this.selectedDataset || model.dataset === this.selectedDataset;
      const modelMatch = !this.selectedModelType || model.model === this.selectedModelType;
      return datasetMatch && modelMatch;
    });
    this.createCharts();
  }

  createCharts(): void {
    this.createBarChart();
    this.createRadarChart();
  }

  createBarChart(): void {
    const ctx = document.getElementById('barChart') as HTMLCanvasElement;
    if (this.barChart) {
      this.barChart.destroy();
    }

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: this.filteredResults.map(model => `${model.model} (${model.dataset})`),
        datasets: [
          {
            label: 'R² Score',
            data: this.filteredResults.map(model => model.metrics.r2_score),
            backgroundColor: this.getBackgroundColor(0, 0.7),
            borderColor: this.getBackgroundColor(0, 1),
            borderWidth: 1,
            borderRadius: 4,
            barThickness: 20
          },
          {
            label: 'RMSE',
            data: this.filteredResults.map(model => model.metrics.rmse),
            backgroundColor: this.getBackgroundColor(1, 0.7),
            borderColor: this.getBackgroundColor(1, 1),
            borderWidth: 1,
            borderRadius: 4,
            barThickness: 20
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Model Performance Metrics',
            font: {
              size: 16,
              weight: 'bold',
              family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
            },
            padding: 20
          },
          legend: {
            position: 'top',
            align: 'center',
            labels: {
              padding: 20,
              usePointStyle: true,
              pointStyle: 'circle',
              font: {
                size: 12,
                family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              size: 13,
              family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
            },
            bodyFont: {
              size: 12,
              family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
            },
            padding: 12,
            cornerRadius: 6,
            displayColors: true
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              font: {
                size: 11,
                family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 11,
                family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
              },
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    };

    this.barChart = new Chart(ctx, config);
  }

  createRadarChart(): void {
    const ctx = document.getElementById('radarChart') as HTMLCanvasElement;
    if (this.radarChart) {
      this.radarChart.destroy();
    }

    const config: ChartConfiguration = {
      type: 'radar',
      data: {
        labels: ['R² Score', 'MSE', 'MAE', 'RMSE'],
        datasets: this.filteredResults.map((result, index) => ({
          label: `${result.model} (${result.dataset})`,
          data: [
            result.metrics.r2_score,
            result.metrics.mse,
            result.metrics.mae,
            result.metrics.rmse
          ],
          backgroundColor: this.getBackgroundColor(index, 0.2),
          borderColor: this.getBackgroundColor(index, 1),
          borderWidth: 2,
          pointBackgroundColor: this.getBackgroundColor(index, 1),
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: this.getBackgroundColor(index, 1),
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: true
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Model Performance Comparison',
            font: {
              size: 16,
              weight: 'bold',
              family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
            },
            padding: 20
          },
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              pointStyle: 'circle',
              font: {
                size: 12,
                family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              size: 13,
              family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
            },
            bodyFont: {
              size: 12,
              family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
            },
            padding: 12,
            cornerRadius: 6,
            displayColors: true
          }
        },
        scales: {
          r: {
            min: 0,
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.1)',
            },
            angleLines: {
              color: 'rgba(0, 0, 0, 0.1)',
            },
            pointLabels: {
              font: {
                size: 12,
                family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                weight: 'bold'
              }
            },
            ticks: {
              backdropColor: 'transparent',
              font: {
                size: 10
              }
            }
          }
        }
      }
    };

    this.radarChart = new Chart(ctx, config);
  }

  private getBackgroundColor(index: number, alpha: number): string {
    const colors = [
      `rgba(54, 162, 235, ${alpha})`,   // Blue
      `rgba(255, 99, 132, ${alpha})`,   // Red
      `rgba(75, 192, 192, ${alpha})`,   // Teal
      `rgba(255, 159, 64, ${alpha})`,   // Orange
      `rgba(153, 102, 255, ${alpha})`,  // Purple
      `rgba(255, 205, 86, ${alpha})`,   // Yellow
      `rgba(201, 203, 207, ${alpha})`,  // Grey
      `rgba(0, 150, 136, ${alpha})`,    // Teal
      `rgba(233, 30, 99, ${alpha})`,    // Pink
      `rgba(156, 39, 176, ${alpha})`    // Purple
    ];
    return colors[index % colors.length];
  }
}