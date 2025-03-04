import { Component, model, OnInit, ViewChild } from '@angular/core';
import { TableModule } from 'primeng/table';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { SplitButtonModule } from 'primeng/splitbutton';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { FormsModule, ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { FileUploadModule } from 'primeng/fileupload';
import { RippleModule } from 'primeng/ripple';
import { ApiService } from '../../../core/services/api.service';
import { FileUpload } from 'primeng/fileupload';
import { MessageService } from 'primeng/api';
import { ConfirmationService } from 'primeng/api';
import { Model } from '../../../models/model.model';
import { Observable } from 'rxjs';
import { DialogModule } from 'primeng/dialog';

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
    DialogModule,
    ReactiveFormsModule,
    FormsModule,
  ],
  templateUrl: './admin-model.component.html',
  styleUrl: './admin-model.component.css'
})
export class AdminModelComponent implements OnInit {
  @ViewChild('fu', { static: false }) fileUploader!: FileUpload;

  models: Model[] = [];
  selectedModel: Model | null = null;
  selectedFiles: File[] = [];

  firstElement: number = 0;
  rowsPerPage: number = 10;
  expandedRows: { [key: string]: boolean } = {};

  isEditVisible: boolean = false;

  modelEditForm = new FormGroup({
    model_id: new FormControl(''),
    name: new FormControl('', [Validators.required, Validators.minLength(1), Validators.maxLength(20)]),
    commission: new FormControl('', [Validators.required, Validators.pattern('^[0-9]+(\\.[0-9]+)?$')]),
  });

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
              model.running = response.model_id == model.model_id ? response.running : false;
            },
            error: (error) => console.error('Failed to fetch process:', error),
          });
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

  editModel(model: Model) {
    this.selectedModel = model;

    this.modelEditForm.setValue({
      model_id: model.model_id.toString(),
      name: model.name,
      commission: model.commission?.toString() || null
    });

    this.modelEditForm.get('model_id')?.disable();

    this.isEditVisible = true;
  }

  saveModel() {
    this.apiService.put(`v1/models/${this.selectedModel?.model_id}`, this.modelEditForm.value).subscribe({
      next: (response) => {
        console.log('Model updated:', response);
        this.messageService.add({ severity: 'success', summary: 'Model updated', detail: 'The model has been updated successfully.' });
        this.getModels();
        this.isEditVisible = false;
      },
      error: (error) => this.messageService.add({ severity: 'error', summary: 'Model update failed', detail: 'The model could not be updated.' }),
    });
  }

  trainModel(model: Model) {
    const date = new Date(Date.now());
    const formatted_date = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
    const body = {"start_date": formatted_date}
    this.apiService.post(`v1/models/${model.model_id}/train`, body).subscribe({
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

            this.getBacktestEndStatus().subscribe({
              next: (status) => {
                console.log('Model backtesting status:', status === "completed");
                if (status === 'completed') {
                  model.running = false;
                  this.messageService.add({ severity: 'success', summary: 'Model backtesting completed', detail: 'The model backtesting has completed successfully.' });
                }
              }
            });
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

  getBacktestEndStatus(): Observable<string> {
    return this.apiService.getStream('v1/models/backtest/stream');
  }
}
