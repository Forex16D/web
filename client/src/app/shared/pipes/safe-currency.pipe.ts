import { Pipe, PipeTransform } from '@angular/core';
import { CurrencyPipe } from '@angular/common';

@Pipe({
  name: 'safeCurrency',
})
export class SafeCurrencyPipe implements PipeTransform {
  constructor(private currencyPipe: CurrencyPipe) {}

  transform(value: any, currencyCode: string = 'USD', display: string | boolean = 'symbol', digitsInfo?: string): string {
    const numericValue = isNaN(Number(value)) ? 0 : Number(value);
    return this.currencyPipe.transform(numericValue, currencyCode, display, digitsInfo) || '';
  }
}