import { isPlatformBrowser } from '@angular/common';
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

  constructor (private platformService: PlatformService) {
    this.loadTheme();
  }

  loadTheme(): void {
    if (this.platformService.isBrowser()) {
      const storedTheme = localStorage.getItem(this.themeKey) as Theme;
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
    localStorage.setItem(this.themeKey, this.currentTheme);
    this.applyTheme();
  }
}
