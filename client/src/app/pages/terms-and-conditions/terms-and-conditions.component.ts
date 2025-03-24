import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { RouterLink } from '@angular/router';
import { PriceChartComponent } from '../price-chart/price-chart.component';
import { MiniPriceChartComponent } from '../../components/mini-price-chart/mini-price-chart.component';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-terms-and-conditions',
  imports: [
    ButtonModule, 
    RouterLink, 
    PriceChartComponent, 
    MiniPriceChartComponent,
    TagModule,
  ],
  templateUrl: './terms-and-conditions.component.html',
  styleUrl: './terms-and-conditions.component.css'
})
export class TermsAndConditionsComponent {

}
