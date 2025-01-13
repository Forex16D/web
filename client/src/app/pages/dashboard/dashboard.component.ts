import { Component, viewChild, ViewChild } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { PortfolioCardComponent } from '../../components/portfolio-card/portfolio-card.component';
import { NgClass, NgFor, NgComponentOutlet } from '@angular/common';
import { ViewContainerRef } from '@angular/core';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-dashboard',
  imports: [ButtonModule, PortfolioCardComponent, NgClass, NgFor, NgComponentOutlet],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  vcr = viewChild('container', {read: ViewContainerRef});
  isHidden = true;
  components = [PortfolioCardComponent, PortfolioCardComponent, PortfolioCardComponent, PortfolioCardComponent]
  constructor(private themeService: ThemeService) {}

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
