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
import { response } from 'express';

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
  isBulkPayment: boolean = false;
  paymentForm!: FormGroup;
  receiptImage: any = null;
  imagePreview: string | null = null;
  isSubmitting: boolean = false;
  

  paymentMethods = [
    { label: 'Credit Card', value: 'credit_card' },
    { label: 'Bank Transfer', value: 'bank_transfer' },
    { label: 'PayPal', value: 'paypal' },
    { label: 'Cash', value: 'cash' }
  ];

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
  }

  initForm(): void {
    this.paymentForm = this.fb.group({
      paymentMethod: ['bank_transfer', Validators.required],
      referenceNumber: ['', Validators.required],
      paymentDate: [new Date(), Validators.required],
      notes: ['']
    });
  }

  getBill(): void {
    let queryparam;
    this.activatedRoute.queryParams.subscribe(params => {
      queryparam = params['bill_id'];
    });
    this.apiService.get(`v1/bills/${queryparam}`).subscribe({
      next: (response: any) => {
        this.amount = response.bill.net_amount;
      },
      error: (error) => console.log(error),
    })
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
      
      // Get amount
      if (params['amount']) {
        this.amount = parseFloat(params['amount']);
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
    if (this.paymentForm.invalid || !this.receiptImage) {
      this.messageService.add({
        severity: 'error',
        summary: 'Missing Information',
        detail: 'Please fill all required fields and upload a receipt image'
      });
      return;
    }

    this.isSubmitting = true;
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('receipt', this.receiptImage);
    formData.append('payment_method', this.paymentForm.value.paymentMethod);
    formData.append('reference_number', this.paymentForm.value.referenceNumber);
    formData.append('payment_date', this.paymentForm.value.paymentDate.toISOString());
    formData.append('notes', this.paymentForm.value.notes || '');
    
    if (this.isBulkPayment) {
      formData.append('bill_ids', JSON.stringify(this.billIds));
    } else {
      formData.append('bill_id', this.billId!.toString());
    }
    
    formData.append('amount', this.amount.toString());

    // In a real app, this would submit to your API
    // For demo purposes, we'll just simulate a successful submission
    setTimeout(() => {
      this.isSubmitting = false;
      this.messageService.add({
        severity: 'success',
        summary: 'Payment Successful',
        detail: `Your payment of $${this.amount.toFixed(2)} has been processed successfully`
      });
      
      // Navigate back to bills page after 2 seconds
      setTimeout(() => {
        this.router.navigate(['/bills']);
      }, 2000);
    }, 1500);
    
    // Actual API call would be like:
    /*
    this.apiService.post('/v1/payments', formData).subscribe({
      next: (response) => {
        this.isSubmitting = false;
        this.messageService.add({
          severity: 'success',
          summary: 'Payment Successful',
          detail: `Your payment of $${this.amount.toFixed(2)} has been processed successfully`
        });
        setTimeout(() => this.router.navigate(['/bills']), 2000);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.messageService.add({
          severity: 'error',
          summary: 'Payment Failed',
          detail: error.message || 'An error occurred while processing your payment'
        });
      }
    });
    */
  }

  cancelPayment(): void {
    this.router.navigate(['/bills']);
  }
}