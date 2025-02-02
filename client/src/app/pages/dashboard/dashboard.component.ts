import { Component, viewChild } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { PortfolioCardComponent } from '../../components/portfolio-card/portfolio-card.component';
import { NgFor } from '@angular/common';
import { ViewContainerRef } from '@angular/core';
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

import { NgxEchartsModule, provideEchartsCore, NgxEchartsDirective } from 'ngx-echarts';

import * as echarts from 'echarts/core';
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
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
  providers: [
    provideEchartsCore({ echarts }),
  ],
})
export class DashboardComponent {
  vcr = viewChild('container', { read: ViewContainerRef });
  isBalanceVisible = false;
  isDialogVisible = false;

  components = [PortfolioCardComponent, PortfolioCardComponent, PortfolioCardComponent, PortfolioCardComponent]
  portfolioDataArray = [
    {
      credential: { id: '0', name: 'Portfolio 1', login: '334067889' },
      data: { pnl: '200', winrate: '85', roi: '10', balance: '1500.25' },
    },
    {
      credential: { id: '1', name: 'Portfolio 2', login: '44528976' },
      data: { pnl: '-102', winrate: '8', roi: '-10', balance: '1500000' },
    },
    {
      credential: { id: '2', name: 'Portfolio 3', login: '66548884' },
    },
  ];

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

  constructor(private themeService: ThemeService) { }

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
}
