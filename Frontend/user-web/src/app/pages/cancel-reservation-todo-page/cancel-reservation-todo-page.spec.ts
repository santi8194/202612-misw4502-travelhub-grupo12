import { Location } from '@angular/common';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { CancelReservationTodoPage } from './cancel-reservation-todo-page';

describe('CancelReservationTodoPage', () => {
  let fixture: ComponentFixture<CancelReservationTodoPage>;
  let locationSpy: jasmine.SpyObj<Location>;
  let router: Router;

  beforeEach(async () => {
    locationSpy = jasmine.createSpyObj<Location>('Location', ['back']);

    await TestBed.configureTestingModule({
      imports: [CancelReservationTodoPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Location, useValue: locationSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CancelReservationTodoPage);
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  it('should render the temporary cancellation TODO page without starting a flow', () => {
    const page = fixture.nativeElement.querySelector('[data-testid="cancel-reservation-todo-page"]');

    expect(page).toBeTruthy();
    expect(page.textContent).toContain('TODO: Flujo de cancelaci');
    expect(page.textContent).toContain('pantalla es temporal');
  });

  it('should provide a back action', () => {
    const navigateSpy = spyOn(router, 'navigate').and.resolveTo(true);
    const backButton = fixture.nativeElement.querySelector('[data-testid="cancel-reservation-back"]') as HTMLButtonElement;

    backButton.click();

    expect(locationSpy.back.calls.count() + navigateSpy.calls.count()).toBe(1);
  });
});
