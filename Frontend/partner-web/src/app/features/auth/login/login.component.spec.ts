import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';
import { LoginComponent } from './login.component';
import { AuthService } from '../../../core/services/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    authService = jasmine.createSpyObj('AuthService', ['login']);
    router = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [LoginComponent, ReactiveFormsModule, TranslateModule.forRoot()],
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router },
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;

    const translateService = TestBed.inject(TranslateService);
    translateService.setTranslation('en', {
      LOGIN: {
        TITLE: 'TravelHub Partner',
        SUBTITLE: 'Partner Portal',
        EMAIL_LABEL: 'Email',
        EMAIL_PLACEHOLDER: 'partner@hotel.com',
        PASSWORD_LABEL: 'Password',
        PASSWORD_PLACEHOLDER: '••••••••',
        REMEMBER_ME: 'Remember me',
        FORGOT_PASSWORD: 'Forgot your password?',
        SUBMIT: 'Sign In',
        LOADING: 'Verifying credentials...',
        ERROR_FALLBACK: 'Could not sign in. Please check your credentials or try again later.'
      }
    });
    translateService.use('en');

    fixture.detectChanges();
  });

  // ─── Initialization ───

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize the form with empty values', () => {
    expect(component.loginForm.value).toEqual({
      email: '',
      password: '',
      rememberMe: false,
    });
  });

  it('should start with isLoading false and no error', () => {
    expect(component.isLoading).toBeFalse();
    expect(component.errorMessage).toBe('');
  });

  // ─── Form validation ───

  it('should mark form as invalid when empty', () => {
    expect(component.loginForm.valid).toBeFalse();
  });

  it('should mark email as invalid with bad format', () => {
    component.loginForm.patchValue({ email: 'not-email', password: '123' });
    expect(component.loginForm.valid).toBeFalse();
    expect(component.loginForm.get('email')!.hasError('email')).toBeTrue();
  });

  it('should mark form as valid with correct values', () => {
    component.loginForm.patchValue({ email: 'a@b.com', password: '123' });
    expect(component.loginForm.valid).toBeTrue();
  });

  it('should mark password as required', () => {
    component.loginForm.patchValue({ email: 'a@b.com', password: '' });
    expect(component.loginForm.get('password')!.hasError('required')).toBeTrue();
  });

  // ─── onSubmit() success ───

  it('should call authService.login and navigate on success', () => {
    authService.login.and.returnValue(of({
      access_token: 'tok',
      refresh_token: 'ref',
      token_type: 'bearer',
    }));

    component.loginForm.patchValue({ email: 'a@b.com', password: '123' });
    component.onSubmit();

    expect(authService.login).toHaveBeenCalledWith({ email: 'a@b.com', password: '123' });
    expect(router.navigate).toHaveBeenCalledWith(['/']);
    expect(component.isLoading).toBeFalse();
    expect(component.errorMessage).toBe('');
  });

  // ─── onSubmit() error ───

  it('should show error detail from backend on login failure', () => {
    authService.login.and.returnValue(
      throwError(() => ({ error: { detail: 'Correo o contraseña incorrectos' } }))
    );

    component.loginForm.patchValue({ email: 'a@b.com', password: 'wrong' });
    component.onSubmit();

    expect(component.isLoading).toBeFalse();
    expect(component.errorMessage).toBe('Correo o contraseña incorrectos');
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('should show fallback error message when no detail', () => {
    authService.login.and.returnValue(throwError(() => ({ error: {} })));

    component.loginForm.patchValue({ email: 'a@b.com', password: 'wrong' });
    component.onSubmit();

    expect(component.errorMessage).toContain('Could not sign in');
  });

  // ─── onSubmit() when form invalid ───

  it('should not call login when form is invalid', () => {
    component.onSubmit();
    expect(authService.login).not.toHaveBeenCalled();
  });

  // ─── Template rendering ───

  it('should disable submit button when form is invalid', () => {
    fixture.detectChanges();
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-login"]') as HTMLButtonElement;
    expect(btn.disabled).toBeTrue();
  });

  it('should enable submit button when form is valid', () => {
    component.loginForm.patchValue({ email: 'a@b.com', password: '123' });
    fixture.detectChanges();
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-login"]') as HTMLButtonElement;
    expect(btn.disabled).toBeFalse();
  });

  it('should display error banner when errorMessage is set', () => {
    component.errorMessage = 'Algo salió mal';
    fixture.detectChanges();
    const banner = fixture.nativeElement.querySelector('[data-testid="login-error"]');
    expect(banner).toBeTruthy();
    expect(banner.textContent).toContain('Algo salió mal');
  });

  it('should not display error banner when errorMessage is empty', () => {
    component.errorMessage = '';
    fixture.detectChanges();
    const banner = fixture.nativeElement.querySelector('[data-testid="login-error"]');
    expect(banner).toBeNull();
  });

  // ─── Destroy ───

  it('ngOnDestroy should complete destroy$ subject', () => {
    spyOn(component['destroy$'], 'next');
    spyOn(component['destroy$'], 'complete');

    component.ngOnDestroy();

    expect(component['destroy$'].next).toHaveBeenCalled();
    expect(component['destroy$'].complete).toHaveBeenCalled();
  });
});
