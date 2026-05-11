import { Pipe, PipeTransform } from '@angular/core';
import { I18nService } from '../../core/i18n/i18n.service';

@Pipe({
  name: 'translate',
  standalone: true,
  pure: false,
})
export class TranslatePipe implements PipeTransform {
  constructor(private readonly i18n: I18nService) {}

  transform(
    key: string | null | undefined,
    params?: Record<string, string | number | undefined | null>
  ): string {
    if (!key) {
      return '';
    }

    return this.i18n.translate(key, params);
  }
}