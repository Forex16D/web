import { Component } from '@angular/core';
import { NgIf } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { AdminUserComponent } from './admin-user/admin-user.component';
import { AdminModelComponent } from './admin-model/admin-model.component';
import { AdminReportComponent } from './admin-report/admin-report.component';
import { AdminNavbarComponent } from '../../components/admin-navbar/admin-navbar.component';

@Component({
  selector: 'app-admin',
  imports: [
    AdminSidebarComponent, 
    AdminUserComponent, 
    AdminModelComponent, 
    AdminReportComponent, 
    AdminNavbarComponent,
    NgIf
  ],
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})

export class AdminComponent {
  isVisible = true;
  isMouseOver = false;
  view: string | null = null;

  constructor(private activatedRoute: ActivatedRoute) {}

  ngOnInit() {
    this.activatedRoute.queryParams.subscribe(params => {
      this.view = params['view'] || null;
    });
  }
}
