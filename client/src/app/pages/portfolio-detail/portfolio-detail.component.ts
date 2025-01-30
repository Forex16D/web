import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-portfolio-detail',
  imports: [RouterLink, ButtonModule],
  templateUrl: './portfolio-detail.component.html',
  styleUrl: './portfolio-detail.component.css'
})
export class PortfolioDetailComponent {

}
