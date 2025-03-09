import { Component, effect, inject, OnInit, signal } from '@angular/core';
import { TableModule } from 'primeng/table';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { SplitButtonModule } from 'primeng/splitbutton';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { FormsModule } from '@angular/forms';
import { JsonPipe, NgIf } from '@angular/common';
import { FileUploadModule } from 'primeng/fileupload';
import { Router, ActivatedRoute } from '@angular/router';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ApiService } from '../../../core/services/api.service';
import { TagModule } from 'primeng/tag';
import { ConfirmDialogModule } from 'primeng/confirmdialog';

interface User {
  user_id: string;
  email: string;
  role: string;
}

interface UserResponse {
  users: User[];
  total_users: number;
}

@Component({
  selector: 'app-admin-user',
  imports: [
    TableModule,
    ToolbarModule,
    TagModule,
    ButtonModule,
    IconFieldModule,
    InputIconModule,
    SplitButtonModule,
    InputTextModule,
    CheckboxModule,
    FormsModule,
    JsonPipe,
    FileUploadModule,
    NgIf,
    ConfirmDialogModule
  ],
  templateUrl: './admin-user.component.html',
  styleUrls: ['./admin-user.component.css']
})
export class AdminUserComponent implements OnInit {
  private activatedRoute = inject(ActivatedRoute);
  private router = inject(Router);
  private apiService = inject(ApiService);
  private messageService = inject(MessageService);

  users = signal<User[]>([]);
  selectedUsers = signal<User[]>([]);
  page = signal<number>(1);
  limit = signal<number>(10);
  totalRecords = signal<number>(0);
  loading = signal<boolean>(false);

  constructor(private confirmationService: ConfirmationService) {
    effect(() => {
      this.updateQueryParams(this.page(), this.limit());
    });
  }

  ngOnInit(): void {
    this.activatedRoute.queryParams.subscribe((params) => {
      const page = params['page'] ? parseInt(params['page'], 10) : 1;
      const limit = params['limit'] ? parseInt(params['limit'], 10) : 10;
      this.page.set(page);
      this.limit.set(limit);
      this.loadUsers();
    });
  }

  loadUsers(): void {
    this.loading.set(true);
    this.apiService.get<UserResponse>(`v1/users?page=${this.page()}&limit=${this.limit()}`).subscribe({
      next: (response) => {
        this.users.set(response.users);
        this.totalRecords.set(response.total_users);
        this.loading.set(false);
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load users' });
        this.loading.set(false);
      }
    });
  }

  deleteUser(userId: string): void {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete selected user?`,
      header: 'Delete Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Delete',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.apiService.delete(`v1/users/${userId}`).subscribe({
          next: () => {
            this.messageService.add({ severity: 'success', summary: 'Success', detail: `User ${userId} has been deleted` });
            this.loadUsers();
          },
          error: () => this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete user' })
        });
      }
    });
  }

  bulkDeleteUsers(): void {
    if (this.selectedUsers().length === 0) return;
    if (confirm(`Are you sure you want to delete ${this.selectedUsers().length} selected users?`)) {
      const selectedIds = this.selectedUsers().map(user => user.user_id);
      this.apiService.post('v1/users/bulk-delete', { user_ids: selectedIds }).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Success', detail: `${selectedIds.length} users have been deleted` });
          this.loadUsers();
        },
        error: () => this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete users' })
      });
    }
  }

  updateQueryParams(page: number, limit: number) {
    this.router.navigate([], { relativeTo: this.activatedRoute, queryParams: { page, limit }, queryParamsHandling: 'merge' });
  }

  onPageChange(event: any): void {
    const newPage = event.page !== undefined ? event.page + 1 : 1; // Ensure page is valid
    const newLimit = event.rows || this.limit(); // Ensure limit is valid
  
    this.page.set(newPage);
    this.limit.set(newLimit);
    this.loadUsers();
  }
  

  exportUsers(): void {
    // Implement export functionality
    this.messageService.add({
      severity: 'info',
      summary: 'Export',
      detail: 'User export started'
    });
  }

  importUsers(event: any): void {
    if (event.files && event.files.length > 0) {
      // Handle file import
      this.messageService.add({
        severity: 'info',
        summary: 'Import',
        detail: `File ${event.files[0].name} uploaded successfully`
      });
    }
  }

  createNewUser(): void {
    // Open dialog or navigate to create user form
    this.messageService.add({
      severity: 'info',
      summary: 'New User',
      detail: 'Create new user functionality triggered'
    });
  }

  editUser(userId: string): void {
    // Open dialog or navigate to edit user form
    this.messageService.add({
      severity: 'info',
      summary: 'Edit User',
      detail: `Edit user ${userId} functionality triggered`
    });
  }

}
