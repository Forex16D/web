import { Component, Input} from '@angular/core';

@Component({
  selector: 'app-logo',
  imports: [],
  templateUrl: './logo.component.html',
  styleUrl: './logo.component.css'
})
export class LogoComponent {
  @Input() size = '32px';
  color1 = '#D4AF37';
  color2 = '#0ECB81'
}
