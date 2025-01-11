import { Component } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button'; 
import { PortfolioCardComponent } from '../../components/portfolio-card/portfolio-card.component';

@Component({
  selector: 'app-dashboard',
  imports: [MatSlideToggleModule, MatButtonModule, PortfolioCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  
  constructor(private themeService: ThemeService ) {}

  lightMode() {
    this.themeService.toggleTheme();
  }
}
