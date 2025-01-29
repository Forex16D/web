import { Component, AfterViewInit } from '@angular/core';


@Component({
  selector: 'app-price-chart',
  imports: [],
  templateUrl: './price-chart.component.html',
  styleUrl: './price-chart.component.css'
})
export class PriceChartComponent implements AfterViewInit {
  symbol = 'USDJPY';
  private widget: any;

  ngAfterViewInit() {
    this.initTradingViewWidget(this.symbol);
  }

  private initTradingViewWidget(symbol: string): void {
    if ((window as any).TradingView) {
      this.widget = new (window as any).TradingView.widget({
        container_id: 'tradingview-container',
        autosize: true,
        symbol: symbol,
        interval: 'D',
        timezone: 'Etc/UTC',
        theme: 'dark',
        style: '1',
        locale: 'en',
        toolbar_bg: '#f1f3f6',
        enable_publishing: false,
        hide_top_toolbar: false,
        save_image: false,
        studies: [],
        details: false,
      });
    } else {
      console.error('TradingView script not loaded!');
    }
  }

  changeSymbol(newSymbol: string): void {
    this.symbol = newSymbol;
    this.initTradingViewWidget(this.symbol);
  }
}
