import { provideZonelessChangeDetection } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { convertToParamMap, ActivatedRoute, provideRouter } from '@angular/router';
import { ConfirmReservationPage } from './confirm-reservation-page';

describe('ConfirmReservationPage', () => {
  let fixture: ComponentFixture<ConfirmReservationPage>;
  let component: ConfirmReservationPage;

  function configureRoute(status: 'confirmed' | 'rejected', reason: string): void {
    TestBed.overrideProvider(ActivatedRoute, {
      useValue: {
        snapshot: {
          paramMap: convertToParamMap({ id_reserva: 'reserva-test-123' }),
          queryParamMap: convertToParamMap({ status, reason }),
        },
      },
    });
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfirmReservationPage],
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: convertToParamMap({ id_reserva: 'reserva-test-123' }),
              queryParamMap: convertToParamMap({ status: 'confirmed', reason: 'Reserva formalizada correctamente' }),
            },
          },
        },
      ],
    }).compileComponents();
  });

  it('should create', () => {
    fixture = TestBed.createComponent(ConfirmReservationPage);
    component = fixture.componentInstance;
    fixture.detectChanges();

    expect(component).toBeTruthy();
  });

  it('should render confirmed reservation state', () => {
    configureRoute('confirmed', 'Reserva formalizada correctamente');

    fixture = TestBed.createComponent(ConfirmReservationPage);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-title"]');
    const reason = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-reason"]');

    expect(title.textContent).toContain('Reserva Confirmada');
    expect(reason.textContent).toContain('Tu reserva ha sido confirmada. Se ha enviado un correo con los detalles.');
    expect(component.isConfirmed()).toBeTrue();
  });

  it('should render rejected reservation state', () => {
    configureRoute('rejected', 'La reserva debe estar en estado HOLD para ser formalizada');

    fixture = TestBed.createComponent(ConfirmReservationPage);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-title"]');
    const reason = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-reason"]');

    expect(title.textContent).toContain('Reserva no confirmada');
    expect(reason.textContent).toContain('La reserva debe estar en estado HOLD para ser formalizada');
    expect(component.isConfirmed()).toBeFalse();
  });
});