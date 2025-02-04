import { CanActivateFn } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';

export const authRedirectGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return new Observable<boolean>((observer) => {
    authService.isAuthenticated().subscribe((isAuthenticated) => {
      if (isAuthenticated) {
        router.navigate(['']);
        observer.next(false);
      } else {
        observer.next(true);
      }
      observer.complete();
    });
  });
};
