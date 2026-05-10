import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Router } from '@angular/router';
import { of } from 'rxjs';

import { HeaderComponent } from './header';
import { AuthService } from '../../../core/services/auth';
import { NotificationService } from '../../../core/services/notification';
import { BookingService } from '../../../core/services/booking';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;
  let router: Router;
  let authService: AuthService;
  let notificationService: NotificationService;
  let bookingService: BookingService;

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
    authService = TestBed.inject(AuthService);
    notificationService = TestBed.inject(NotificationService);
    bookingService = TestBed.inject(BookingService);
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

  it('should load and display the full name from user profile when profile menu is opened', (done) => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'a.perez');

    const mockUserProfile = {
      id_usuario: 'user-123',
      full_name: 'Ana Perez',
      email: 'ana@travelhub.com',
    };

    spyOn(authService, 'getUserProfile').and.returnValue(of(mockUserProfile));

    fixture.detectChanges();
    component.toggleProfileMenu();
    fixture.detectChanges();

    fixture.whenStable().then(() => {
      fixture.detectChanges();
      
      const dropdown = fixture.nativeElement.querySelector('.profile-dropdown');
      expect(dropdown.textContent).toContain('Ana Perez');
      expect(dropdown.textContent).toContain('Mis Reservas');
      expect(dropdown.textContent).toContain('Cerrar sesión');
      expect(authService.getUserProfile).toHaveBeenCalledWith('user-123');
      done();
    });
  });

  it('should display fallback username when user profile endpoint fails', () => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'a.perez');

    spyOn(authService, 'getUserProfile').and.returnValue(of({}));

    fixture.detectChanges();
    component.toggleProfileMenu();
    fixture.detectChanges();

    const displayName = component.getProfileDisplayName();
    expect(displayName).toBe('a.perez');
  });

  it('should navigate to mis reservas when authenticated user clicks the menu action', async () => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'a.perez');

    const mockUserProfile = {
      id_usuario: 'user-123',
      full_name: 'Ana Perez'
    };

    spyOn(authService, 'getUserProfile').and.returnValue(of(mockUserProfile));
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

  it('should show success notification when user logs out', () => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'a.perez');

    // Set booking session in sessionStorage
    sessionStorage.setItem('booking-session:test-signature', JSON.stringify({
      expiresAt: Date.now() + 900000
    }));
    sessionStorage.setItem('hold:reservation-123', JSON.stringify({
      holdId: 'optimistic-hold'
    }));

    const notificationSpy = spyOn(notificationService, 'showSuccess');
    const navigateSpy = spyOn(router, 'navigate').and.returnValue(Promise.resolve(true));
    const mockUserProfile = {
      id_usuario: 'user-123',
      username: 'a.perez'
    };

    spyOn(authService, 'getUserProfile').and.returnValue(of(mockUserProfile));

    fixture.detectChanges();
    component.toggleProfileMenu();
    fixture.detectChanges();

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('.dropdown-item--button')) as HTMLButtonElement[];
    const logoutButton = buttons.find(button => button.textContent?.includes('Cerrar sesión'));

    expect(logoutButton).toBeTruthy();

    logoutButton?.click();
    fixture.detectChanges();

    expect(notificationSpy).toHaveBeenCalledWith('Tu sesión ha sido cerrada exitosamente.');
    expect(navigateSpy).toHaveBeenCalledWith(['/']);
    expect(component.userProfile()).toBeNull();
    
    // Verify session storage was cleared
    expect(sessionStorage.getItem('booking-session:test-signature')).toBeNull();
    expect(sessionStorage.getItem('hold:reservation-123')).toBeNull();
  });

  it('should cancel active reservation before redirecting to home on logout', () => {
    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'ana@travelhub.com');
    localStorage.setItem('th_user_id', 'user-123');
    localStorage.setItem('th_user_name', 'a.perez');

    const cancelSpy = spyOn(bookingService, 'cancelBookingById').and.returnValue(of({}));
    const navigateSpy = spyOn(router, 'navigate').and.returnValue(Promise.resolve(true));
    spyOnProperty(router, 'url', 'get').and.returnValue('/booking/reserva-123');

    component.logout();

    expect(cancelSpy).toHaveBeenCalledWith('reserva-123');
    expect(navigateSpy).toHaveBeenCalledWith(['/']);
  });
});
