import { Component, ElementRef, model, OnInit, ViewChild } from '@angular/core';
import { TableModule } from 'primeng/table';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { SplitButtonModule } from 'primeng/splitbutton';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { FormsModule } from '@angular/forms';;
import { FileUploadModule } from 'primeng/fileupload';
import { RippleModule } from 'primeng/ripple';
import { ApiService } from '../../../core/services/api.service';
import { FileUpload } from 'primeng/fileupload';
import { MessageService } from 'primeng/api';
import { ConfirmationService } from 'primeng/api';
import { Model } from '../../../models/model.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-admin-model',
  imports: [
    TableModule,
    ToolbarModule,
    ButtonModule,
    IconFieldModule,
    InputIconModule,
    SplitButtonModule,
    InputTextModule,
    CheckboxModule,
    FormsModule,
    FileUploadModule,
    RippleModule,
  ],
  templateUrl: './admin-model.component.html',
  styleUrl: './admin-model.component.css'
})
export class AdminModelComponent implements OnInit {
  @ViewChild('fu', { static: false }) fileUploader!: FileUpload;

  models: Model[] = [];
  selectedModels: any[] = [];
  selectedFiles: File[] = [];

  firstElement: number = 0;
  rowsPerPage: number = 10;
  expandedRows: { [key: string]: boolean } = {};

  constructor(
    private apiService: ApiService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService,
  ) { }

  ngOnInit() {
    this.getModels();
    // this.getProcesses();
  }

  onPageChange(event: any) {
    this.firstElement = event.first;
    this.rowsPerPage = event.rows;
    console.log(event)
    console.log('Current Page:', this.firstElement);
    console.log('Rows Per Page:', this.rowsPerPage);

    this.loadUsers(this.firstElement, this.rowsPerPage);
  }

  loadUsers(firstElement: number, size: number) {
    console.log(`Fetching ${firstElement}-${firstElement + size - 1}`);
  }

  onFileSelected(event: any) {
    this.selectedFiles = event.files;
    console.log('Selected Files:', this.selectedFiles);
  }

  uploadFile() {
    const formData = new FormData();

    for (let i = 0; i < this.selectedFiles.length; i++) {
      formData.append('files[]', this.selectedFiles[i], this.selectedFiles[i].name);
    }

    const headers = {}
    this.apiService.post('v1/models', formData, headers, true).subscribe({
      next: (response) => {
        console.log('Upload successful:', response)
        this.messageService.add({ severity: 'success', summary: 'Upload successful', detail: 'Your file has been uploaded successfully.' });
        this.getModels();
      },
      error: (error) => {
        console.error('Upload failed:', error)
        this.messageService.add({ severity: 'error', summary: 'Upload failed', detail: 'Your file could not be uploaded.' });
      }
    });

    this.fileUploader.clear();
  }

  toggleRow(model: Model) {
    const modelId = model.model_id;
    if (this.expandedRows[modelId]) {
      delete this.expandedRows[modelId];
    } else {
      this.expandedRows[modelId] = true;
    }
  }

  expandAll() {
    this.expandedRows = this.models.reduce((acc: { [key: string]: boolean }, model) => {
      acc[model.model_id] = true;
      return acc;
    }, {});
  }


  collapseAll() {
    this.expandedRows = {};
  }

  getModels() {
    this.apiService.get('v1/models').subscribe({
      next: (response: any) => {
        this.models = response.models;
        for (let model of this.models) {
          this.getProcess(model).subscribe({
            next: (response) => {
              model.running = response.model_id == model.model_id? response.running : false;
            },
            error: (error) => console.error('Failed to fetch process:', error),
          });
          console.log(this.getProcess(model));
        }
      },
      error: (error) => console.error('Failed to fetch models:', error),
    });
  }

  deleteModel(model: Model) {
    this.confirmationService.confirm({
      message: 'Are you sure you want to delete this model?',
      header: 'Delete Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Delete',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.apiService.delete(`v1/models/${model.model_id}`).subscribe({
          next: (response) => {
            console.log('Model deleted:', model);
            this.models = this.models.filter((m) => m.model_id !== model.model_id);
            this.messageService.add({ severity: 'success', summary: 'Model deleted', detail: 'The model has been deleted successfully.' });
          },
          error: (error) => this.messageService.add({ severity: 'error', summary: 'Model deletion failed', detail: 'The model could not be deleted.' }),
        });
      }
    });
  }

  trainModel(model: Model) {
    this.apiService.post(`v1/models/${model.model_id}/train`, {}).subscribe({
      next: (response) => {
        console.log('Model training started:', model);
        this.messageService.add({ severity: 'success', summary: 'Model training started', detail: 'The model training has started successfully.' });
      },
      error: (error) => this.messageService.add({ severity: 'error', summary: 'Model training failed', detail: 'The model training could not be started.' }),
    });
  }

  backtestModel(model: Model) {
    this.confirmationService.confirm({
      message: 'Are you sure you want to start the backtesting process for this model?',
      header: 'Backtest Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Backtest',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-success',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.apiService.post(`v1/models/${model.model_id}/backtest`, {}).subscribe({
          next: (response) => {
            console.log('Model backtesting started:', model);
            this.messageService.add({ severity: 'success', summary: 'Model backtesting started', detail: 'The model backtesting has started successfully.' });
            model.running = true;
          },
          error: (error) => {
          if (error.status === 400) {
            this.messageService.add({ severity: 'error', summary: 'Model backtesting failed', detail: 'The model is already running a backtest.' })
          } else {
            this.messageService.add({ severity: 'error', summary: 'Model backtesting failed', detail: 'The model backtesting could not be started.' })
          }
        },
        });
      }
    });
  }

  stopBacktest(model: Model) {
    this.confirmationService.confirm({
      message: 'Are you sure you want to stop the backtesting process for this model?',
      header: 'Stop Backtest Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Stop Backtest',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.apiService.post(`v1/models/${model.model_id}/backtest/stop`, {}).subscribe({
          next: (response) => {
            console.log('Model backtesting stopped:', model);
            this.messageService.add({ severity: 'success', summary: 'Model backtesting stopped', detail: 'The model backtesting has stopped successfully.' });
            model.running = false;
          },
          error: (error) => {
            if (error.status === 400) {
              this.messageService.add({ severity: 'error', summary: 'Model backtesting stop failed', detail: 'The model is not running a backtest.' })
            } else {
            this.messageService.add({ severity: 'error', summary: 'Model backtesting stop failed', detail: 'The model backtesting could not be stopped.' })
            }
          },
        });
      }
    });
  }

  getProcesses() {
    this.apiService.get('v1/models/status').subscribe({
      next: (response) => {
        console.log('Processes:', response);
      },
      error: (error) => console.error('Failed to fetch processes:', error),
    });
  }

  getProcess(model: Model): Observable<any> {
    return this.apiService.get(`v1/models/${model.model_id}/status`);
  }

}
