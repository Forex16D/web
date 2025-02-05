import { NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { FocusTrapModule } from 'primeng/focustrap';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { PasswordModule } from 'primeng/password';
import { LogoComponent } from '../../components/logo/logo.component';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  standalone: true,
  imports: [
    ReactiveFormsModule,
    NgIf,
    LogoComponent,
    ButtonModule,
    FormsModule,
    PasswordModule,
    InputTextModule,
    MessageModule,
    CheckboxModule,
    RouterLink,
    FocusTrapModule,
  ],
})

export class LoginComponent {
  credentialForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl(''),
    remember: new FormControl(false)
  });

  returnUrl: string = '/';
  submitted = false;

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.returnUrl = params['returnUrl'] || '/';
    });
  }

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private messageService: MessageService,
  ) { }

  get email() {
    return this.credentialForm.get('email') as FormControl;
  }

  get password() {
    return this.credentialForm.get('password') as FormControl;
  }

  login(): void {
    this.submitted = true;
    if (this.credentialForm.invalid) {
      this.credentialForm.markAllAsTouched();
      return;
    }

    if (this.credentialForm.valid) {
      const { email, password } = this.credentialForm.value;

      this.authService.login(email as string, password as string).subscribe({
        next: (response) => {
          console.log('Login Successful:', response);
          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
          this.router.navigateByUrl(returnUrl);
        },
        error: (error) => {
          console.error('Login Failed:', error);
          let error_message = error.message; 
          switch (error.status) {
            case 401:
              error_message = 'Invalid email or password';
              break;
          }

          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: error_message
          });
        }
      });
    } else {
      console.error('Invalid form submission');
    }
  }
}
