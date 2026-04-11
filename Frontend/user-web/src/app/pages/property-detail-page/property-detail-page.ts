import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HeaderComponent } from '../../shared/components/header/header';

interface PropertyLocation {
  ciudad?: string;
  pais?: string;
}

interface PropertyCoordinates {
  lat?: number;
  lon?: number;
}

interface PropertyDetailData {
  id_propiedad?: string;
  nombre?: string;
  estrellas?: number;
  ubicacion?: PropertyLocation;
  coordenadas?: PropertyCoordinates;
  porcentaje_impuesto?: string;
  categoria_nombre?: string;
  descripcion?: string;
  amenidades_destacadas?: string[];
  imagen_principal_url?: string;
  precio_base?: string;
  moneda?: string;
  capacidad_pax?: number;
}

interface PropertyApiResponse {
  id_propiedad?: string;
  nombre?: string;
  estrellas?: number;
  ubicacion?: {
    ciudad?: string;
    pais?: string;
    coordenadas?: {
      lat?: number;
      lon?: number;
    };
  };
  porcentaje_impuesto?: string;
  categorias_habitacion?: number;
}

interface CategoryCardData {
  id_categoria: string;
  codigo_mapeo_pms: string;
  categoria_nombre: string;
  precio_base: number;
  moneda: string;
  capacidad_pax: number;
  imagen_principal_url: string;
  amenidades_destacadas: string[];
}

@Component({
  selector: 'app-property-detail-page',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './property-detail-page.html',
  styleUrl: './property-detail-page.css',
})
export class PropertyDetailPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);

  readonly loading = signal(true);
  readonly creatingBooking = signal(false);
  readonly loadingCategories = signal(false);
  readonly error = signal<string | null>(null);
  readonly categoriesError = signal<string | null>(null);
  readonly property = signal<PropertyDetailData | null>(null);
  readonly categories = signal<CategoryCardData[]>([]);
  readonly selectedCategoryId = signal('');
  readonly checkInInput = signal('');
  readonly checkOutInput = signal('');
  readonly guestsInput = signal(1);

  readonly propertyId = computed(() => this.route.snapshot.paramMap.get('property_id') ?? '');
  readonly todayIso = computed(() => new Date().toISOString().split('T')[0]);
  readonly selectedCategory = computed(() =>
    this.categories().find((category) => category.id_categoria === this.selectedCategoryId()) ?? null
  );
  readonly canReserve = computed(() => {
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    const guests = this.guestsInput();
    return !!this.selectedCategoryId() && !!checkIn && !!checkOut && checkOut > checkIn && guests > 0;
  });

  constructor() {
    this.checkInInput.set(this.route.snapshot.queryParamMap.get('fecha_inicio') ?? '');
    this.checkOutInput.set(this.route.snapshot.queryParamMap.get('fecha_fin') ?? '');
    this.guestsInput.set(Number(this.route.snapshot.queryParamMap.get('huespedes') ?? '1') || 1);
    this.loadPropertyDetail();
  }

  private loadPropertyDetail(): void {
    const propertyId = this.propertyId();
    if (!propertyId) {
      this.error.set('No se encontró el identificador de la propiedad.');
      this.loading.set(false);
      console.warn('[PropertyDetailPage] Missing property_id route param');
      return;
    }

    console.info('[PropertyDetailPage] Loading property detail', {
      propertyId,
      checkIn: this.checkInInput(),
      checkOut: this.checkOutInput(),
      guests: this.guestsInput(),
    });

    this.bookingService.getPropertyById(propertyId).pipe(
      catchError((error) => {
        console.error('[PropertyDetailPage] getPropertyById failed', { propertyId, error });
        this.error.set('No fue posible cargar el detalle de la propiedad.');
        return of(null);
      }),
      finalize(() => this.loading.set(false))
    ).subscribe((propertyResponse: PropertyApiResponse | null) => {
      if (!propertyResponse) {
        return;
      }

      console.info('[PropertyDetailPage] Raw property response', propertyResponse);

      const fallbackData: PropertyDetailData = {
        id_propiedad: propertyId,
        categoria_nombre: this.route.snapshot.queryParamMap.get('categoria_nombre') ?? undefined,
        imagen_principal_url: this.route.snapshot.queryParamMap.get('imagen_principal_url') ?? undefined,
        precio_base: this.route.snapshot.queryParamMap.get('precio_base') ?? undefined,
        moneda: this.route.snapshot.queryParamMap.get('moneda') ?? undefined,
      };

      this.property.set(this.normalizePropertyResponse(propertyResponse, fallbackData));

      console.info('[PropertyDetailPage] Property detail loaded', this.property());
      this.loadCategories(propertyId);
    });
  }

  private normalizePropertyResponse(
    response: PropertyApiResponse,
    fallbackData: PropertyDetailData
  ): PropertyDetailData {
    const locationSource = response?.ubicacion as any;
    const city = locationSource?.ciudad ?? (response as any)?.ciudad;
    const country = locationSource?.pais ?? (response as any)?.pais;
    const coordinates = locationSource?.coordenadas ?? (response as any)?.coordenadas;

    return {
      ...fallbackData,
      ...response,
      ubicacion: {
        ciudad: city ?? fallbackData.ubicacion?.ciudad ?? 'N/A',
        pais: country ?? fallbackData.ubicacion?.pais ?? 'N/A',
      },
      coordenadas: {
        lat: coordinates?.lat,
        lon: coordinates?.lon ?? coordinates?.lng,
      },
    };
  }

  private loadCategories(propertyId: string): void {
    this.loadingCategories.set(true);
    this.categoriesError.set(null);
    this.bookingService.getPropertyCategories(propertyId).pipe(
      catchError((error) => {
        console.error('[PropertyDetailPage] getPropertyCategories failed', { propertyId, error });
        this.categoriesError.set('No fue posible cargar las categorias de esta propiedad.');
        return of([]);
      }),
      finalize(() => this.loadingCategories.set(false))
    ).subscribe((response) => {
      const categories = this.normalizeCategoriesResponse(response);
      this.categories.set(categories);
      this.ensureSelectedCategory();

      console.info('[PropertyDetailPage] Categories loaded', {
        totalCategories: categories.length,
        selectedCategoryId: this.selectedCategoryId(),
      });
    });
  }

  private normalizeCategoriesResponse(response: any): CategoryCardData[] {
    const rawCategories = Array.isArray(response)
      ? response
      : response?.categorias ?? response?.categories ?? response?.resultados ?? [];

    if (!Array.isArray(rawCategories)) {
      return [];
    }

    return rawCategories
      .map((item: any) => ({
        id_categoria: String(item?.id_categoria ?? item?.idCategoria ?? ''),
        codigo_mapeo_pms: String(item?.codigo_mapeo_pms ?? item?.codigoMapeoPms ?? 'N/A'),
        categoria_nombre: String(item?.categoria_nombre ?? item?.nombre_comercial ?? item?.nombre ?? 'Categoria'),
        precio_base: this.normalizeCategoryAmount(item),
        moneda: this.normalizeCategoryCurrency(item),
        capacidad_pax: Number(item?.capacidad_pax ?? item?.capacidad ?? 1) || 1,
        imagen_principal_url: String(item?.imagen_principal_url ?? this.property()?.imagen_principal_url ?? ''),
        amenidades_destacadas: Array.isArray(item?.amenidades_destacadas) ? item.amenidades_destacadas : [],
      }))
      .filter((item: CategoryCardData) => item.id_categoria.length > 0);
  }

  private normalizeCategoryAmount(item: any): number {
    const rawPrice = item?.precio_base;

    if (typeof rawPrice === 'object' && rawPrice !== null) {
      const amount = Number(rawPrice?.monto ?? rawPrice?.amount ?? 0);
      return Number.isFinite(amount) ? amount : 0;
    }

    const amount = Number(rawPrice ?? item?.monto_precio_base ?? item?.precio ?? 0);
    return Number.isFinite(amount) ? amount : 0;
  }

  private normalizeCategoryCurrency(item: any): string {
    const rawPrice = item?.precio_base;

    if (typeof rawPrice === 'object' && rawPrice !== null) {
      return String(rawPrice?.moneda ?? rawPrice?.currency ?? item?.moneda ?? item?.moneda_precio_base ?? '$');
    }

    return String(item?.moneda ?? item?.moneda_precio_base ?? '$');
  }

  currencySymbol(moneda: string): string {
    return moneda === 'USD' ? '$' : moneda;
  }

  private ensureSelectedCategory(): void {
    if (this.selectedCategoryId() && this.categories().some((c) => c.id_categoria === this.selectedCategoryId())) {
      return;
    }

    this.selectedCategoryId.set(this.categories()[0]?.id_categoria ?? '');
  }

  selectCategory(categoryId: string): void {
    this.selectedCategoryId.set(categoryId);
    console.info('[PropertyDetailPage] Category selected', { categoryId });
  }

  onCheckInChange(value: string): void {
    this.checkInInput.set(value);
    if (this.checkOutInput() && this.checkOutInput() <= value) {
      this.checkOutInput.set('');
    }
  }

  onCheckOutChange(value: string): void {
    this.checkOutInput.set(value);
  }

  onGuestsChange(value: string): void {
    const parsed = Number(value);
    this.guestsInput.set(Number.isFinite(parsed) && parsed > 0 ? parsed : 1);
  }

  reservar(): void {
    const propertyId = this.propertyId();
    const categoryId = this.selectedCategoryId();
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    const guests = this.guestsInput();

    if (!propertyId || !categoryId || !checkIn || !checkOut || checkOut <= checkIn || guests <= 0) {
      console.error('[PropertyDetailPage] reservar blocked due to missing query params', {
        propertyId,
        categoryId,
        checkIn,
        checkOut,
        guests,
      });
      this.error.set('Faltan datos para crear la reserva. Regresa al listado y selecciona de nuevo.');
      return;
    }

    this.creatingBooking.set(true);
    this.error.set(null);

    const request = {
      id_usuario: this.resolveUserId(),
      id_categoria: categoryId,
      fecha_check_in: checkIn,
      fecha_check_out: checkOut,
      ocupacion: {
        adultos: guests,
        ninos: 0,
        infantes: 0,
      },
    };

    console.info('[PropertyDetailPage] Creating booking', request);

    this.bookingService.createBooking(request).pipe(
      finalize(() => this.creatingBooking.set(false)),
      catchError((error) => {
        console.error('[PropertyDetailPage] createBooking failed', { request, error });
        this.error.set('No fue posible crear la reserva. Intenta nuevamente.');
        return of(null);
      })
    ).subscribe((response) => {
      if (!response?.id_reserva) {
        console.error('[PropertyDetailPage] createBooking response without id_reserva', response);
        this.error.set('La reserva fue creada sin identificador valido.');
        return;
      }

      console.info('[PropertyDetailPage] Booking created, redirecting', response);
      this.router.navigate(['/booking', response.id_reserva]);
    });
  }

  private resolveUserId(): string {
    const key = 'user_id';
    const stored = localStorage.getItem(key);
    if (stored) {
      return stored;
    }

    const generated = crypto.randomUUID();
    localStorage.setItem(key, generated);
    console.warn('[PropertyDetailPage] user_id not found in localStorage. Generated temporary UUID user_id.', generated);
    return generated;
  }
}
