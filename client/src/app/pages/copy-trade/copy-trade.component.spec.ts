import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CopyTradeComponent } from './copy-trade.component';

describe('CopyTradeComponent', () => {
  let component: CopyTradeComponent;
  let fixture: ComponentFixture<CopyTradeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CopyTradeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CopyTradeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
