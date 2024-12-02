import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { TrainFormComponent } from './components/train-form/train-form.component';
import { ModelComparisonComponent } from './components/model-comparison/model-comparison.component';
import { ModelDetailsComponent } from './components/model-details/model-details.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'train-form', component: TrainFormComponent },
  { path: 'model-comparison', component: ModelComparisonComponent },
  { path: 'model-details/:id', component: ModelDetailsComponent },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }