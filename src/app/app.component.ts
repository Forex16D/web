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
  templateUrl: './app.component.html',
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
