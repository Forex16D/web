import { Component, effect, inject, OnInit, signal } from '@angular/core';
import { TableModule } from 'primeng/table';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule } from '@angular/forms';
import { NgIf, DatePipe } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ApiService } from '../../../core/services/api.service';
import { ConfirmDialogModule } from 'primeng/confirmdialog';

interface WithdrawRequest {
  withdraw_id: number;
  user_id: string;
  amount: string;
  method: string;
  bank_account: string;
  wallet_address: string | null;
  status: 'pending' | 'approved' | 'rejected';
  created_date: string;
  approved_date: string | null;
  selectedAction?: { label: string; value: string };
}

interface WithdrawResponse {
  requests: WithdrawRequest[];
  total: number;
}

@Component({
  selector: 'app-admin-request',
  imports: [
    TableModule,
    ToolbarModule,
    TagModule,
    ButtonModule,
    DropdownModule,
    FormsModule,
    NgIf,
    ConfirmDialogModule,
  ],
  templateUrl: './admin-request.component.html',
  styleUrls: ['./admin-request.component.css'],
  providers: [DatePipe]
})
export class AdminRequestComponent implements OnInit {
  private activatedRoute = inject(ActivatedRoute);
  private router = inject(Router);
  private apiService = inject(ApiService);
  private messageService = inject(MessageService);
  private datePipe = inject(DatePipe);

  requests = signal<WithdrawRequest[]>([]);
  selectedRequests = signal<WithdrawRequest[]>([]);
  page = signal<number>(1);
  limit = signal<number>(10);
  totalRecords = signal<number>(0);
  loading = signal<boolean>(false);

  // Action options for dropdown
  actionOptions = [
    { label: 'Approve', value: 'approve' },
    { label: 'Reject', value: 'reject' }
  ];

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
      this.loadRequests();
    });
  }

  loadRequests(): void {
    this.loading.set(true);
    this.apiService.get<WithdrawResponse>(`v1/withdrawals/admin`).subscribe({
      next: (response) => {
        this.requests.set(response.requests);
        this.totalRecords.set(response.total || response.requests.length);
        this.loading.set(false);
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load withdraw requests' });
        this.loading.set(false);
      }
    });
  }

  formatDate(dateString: string): string {
    return this.datePipe.transform(dateString, 'MMM d, y, h:mm a') || dateString;
  }

  refreshRequests(): void {
    this.loadRequests();
    this.selectedRequests.set([]);
  }

  submitAction(requestId: number, action?: string): void {
    if (!action) return;

    this.confirmationService.confirm({
      message: `Are you sure you want to ${action} this withdrawal request?`,
      header: 'Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: action === 'approve' ? 'Approve' : 'Reject',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: action === 'approve' ? 'p-button-success' : 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        this.loading.set(true);
        
        const urlAction = action === 'approve' ? 'approved' : 'rejected';
        this.apiService.put(`v1/withdrawals/${requestId}/${urlAction}`, {}).subscribe({
          next: () => {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: `Withdraw request ${action === 'approve' ? 'approved' : 'rejected'} successfully`
            });
            this.loadRequests();
            this.loading.set(false);
          },
          error: () => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: `Failed to ${action} withdraw request`
            });
            this.loading.set(false);
          }
        });
      }
    });
  }

  bulkApproveRequests(): void {
    if (this.selectedRequests().length === 0) return;
    
    this.confirmationService.confirm({
      message: `Are you sure you want to approve ${this.selectedRequests().length} withdraw requests?`,
      header: 'Confirm Bulk Approval',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Approve',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-success',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        const requestIds = this.selectedRequests().map(r => r.withdraw_id);
        this.loading.set(true);
        
        this.apiService.post('v1/withdrawals/bulk-approve', { request_ids: requestIds }).subscribe({
          next: () => {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: `${requestIds.length} withdraw requests approved successfully`
            });
            this.loadRequests();
            this.selectedRequests.set([]);
            this.loading.set(false);
          },
          error: () => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to approve the selected requests'
            });
            this.loading.set(false);
          }
        });
      }
    });
  }

  bulkRejectRequests(): void {
    if (this.selectedRequests().length === 0) return;
    
    this.confirmationService.confirm({
      message: `Are you sure you want to reject ${this.selectedRequests().length} withdraw requests?`,
      header: 'Confirm Bulk Rejection',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Reject',
      rejectLabel: 'Cancel',
      acceptButtonStyleClass: 'p-button-danger',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      accept: () => {
        const requestIds = this.selectedRequests().map(r => r.withdraw_id);
        this.loading.set(true);
        
        this.apiService.post('v1/withdrawals/bulk-reject', { request_ids: requestIds }).subscribe({
          next: () => {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: `${requestIds.length} withdraw requests rejected successfully`
            });
            this.loadRequests();
            this.selectedRequests.set([]);
            this.loading.set(false);
          },
          error: () => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to reject the selected requests'
            });
            this.loading.set(false);
          }
        });
      }
    });
  }

  updateQueryParams(page: number, limit: number): void {
    this.router.navigate([], { relativeTo: this.activatedRoute, queryParams: { page, limit }, queryParamsHandling: 'merge' });
  }

  onPageChange(event: any): void {
    const newPage = event.page !== undefined ? event.page + 1 : 1; // Ensure page is valid
    const newLimit = event.rows || this.limit(); // Ensure limit is valid
  
    this.page.set(newPage);
    this.limit.set(newLimit);
    this.loadRequests();
  }
}