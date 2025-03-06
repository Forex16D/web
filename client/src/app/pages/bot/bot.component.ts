import { Component, OnInit } from '@angular/core';
import { BotCardComponent } from '../../components/bot-card/bot-card.component';
import { ApiService } from '../../core/services/api.service';
import { Model } from '../../models/model.model';
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-bot',
  imports: [
    BotCardComponent,
    NgFor
  ],
  templateUrl: './bot.component.html',
  styleUrl: './bot.component.css'
})
export class BotComponent implements OnInit {
  models: Model[] = [];

  constructor(
    private apiService: ApiService,
  ) {}

  ngOnInit(): void {
    this.getModels();
  }

  getModels(): void {
    this.apiService.get('v1/models/user').subscribe({
      next: (response: any) => this.models = response.models,
      error: (error) => console.error('Failed to fetch models:', error),
    });
  }
}
