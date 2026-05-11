import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { I18nService } from './i18n.service';

describe('I18nService', () => {
  let service: I18nService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideZonelessChangeDetection()],
    });
    service = TestBed.inject(I18nService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  // ── Language management ──────────────────────────────────────────────────

  it('should default to es when localStorage is empty', () => {
    expect(service.language()).toBe('es');
  });

  it('should restore "en" from localStorage', () => {
    localStorage.setItem('th_language', 'en');
    // Re-create inside an injection context to pick up the stored value
    const fresh = TestBed.runInInjectionContext(() => new I18nService());
    expect(fresh.language()).toBe('en');
  });

  it('should default to es when localStorage has an unsupported value', () => {
    localStorage.setItem('th_language', 'fr');
    const fresh = TestBed.runInInjectionContext(() => new I18nService());
    expect(fresh.language()).toBe('es');
  });

  it('setLanguage() should switch to "en"', () => {
    service.setLanguage('en');
    expect(service.language()).toBe('en');
  });

  it('setLanguage() should switch back to "es"', () => {
    service.setLanguage('en');
    service.setLanguage('es');
    expect(service.language()).toBe('es');
  });

  it('supportedLanguages returns both language options', () => {
    const langs = service.supportedLanguages;
    expect(langs.map(l => l.code)).toEqual(['es', 'en']);
  });

  it('activeLanguageLabel returns the label of the current language', () => {
    service.setLanguage('es');
    expect(service.activeLanguageLabel).toBe('Español');
    service.setLanguage('en');
    expect(service.activeLanguageLabel).toBe('English');
  });

  // ── translate ────────────────────────────────────────────────────────────

  it('translate() returns es translation when language is es', () => {
    service.setLanguage('es');
    expect(service.translate('hero.title')).toBe('¿A dónde quieres ir hoy?');
  });

  it('translate() returns en translation when language is en', () => {
    service.setLanguage('en');
    expect(service.translate('hero.title')).toBe('Where do you want to go today?');
  });

  it('translate() returns the key when translation is missing', () => {
    expect(service.translate('non.existent.key')).toBe('non.existent.key');
  });

  it('translate() interpolates params', () => {
    const result = service.translate('search.results.title', { city: 'Medellín' });
    expect(result).toContain('Medellín');
  });

  it('translate() replaces null param token with empty string', () => {
    const result = service.translate('search.results.title', { city: null });
    expect(result).toBe('Estancias en ');
  });

  it('translate() replaces undefined param token with empty string', () => {
    const result = service.translate('search.results.title', { city: undefined });
    expect(result).toBe('Estancias en ');
  });

  it('translate() returns template unchanged when no params passed', () => {
    const result = service.translate('common.loading');
    expect(result).toBe('Cargando...');
  });

  // ── formatDate ───────────────────────────────────────────────────────────

  it('formatDate() returns empty string for empty input', () => {
    expect(service.formatDate('')).toBe('');
  });

  it('formatDate() returns original value for invalid date string', () => {
    expect(service.formatDate('not-a-date')).toBe('not-a-date');
  });

  it('formatDate() formats a valid ISO date in es locale', () => {
    service.setLanguage('es');
    const result = service.formatDate('2026-05-01');
    expect(result).toBeTruthy();
    expect(result).not.toBe('');
  });

  it('formatDate() formats a valid ISO date in en locale', () => {
    service.setLanguage('en');
    const result = service.formatDate('2026-05-01');
    expect(result).toBeTruthy();
    expect(result).not.toBe('');
  });

  it('formatMonthYear() returns month and year string', () => {
    service.setLanguage('es');
    const result = service.formatMonthYear('2026-05-01');
    expect(result).toBeTruthy();
  });

  // ── formatCurrency ───────────────────────────────────────────────────────

  it('formatCurrency() returns empty string for null', () => {
    expect(service.formatCurrency(null)).toBe('');
  });

  it('formatCurrency() returns empty string for undefined', () => {
    expect(service.formatCurrency(undefined)).toBe('');
  });

  it('formatCurrency() returns empty string for NaN', () => {
    expect(service.formatCurrency(NaN)).toBe('');
  });

  it('formatCurrency() formats a number in es locale', () => {
    service.setLanguage('es');
    const result = service.formatCurrency(1500, 'COP');
    expect(result).toBeTruthy();
    expect(result).toContain('1');
  });

  it('formatCurrency() formats a number in en locale', () => {
    service.setLanguage('en');
    const result = service.formatCurrency(1500, 'USD');
    expect(result).toBeTruthy();
    expect(result).toContain('1');
  });

  // ── formatNumber ─────────────────────────────────────────────────────────

  it('formatNumber() returns empty string for null', () => {
    expect(service.formatNumber(null)).toBe('');
  });

  it('formatNumber() returns empty string for undefined', () => {
    expect(service.formatNumber(undefined)).toBe('');
  });

  it('formatNumber() returns empty string for NaN', () => {
    expect(service.formatNumber(NaN)).toBe('');
  });

  it('formatNumber() formats a number in es locale', () => {
    service.setLanguage('es');
    const result = service.formatNumber(1234567);
    expect(result).toBeTruthy();
  });

  it('formatNumber() formats a number in en locale', () => {
    service.setLanguage('en');
    const result = service.formatNumber(1234567);
    expect(result).toBeTruthy();
  });
});
