import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button'
import { ThemeService } from '../../core/services/theme.service';

@Component({
  selector: 'app-dashboard',
  imports: [ButtonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  
  constructor(private themeService: ThemeService ) {}

  lightMode() {
    this.themeService.toggleTheme();
  }
}
