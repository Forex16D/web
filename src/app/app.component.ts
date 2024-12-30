import { Component, Inject, PLATFORM_ID, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from './core/auth/auth.service';
import { NgIf, isPlatformBrowser } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { PlatformService } from './core/services/platform.service';
import { ThemeService } from './core/services/theme.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NgIf, RouterLink],
  template: `
  <ng-container *ngIf="isBrowser; else ssrPlaceholder">
    <a routerLink="/">Home</a>
    |
    <a routerLink="/dashboard">Dashboard</a>
    <router-outlet></router-outlet>
    <button *ngIf="isAuth" (click)="logout()">Logout</button>
  </ng-container>
  <ng-template #ssrPlaceholder>   
    <div class="loading-spinner">Loading...</div>
  </ng-template>

  `,
  styleUrls: ['./app.component.css'],
})
export class AppComponent {   
  title = 'forex16d';
  isAuth = signal(false);
  isBrowser: boolean;

  constructor(private authService: AuthService, 
    private router: Router, 
    private platformService : PlatformService,
  ) {
    this.isBrowser = this.platformService.isBrowser();
    this.isAuth.set(authService.authState);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
