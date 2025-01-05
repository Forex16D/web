import { Injectable, signal, OnInit } from '@angular/core';
import { PlatformService } from '../services/platform.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService implements OnInit {
  private authStateSignal = signal(false);
  get authState() {
    return this.authStateSignal();
  }

  constructor(private platformService: PlatformService) {}

  ngOnInit(): void {
    if (this.platformService.isBrowser()) {
      const token = localStorage.getItem('authToken');
      this.authStateSignal.set(!!token);
    }
  }

  register(): void {
    console.log('registered');
  }

  login(): void {
    if (this.platformService.isBrowser()){
      localStorage.setItem('authToken', 'thisisauth');
      this.authStateSignal.set(true);
    }
  }

  logout(): void {
    if (this.platformService.isBrowser()){
      localStorage.removeItem('authToken');
      this.authStateSignal.set(false);
    }
  }

  isAuthenticated(): boolean {
    if (this.platformService.isBrowser()) {
      return !!localStorage.getItem('authToken');
    }
    return false;
  }

  getToken(): string | null {
    return localStorage.getItem('authToken');
  }
}
