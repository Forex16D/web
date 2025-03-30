import { Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { ChartModule } from 'primeng/chart';
import { CurrencyPipe } from '@angular/common';
import { NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Model } from '../../models/model.model';

@Component({
  selector: 'app-bot-card',
  imports: [ButtonModule, TagModule, ChartModule, NgClass, RouterLink],
  templateUrl: './bot-card.component.html',
  styleUrl: './bot-card.component.css',
  providers: [CurrencyPipe],
})
export class BotCardComponent {
  @Input() model?: Model;

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  roiFormatted: string = '-';
  balanceFormatted: string = '-';
  pnlTextColor: string = 'text-white';

  constructor(private currency: CurrencyPipe) { }

  ngOnChanges(): void {
    this.transformData();
  }

  updateGraphData(): void {
    if (!this.model) return;
    this.graphData = {
      labels: this.model.weekly_profits.map(profit => profit.week_start),
      datasets: [
        {
          data: this.model.weekly_profits.map(profit => profit.weekly_profit),
          borderColor: '#05df72',
          backgroundColor: '#172425',
          tension: 0.4,
          fill: true,
          borderWidth: 2,
        }
      ]
    };
  }

  graphData = {
    labels: ['January', 'February', 'March', 'April'],
    datasets: [
      {
        data: [-1, 65, 59, 80],
        borderColor: '#05df72',
        backgroundColor: '#172425',
        tension: 0.4,
        fill: true,
        borderWidth: 2,
      }
    ]
  };

  options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false // Hides the legend
      }
    },
    scales: {
      x: {
        display: false
      },
      y: {
        display: false
      }
    },
    layout: {
      padding: 0 // No padding around the chart
    },
    elements: {
      point: {
        radius: 0 // Removes points
      }
    }
  };

  onChartHover(event: any) {
    const activePoints = event.chart.getElementsAtEventForMode(event.event, 'nearest', { intersect: true }, true);
    if (activePoints.length > 0) {
      const index = activePoints[0].index;
      const label = event.chart.graphData.labels[index];
      const value = event.chart.graphData.datasets[0].data[index];
      console.log(`Hovered over: ${label} - ${value}`);
    }
  }


  transformData(): void {
    const pnlValue: number = this.model?.monthly_pnl || 0;
    const winrateValue: number = this.model?.winrate || 0;
    console.log(winrateValue)
    this.pnlTextColor = pnlValue > 0 ? 'text-green-400' : pnlValue < 0 ? 'text-red-400' : 'text-white';
    this.pnlFormatted = isNaN(pnlValue) ? '-' : pnlValue >= 0 ? `+$${pnlValue}` : `-$${Math.abs(pnlValue)}`;
    this.winrateFormatted = isNaN(winrateValue) ? '-' : `${Number(winrateValue).toFixed(2)}%`;
  }

}