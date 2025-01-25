import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminModelComponent } from './admin-model.component';

describe('AdminModelComponent', () => {
  let component: AdminModelComponent;
  let fixture: ComponentFixture<AdminModelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminModelComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminModelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
