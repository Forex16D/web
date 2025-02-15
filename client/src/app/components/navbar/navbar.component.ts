import { NgClass, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { DividerModule } from 'primeng/divider';
import { LogoComponent } from '../logo/logo.component';
import { ButtonModule } from 'primeng/button';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { MessageService } from 'primeng/api';
import { ConfirmationService } from 'primeng/api';
import { Router } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { response } from 'express';

@Component({
  selector: 'app-navbar',
  imports: [
    NgClass,
    DividerModule,
    LogoComponent,
    ButtonModule,
    RouterLink,
    NgIf,
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {
  isVisible = true;
  profile: any = {};

  constructor(
    public authService: AuthService,
    private router: Router,
    private confirmationService: ConfirmationService,
    private messageService: MessageService,
    private apiService: ApiService,
  ) { 
    this.getProfile()
  }

  logout(event: Event): void {
    this.confirmationService.confirm({
      target: event.target as EventTarget,
      message: 'Are you sure you want to log out?',
      header: 'Log out Confirmation',
      icon: 'pi pi-sign-out',
      acceptLabel: 'Log out',
      rejectLabel: 'Cancel',
      closeOnEscape: true,
      closable: true,
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.messageService.add({ severity: 'info', summary: 'Logged out', detail: 'You have successfully logged out.' });
        this.authService.logout();
        this.router.navigate(['/']);
      },
    });
  }

  login(): void {
    this.router.navigate(['/login']);
  }

  getProfile(): void {
    this.apiService.get('v1/users/profile').subscribe({
      next: (response) => this.profile = response,
      error: (error) => console.error(error)
    })
  }
}
