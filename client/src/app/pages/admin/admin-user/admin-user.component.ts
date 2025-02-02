import { Component, effect, signal } from '@angular/core';
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
import { HttpClient } from '@angular/common/http';

interface UserResponse {
  users: any[];
  total_users: number;
}

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
  users = signal<any[]>([]);
  selectedUsers = signal<any[]>([]);

  page = signal<number>(1);
  limit = signal<number>(10);
  fetchedUsers = 1;

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private http: HttpClient
  ) {
    
    this.loadUsers(1, 100);
    this.activatedRoute.queryParams.subscribe((params) => {
      const page = params['page'] ? parseInt(params['page'], 10) : 1;
      const limit = params['limit'] ? parseInt(params['limit'], 10) : 10;
      this.page.set(page);
      this.limit.set(limit);
    });

    effect(() => {
      console.log('something change')
      const currentPage = this.page();
      const currentLimit = this.limit();
      this.updateQueryParams(currentPage, currentLimit);
    });
  }

  onPageChange(event: any) {
    const newPage = (event.first / event.rows) + 1;
    const newLimit = event.rows;

    this.page.set(newPage);
    this.limit.set(newLimit);
  }

  loadUsers(page: number, limit: number) {
    console.log(`Fetching users for page ${page} with limit ${limit}`);
    console.log('First:', (this.page() - 1) * this.limit())
    this.http.get<UserResponse>(`http://127.0.0.1:5000/v1/users?page=${page}&limit=${limit}`).subscribe({
      next: (response) => {

        this.users.set(response.users);
        console.log('Fetched users:', response.users);
      },
      error: (error) => {
        console.error('Error fetching users:', error);
      }
    });
  }

  updateQueryParams(page: number, limit: number) {
    this.router.navigate([], {
      relativeTo: this.activatedRoute,
      queryParams: { page, limit },
      queryParamsHandling: 'merge'
    });
  }
}
