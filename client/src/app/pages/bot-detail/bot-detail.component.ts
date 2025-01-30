import { Component } from '@angular/core';
import { EChartsCoreOption } from 'echarts/core';
import { NgxEchartsModule, provideEchartsCore, NgxEchartsDirective } from 'ngx-echarts';
import { BarChart } from 'echarts/charts';
import { LineChart } from 'echarts/charts';
import { GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { PriceChartComponent } from '../price-chart/price-chart.component';
import { NgClass } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';

import * as echarts from 'echarts/core';
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
  ],
  templateUrl: './bot-detail.component.html',
  styleUrl: './bot-detail.component.css',
  providers: [
    provideEchartsCore({ echarts }),
  ],
})

export class BotDetailComponent {
  visible = false;

  showDialog(): void {
    this.visible = !this.visible;
  }

  data = {
    backtest: "126D",
    start_balance: "1000",
    risk_reward_ratio: "2.26",
    roi: "0.71",
    pnl: "$710.86",
    max_drawdown: "0.16",
    winrate: "0.5882",
    win: "20",
    loss: "14",
    total: "34",
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
}
