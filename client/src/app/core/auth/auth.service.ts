import { Injectable, Inject, PLATFORM_ID, signal, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';
import { isPlatformBrowser } from '@angular/common';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class AuthService {
  private authStateSignal = signal(this.isAuthenticated());

  get authState1() {
    return this.authStateSignal
  }

  get authState() {
    return this.authStateSignal();
  }

  constructor(@Inject(PLATFORM_ID) private platformId: object, private apiService: ApiService) {
    this.authStateSignal.set(this.isAuthenticated())
  }

  register(): void {
    console.log('registered');
  }

  login(email: string, password: string): Observable<any> {
    if (isPlatformBrowser(this.platformId)) {
      const data = { email, password };
      return this.apiService.postData('v1/login', data).pipe(
        tap((response) => {
          if (response.token) {
            localStorage.setItem('authToken', response.token);
            this.authStateSignal.set(true);
          } else {
            console.error('Login response did not contain a token');
            this.authStateSignal.set(false); 
          }
        })
      );
    } else {
      return new Observable(observer => {
        observer.error('Login can only be performed in a browser environment');
      });
    }
  }

  logout(): void {
    if (isPlatformBrowser(this.platformId)){
      localStorage.removeItem('authToken');
      this.authStateSignal.set(false);
    }
  }

  isAuthenticated(): boolean {
    if (isPlatformBrowser(this.platformId)) {
      return !!localStorage.getItem('authToken');
    }
    return false;
  }

  getToken(): string | null {
    return localStorage.getItem('authToken');
  }
}
