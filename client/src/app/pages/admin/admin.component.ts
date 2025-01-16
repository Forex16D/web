import { Component } from '@angular/core';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { DrawerModule } from 'primeng/drawer';
import { DividerModule } from 'primeng/divider';
import { MenuModule } from 'primeng/menu';
import { LogoComponent } from '../../components/logo/logo.component';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-admin',
  imports: [AdminSidebarComponent,
    DrawerModule,
    DividerModule,
    MenuModule,
    LogoComponent,
    NgIf],
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})
export class AdminComponent {
  isVisible = true;
  isMouseOver = false;
}
