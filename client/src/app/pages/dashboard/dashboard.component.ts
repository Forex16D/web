import { Component, viewChild} from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { PortfolioCardComponent } from '../../components/portfolio-card/portfolio-card.component';
import { NgFor, NgComponentOutlet } from '@angular/common';
import { ViewContainerRef } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { BotCardComponent } from '../../components/bot-card/bot-card.component';

@Component({
  selector: 'app-dashboard',
  imports: [ButtonModule, PortfolioCardComponent, NgFor, NgComponentOutlet, BotCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  vcr = viewChild('container', { read: ViewContainerRef });
  isHidden = true;
  components = [PortfolioCardComponent, PortfolioCardComponent, PortfolioCardComponent, PortfolioCardComponent]
  portfolioDataArray =  [
    {
      credential: { name: 'John Doe', login: '334067889' },
      data: { pnl: '200', winrate: '85', roi: '10', balance: '1500.25' },
    },
    {
      credential: { name: 'Jane Doe', login: '44528976' },
      data: { pnl: '-102', winrate: '8', roi: '-10', balance: '1500000' },
    },
    {
      credential: { name: 'Chris Lee', login: '66548884' },
    },
  ];

  
  defaultData = {
    pnl: '',
    winrate: '',
    roi: '',
    balance: '',
  };

  constructor(private themeService: ThemeService) { }

  createComponent(): void {
    this.vcr()?.createComponent(PortfolioCardComponent);
  }

  lightMode() {
    this.themeService.toggleTheme();
  }

  toggleVisibility(): void {
    this.isHidden = !this.isHidden;
  }
}
