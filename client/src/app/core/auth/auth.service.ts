import { Injectable, Inject, PLATFORM_ID, signal } from '@angular/core';
import { ApiService } from '../services/api.service';
import { isPlatformBrowser } from '@angular/common';
import { Observable, of } from 'rxjs';
import { tap, map, catchError } from 'rxjs/operators';

interface LoginResponse {
  token: string;
}

interface AuthResponse {
  authentication: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authStateSignal = signal(false);

  get authState() {
    return this.authStateSignal();
  }

  constructor(@Inject(PLATFORM_ID) private platformId: object, private apiService: ApiService) {
    this.initializeAuthState();
  }

  private initializeAuthState(): void {
    this.isAuthenticated().subscribe((isAuth) => {
      this.authStateSignal.set(isAuth);
    });
  }

  register(email: string, password: string, confirmPassword: string): Observable<any> {
    if (isPlatformBrowser(this.platformId)) {
      const data = { email, password, confirmPassword };
      return this.apiService.post('v1/register', data);
    } else {
      return new Observable(observer => {
        observer.error('Register can only be performed in a browser environment');
      });
    }
  }

  login(email: string, password: string): Observable<LoginResponse> {
    if (isPlatformBrowser(this.platformId)) {
      const data = { email, password };
      return this.apiService.post<LoginResponse>('v1/login', data).pipe(
        tap((response: LoginResponse) => {
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
      return new Observable((observer) => {
        observer.error('Login can only be performed in a browser environment');
      });
    }
  }

  logout(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('authToken');
      this.authStateSignal.set(false);
    }
  }

  isAuthenticated(): Observable<boolean> {
    if (isPlatformBrowser(this.platformId)) {
      return this.apiService.get<AuthResponse>('v1/auth').pipe(
        tap((response: AuthResponse) => {
          if (response.authentication) {
            this.authStateSignal.set(true);
          } else {
            this.authStateSignal.set(false);
          }
        }),
        map((response: AuthResponse) => response.authentication),
        catchError((error) => {
          console.error('Error checking authentication:', error);
          this.authStateSignal.set(false);
          return of(false);
        })
      );
    }
    return of(false);
  }

  getToken(): string | null {
    return localStorage.getItem('authToken');
  }
}
