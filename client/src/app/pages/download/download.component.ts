import { Component } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-download',
  imports: [
    ButtonModule,

  ],
  templateUrl: './download.component.html',
  styleUrl: './download.component.css'
})
export class DownloadComponent {
  constructor(private apiService: ApiService) {}

  downloadStandard() {
    const fileName = 'forex16d.ex5';
    this.apiService.downloadFile(fileName);
  }

  downloadSubscriber() {
    const fileName = 'subscriber.ex5';
    this.apiService.downloadFile(fileName);
  }
}