import { Component } from '@angular/core';
import { LogoComponent } from '../../components/logo/logo.component';
import { NgClass, NgStyle } from '@angular/common';
import { DividerModule } from 'primeng/divider';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-admin-sidebar',
  imports: [LogoComponent, NgClass, DividerModule, NgStyle],
  templateUrl: './admin-sidebar.component.html',
  styleUrl: './admin-sidebar.component.css',
  standalone: true,
})

export class AdminSidebarComponent {
  isVisible = false;
  isMouseOver = false;

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
  ) { }

  updateQueryParams(value: string) {
    this.router.navigate(
      [],
      {
        relativeTo: this.activatedRoute,
        queryParams: { view: value },
        queryParamsHandling: 'merge'
      }
    );
  }
}