import { SafeCurrencyPipe } from './safe-currency.pipe';

describe('SafeCurrencyPipe', () => {
  it('create an instance', () => {
    const pipe = new SafeCurrencyPipe();
    expect(pipe).toBeTruthy();
  });
});
