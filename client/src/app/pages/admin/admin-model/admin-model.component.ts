import { Component, OnInit, ViewChild } from '@angular/core';
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
import { Observable, Subject } from 'rxjs';
import { DialogModule } from 'primeng/dialog';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { NgIf } from '@angular/common';

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
    ConfirmDialogModule,
    NgIf
  ],
  templateUrl: './admin-model.component.html',
  styleUrl: './admin-model.component.css'
})
export class AdminModelComponent implements OnInit {
  @ViewChild('fu', { static: false }) fileUploader!: FileUpload;

  models: Model[] = [];
  filteredModels: Model[] = [];
  selectedModels: Model[] = [];
  selectedModel: Model | null = null;
  selectedFiles: File[] = [];
  loading: boolean = false;
  editingNewModel: boolean = false;

  firstElement: number = 0;
  rowsPerPage: number = 10;
  expandedRows: { [key: string]: boolean } = {};

  isEditVisible: boolean = false;
  
  searchQuery: string = '';
  searchSubject = new Subject<string>();

  modelEditForm = new FormGroup({
    model_id: new FormControl('', [Validators.required]),
    name: new FormControl('', [Validators.required, Validators.minLength(1), Validators.maxLength(20)]),
    symbol: new FormControl(''),
    commission: new FormControl('', [Validators.required, Validators.pattern('^[0-9]+(\\.[0-9]+)?$')]),
  });

  constructor(
    private apiService: ApiService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService,
  ) { }

  ngOnInit() {
    this.getModels();
    
    // Set up debounced search
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(query => {
      this.performSearch(query);
    });
  }

  onPageChange(event: any) {
    this.firstElement = event.first;
    this.rowsPerPage = event.rows;
    this.loadModels(this.firstElement, this.rowsPerPage);
  }

  loadModels(firstElement: number, size: number) {
    console.log(`Fetching models ${firstElement}-${firstElement + size - 1}`);
    // Implement pagination if your API supports it
  }

  onSearch(event: any) {
    const query = event.target.value.toLowerCase();
    this.searchQuery = query;
    this.searchSubject.next(query);
  }

  performSearch(query: string) {
    if (!query || query.trim() === '') {
      // If search is empty, restore original list
      this.filteredModels = [...this.models];
    } else {
      // Filter models based on search query
      this.filteredModels = this.models.filter(model => 
        model.model_id.toString().toLowerCase().includes(query) ||
        model.name.toLowerCase().includes(query) ||
        (model.symbol && model.symbol.toLowerCase().includes(query))
      );
    }
    
    // Reset pagination to first page when searching
    this.firstElement = 0;
  }

  clearSearch() {
    this.searchQuery = '';
    this.filteredModels = [...this.models];
  }

  onFileSelected(event: any) {
    this.selectedFiles = event.files;
    console.log('Selected Files:', this.selectedFiles);
  }

  uploadFile() {
    if (this.selectedFiles.length === 0) {
      this.messageService.add({ severity: 'warn', summary: 'No files selected', detail: 'Please select a file to upload.' });
      return;
    }

    const formData = new FormData();

    for (let i = 0; i < this.selectedFiles.length; i++) {
      formData.append('files[]', this.selectedFiles[i], this.selectedFiles[i].name);
    }

    const headers = {};
    this.loading = true;
    this.apiService.post('v1/models', formData, headers, true).subscribe({
      next: (response) => {
        console.log('Upload successful:', response);
        this.messageService.add({ severity: 'success', summary: 'Upload successful', detail: 'Your file has been uploaded successfully.' });
        this.getModels();
        this.loading = false;
      },
      error: (error) => {
        console.error('Upload failed:', error);
        this.messageService.add({ severity: 'error', summary: 'Upload failed', detail: 'Your file could not be uploaded.' });
        this.loading = false;
      },
      complete: () => {
        this.fileUploader.clear();
      }
    });
  }

  toggleRow(model: Model) {
    this.expandedRows = { ...this.expandedRows };
    if (this.expandedRows[model.model_id]) {
      delete this.expandedRows[model.model_id];
    } else {
      this.expandedRows[model.model_id] = true;
    }
  }
  
  expandAll() {
    const expandedState = this.filteredModels.reduce((acc: { [key: string]: boolean }, model) => {
      acc[model.model_id] = true;
      return acc;
    }, {});
    this.expandedRows = { ...expandedState }; // Assign a new reference
  }
  
  collapseAll() {
    this.expandedRows = {};
  }

  getModels() {
    this.loading = true;
    this.apiService.get('v1/models').subscribe({
      next: (response: any) => {
        this.models = response.models;
        this.filteredModels = [...this.models]; // Initialize filtered models with all models
        
        for (let model of this.models) {
          this.getProcess(model).subscribe({
            next: (response) => {
              model.running = response.model_id === model.model_id ? response.running : false;
            },
            error: (error) => console.error('Failed to fetch process:', error),
          });
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Failed to fetch models:', error);
        this.loading = false;
        this.messageService.add({ severity: 'error', summary: 'Failed to load models', detail: 'Could not retrieve the list of models.' });
      },
    });
  }

  confirmDelete(model: Model) {
    this.confirmationService.confirm({
      message: 'Are you sure you want to delete this model?',
      header: 'Delete Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Delete',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.deleteModel(model);
      }
    });
  }

  confirmDeleteMultiple() {
    if (!this.selectedModels || this.selectedModels.length === 0) {
      return;
    }

    this.confirmationService.confirm({
      message: `Are you sure you want to delete ${this.selectedModels.length} selected models?`,
      header: 'Delete Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Delete All',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.deleteSelectedModels();
      }
    });
  }

  deleteSelectedModels() {
    const deletePromises = this.selectedModels.map(model => 
      this.apiService.delete(`v1/models/${model.model_id}`).toPromise()
    );

    Promise.all(deletePromises)
      .then(() => {
        const count = this.selectedModels.length;
        this.models = this.models.filter(model => !this.selectedModels.includes(model));
        this.filteredModels = this.filteredModels.filter(model => !this.selectedModels.includes(model));
        this.selectedModels = [];
        this.messageService.add({ 
          severity: 'success', 
          summary: 'Models deleted', 
          detail: `${count} model${count > 1 ? 's' : ''} deleted successfully.` 
        });
      })
      .catch(error => {
        console.error('Failed to delete models:', error);
        this.messageService.add({ 
          severity: 'error', 
          summary: 'Deletion failed', 
          detail: 'One or more models could not be deleted.' 
        });
      });
  }

  deleteModel(model: Model) {
    this.apiService.delete(`v1/models/${model.model_id}`).subscribe({
      next: (response) => {
        console.log('Model deleted:', model);
        this.models = this.models.filter((m) => m.model_id !== model.model_id);
        this.filteredModels = this.filteredModels.filter((m) => m.model_id !== model.model_id);
        this.messageService.add({ severity: 'success', summary: 'Model deleted', detail: 'The model has been deleted successfully.' });
      },
      error: (error) => this.messageService.add({ severity: 'error', summary: 'Model deletion failed', detail: 'The model could not be deleted.' }),
    });
  }

  createNewModel() {
    this.editingNewModel = true;
    this.selectedModel = null;
    
    this.modelEditForm.reset();
    this.modelEditForm.get('model_id')?.enable();
    
    this.isEditVisible = true;
  }

  editModel(model: Model) {
    this.editingNewModel = false;
    this.selectedModel = model;

    this.modelEditForm.setValue({
      model_id: model.model_id.toString(),
      name: model.name,
      symbol: model.symbol || '',
      commission: model.commission?.toString() || ''
    });

    this.modelEditForm.get('model_id')?.disable();

    this.isEditVisible = true;
  }

  saveModel() {
    if (this.modelEditForm.invalid) {
      this.messageService.add({ severity: 'error', summary: 'Invalid form', detail: 'Please fill all required fields correctly.' });
      return;
    }

    const formValues = this.modelEditForm.value;
    
    if (this.editingNewModel) {
      // Create new model
      this.apiService.post('v1/models/create', formValues).subscribe({
        next: (response) => {
          console.log('Model created:', response);
          this.messageService.add({ severity: 'success', summary: 'Model created', detail: 'The model has been created successfully.' });
          this.getModels();
          this.isEditVisible = false;
        },
        error: (error) => this.messageService.add({ severity: 'error', summary: 'Model creation failed', detail: 'The model could not be created.' }),
      });
    } else {
      // Update existing model
      this.apiService.put(`v1/models/${this.selectedModel?.model_id}`, formValues).subscribe({
        next: (response) => {
          console.log('Model updated:', response);
          this.messageService.add({ severity: 'success', summary: 'Model updated', detail: 'The model has been updated successfully.' });
          this.getModels();
          this.isEditVisible = false;
        },
        error: (error) => this.messageService.add({ severity: 'error', summary: 'Model update failed', detail: 'The model could not be updated.' }),
      });
    }
  }

  trainModel(model: Model) {
    this.confirmationService.confirm({
      message: 'Are you sure you want to start the training process for this model?',
      header: 'Training Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Train',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-success',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        const date = new Date(Date.now());
        const formatted_date = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
        const body = { "start_date": formatted_date };
        model.running = true;
        this.apiService.post(`v1/models/${model.model_id}/train`, body).subscribe({
          next: (response) => {
            this.messageService.add({ severity: 'success', summary: 'Model training started', detail: 'The model training has started successfully.' });

            this.getBacktestEndStatus().subscribe({
              next: (status) => {
                console.log('Model training completed:', status === "completed");
                if (status === 'completed') {
                  model.running = false;
                  this.messageService.add({ severity: 'success', summary: 'Model training completed', detail: 'The model training has completed successfully.' });
                }
              }
            });
          },
          error: (error) => this.messageService.add({ severity: 'error', summary: 'Model training failed', detail: 'The model training could not be started.' }),
        });
      }
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
                console.log('Model backtesting completed:', status === "completed");
                if (status === 'completed') {
                  model.running = false;
                  this.messageService.add({ severity: 'success', summary: 'Model backtesting completed', detail: 'The model backtesting has completed successfully.' });
                }
              }
            });
          },
          error: (error) => {
            if (error.status === 400) {
              this.messageService.add({ severity: 'error', summary: 'Model backtesting failed', detail: 'The model is already running a backtest.' });
            } else {
              this.messageService.add({ severity: 'error', summary: 'Model backtesting failed', detail: 'The model backtesting could not be started.' });
            }
          },
        });
      }
    });
  }

  stopEvaluate(model: Model) {
    this.confirmationService.confirm({
      message: 'Are you sure you want to stop the process for this model?',
      header: 'Stop Process Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Stop Process',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.apiService.post(`v1/models/${model.model_id}/evaluate/stop`, {}).subscribe({
          next: (response) => {
            this.messageService.add({ severity: 'success', summary: 'Process stopped', detail: 'The model process has stopped successfully.' });
            model.running = false;
          },
          error: (error) => {
            if (error.status === 400) {
              this.messageService.add({ severity: 'error', summary: 'Process stop failed', detail: 'The model is not running a process.' });
            } else {
              this.messageService.add({ severity: 'error', summary: 'Process stop failed', detail: 'The model process could not be stopped.' });
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