import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

// PrimeNG Imports
import { FileUploadModule } from 'primeng/fileupload';
import { MultiSelectModule } from 'primeng/multiselect';
import { DropdownModule } from 'primeng/dropdown';
import { InputSwitchModule } from 'primeng/inputswitch';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { TableModule } from 'primeng/table';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { MessagesModule } from 'primeng/messages';
import { CardModule } from 'primeng/card';
import { ChartModule } from 'primeng/chart';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import { TrainFormComponent } from './components/train-form/train-form.component';
import { ModelDetailsComponent } from './components/model-details/model-details.component';
import { ModelComparisonComponent } from './components/model-comparison/model-comparison.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    TrainFormComponent,
    ModelDetailsComponent,
    ModelComparisonComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    FileUploadModule,
    MultiSelectModule,
    DropdownModule,
    InputSwitchModule,
    InputNumberModule,
    InputTextModule,
    ButtonModule,
    ToastModule,
    TableModule,
    ProgressSpinnerModule,
    MessageModule,
    MessagesModule,
    CardModule,
    ChartModule
  ],
  providers: [MessageService],
  bootstrap: [AppComponent]
})
export class AppModule { }