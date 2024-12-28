// import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs';
import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authStateSubject = new BehaviorSubject<boolean>(this.isAuthenticated());
  authState$ = this.authStateSubject.asObservable();
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
      this.authStateSubject.next(!!token);
    }
  }

  login(): void {
    if (isPlatformBrowser(this.platformId)){
      localStorage.setItem('authToken', 'thisisauth')
      this.authStateSubject.next(true);
    }
  } 
  
  logout(): void {
    if (isPlatformBrowser(this.platformId)){
      localStorage.removeItem('authToken');
      this.authStateSubject.next(false);
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
