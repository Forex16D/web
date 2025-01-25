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
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-admin-user',
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
  templateUrl: './admin-user.component.html',
  styleUrl: './admin-user.component.css'
})
export class AdminUserComponent {
  users: any[] = [];
  selectedUsers: any[] = [];

  page: number = 1;
  limit: number = 10;

  constructor(private router: Router, private activatedRoute: ActivatedRoute) {
    this.users = [
      { id: 0, name: 'John Doe', isOverdue: false },
      { id: 1, name: 'John Doe', isOverdue: false },
      { id: 2, name: 'Jane Smith', isOverdue: true },
      { id: 3, name: 'Mark Brown', isOverdue: false },
      { id: 4, name: 'John Doe', isOverdue: false },
      { id: 5, name: 'Jane Smith', isOverdue: true },
      { id: 6, name: 'Mark Brown', isOverdue: false },
      { id: 7, name: 'John Doe', isOverdue: false },
      { id: 8, name: 'Jane Smith', isOverdue: true },
      { id: 9, name: 'Mark Brown', isOverdue: false },
      { id: 10, name: 'John Doe', isOverdue: false },
      { id: 11, name: 'Jane Smith', isOverdue: true },
      { id: 12, name: 'Mark Brown', isOverdue: false },
      { id: 13, name: 'John Doe', isOverdue: false },
      { id: 14, name: 'Jane Smith', isOverdue: true },
      { id: 15, name: 'Mark Brown', isOverdue: false },
      { id: 16, name: 'John Doe', isOverdue: false },
      { id: 17, name: 'Jane Smith', isOverdue: true },
      { id: 18, name: 'Mark Brown', isOverdue: false },
      { id: 19, name: 'John Doe', isOverdue: false },
      { id: 20, name: 'Jane Smith', isOverdue: true },
      { id: 21, name: 'Mark Brown', isOverdue: false },
    ];
    this.loadUsers(this.page, this.limit)
  }

  onPageChange(event: any) {
    this.limit = event.rows;
    this.page = event.first / this.limit + 1;
    console.log(event)
    console.log('Current Page:', this.page);
    console.log('Limit:', this.limit);

    this.updateQueryParams(this.page, this.limit)
    this.loadUsers(this.page, this.limit);
  }

  loadUsers(page: number, limit: number) {
    console.log(`Fetching users for page ${page} with limit ${limit}`);
  }

  updateQueryParams(page: number, limit: number) {
    this.router.navigate([], {
      relativeTo: this.activatedRoute,
      queryParams: { page, limit },
      queryParamsHandling: 'merge'
    });
  }
}
