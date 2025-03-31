import { AfterViewInit, Component, Input, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { ChartModule } from 'primeng/chart';
import { CurrencyPipe } from '@angular/common';
import { NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Model } from '../../models/model.model';

import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { EChartsOption } from 'echarts/types/dist/shared';
import { NgxEchartsDirective } from 'ngx-echarts';

echarts.use([LineChart]);
@Component({
  selector: 'app-bot-card',
  imports: [ButtonModule, TagModule, ChartModule, NgClass, RouterLink, NgxEchartsDirective],
  templateUrl: './bot-card.component.html',
  styleUrl: './bot-card.component.css',
  providers: [CurrencyPipe],
})
export class BotCardComponent implements OnInit, AfterViewInit {
  @Input() model?: Model;

  lineChart: EChartsOption = {};

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  roiFormatted: string = '-';
  balanceFormatted: string = '-';
  pnlTextColor: string = 'text-white';

  constructor() { }

  ngOnInit(): void {
    this.updatePnlFormatted()
    this.updateWinrateFormatted()
  }

  ngAfterViewInit(): void {
    this.updateChartData();
  }

  updatePnlFormatted(): void {
    if (!this.model) return;
    const pnl = this.model.monthly_pnl || 0;
    this.pnlFormatted = pnl >= 0 ? `+$${pnl.toFixed(2)}` : `-$${Math.abs(pnl).toFixed(2)}`;
    this.pnlTextColor = pnl >= 0 ? 'text-green-500' : 'text-red-500';
  }

  updateWinrateFormatted(): void {
    if (!this.model || !this.model.winrate) return;
    this.winrateFormatted = `${Number(this.model.winrate).toFixed(2)}%`;
  }


  updateChartData(): void {
    if (!this.model) return;
    
    const data = this.model.weekly_profits?.map(profit => profit.weekly_profit) || [-1, 65, 59, 80];
    const labels = this.model.weekly_profits?.map(profit => profit.week_start) || ['January', 'February', 'March', 'April'];
    
    this.lineChart = {
      grid: {
        left: 0,
        right: 0,
        top: 0,
        bottom: 0
      },
      xAxis: {
        type: 'category',
        data: labels,
        show: false
      },
      yAxis: {
        type: 'value',
        show: false
      },
      series: [{
        data: data,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#05df72',
          width: 2
        },
        areaStyle: {
          color: '#172425'
        }
      }],
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const value = params[0].value;
          return `${params[0].name}: ${value >= 0 ? '+' : ''}$${value.toFixed(2)}`;
        }
      }
    };
  }

  onChartHover(event: any) {
    const activePoints = event.chart.getElementsAtEventForMode(event.event, 'nearest', { intersect: true }, true);
    if (activePoints.length > 0) {
      const index = activePoints[0].index;
      const label = event.chart.graphData.labels[index];
      const value = event.chart.graphData.datasets[0].data[index];
      console.log(`Hovered over: ${label} - ${value}`);
    }
  }
}