import { Component, signal, viewChild, ViewContainerRef } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { PortfolioCardComponent } from '../../components/portfolio-card/portfolio-card.component';
import { NgFor, NgIf } from '@angular/common';
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

import * as echarts from 'echarts/core';
import { InputNumberModule } from 'primeng/inputnumber';
echarts.use([BarChart, GridComponent, CanvasRenderer]);

interface PortfolioResponse {
  connected: boolean
  create_at: string
  login: string
  model_id: string | null
  name: string
  portfolio_id: string
  token_id: string | null
  user_id: string
}

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
    InputNumberModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
  providers: [provideEchartsCore({ echarts }),],
})
export class DashboardComponent {
  vcr = viewChild('container', { read: ViewContainerRef });
  isBalanceVisible = false;
  isDialogVisible = false;
  portfolios = signal<PortfolioResponse[]>([]);

  portfolioForm = new FormGroup({
    name: new FormControl('', [Validators.required, Validators.minLength(1), Validators.maxLength(20)]),
    login: new FormControl(null, [Validators.required, Validators.pattern('[0-9]*')]),
  });

  submitted: boolean = false;

  components = [PortfolioCardComponent, PortfolioCardComponent]
  // portfolioDataArray = [
  //   {
  //     credential: { id: '0', name: 'Portfolio 1', login: '334067889' },
  //     data: { pnl: '200', winrate: '85', roi: '10', balance: '1500.25' },
  //   },
  // ];

  defaultData = {
    pnl: '',
    winrate: '',
    roi: '',
    balance: '',
  };

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
  ) {
    this.getPortfolios()
  }

  getPortfolios(): void {
    this.apiService.get<PortfolioResponse[]>('v1/portfolios').subscribe({
      next: (response: PortfolioResponse[]) => {
        this.portfolios.set(response);
        console.log(response);
      },
      error: (error) => {
        console.error('Fetch failed:', error);
      },
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
        console.error('Fetch failed:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error
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
}
