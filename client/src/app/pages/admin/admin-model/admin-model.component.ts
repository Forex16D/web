import { Component } from '@angular/core';
import { TableModule } from 'primeng/table';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { SplitButtonModule } from 'primeng/splitbutton';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { FormsModule } from '@angular/forms';
import { JsonPipe } from '@angular/common';
import { FileUploadModule } from 'primeng/fileupload';

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
    JsonPipe,
    FileUploadModule,
  ],
  templateUrl: './admin-model.component.html',
  styleUrl: './admin-model.component.css'
})
export class AdminModelComponent {
  models: any[] = [];
  selectedModels: any[] = [];

  firstElement: number = 0;
  rowsPerPage: number = 10;

  constructor() {
    this.models = [
      { id: 0, name: 'John Doe', isOverdue: false },
      { id: 1, name: 'John Doe', isOverdue: false },
    ];
    this.loadUsers(this.firstElement, this.rowsPerPage)
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
}
