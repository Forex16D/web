import { Component } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { FormGroup, FormControl, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { LogoComponent } from '../../components/logo/logo.component';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { FocusTrapModule } from 'primeng/focustrap';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

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
    ToastModule
  ],
  providers: [MessageService],
})

export class LoginComponent {
  credentialForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),  // Fix here
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
          console.error('Login Failed:', error.error.error);
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error.error
          })
        }
      });
    } else {
      console.error('Invalid form submission');
    }
  }
}
