import { Component, OnInit } from '@angular/core';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { NgIf } from '@angular/common';
import { AdminUserComponent } from './admin-user/admin-user.component';
import { ActivatedRoute } from '@angular/router';
import { AdminModelComponent } from './admin-model/admin-model.component';

@Component({
  selector: 'app-admin',
  imports: [AdminSidebarComponent, AdminUserComponent, AdminModelComponent, NgIf],
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
