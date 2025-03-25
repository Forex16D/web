import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { RouterLink } from '@angular/router';
import { MiniPriceChartComponent } from '../../components/mini-price-chart/mini-price-chart.component';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-home',
  imports: [
    ButtonModule, 
    RouterLink,
    MiniPriceChartComponent,
    TagModule,
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  backgroundImage: string = '/images/the_ai.jpg';
}
