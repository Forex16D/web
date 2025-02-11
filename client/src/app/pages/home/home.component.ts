import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { RouterLink } from '@angular/router';
import { PriceChartComponent } from '../price-chart/price-chart.component';
import { MiniPriceChartComponent } from '../../components/mini-price-chart/mini-price-chart.component';

@Component({
  selector: 'app-home',
  imports: [ButtonModule, RouterLink, PriceChartComponent, MiniPriceChartComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  backgroundImage: string = '/images/the_ai.jpg';
}
