import { Component, Input, OnInit, signal } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { ChartModule } from 'primeng/chart';
import { CurrencyPipe, NgClass, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Expert } from '../../models/expert.model';
import { DialogModule } from 'primeng/dialog';
import { DropdownModule } from 'primeng/dropdown';
import { ApiService } from '../../core/services/api.service';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-expert-card',
  standalone: true,
  imports: [
    ButtonModule,
    TagModule,
    ChartModule,
    NgClass,
    RouterLink,
    NgIf,
    DialogModule,
    DropdownModule,
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './expert-card.component.html',
  styleUrls: ['./expert-card.component.css'],
  providers: [CurrencyPipe],
})
export class ExpertCardComponent implements OnInit{
  @Input() portfolio?: Expert;

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  profitFormatted: string = '-';
  pnlTextColor: string = 'text-white';

  dialogVisible = false;
  userPortfolios = signal<any[]>([])
  selectedPortfolio: any | null =  null;

  constructor(private currency: CurrencyPipe, private apiService: ApiService, private messageService: MessageService) { }

  ngOnInit(): void {
    this.getPortfolios()
  }

  ngOnChanges(): void {
    this.transformData();

    if (this.portfolio && this.portfolio.weekly_profits && this.portfolio.weekly_profits.length > 0) {
      console.log(this.portfolio.weekly_profits);
      this.updateGraphData();
    }
  }

  getPortfolios(): void {
    this.apiService.get('v1/portfolios').subscribe({
      next: (response: any) => {
        this.userPortfolios.set(response);
        console.log(response);
      },
      error: (error) => {
        console.error('Fetch failed:', error);
      },
    });
  }

  updateGraphData(): void {
    if (!this.portfolio) return;
    this.graphData = {
      labels: this.portfolio.weekly_profits.map(profit => profit.week_start),
      datasets: [
        {
          data: this.portfolio.weekly_profits.map(profit => profit.weekly_profit),
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
    labels: ['A'],
    datasets: [
      {
        data: [0],
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

  onCopyTrade(): void {
    this.copy_trade();
    this.dialogVisible = false;
  }

  copy_trade(): void {
    const body = {
      portfolio_id: this.selectedPortfolio?.portfolio_id
    };

    this.apiService.put(`/v1/portfolios/${this.portfolio?.portfolio_id}/copy`, body).subscribe({
      next: (response) => {
        console.log(response);
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Copy trade Successfully'
        });
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'error',
          detail: 'Copy trade Failed'
        });
        console.error('Fetch failed:', error);
      },
    });
  }

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