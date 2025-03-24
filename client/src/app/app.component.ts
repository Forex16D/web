import { Component, Inject, OnInit, PLATFORM_ID, signal } from '@angular/core';
import { Router, RouterLink, NavigationEnd } from '@angular/router';
import { AuthService } from './core/auth/auth.service';
import { NgClass, NgIf } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { PlatformService } from './core/services/platform.service';
import { LogoComponent } from './components/logo/logo.component';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { NavbarComponent } from './components/navbar/navbar.component';
import { ConfirmationService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { FooterComponent } from './components/footer/footer.component';
@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet, 
    NgIf, 
    RouterLink, 
    LogoComponent, 
    ToastModule, 
    NavbarComponent, 
    NgClass, 
    ConfirmDialogModule,
    FooterComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [MessageService, ConfirmationService]
})
export class AppComponent {   
  title = 'forex16d';
  isBrowser: boolean;
  showNavbar = true;
  private routesWithoutNavbar = ['/login', '/register', '/admin'];

  constructor(
    public authService: AuthService, 
    public router: Router, 
    private platformService : PlatformService,
    private messageService: MessageService,
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
