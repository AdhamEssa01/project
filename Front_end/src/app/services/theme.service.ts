import { DOCUMENT, isPlatformBrowser } from '@angular/common';
import { Injectable, PLATFORM_ID, inject, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly document = inject(DOCUMENT);
  private readonly platformId = inject(PLATFORM_ID);
  private readonly storageKey = 'jobfinder-theme';

  readonly isDarkMode = signal(false);

  constructor() {
    this.initializeTheme();
  }

  toggleTheme(): void {
    this.setDarkMode(!this.isDarkMode());
  }

  setDarkMode(enabled: boolean): void {
    this.isDarkMode.set(enabled);

    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    this.document.documentElement.classList.toggle('app-dark', enabled);
    this.document.body.classList.toggle('app-dark', enabled);

    try {
      localStorage.setItem(this.storageKey, enabled ? 'dark' : 'light');
    } catch {
      // Ignore storage access failures and keep the in-memory state.
    }
  }

  private initializeTheme(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    let savedTheme: string | null = null;

    try {
      savedTheme = localStorage.getItem(this.storageKey);
    } catch {
      savedTheme = null;
    }

    const prefersDark =
      typeof window !== 'undefined' &&
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-color-scheme: dark)').matches;

    this.setDarkMode(savedTheme ? savedTheme === 'dark' : prefersDark);
  }
}
