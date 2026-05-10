import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { ActivatedRoute, Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { CompactSearchBarComponent } from './compact-search-bar';
import { SearchStateService } from '../../../core/services/search-state';

describe('CompactSearchBarComponent', () => {
  let fixture: ComponentFixture<CompactSearchBarComponent>;
  let component: CompactSearchBarComponent;
  let router: Router;
  let searchState: SearchStateService;

  async function setup(params: Record<string, string> = {}): Promise<void> {
    TestBed.resetTestingModule();

    await TestBed.configureTestingModule({
      imports: [CompactSearchBarComponent],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            queryParams: of(params),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CompactSearchBarComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    searchState = TestBed.inject(SearchStateService);
    fixture.detectChanges();
  }

  it('should not render when city is missing', async () => {
    await setup();

    expect(component.cityLabel()).toBe('');
    expect(component.datesLabel()).toBe('');
    expect(component.guestsLabel()).toContain('1');
    expect(fixture.nativeElement.querySelector('[data-testid="compact-search-bar"]')).toBeNull();
  });

  it('should render city, same-month dates and plural guests', async () => {
    await setup({
      ciudad: 'Bogota',
      estado_provincia: 'Cundinamarca',
      pais: 'Colombia',
      fecha_inicio: '2026-03-07',
      fecha_fin: '2026-03-10',
      huespedes: '3',
    });

    expect(fixture.nativeElement.querySelector('[data-testid="compact-city"]').textContent).toContain('Bogota');
    expect(fixture.nativeElement.querySelector('[data-testid="compact-dates"]').textContent).toContain('mar');
    expect(fixture.nativeElement.querySelector('[data-testid="compact-dates"]').textContent).toContain('10');
    expect(fixture.nativeElement.querySelector('[data-testid="compact-guests"]').textContent).toContain('3');
    expect(component.guestsLabel()).toContain('es');
  });

  it('should format dates across different months', async () => {
    await setup({
      ciudad: 'Bogota',
      fecha_inicio: '2026-03-30',
      fecha_fin: '2026-04-02',
      huespedes: '1',
    });

    expect(component.datesLabel()).toContain('mar');
    expect(component.datesLabel()).toContain('abr');
    expect(component.guestsLabel()).not.toContain('es');
  });

  it('should navigate to home and store current search when edited', async () => {
    await setup({
      ciudad: 'Bogota',
      estado_provincia: 'Cundinamarca',
      pais: 'Colombia',
      fecha_inicio: '2026-03-07',
      fecha_fin: '2026-03-10',
      huespedes: '2',
    });
    spyOn(router, 'navigate').and.resolveTo(true);

    component.onEditSearch();

    expect(searchState.currentSearch()).toEqual({
      location: 'Bogota, Cundinamarca, Colombia',
      checkIn: '2026-03-07',
      checkOut: '2026-03-10',
      guests: 2,
      selectedDestination: {
        ciudad: 'Bogota',
        estado_provincia: 'Cundinamarca',
        pais: 'Colombia',
      },
    });
    expect(router.navigate).toHaveBeenCalledWith(['/']);
  });

  it('should ignore edit action when city is empty', async () => {
    await setup({
      fecha_inicio: '2026-03-07',
      fecha_fin: '2026-03-10',
      huespedes: 'not-a-number',
    });
    spyOn(router, 'navigate').and.resolveTo(true);
    spyOn(searchState, 'set');

    component.onEditSearch();

    expect(searchState.set).not.toHaveBeenCalled();
    expect(router.navigate).not.toHaveBeenCalled();
  });
});
