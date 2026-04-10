import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { SearchResultsPage } from './search-results-page';

describe('SearchResultsPage', () => {
  let component: SearchResultsPage;
  let fixture: ComponentFixture<SearchResultsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchResultsPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SearchResultsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the main content area', () => {
    const main = fixture.nativeElement.querySelector('[data-testid="results-main"]');
    expect(main).toBeTruthy();
  });

  it('should render the results header section', () => {
    const header = fixture.nativeElement.querySelector('[data-testid="results-header"]');
    expect(header).toBeTruthy();
  });

  it('should render the title with "Stays in Bordeaux"', () => {
    const title = fixture.nativeElement.querySelector('[data-testid="results-title"]');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toBe('Stays in Bordeaux');
  });

  it('should render the subtitle mentioning Bordeaux', () => {
    const subtitle = fixture.nativeElement.querySelector('[data-testid="results-subtitle"]');
    expect(subtitle).toBeTruthy();
    expect(subtitle.textContent).toContain('Bordeaux');
  });

  it('should render the divider', () => {
    const divider = fixture.nativeElement.querySelector('[data-testid="results-divider"]');
    expect(divider).toBeTruthy();
  });

  it('should render the results grid', () => {
    const grid = fixture.nativeElement.querySelector('[data-testid="results-grid"]');
    expect(grid).toBeTruthy();
  });

  it('should render exactly 3 hospedaje cards', () => {
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="hospedaje-card"]');
    expect(cards.length).toBe(3);
  });

  it('should render the header component', () => {
    const header = fixture.nativeElement.querySelector('app-header');
    expect(header).toBeTruthy();
  });

  it('should render the footer component', () => {
    const footer = fixture.nativeElement.querySelector('app-footer');
    expect(footer).toBeTruthy();
  });

  it('should have 3 hospedajes in the signal', () => {
    expect(component.hospedajes().length).toBe(3);
  });

  it('should have ciudadBusqueda computed as "Bordeaux"', () => {
    expect(component.ciudadBusqueda()).toBe('Bordeaux');
  });

  it('should have totalResultados computed as 3', () => {
    expect(component.totalResultados()).toBe(3);
  });
});
