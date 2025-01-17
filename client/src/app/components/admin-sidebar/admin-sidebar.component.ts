import { Component } from '@angular/core';
import { LogoComponent } from '../../components/logo/logo.component';
import { NgClass } from '@angular/common';
import { DividerModule } from 'primeng/divider';

@Component({
  selector: 'app-admin-sidebar',
  imports: [LogoComponent, NgClass, DividerModule],
  templateUrl: './admin-sidebar.component.html',
  styleUrl: './admin-sidebar.component.css',
})
  export class AdminSidebarComponent {
    isVisible = true;
    isMouseOver = false;
  }
