import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { authGuard } from './core/auth/auth.guard';
import { authRedirectGuard } from './core/auth/auth-redirect.guard';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { RegisterComponent } from './pages/register/register.component';
import { AdminComponent } from './pages/admin/admin.component';
import { adminAuthGuard } from './core/auth/admin-auth.guard';
import { HomeComponent } from './pages/home/home.component';
import { BotComponent } from './pages/bot/bot.component';
import { BotDetailComponent } from './pages/bot-detail/bot-detail.component';
import { PriceChartComponent } from './pages/price-chart/price-chart.component';
import { PortfolioDetailComponent } from './pages/portfolio-detail/portfolio-detail.component';
import { BillComponent } from './pages/bill/bill.component';
import { PaymentComponent } from './pages/payment/payment.component';
import { CopyTradeComponent } from './pages/copy-trade/copy-trade.component';
import { TermsAndConditionsComponent } from './pages/terms-and-conditions/terms-and-conditions.component';
import { DownloadComponent } from './pages/download/download.component';
import { getPrerenderParams } from '../server';

export const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
  },
  {
    path: 'login',
    component: LoginComponent,
    canActivate: [authRedirectGuard]
  },
  {
    path: 'register',
    component: RegisterComponent,
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [adminAuthGuard]
  },
  {
    path: 'bot',
    component: BotComponent,
  },
  {
    path: 'copy-trade',
    component: CopyTradeComponent,
  },
  {
    path: 'bot/detail/:model_id',
    component: BotDetailComponent,
    data: {prerender: false}    
  },
  {
    path: 'price-chart',
    component: PriceChartComponent,
  },
  {
    path: 'portfolio/:portfolio_id',
    component: PortfolioDetailComponent,
  },
  {
    path: 'bills',
    component: BillComponent,
    canActivate: [authGuard]
  },
  {
    path: 'payment',
    component: PaymentComponent,
  },
  {
    path: 'terms-and-conditions',
    component: TermsAndConditionsComponent,
  },
  {
    path: 'download',
    component: DownloadComponent,
  }
];

