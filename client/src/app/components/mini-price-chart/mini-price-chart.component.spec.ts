import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MiniPriceChartComponent } from './mini-price-chart.component';

describe('MiniPriceChartComponent', () => {
  let component: MiniPriceChartComponent;
  let fixture: ComponentFixture<MiniPriceChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MiniPriceChartComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MiniPriceChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
