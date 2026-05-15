import { Injectable, effect, inject, signal } from '@angular/core';
import { I18nService } from '../i18n/i18n.service';

export type CurrencyCode = 'COP' | 'PEN' | 'USD' | 'MXN' | 'CLP';

export interface CurrencyOption {
  code: CurrencyCode;
  symbol: string;
  label: string;
}

const CURRENCY_STORAGE_KEY = 'th_currency';

/**
 * Approximate exchange rates relative to COP (base currency).
 * 1 COP = X <foreign currency>
 */
const RATES_FROM_COP: Record<CurrencyCode, number> = {
  COP: 1,
  PEN: 1 / 1_100,
  USD: 1 / 4_100,
  MXN: 1 / 241,
  CLP: 1 / 4.5,
};

/** Convert any amount in the given currency back to COP, then to target. */
function convertAmount(
  amount: number,
  fromCurrency: CurrencyCode,
  toCurrency: CurrencyCode,
): number {
  if (fromCurrency === toCurrency) return amount;
  const amountInCop = amount / RATES_FROM_COP[fromCurrency];
  return amountInCop * RATES_FROM_COP[toCurrency];
}

@Injectable({ providedIn: 'root' })
export class CurrencyService {
  private readonly i18n = inject(I18nService);

  readonly supportedCurrencies: CurrencyOption[] = [
    { code: 'COP', symbol: '$', label: 'COP' },
    { code: 'PEN', symbol: 'S/', label: 'PEN' },
    { code: 'USD', symbol: '$', label: 'USD' },
    { code: 'MXN', symbol: '$', label: 'MXN' },
    { code: 'CLP', symbol: '$', label: 'CLP' },
  ];

  readonly activeCurrency = signal<CurrencyCode>(this.resolveInitialCurrency());

  readonly activeCurrencyOption = () =>
    this.supportedCurrencies.find(c => c.code === this.activeCurrency())!;

  constructor() {
    effect(() => {
      const code = this.activeCurrency();
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(CURRENCY_STORAGE_KEY, code);
      }
    });
  }

  setCurrency(code: CurrencyCode): void {
    this.activeCurrency.set(code);
  }

  /**
   * Convert `amount` from `fromCurrency` to the currently active display currency
   * and format it with the correct locale and symbol.
   */
  format(amount: number | string | null | undefined, fromCurrency: string = 'COP'): string {
    if (amount === null || amount === undefined) return '';
    const numeric = Number(amount);
    if (Number.isNaN(numeric)) return '';

    const from = this.normalizeCurrency(fromCurrency);
    const to = this.activeCurrency();
    const converted = convertAmount(numeric, from, to);
    return this.i18n.formatCurrency(converted, to);
  }

  /** Returns the symbol for the currently active currency. */
  get symbol(): string {
    return this.activeCurrencyOption().symbol;
  }

  private normalizeCurrency(code: string): CurrencyCode {
    const upper = code?.toUpperCase() as CurrencyCode;
    return (['COP', 'PEN', 'USD', 'MXN', 'CLP'] as CurrencyCode[]).includes(upper) ? upper : 'COP';
  }

  private resolveInitialCurrency(): CurrencyCode {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(CURRENCY_STORAGE_KEY);
      if (stored === 'COP' || stored === 'PEN' || stored === 'USD' || stored === 'MXN' || stored === 'CLP') {
        return stored;
      }
    }
    return 'COP';
  }
}
