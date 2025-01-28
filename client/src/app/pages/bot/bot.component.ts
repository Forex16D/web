import { Component } from '@angular/core';
import { BotCardComponent } from '../../components/bot-card/bot-card.component';
import { Input } from '@angular/core';
import { CurrencyPipe } from '@angular/common';

@Component({
  selector: 'app-bot',
  imports: [BotCardComponent],
  templateUrl: './bot.component.html',
  styleUrl: './bot.component.css'
})
export class BotComponent {

}
