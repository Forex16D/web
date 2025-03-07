import { Component, OnInit, signal } from '@angular/core';
import { PriceChartComponent } from '../price-chart/price-chart.component';
import { NgClass, NgFor } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { PortfolioResponse } from '../../models/portfolio-response.model';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import { BarChart } from 'echarts/charts';
import { LineChart } from 'echarts/charts';
import { EChartsCoreOption } from 'echarts/core';
import { GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { NgxEchartsModule, provideEchartsCore, NgxEchartsDirective } from 'ngx-echarts';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../core/services/api.service';

import * as echarts from 'echarts/core';
import { MessageService } from 'primeng/api';
echarts.use([BarChart, LineChart, GridComponent, CanvasRenderer]);

@Component({
  selector: 'app-bot-detail',
  imports: [
    NgxEchartsDirective,
    NgxEchartsModule,
    PriceChartComponent,
    NgClass,
    ButtonModule,
    DialogModule,
    InputTextModule,
    DropdownModule,
    FormsModule,
    ReactiveFormsModule,
    DatePipe,
    NgFor,
  ],
  templateUrl: './bot-detail.component.html',
  styleUrl: './bot-detail.component.css',
  providers: [
    provideEchartsCore({ echarts }),
  ],
})

export class BotDetailComponent implements OnInit {
  visible = false;

  data = {
    backtest: '126D',
    start_balance: '1000',
    risk_reward_ratio: '2.26',
    roi: '0.71',
    pnl: '$710.86',
    max_drawdown: '0.16',
    winrate: '0.5882',
    win: '20',
    loss: '14',
    total: '34',
  }

  portfolios = signal<PortfolioResponse[]>([]);
  model: any;
  model_id!: string;

  selectedPortfolio: PortfolioResponse | null = null;

  constructor(
    private apiService: ApiService,
    private route: ActivatedRoute,
    private messageService: MessageService,
  ) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.model_id = params.get('model_id') || '';
      this.getModels();
    });
  }

  onCopyTrade(): void {
    this.copy_trade();
    this.visible = false;
  }
  
  showDialog(): void {
    this.getPortfolios();
    this.visible = !this.visible;
  }

  barData = [12, -150, 30, 40, 160, 130, 200];

  barChart: EChartsCoreOption = {
    grid: {
      left: '5%',
      right: '5%',
      top: '10%',
      bottom: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: this.barData.map((value) => ({
          value: value,
          itemStyle: {
            color: value > 0 ? '#22c55e' : '#ef4444',
          },
        })),
        type: 'bar',
        barWidth: '20%',
      },
    ],
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
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: [1, 6, 8, 16, 26, 30, 62],
        type: 'line',
        areaStyle: {},
        itemStyle: {
          color: '#22c55e',
        },
      },
    ],
  };

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

  getModels(): void {
    if (!this.model_id) return;

    this.apiService.get(`v1/models/${this.model_id}`).subscribe({
      next: (response: any) => this.model = response.model,
      error: (error) => console.error('Failed to fetch models:', error),
    });
  }
  
  copy_trade(): void {
    const body = {
      portfolio_id: this.selectedPortfolio?.portfolio_id
    };

    this.apiService.put(`/v1/models/${this.model_id}/copy`, body).subscribe({
      next: (response) => {
        console.log(response);
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Copy trade Successfully'
        });
      },
      error: (error) => {
        console.error('Fetch failed:', error);
      },
    });
  }
}
