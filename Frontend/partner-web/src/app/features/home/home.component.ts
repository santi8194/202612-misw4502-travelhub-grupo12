import { Component, OnInit } from '@angular/core';
import { NavbarComponent } from '../../shared/components/navbar/navbar.component';
import { CommonModule } from '@angular/common';
import { AuthService, UserProfile } from '../../core/services/auth.service';

@Component({
    selector: 'app-home',
    imports: [NavbarComponent, CommonModule],
    templateUrl: './home.component.html',
    styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
    user: UserProfile | null = null;
    loading = true;
    error = false;

    constructor(private authService: AuthService) {}

    ngOnInit(): void {
        this.authService.getCurrentUser().subscribe({
            next: (profile) => {
                this.user = profile;
                this.loading = false;
            },
            error: () => {
                this.error = true;
                this.loading = false;
            }
        });
    }
}
