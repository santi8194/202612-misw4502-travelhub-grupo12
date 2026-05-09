import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';

import { BookingCartFormComponent } from './booking-cart-form';
import { GuestForm } from '../../../../models/guest.interface';

describe('BookingCartFormComponent', () => {
  let component: BookingCartFormComponent;
  let fixture: ComponentFixture<BookingCartFormComponent>;

  const baseForm: GuestForm = {
    name: 'Ana',
    lastName: 'Perez',
    email: 'ana@travelhub.com',
    phone: '+573001112233',
    detailedRequest: '',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BookingCartFormComponent],
      providers: [provideZonelessChangeDetection()],
    }).compileComponents();

    fixture = TestBed.createComponent(BookingCartFormComponent);
    component = fixture.componentInstance;
  });

  it('should keep continue button disabled when phone is incomplete', () => {
    component.form = {
      ...baseForm,
      phone: '+57300111',
    };
    component.disableContinue = false;

    fixture.detectChanges();

    const btn: HTMLButtonElement = fixture.nativeElement.querySelector('[data-testid="continue-payment-btn"]');
    expect(btn.disabled).toBeTrue();
    expect(component.isFormValid()).toBeFalse();
  });

  it('should enable continue button when phone is complete with country code', () => {
    component.form = { ...baseForm };
    component.disableContinue = false;

    fixture.detectChanges();

    const btn: HTMLButtonElement = fixture.nativeElement.querySelector('[data-testid="continue-payment-btn"]');
    expect(btn.disabled).toBeFalse();
    expect(component.isFormValid()).toBeTrue();
  });

  it('should emit continuePayment only with valid form', () => {
    component.form = {
      ...baseForm,
      phone: '+57300111',
    };
    component.disableContinue = false;

    fixture.detectChanges();

    const emitSpy = spyOn(component.continuePayment, 'emit');
    component.onContinuePayment();
    expect(emitSpy).not.toHaveBeenCalled();

    component.form = { ...baseForm };
    fixture.detectChanges();

    component.onContinuePayment();
    expect(emitSpy).toHaveBeenCalledTimes(1);
  });
});
