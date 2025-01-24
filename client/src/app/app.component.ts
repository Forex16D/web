import { Component, Inject, OnInit, PLATFORM_ID, signal } from '@angular/core';
import { Router, RouterLink, NavigationEnd } from '@angular/router';
import { AuthService } from './core/auth/auth.service';
import { NgIf } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { PlatformService } from './core/services/platform.service';
import { LogoComponent } from './components/logo/logo.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NgIf, RouterLink, LogoComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {   
  title = 'forex16d';
  isBrowser: boolean;
  showNavbar = true;
  private routesWithoutNavbar = ['/login', '/register'];

  constructor(
    public authService: AuthService, 
    private router: Router, 
    private platformService : PlatformService,
  ) {
    this.isBrowser = this.platformService.isBrowser();
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        const path = event.url.split('?')[0];
        this.showNavbar = !this.routesWithoutNavbar.includes(path);
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
