import { Location } from '@angular/common';
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HeaderComponent } from '../../shared/components/header/header';

@Component({
  selector: 'app-cancel-reservation-todo-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent],
  templateUrl: './cancel-reservation-todo-page.html',
  styleUrl: './cancel-reservation-todo-page.css',
})
export class CancelReservationTodoPage {
  private readonly location = inject(Location);
  private readonly router = inject(Router);

  protected goBack(): void {
    if (window.history.length > 1) {
      this.location.back();
      return;
    }

    this.router.navigate(['/mis-reservas']);
  }
}
