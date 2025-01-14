import { CanActivateFn } from '@angular/router';

export const adminAuthGuard: CanActivateFn = (route, state) => {
  // send request to admin api
  return true;
};
