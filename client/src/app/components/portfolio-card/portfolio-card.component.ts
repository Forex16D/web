import { Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { SafeCurrencyPipe } from '../../shared/pipes/safe-currency.pipe';
import { CurrencyPipe } from '@angular/common';
import { NgClass } from '@angular/common';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-portfolio-card',
  imports: [ButtonModule, SafeCurrencyPipe, CurrencyPipe, NgClass, TagModule],
  templateUrl: './portfolio-card.component.html',
  styleUrl: './portfolio-card.component.css',
  providers: [CurrencyPipe]
})
export class PortfolioCardComponent {
  @Input() credential = {
    name: 'Portfolio',
    login: 'login',
  }

  @Input() data = {
    pnl: '',
    winrate: '',
    roi: '',
    balance: '',
  };

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  roiFormatted: string = '-';
  balanceFormatted: string = '-';
  pnlTextColor: string = 'text-white';

  constructor(private currency: CurrencyPipe) { }

  ngOnChanges(): void {
    this.transformData();
  }

  transformData(): void {
    const pnlValue  = parseFloat(this.data.pnl);
    const winrateValue  = parseFloat(this.data.winrate);
    const roiValue  = parseFloat(this.data.roi);
    const balanceValue = parseFloat(this.data.balance);

    this.pnlTextColor = pnlValue > 0 ? 'text-green-400' : pnlValue < 0 ? 'text-red-400' : 'text-white'; 
    this.pnlFormatted = isNaN(pnlValue) ? '-' : pnlValue >= 0 ? `+$${pnlValue}` : `-$${Math.abs(pnlValue)}`;
    this.winrateFormatted = isNaN(winrateValue) ? '-' : `${winrateValue}%`;
    this.roiFormatted = isNaN(roiValue) ? '-' : `${roiValue}%`;
    this.balanceFormatted = isNaN(balanceValue)
      ? '-'
      : this.currency.transform(balanceValue, 'USD', 'symbol', '.2-2') || '-';
  }
}