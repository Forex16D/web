import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { DropdownModule } from 'primeng/dropdown';
import { FileUploadModule } from 'primeng/fileupload';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { ImageModule } from 'primeng/image';
import { ApiService } from '../../core/services/api.service';
import { TextareaModule } from 'primeng/textarea';

@Component({
  selector: 'app-payment',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    InputNumberModule,
    DropdownModule,
    FileUploadModule,
    ProgressSpinnerModule,
    FormsModule,
    ReactiveFormsModule,
    ImageModule,
    TextareaModule
  ],
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.css']
})
export class PaymentComponent implements OnInit {
  billId: number | null = null;
  billIds: number[] = [];
  amount: number = 0;
  amount_usd: number = 0;
  created_at: Date = new Date;
  isBulkPayment: boolean = false;
  paymentForm!: FormGroup;
  receiptImage: any = null;
  imagePreview: string | null = null;
  isSubmitting: boolean = false;

  paymentMethod: 'wallet' | 'receipt' | null = null;
  walletBalance: number = 0;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private fb: FormBuilder,
    private messageService: MessageService,
    private apiService: ApiService
  ) { }

  ngOnInit(): void {
    this.initForm();
    this.parseQueryParams();
    this.getBill();
    this.getBalance();
  }

  initForm(): void {
    this.paymentForm = this.fb.group({
      notes: ['']
    });
  }

  selectPaymentMethod(method: 'wallet' | 'receipt') {
    this.paymentMethod = method;
  }

  getBill(): void {
    let queryparam;
    this.activatedRoute.queryParams.subscribe(params => {
      queryparam = params['bill_id'];
    });
    this.apiService.get(`v1/bills/${queryparam}`).subscribe({
      next: (response: any) => {
        this.amount = response.bill.net_amount;
        this.amount_usd = response.bill.net_amount_usd;
        this.created_at = response.bill.created_at;
      },
      error: (error) => console.log(error),
    })
  }

  getBalance(): void {
    this.apiService.get('v1/balance').subscribe({
      next: (response: any) => {
        this.walletBalance = response.balance
        console.log(response);
      },
      error: (error) => {
        console.error('Fetch failed:', error);
      }
    });
  }

  parseQueryParams(): void {
    this.route.queryParams.subscribe(params => {
      // Check if it's a bulk payment
      if (params['bulk'] === 'true') {
        this.isBulkPayment = true;
        if (params['bill_ids']) {
          this.billIds = params['bill_ids'].split(',').map((id: string) => parseInt(id, 10));
        }
      } else {
        // Single bill payment
        if (params['bill_id']) {
          this.billId = parseInt(params['bill_id'], 10);
        }
      }
    });
  }

  onFileSelect(event: any): void {
    if (event.files && event.files.length) {
      const file = event.files[0];
      this.receiptImage = file;

      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  clearImage(): void {
    this.receiptImage = null;
    this.imagePreview = null;
  }

  submitPayment(): void {
    if (this.paymentForm.invalid) {
      this.messageService.add({
        severity: 'error',
        summary: 'Missing Information',
        detail: 'Please fill in all required fields.'
      });
      return;
    }
    
    if (this.walletBalance < this.amount_usd) {
      this.messageService.add({
        severity: 'error',
        summary: 'Insufficient Funds',
        detail: `Your balance ($${this.walletBalance.toFixed(2)}) is lower than the required amount ($${this.amount_usd.toFixed(2)}).`
      });
      return;
    }
    
    if (this.paymentMethod === 'receipt' && !this.receiptImage) {
      this.messageService.add({
        severity: 'error',
        summary: 'Receipt Required',
        detail: 'Please upload a receipt to proceed with the payment.'
      });
      return;
    }    

    this.isSubmitting = true;
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('receipt', this.receiptImage);
    formData.append('notes', this.paymentForm.value.notes || '');
    formData.append('method', this.paymentMethod || '');

    if (this.isBulkPayment) {
      formData.append('bill_ids', JSON.stringify(this.billIds));
    } else {
      formData.append('bill_id', this.billId!.toString());
    }

    formData.append('amount', this.amount.toString());

    const headers = {}
    this.apiService.post('/v1/payments', formData, headers, true).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Payment Successful',
          detail: `Your payment of ฿${this.amount.toFixed(2)} has been processed successfully`
        });
        this.router.navigate(['/bills']);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.messageService.add({
          severity: 'error',
          summary: 'Payment Failed',
          detail: 'An error occurred while processing your payment'
        });
      }
    });
  }

  cancelPayment(): void {
    this.router.navigate(['/bills']);
  }
}