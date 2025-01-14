import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'plusMinusNumber',
})
export class PlusMinusNumberPipe implements PipeTransform {
  transform(value: number | null | undefined): string {
    if (value === null || value === undefined || typeof value !== 'number') {
      return '';
    }

    return value >= 0 ? `+${value}` : `${value}`;
  }
}