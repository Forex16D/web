import { Component } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import {MatButtonModule} from '@angular/material/button'; 

@Component({
  selector: 'app-dashboard',
  imports: [MatSlideToggleModule, MatButtonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  
  constructor(private themeService: ThemeService ) {}

  lightMode() {
    this.themeService.toggleTheme();
  }
}
