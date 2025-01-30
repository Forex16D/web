import { Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CurrencyPipe } from '@angular/common';
import { NgClass } from '@angular/common';
import { TagModule } from 'primeng/tag';
import { MenuModule } from 'primeng/menu';
import { RippleModule } from 'primeng/ripple';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { RouterLink } from '@angular/router';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-portfolio-card',
  imports: [
    ButtonModule,
    NgClass,
    TagModule,
    MenuModule,
    RippleModule,
    DialogModule,
    InputTextModule,
    RouterLink,
  ],
  templateUrl: './portfolio-card.component.html',
  styleUrl: './portfolio-card.component.css',
  providers: [CurrencyPipe]
})
export class PortfolioCardComponent {
  @Input() credential = {
    id: '0',
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

  visible = false;

  menuItems = [
    { label: 'Detail', icon: 'pi pi-info-circle', command: () => this.detailItem() },
    { label: 'Edit', icon: 'pi pi-cog', command: () => this.editItem() },
    { label: 'Delete', icon: 'pi pi-trash' }
  ];

  constructor(
    private currency: CurrencyPipe,
    private activatedRoute: ActivatedRoute,
    private router: Router,
  ) { }

  ngOnChanges(): void {
    this.transformData();
  }

  transformData(): void {
    const pnlValue = parseFloat(this.data.pnl);
    const winrateValue = parseFloat(this.data.winrate);
    const roiValue = parseFloat(this.data.roi);
    const balanceValue = parseFloat(this.data.balance);

    this.pnlTextColor = pnlValue > 0 ? 'text-green-400' : pnlValue < 0 ? 'text-red-400' : 'text-white';
    this.pnlFormatted = isNaN(pnlValue) ? '-' : pnlValue >= 0 ? `+$${pnlValue}` : `-$${Math.abs(pnlValue)}`;
    this.winrateFormatted = isNaN(winrateValue) ? '-' : `${winrateValue}%`;
    this.roiFormatted = isNaN(roiValue) ? '-' : `${roiValue}%`;
    this.balanceFormatted = isNaN(balanceValue)
      ? '-'
      : this.currency.transform(balanceValue, 'USD', 'symbol', '.2-2') || '-';
  }

  editItem(): void {
    this.visible = true;
  }

  detailItem(): void {
    this.router.navigate([`/portfolio/${this.credential.id}`])
  }
}