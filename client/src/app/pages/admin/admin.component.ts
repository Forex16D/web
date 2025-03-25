import { Component } from '@angular/core';
import { NgIf } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { AdminUserComponent } from './admin-user/admin-user.component';
import { AdminModelComponent } from './admin-model/admin-model.component';
import { AdminNavbarComponent } from '../../components/admin-navbar/admin-navbar.component';
import { AdminHomeComponent } from './admin-home/admin-home.component';

@Component({
  selector: 'app-admin',
  imports: [
    AdminUserComponent, 
    AdminModelComponent, 
    AdminNavbarComponent,
    AdminHomeComponent,
    NgIf
  ],
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})

export class AdminComponent {
  isVisible = true;
  isMouseOver = false;
  view: string | null = null;

  constructor(private activatedRoute: ActivatedRoute, private router: Router) {}

  ngOnInit() {
    this.activatedRoute.queryParams.subscribe(params => {
      this.view = params['view'] || null;
    });
    const queryParams = this.activatedRoute.snapshot.queryParams;
    
    if (Object.keys(queryParams).length === 0) {
      this.router.navigate(
        [],
        {
          relativeTo: this.activatedRoute,
          queryParams: { view: 'home' },
          queryParamsHandling: 'replace'
        }
      );
    }
  }
}
