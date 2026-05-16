import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { BookingCartStepperComponent } from './booking-cart-stepper';

describe('BookingCartStepperComponent', () => {
  let fixture: ComponentFixture<BookingCartStepperComponent>;
  let component: BookingCartStepperComponent;

  async function setup(variant: 'cart' | 'confirmed' | 'rejected' = 'cart') {
    await TestBed.configureTestingModule({
      imports: [BookingCartStepperComponent],
      providers: [provideZonelessChangeDetection()],
    }).compileComponents();
    fixture = TestBed.createComponent(BookingCartStepperComponent);
    component = fixture.componentInstance;
    component.variant = variant;
    fixture.detectChanges();
  }

  it('should create the component', async () => {
    await setup();
    expect(component).toBeTruthy();
  });

  describe('variant = "cart"', () => {
    it('isCart() returns true', async () => {
      await setup('cart');
      expect(component.isCart()).toBeTrue();
    });

    it('isConfirmed() returns false', async () => {
      await setup('cart');
      expect(component.isConfirmed()).toBeFalse();
    });

    it('isRejected() returns false', async () => {
      await setup('cart');
      expect(component.isRejected()).toBeFalse();
    });

    it('isResult() returns false', async () => {
      await setup('cart');
      expect(component.isResult()).toBeFalse();
    });
  });

  describe('variant = "confirmed"', () => {
    it('isCart() returns false', async () => {
      await setup('confirmed');
      expect(component.isCart()).toBeFalse();
    });

    it('isConfirmed() returns true', async () => {
      await setup('confirmed');
      expect(component.isConfirmed()).toBeTrue();
    });

    it('isRejected() returns false', async () => {
      await setup('confirmed');
      expect(component.isRejected()).toBeFalse();
    });

    it('isResult() returns true when confirmed', async () => {
      await setup('confirmed');
      expect(component.isResult()).toBeTrue();
    });
  });

  describe('variant = "rejected"', () => {
    it('isCart() returns false', async () => {
      await setup('rejected');
      expect(component.isCart()).toBeFalse();
    });

    it('isConfirmed() returns false', async () => {
      await setup('rejected');
      expect(component.isConfirmed()).toBeFalse();
    });

    it('isRejected() returns true', async () => {
      await setup('rejected');
      expect(component.isRejected()).toBeTrue();
    });

    it('isResult() returns true when rejected', async () => {
      await setup('rejected');
      expect(component.isResult()).toBeTrue();
    });
  });
});
