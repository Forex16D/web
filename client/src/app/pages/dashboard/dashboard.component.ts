import { Component, OnInit, signal, viewChild, ViewContainerRef } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { PortfolioCardComponent } from '../../components/portfolio-card/portfolio-card.component';
import { DecimalPipe, NgFor, NgIf } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { BotCardComponent } from '../../components/bot-card/bot-card.component';
import { NgClass } from '@angular/common';
import { ToolbarModule } from 'primeng/toolbar';
import { BarChart } from 'echarts/charts';
import { EChartsCoreOption } from 'echarts/core';
import { GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { ApiService } from '../../core/services/api.service';
import { MessageService } from 'primeng/api';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgxEchartsModule, provideEchartsCore, NgxEchartsDirective } from 'ngx-echarts';
import { MessageModule } from 'primeng/message';
import { FocusTrapModule } from 'primeng/focustrap';
import { PortfolioResponse } from '../../models/portfolio-response.model';

import * as echarts from 'echarts/core';
import { InputNumberModule } from 'primeng/inputnumber';
import { DropdownModule } from 'primeng/dropdown';
import { CheckboxModule } from 'primeng/checkbox';
import { TextareaModule } from 'primeng/textarea';
echarts.use([BarChart, GridComponent, CanvasRenderer]);

@Component({
  selector: 'app-dashboard',
  imports: [
    ButtonModule,
    PortfolioCardComponent,
    NgFor,
    BotCardComponent,
    NgClass,
    NgxEchartsDirective,
    NgxEchartsModule,
    ToolbarModule,
    DialogModule,
    InputTextModule,
    FormsModule,
    FocusTrapModule,
    ReactiveFormsModule,
    MessageModule,
    NgIf,
    InputNumberModule,
    DropdownModule,
    CheckboxModule,
    DecimalPipe,
    TextareaModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
  providers: [provideEchartsCore({ echarts }),],
})
export class DashboardComponent implements OnInit {
  vcr = viewChild('container', { read: ViewContainerRef });
  
  // UI state variables
  isBalanceVisible = false;
  isDialogVisible = false;
  isWithdrawDialogVisible = false;
  showCommission = false;
  processing = false;
  submitted = false;
  withdrawSubmitted = false;

  // Data variables
  portfolios = signal<PortfolioResponse[]>([]);
  withdrawalMethods = [
    { name: 'Bank Transfer', code: 'bank' },
    { name: 'Credit/Debit Card', code: 'card' },
    { name: 'Cryptocurrency', code: 'crypto' },
    { name: 'PayPal', code: 'paypal' }
  ];
  walletBalance = 0;
  commissionIncome = 0;
  acc_profit = 0;
  withdrawalFee = 1.5;

  // Forms
  portfolioForm = new FormGroup({
    name: new FormControl('', [Validators.required, Validators.minLength(1), Validators.maxLength(20)]),
    login: new FormControl(null, [Validators.required, Validators.pattern('[0-9]*')]),
  });

  withdrawForm = new FormGroup({
    amount: new FormControl(null, [Validators.required, Validators.min(10), Validators.max(this.walletBalance)]),
    method: new FormControl('', Validators.required),
    bankAccount: new FormControl(''),
    walletAddress: new FormControl(''),
    notes: new FormControl(''),
    confirmation: new FormControl(false, Validators.requiredTrue),
  });
  
  lineChart: EChartsCoreOption = {
    grid: {
      left: '5%',
      right: '5%',
      top: '10%',
      bottom: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: [0, 1, 2, 3, 4, 5, 6],
      // boundaryGap: false
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: [10000, 12000, 13000, 14000, 15000, 15000, 20000],
        type: 'bar',
        areaStyle: {},
        itemStyle: {
          color: '#22c55e',
        },
        smooth: true, // Adds a smoother curve
      },
    ],
    responsive: true, // Ensures it adapts to container changes
  };
  
  constructor(
    private themeService: ThemeService,
    private apiService: ApiService,
    private messageService: MessageService,
  ) { }

  ngOnInit(): void {
    this.getPortfolios()
    this.getBalance()
    this.withdrawForm.get('method')?.valueChanges.subscribe(method => {
      if (method === 'bank') {
        this.withdrawForm.get('bankAccount')?.setValidators([Validators.required, Validators.minLength(8)]);
        this.withdrawForm.get('walletAddress')?.clearValidators();
      } else if (method === 'crypto') {
        this.withdrawForm.get('walletAddress')?.setValidators([Validators.required, Validators.minLength(25)]);
        this.withdrawForm.get('bankAccount')?.clearValidators();
      } else {
        this.withdrawForm.get('bankAccount')?.clearValidators();
        this.withdrawForm.get('walletAddress')?.clearValidators();
      }
      
      this.withdrawForm.get('bankAccount')?.updateValueAndValidity();
      this.withdrawForm.get('walletAddress')?.updateValueAndValidity();
    });
  }
  
  getPortfolios(): void {
    this.apiService.get<PortfolioResponse[]>('v1/portfolios').subscribe({
      next: (response: PortfolioResponse[]) => {
        this.portfolios.set(response);
        this.acc_profit = response.reduce((acc, portfolio) => acc + (portfolio.total_profit || 0), 0);
        for (let portfolio of this.portfolios()) {
          if (portfolio.is_expert) {
            this.showCommission = true;
            this.getCommission();
            break;
          }
        }
      },
      error: (error) => {
        console.error('Fetch failed:', error);
      },
    });
  }

  getCommission(): void {
    this.apiService.get<any[]>('v1/portfolios/commission').subscribe({
      next: (response: any[]) => {
        this.commissionIncome = response.reduce((acc, item) => acc + item.total_profit, 0);
      },
      error: (error) => {
        console.error('Fetch failed:', error);
      }
    });
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

  removePortfolio(portfolioId: string): void {
    this.portfolios.set(this.portfolios().filter(portfolio => portfolio.portfolio_id !== portfolioId));
  }

  createPortfolio(): void {
    this.submitted = true;
    if (this.portfolioForm.invalid)
      return

    const data = this.portfolioForm.value
    this.apiService.post('v1/portfolios', data).subscribe({
      next: (response) => {
        this.submitted = false;
        this.isDialogVisible = false;
        this.portfolioForm.reset()
        this.getPortfolios()

        console.log(response);
      },
      error: (error) => {
        console.error('Create failed:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Error Creating Portfolio'
        })
      }
    })
  }

  createComponent(): void {
    this.vcr()?.createComponent(PortfolioCardComponent);
  }

  lightMode() {
    this.themeService.toggleTheme();
  }

  toggleBalance(): void {
    this.isBalanceVisible = !this.isBalanceVisible;
  }

  showDialog(): void {
    this.isDialogVisible = true;
  }

  resetForm(): void {
    this.submitted = false;
    this.portfolioForm.reset();
  }

  showWithdrawDialog(): void {
    this.isWithdrawDialogVisible = true;
  }

  resetWithdrawForm(): void {
    this.withdrawForm.reset();
    this.withdrawSubmitted = false;
    this.processing = false;
  }

  shouldShowBankAccount(): boolean {
    return this.withdrawForm.get('method')?.value === 'bank';
  }

  shouldShowWalletAddress(): boolean {
    return this.withdrawForm.get('method')?.value === 'crypto';
  }

  calculateFee(): number {
    const amount = this.withdrawForm.get('amount')?.value || 0;
    return (amount * this.withdrawalFee) / 100;
  }

  calculateNetAmount(): number {
    const amount = this.withdrawForm.get('amount')?.value || 0;
    return amount - this.calculateFee();
  }

  processWithdrawal(): void {
    this.withdrawSubmitted = true;
    
    if (this.withdrawForm.invalid) {
      return;
    }
    
    this.processing = true;
    
    // Implement your withdrawal processing logic here
    // For example:
    // this.walletService.processWithdrawal(this.withdrawForm.value).subscribe(
    //   response => {
    //     this.messageService.add({severity: 'success', summary: 'Success', detail: 'Withdrawal processed successfully'});
    //     this.walletBalance -= this.withdrawForm.get('amount')?.value;
    //     this.isWithdrawDialogVisible = false;
    //     this.processing = false;
    //   },
    //   error => {
    //     this.messageService.add({severity: 'error', summary: 'Error', detail: error.message});
    //     this.processing = false;
    //   }
    // );
    
    // For demo purposes, simulate API call
    setTimeout(() => {
      console.log('Withdrawal processed:', this.withdrawForm.value);
      this.isWithdrawDialogVisible = false;
      this.processing = false;
    }, 1500);
  }
}
