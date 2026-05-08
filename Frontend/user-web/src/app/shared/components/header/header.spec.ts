import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Router } from '@angular/router';

import { HeaderComponent } from './header';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;
  let router: Router;

  beforeEach(async () => {
    localStorage.clear();

    await TestBed.configureTestingModule({
      imports: [HeaderComponent],
      providers: [provideZonelessChangeDetection(), provideHttpClient(), provideRouter([])],
    })
    .compileComponents();

    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show login and register options when there is no active session', () => {
    component.toggleProfileMenu();
    fixture.detectChanges();

    const dropdown = fixture.nativeElement.querySelector('.profile-dropdown');
    expect(dropdown).toBeTruthy();
    expect(dropdown.textContent).toContain('Registrarse');
    expect(dropdown.textContent).toContain('Iniciar Sesión');
  });

  it('should show the authenticated user information when a session exists', () => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'Ana Perez');

    fixture.detectChanges();
    component.toggleProfileMenu();
    fixture.detectChanges();

    const dropdown = fixture.nativeElement.querySelector('.profile-dropdown');
    expect(dropdown.textContent).toContain('Ana Perez');
    expect(dropdown.textContent).toContain('ana@travelhub.com');
    expect(dropdown.textContent).toContain('Mis Reservas');
    expect(dropdown.textContent).toContain('Cerrar sesión');
  });

  it('should navigate to mis reservas when authenticated user clicks the menu action', async () => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'Ana Perez');

    const navigateSpy = spyOn(router, 'navigate').and.returnValue(Promise.resolve(true));

    component.toggleProfileMenu();
    fixture.detectChanges();

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('.dropdown-item--button')) as HTMLButtonElement[];
    const myReservationsButton = buttons.find(button => button.textContent?.includes('Mis Reservas'));

    expect(myReservationsButton).toBeTruthy();

    myReservationsButton?.click();
    fixture.detectChanges();

    expect(navigateSpy).toHaveBeenCalledWith(['/mis-reservas']);
  });
});
