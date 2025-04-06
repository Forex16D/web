import { RenderMode, ServerRoute } from '@angular/ssr';
import { BotDetailComponent } from './pages/bot-detail/bot-detail.component';

export const serverRoutes: ServerRoute[] = [
  {
    path: 'bot/detail/:model_id',
    renderMode: RenderMode.Client,  
  },
  {
    path: 'portfolio/:portfolio_id',
    renderMode: RenderMode.Client,  
  },
  {
    path: '**',
    renderMode: RenderMode.Prerender
  }
];
