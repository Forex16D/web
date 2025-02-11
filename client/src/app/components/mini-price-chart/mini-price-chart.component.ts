import { Component, ElementRef, ViewChild, AfterViewInit, Input } from '@angular/core';

@Component({
  selector: 'app-mini-price-chart',
  imports: [],
  templateUrl: './mini-price-chart.component.html',
  styleUrl: './mini-price-chart.component.css'
})
export class MiniPriceChartComponent implements AfterViewInit {
  @Input() symbol: string = '';

  @ViewChild('tradingviewMiniContainer', { static: true }) tradingviewMiniContainer!: ElementRef;

  ngAfterViewInit() {
    this.loadTradingViewWidget(this.symbol);
  }

  changeSymbol(newSymbol: string) {
    this.symbol = newSymbol;
    this.loadTradingViewWidget(this.symbol);
  }

  loadTradingViewWidget(symbol: string) {
    this.tradingviewMiniContainer.nativeElement.innerHTML = '';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol: symbol,
      width: '100%',
      height: '100%',
      locale: 'en',
      colorTheme: 'dark',
      autosize: true,
    });

    this.tradingviewMiniContainer.nativeElement.appendChild(script);
  }
}

