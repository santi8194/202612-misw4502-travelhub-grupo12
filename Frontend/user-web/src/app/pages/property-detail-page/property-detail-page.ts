import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { SearchService } from '../../core/services/search';
import { Hospedaje } from '../../models/hospedaje.interface';
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

interface CategoryCardData {
  id_categoria: string;
  categoria_nombre: string;
  precio_base: string;
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
  private readonly searchService = inject(SearchService);

  readonly loading = signal(true);
  readonly creatingBooking = signal(false);
  readonly loadingCategories = signal(false);
  readonly error = signal<string | null>(null);
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
    ).subscribe((propertyResponse) => {
      if (!propertyResponse) {
        this.categories.set(this.buildFallbackCategories());
        this.ensureSelectedCategory();
        return;
      }

      const fallbackData: PropertyDetailData = {
        id_propiedad: propertyId,
        categoria_nombre: this.route.snapshot.queryParamMap.get('categoria_nombre') ?? undefined,
        imagen_principal_url: this.route.snapshot.queryParamMap.get('imagen_principal_url') ?? undefined,
        precio_base: this.route.snapshot.queryParamMap.get('precio_base') ?? undefined,
        moneda: this.route.snapshot.queryParamMap.get('moneda') ?? undefined,
      };

      this.property.set({
        ...fallbackData,
        ...propertyResponse,
      });

      console.info('[PropertyDetailPage] Property detail loaded', this.property());
      this.loadCategories(propertyId);
    });
  }

  private loadCategories(propertyId: string): void {
    const ciudad = this.route.snapshot.queryParamMap.get('ciudad') ?? this.property()?.ubicacion?.ciudad ?? '';
    const estadoProvincia = this.route.snapshot.queryParamMap.get('estado_provincia') ?? '';
    const pais = this.route.snapshot.queryParamMap.get('pais') ?? this.property()?.ubicacion?.pais ?? '';
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    const huespedes = this.guestsInput();

    if (!ciudad || !pais || !checkIn || !checkOut || huespedes <= 0) {
      console.warn('[PropertyDetailPage] Missing data to load categories from search endpoint, using fallback query category');
      this.categories.set(this.buildFallbackCategories());
      this.ensureSelectedCategory();
      return;
    }

    this.loadingCategories.set(true);
    this.searchService.searchHospedajes({
      ciudad,
      estado_provincia: estadoProvincia,
      pais,
      fecha_inicio: checkIn,
      fecha_fin: checkOut,
      huespedes,
    }).pipe(
      catchError((error) => {
        console.error('[PropertyDetailPage] searchHospedajes failed while loading categories', { propertyId, error });
        return of({ resultados: [] as Hospedaje[], total: 0 });
      }),
      finalize(() => this.loadingCategories.set(false))
    ).subscribe((response) => {
      const matchedCategories = response.resultados
        .filter((item) => item.id_propiedad === propertyId)
        .map((item) => ({
          id_categoria: item.id_categoria,
          categoria_nombre: item.categoria_nombre,
          precio_base: item.precio_base,
          moneda: item.moneda,
          capacidad_pax: item.capacidad_pax,
          imagen_principal_url: item.imagen_principal_url,
          amenidades_destacadas: item.amenidades_destacadas,
        }));

      const categories = matchedCategories.length > 0 ? matchedCategories : this.buildFallbackCategories();
      this.categories.set(categories);
      this.ensureSelectedCategory();

      console.info('[PropertyDetailPage] Categories loaded', {
        totalCategories: categories.length,
        selectedCategoryId: this.selectedCategoryId(),
      });
    });
  }

  private buildFallbackCategories(): CategoryCardData[] {
    const fallbackCategoryId = this.route.snapshot.queryParamMap.get('id_categoria') ?? '';
    if (!fallbackCategoryId) {
      return [];
    }

    return [
      {
        id_categoria: fallbackCategoryId,
        categoria_nombre: this.route.snapshot.queryParamMap.get('categoria_nombre') ?? 'Categoria',
        precio_base: this.route.snapshot.queryParamMap.get('precio_base') ?? '0',
        moneda: this.route.snapshot.queryParamMap.get('moneda') ?? '$',
        capacidad_pax: Number(this.route.snapshot.queryParamMap.get('huespedes') ?? '1') || 1,
        imagen_principal_url: this.route.snapshot.queryParamMap.get('imagen_principal_url') ?? '',
        amenidades_destacadas: [],
      },
    ];
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
