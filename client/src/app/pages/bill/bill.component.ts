import { DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { DialogModule } from 'primeng/dialog';
import { DropdownModule } from 'primeng/dropdown';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ToolbarModule } from 'primeng/toolbar';
import { TextareaModule } from 'primeng/textarea';
import { ApiService } from '../../core/services/api.service';
import { TooltipModule } from 'primeng/tooltip';

interface Bill {
  bill_id: number;
  created_at: string;
  net_amount: number;
  net_amount_usd: number;
  due_date: Date | null;
  status: string;
  notes?: string;
  commission?: number;
  total_profit?: number;
  model_id?: string;
  portfolio_id?: string;
}

@Component({
  selector: 'app-bill',
  templateUrl: './bill.component.html',
  imports: [
    ToolbarModule,
    ButtonModule,
    DropdownModule,
    TableModule,
    MessageModule,
    TagModule,
    DatePipe,
    DialogModule,
    InputNumberModule,
    InputTextModule,
    FormsModule,
    ReactiveFormsModule,
    DatePickerModule,
    TextareaModule,
    TooltipModule,
  ]
})
export class BillComponent implements OnInit {
  bills: Bill[] = [];
  isBillDialogVisible: boolean = false;
  submitted: boolean = false;
  editMode: boolean = false;
  currentBillId: number = 0;
  currentMonthTotal: number = 0;
  pendingPayments: number = 0;

  statusOptions = [
    { label: 'Pending', value: 'Pending' },
    { label: 'Paid', value: 'Paid' },
    { label: 'Overdue', value: 'Overdue' }
  ];

  filterOptions = [
    { name: 'All', value: null },
    { name: 'Pending', value: 'Pending' },
    { name: 'Paid', value: 'Paid' },
    { name: 'Overdue', value: 'Overdue' }
  ];

  constructor(
    private confirmationService: ConfirmationService,
    private messageService: MessageService,
    private apiService: ApiService,
  ) { }

  ngOnInit(): void {
    this.loadBills().then(() => {
      this.calculateTotals();
    }).catch(error => {
      console.error('Error loading bills:', error);
    });
  }


  loadBills(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.apiService.get('/v1/bills').subscribe({
        next: (response: any) => {
          this.bills = response.bills;
          resolve(); // Resolves the Promise after loading bills
        },
        error: (error) => {
          console.error(error);
          reject(error); // Rejects the Promise on error
        }
      });
    });
  }

  getStatusSeverity(status: string): "success" | "info" | "warn" | "danger" | "secondary" | "contrast" | undefined {
    switch (status.toLowerCase()) {  // Convert to lowercase for comparison
      case 'paid':
        return 'success';
      case 'pending':
        return 'warn';
      case 'overdue':
        return 'danger';
      default:
        return 'info';
    }
  }

  // Update the calculateTotals method
  calculateTotals(): void {
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    console.log(this.bills)
    this.currentMonthTotal = this.bills
      .filter(bill => {
        if (!bill.due_date) return false;
        const billDate = new Date(bill.due_date);
        return billDate.getMonth() === currentMonth && billDate.getFullYear() === currentYear;
      })
      .reduce((sum, bill) => sum + bill.net_amount_usd, 0);
    
    console.log(this.currentMonthTotal);
    this.pendingPayments = this.bills
      .filter(bill => bill.status.toLowerCase() === 'pending' || bill.status.toLowerCase() === 'overdue')
      .reduce((sum, bill) => sum + bill.net_amount_usd, 0);
  }

  makePayment(bill: Bill): void {
    // In a real app, this would open a payment gateway or process payment
    this.confirmationService.confirm({
      message: `Process payment of $${bill.net_amount_usd} for Bill #${bill.bill_id}?`,
      header: 'Confirm Payment',
      icon: 'pi pi-credit-card',
      acceptLabel: 'Proceed',
      rejectLabel: 'Cancel',
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      acceptButtonStyleClass: 'p-button-success',
      accept: () => {
        // Navigate to payment page with bill_id as query parameter
        window.location.href = `/payment?bill_id=${bill.bill_id}`;
      }
    });
  }

  showDetails(bill: Bill): void {
    
  }

  filterBills(event: any): void {
    // In a real app, you would call a service with filter parameters
    // For this demo, we'll just pretend to filter and show a message
    this.messageService.add({
      severity: 'info',
      summary: 'Filter Applied',
      detail: `Showing ${event.value.value || 'All'} bills`
    });
  }

  clearFilters(): void {
    // Reset filters logic would go here
    this.messageService.add({ severity: 'info', summary: 'Filters Cleared', detail: 'Showing all bills' });
  }
}