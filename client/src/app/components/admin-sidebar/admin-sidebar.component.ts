import { Component, ViewEncapsulation } from '@angular/core';
import { LogoComponent } from '../logo/logo.component';
import { RouterLink } from '@angular/router';
import { DrawerModule } from 'primeng/drawer';
import { DividerModule } from 'primeng/divider';

@Component({
  selector: 'app-admin-sidebar',
  imports: [LogoComponent, RouterLink, DrawerModule, DividerModule],
  templateUrl: './admin-sidebar.component.html',
  styleUrl: './admin-sidebar.component.css',
  encapsulation: ViewEncapsulation.None,
})
export class AdminSidebarComponent {
  visible = false;
}
