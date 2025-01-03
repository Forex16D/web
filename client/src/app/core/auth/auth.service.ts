// import { HttpClient } from '@angular/common/http';
import { Injectable, Inject, PLATFORM_ID, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authStateSignal = signal(this.isAuthenticated());
  get authState() {
    return this.authStateSignal();
  }

  private readonly apiUrl = 'https://api.example.com/auth';

  // constructor(private http: HttpClient) {}

  // login(credentials: { email: string; password: string }): Observable<any> {
  //   return this.http.post(`${this.apiUrl}/login`, credentials).pipe(
  //     tap((response: any) => {
  //       if (response.token) {
  //         localStorage.setItem('authToken', response.token);
  //       }
  //     })
  //   );
  // }
  constructor(@Inject(PLATFORM_ID) private platformId: object) {
    if (isPlatformBrowser(this.platformId)) {
      const token = localStorage.getItem('authToken');
      this.authStateSignal.set(!!token);
    }
  }

  login(): void {
    if (isPlatformBrowser(this.platformId)){
      localStorage.setItem('authToken', 'thisisauth')
      this.authStateSignal.set(true);
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
