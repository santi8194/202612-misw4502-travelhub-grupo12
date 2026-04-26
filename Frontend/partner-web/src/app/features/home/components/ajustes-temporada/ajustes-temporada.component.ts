import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { catchError, of } from 'rxjs';
import {
    CatalogService,
    CreateTemporadaBody,
    TemporadaApi,
} from '../../../../core/services/catalog.service';

const PALETTE = ['#dbeafe', '#fce7f3', '#fef9c3', '#d1fae5', '#ede9fe', '#ffedd5'];
const TEXT_PALETTE = ['#1d4ed8', '#be185d', '#a16207', '#065f46', '#6d28d9', '#c2410c'];

@Component({
    selector: 'app-ajustes-temporada',
    standalone: true,
    imports: [CommonModule, FormsModule, TranslateModule],
    templateUrl: './ajustes-temporada.component.html',
    styleUrl: './ajustes-temporada.component.scss',
})
export class AjustesTemporadaComponent implements OnChanges {
    @Input() idPropiedad: string | null = null;

    temporadas: TemporadaApi[] = [];
    loading = false;
    loadError = false;
    saveError = false;

    showForm = false;
    saving = false;

    form: CreateTemporadaBody = { nombre: '', fecha_inicio: '', fecha_fin: '', porcentaje: 0 };
    formErrors: Record<string, string> = {};

    constructor(private catalogService: CatalogService) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['idPropiedad'] && this.idPropiedad) {
            this.cargar();
        }
    }

    cargar(): void {
        if (!this.idPropiedad) return;
        this.loading = true;
        this.loadError = false;
        this.catalogService
            .getTemporadas(this.idPropiedad)
            .pipe(catchError(() => { this.loadError = true; this.loading = false; return of(null); }))
            .subscribe(resp => {
                this.loading = false;
                if (resp) this.temporadas = resp.temporadas;
            });
    }

    colorBg(index: number): string {
        return PALETTE[index % PALETTE.length];
    }

    colorText(index: number): string {
        return TEXT_PALETTE[index % TEXT_PALETTE.length];
    }

    /** Format "YYYY-MM-DD" → "Mon D" */
    formatDate(iso: string): string {
        const d = new Date(iso + 'T00:00:00');
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    openForm(): void {
        this.form = { nombre: '', fecha_inicio: '', fecha_fin: '', porcentaje: 0 };
        this.formErrors = {};
        this.saveError = false;
        this.showForm = true;
    }

    cancelForm(): void {
        this.showForm = false;
    }

    private validate(): boolean {
        this.formErrors = {};
        if (!this.form.nombre.trim()) this.formErrors['nombre'] = 'SEASONS.ERROR_NOMBRE';
        if (!this.form.fecha_inicio) this.formErrors['fecha_inicio'] = 'SEASONS.ERROR_FECHA';
        if (!this.form.fecha_fin) this.formErrors['fecha_fin'] = 'SEASONS.ERROR_FECHA';
        if (this.form.fecha_inicio && this.form.fecha_fin && this.form.fecha_fin <= this.form.fecha_inicio) {
            this.formErrors['fecha_fin'] = 'SEASONS.ERROR_FECHA_ORDEN';
        }
        if (!this.form.porcentaje || this.form.porcentaje <= 0) {
            this.formErrors['porcentaje'] = 'SEASONS.ERROR_PORCENTAJE';
        }
        return Object.keys(this.formErrors).length === 0;
    }

    guardar(): void {
        if (!this.validate() || !this.idPropiedad) return;
        this.saving = true;
        this.saveError = false;
        this.catalogService
            .createTemporada(this.idPropiedad, this.form)
            .pipe(catchError(() => { this.saveError = true; this.saving = false; return of(null); }))
            .subscribe(nueva => {
                this.saving = false;
                if (nueva) {
                    this.temporadas = [...this.temporadas, nueva];
                    this.showForm = false;
                }
            });
    }

    eliminar(idTemporada: string): void {
        if (!this.idPropiedad) return;
        this.catalogService
            .deleteTemporada(this.idPropiedad, idTemporada)
            .pipe(catchError(() => of(null)))
            .subscribe(() => {
                this.temporadas = this.temporadas.filter(t => t.id_temporada !== idTemporada);
            });
    }
}
