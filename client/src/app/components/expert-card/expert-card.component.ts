import { Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { ChartModule } from 'primeng/chart';
import { CurrencyPipe, NgClass, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PortfolioResponse } from '../../models/portfolio-response.model';

@Component({
  selector: 'app-expert-card',
  standalone: true,
  imports: [ButtonModule, TagModule, ChartModule, NgClass, RouterLink, NgIf],
  templateUrl: './expert-card.component.html',
  styleUrls: ['./expert-card.component.css'],
  providers: [CurrencyPipe],
})
export class ExpertCardComponent {
  @Input() portfolio?: PortfolioResponse;

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  profitFormatted: string = '-';
  pnlTextColor: string = 'text-white';

  constructor(private currency: CurrencyPipe) { }

  ngOnChanges(): void {
    this.transformData();
  }

  graphData = {
    labels: ['January', 'February', 'March', 'April'],
    datasets: [
      {
        data: [-1, 65, 59, 1],
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
        display: false
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
      padding: 0
    },
    elements: {
      point: {
        radius: 0
      }
    }
  };

  onChartHover(event: any) {
    const activePoints = event.chart.getElementsAtEventForMode(
      event.event,
      'nearest',
      { intersect: true },
      true
    );

    if (activePoints.length > 0) {
      const index = activePoints[0].index;
      const label = event.chart.graphData.labels[index];
      const value = event.chart.graphData.datasets[0].data[index];
      console.log(`Hovered over: ${label} - ${value}`);
    }
  }

  transformData(): void {
    if (!this.portfolio) return;

    const pnlValue = this.portfolio.monthly_pnl || 0;
    const winrateValue = this.portfolio.winrate || 0;
    const profitValue = this.portfolio.total_profit || 0;

    this.pnlTextColor = pnlValue > 0 ? 'text-green-400' : pnlValue < 0 ? 'text-red-400' : 'text-white';

    this.pnlFormatted = pnlValue === null ? '-' :
      pnlValue >= 0 ? `+$${pnlValue.toFixed(2)}` : `-$${Math.abs(pnlValue).toFixed(2)}`;
    this.winrateFormatted = isNaN(Number(winrateValue)) ? '-' : `${Number(winrateValue).toFixed(1)}%`;
    this.profitFormatted = profitValue === null ? '-' :
      this.currency.transform(profitValue, 'USD', 'symbol', '.2-2') || '-';
  }

  getDaysActive(): string {
    if (!this.portfolio?.created_at) return '-';

    const createdDate = new Date(this.portfolio.created_at);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - createdDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    return `${diffDays}D`;
  }
}