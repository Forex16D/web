import { Injectable } from '@angular/core';
import { PlatformService } from './platform.service';

enum Theme {
  Light = 'light',
  Dark = 'dark',
}

@Injectable({
  providedIn: 'root'
})

export class ThemeService {
  private readonly themeKey = 'app-theme';
  private currentTheme: Theme = Theme.Light;

  constructor(private platformService: PlatformService) {
    this.loadTheme();
  }

  private getCookie(name: string): string | null {
    const matches = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return matches ? decodeURIComponent(matches[1]) : null;
  }

  private setCookie(name: string, value: string, days: number): void {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/`;
  }

  loadTheme(): void {
    if (this.platformService.isBrowser()) {
      const storedTheme = this.getCookie(this.themeKey) as Theme;
      this.currentTheme = storedTheme || Theme.Light;
      this.applyTheme();
    }
  }

  getTheme(): string {
    return this.currentTheme;
  }

  applyTheme(): void {
    document.querySelector('html')?.classList.toggle(Theme.Light, this.currentTheme === Theme.Light);
    document.querySelector('html')?.classList.toggle(Theme.Dark, this.currentTheme === Theme.Dark);
  }

  public toggleTheme(): void {
    this.currentTheme = this.currentTheme === Theme.Light ? Theme.Dark : Theme.Light;
    this.setCookie(this.themeKey, this.currentTheme, 365); // Store in cookie for 1 year
    this.applyTheme();
  }
}
