import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { HospedajeCardComponent } from './hospedaje-card';
import { Hospedaje } from '../../../models/hospedaje.interface';

const mockHospedaje: Hospedaje = {
  id_propiedad: '550e8400-e29b-41d4-a716-446655440000',
  id_categoria: '550e8400-e29b-41d4-a716-446655440001',
  propiedad_nombre: 'Hotel',
  categoria_nombre: 'Bordeaux Getaway',
  imagen_principal_url: 'https://via.placeholder.com/600x400',
  amenidades_destacadas: ['Wifi', 'Cocina', 'Cuarto de ropa', 'Piscina', 'Parking'],
  estrellas: 5,
  rating_promedio: 5.0,
  ciudad: 'Bordeaux',
  estado_provincia: 'Nouvelle-Aquitaine',
  pais: 'Francia',
  coordenadas: { lat: 44.8378, lon: -0.5792 },
  capacidad_pax: 4,
  precio_base: '75.00',
  moneda: 'USD',
  es_reembolsable: true,
};

describe('HospedajeCardComponent', () => {
  let component: HospedajeCardComponent;
  let fixture: ComponentFixture<HospedajeCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HospedajeCardComponent],
      providers: [provideZonelessChangeDetection()],
    }).compileComponents();

    fixture = TestBed.createComponent(HospedajeCardComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('hospedaje', mockHospedaje);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the card container', () => {
    const card = fixture.nativeElement.querySelector('[data-testid="hospedaje-card"]');
    expect(card).toBeTruthy();
  });

  it('should display the title as categoria_nombre', () => {
    const title = fixture.nativeElement.querySelector('[data-testid="card-title"]');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toBe('Bordeaux Getaway');
  });

  it('should display the badge as propiedad_nombre', () => {
    const badge = fixture.nativeElement.querySelector('[data-testid="card-badge"]');
    expect(badge).toBeTruthy();
    expect(badge.textContent.trim()).toBe('Hotel');
  });

  it('should display the location with ciudad and pais', () => {
    const location = fixture.nativeElement.querySelector('[data-testid="card-location"]');
    expect(location).toBeTruthy();
    expect(location.textContent).toContain('Bordeaux');
    expect(location.textContent).toContain('Francia');
  });

  it('should display the rating', () => {
    const rating = fixture.nativeElement.querySelector('[data-testid="card-rating"]');
    expect(rating).toBeTruthy();
    expect(rating.textContent).toContain('5');
  });

  it('should render only the first 3 amenities as pills', () => {
    const pills = fixture.nativeElement.querySelectorAll('[data-testid="card-amenidad"]');
    expect(pills.length).toBe(3);
    expect(pills[0].textContent.trim()).toBe('Wifi');
    expect(pills[1].textContent.trim()).toBe('Cocina');
    expect(pills[2].textContent.trim()).toBe('Cuarto de ropa');
  });

  it('should show "+N más" label when there are more than 3 amenities', () => {
    const extra = fixture.nativeElement.querySelector('[data-testid="card-amenidades-extra"]');
    expect(extra).toBeTruthy();
    expect(extra.textContent).toContain('+2 más');
  });

  it('should display the price', () => {
    const price = fixture.nativeElement.querySelector('[data-testid="card-price-value"]');
    expect(price).toBeTruthy();
    expect(price.textContent).toContain('75.00');
  });

  it('should display the hero image', () => {
    const img = fixture.nativeElement.querySelector('[data-testid="card-image"]');
    expect(img).toBeTruthy();
    expect(img.getAttribute('src')).toContain('placeholder');
  });

  it('should not show "+N más" when amenities are 3 or fewer', async () => {
    const pocoAmenidades: Hospedaje = {
      ...mockHospedaje,
      amenidades_destacadas: ['Wifi', 'Cocina'],
    };
    fixture.componentRef.setInput('hospedaje', pocoAmenidades);
    fixture.detectChanges();

    const extra = fixture.nativeElement.querySelector('[data-testid="card-amenidades-extra"]');
    expect(extra).toBeNull();
  });

  it('should handle zero amenities gracefully', () => {
    const sinAmenidades: Hospedaje = {
      ...mockHospedaje,
      amenidades_destacadas: [],
    };
    fixture.componentRef.setInput('hospedaje', sinAmenidades);
    fixture.detectChanges();

    const pills = fixture.nativeElement.querySelectorAll('[data-testid="card-amenidad"]');
    expect(pills.length).toBe(0);
    const extra = fixture.nativeElement.querySelector('[data-testid="card-amenidades-extra"]');
    expect(extra).toBeNull();
  });

  it('should display EUR currency symbol if moneda is EUR', () => {
    const euroHospedaje: Hospedaje = {
      ...mockHospedaje,
      moneda: 'EUR',
    };
    fixture.componentRef.setInput('hospedaje', euroHospedaje);
    fixture.detectChanges();

    const price = fixture.nativeElement.querySelector('[data-testid="card-price-value"]');
    expect(price.textContent).toContain('EUR');
  });
});
