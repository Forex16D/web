import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';


@Component({
  selector: 'app-price-chart',
  imports: [],
  templateUrl: './price-chart.component.html',
  styleUrl: './price-chart.component.css'
})
export class PriceChartComponent implements AfterViewInit {
  @ViewChild('tradingviewContainer', { static: true }) tradingviewContainer!: ElementRef;

  currentSymbol: string = "OANDA:XAUUSD|1D";

  ngAfterViewInit() {
    this.loadTradingViewWidget(this.currentSymbol);
  }

  changeSymbol(newSymbol: string) {
    this.currentSymbol = newSymbol;
    this.loadTradingViewWidget(this.currentSymbol);
  }

  loadTradingViewWidget(symbol: string) {
    this.tradingviewContainer.nativeElement.innerHTML = '';  // Clear previous widget

    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbols: [[symbol]],
      chartOnly: false,
      width: '100%',
      height: '100%',
      locale: 'en',
      colorTheme: 'dark',
      autosize: true,
      showVolume: false,
      showMA: false,
      hideDateRanges: false,
      hideMarketStatus: false,
      hideSymbolLogo: false,
      scalePosition: 'right',
      scaleMode: 'Normal',
      fontFamily: '-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif',
      fontSize: '10',
      noTimeScale: false,
      valuesTracking: '1',
      changeMode: 'price-and-percent',
      chartType: 'area',
      lineWidth: 2,
      lineType: 0,
      dateRanges: ['1d|1', '1m|30', '3m|60', '12m|1D', '60m|1W', 'all|1M'],
      dateFormat: "dd MMM 'yy"
    });

    this.tradingviewContainer.nativeElement.appendChild(script);
  }
}
