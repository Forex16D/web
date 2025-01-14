import { Routes } from '@angular/router';
import { HelloComponent } from './hello/hello.component';
import { LoginComponent } from './pages/login/login.component';
import { authGuard } from './core/auth/auth.guard';
import { authRedirectGuard } from './core/auth/auth-redirect.guard';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { RegisterComponent } from './pages/register/register.component';
import { AdminComponent } from './pages/admin/admin.component';
import { adminAuthGuard } from './core/auth/admin-auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: HelloComponent,
    canActivate: [authGuard]
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
];
