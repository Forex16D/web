import { Component } from '@angular/core';
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
  ],
  templateUrl: './admin-model.component.html',
  styleUrl: './admin-model.component.css'
})
export class AdminModelComponent {
  models: any[] = [];
  selectedModels: any[] = [];

  firstElement: number = 0;
  rowsPerPage: number = 10;
  expandedRows: { [key: string]: boolean } = {};

  constructor() {
    this.models = [
      { id: 0, name: 'Trend follower XAUUSD 1.2', price: 100.2, winrate: 0.5 },
      { id: 1, name: 'Scalper USDJPY 1.0', price: 0.00, winrate: 0.41},
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

  expandAll() {
    this.expandedRows = this.models.reduce((acc, model) => {
      acc[model.id] = true;
      return acc;
    }, {});
  }

  collapseAll() {
    this.expandedRows = {};
  }

  debugButton(model: any, expanded: boolean) {
    console.log('Button clicked!');
    console.log('Model:', model);
    console.log('Is Expanded:', expanded);
    console.log('Expanded Rows State:', this.expandedRows);
  
    const rowKey = model.id;
    if (this.expandedRows[rowKey]) {
      console.log(`Collapsing row with ID: ${rowKey}`);
      delete this.expandedRows[rowKey];
    } else {
      console.log(`Expanding row with ID: ${rowKey}`);
      this.expandedRows[rowKey] = true;
    }
  }
  
  toggleRow(model: any) {
    const rowKey = model.id;
  
    if (this.expandedRows[rowKey]) {
      delete this.expandedRows[rowKey];
      console.log(`Collapsing row with ID: ${rowKey}`);
    } else {
      this.expandedRows[rowKey] = true;
      console.log(`Expanding row with ID: ${rowKey}`);
    }
  
    console.log('Updated Expanded Rows:', this.expandedRows);
  }

}
