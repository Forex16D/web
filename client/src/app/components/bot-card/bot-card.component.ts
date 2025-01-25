import { Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { SafeCurrencyPipe } from '../../shared/pipes/safe-currency.pipe';
import { CurrencyPipe } from '@angular/common';
import { NgClass } from '@angular/common';
import { TagModule } from 'primeng/tag';
import { ChartModule } from 'primeng/chart';

@Component({
  selector: 'app-bot-card',
  imports: [ButtonModule, SafeCurrencyPipe, CurrencyPipe, NgClass, TagModule, ChartModule],
  templateUrl: './bot-card.component.html',
  styleUrl: './bot-card.component.css'
})
export class BotCardComponent {
  data = {
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
        display:false
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
      const label = event.chart.data.labels[index];
      const value = event.chart.data.datasets[0].data[index];
      console.log(`Hovered over: ${label} - ${value}`);
    }
  }
}