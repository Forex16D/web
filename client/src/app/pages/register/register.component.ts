import { Component, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { FormBuilder, FormGroup, FormControl, ReactiveFormsModule, Validators, AbstractControl, FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { LogoComponent } from '../../components/logo/logo.component';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { FocusTrapModule } from 'primeng/focustrap';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

@Component({
  selector: 'app-register',
  imports: [
    ReactiveFormsModule,
    NgIf,
    LogoComponent,
    ButtonModule,
    FormsModule,
    PasswordModule,
    InputTextModule,
    CheckboxModule,
    FocusTrapModule,
    ToastModule,
    MessageModule,
    RouterLink,
  ],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent {
  credentialForm: FormGroup;
  submitted = false;

  constructor(
    private authService: AuthService,
    private fb: FormBuilder,
    private router: Router,
    private messageService: MessageService,
  ) {

    this.credentialForm = this.fb.group(
      {
        email: ['', [Validators.required, Validators.email]],
        password: ['', [Validators.required, Validators.minLength(6)]],
        confirmPassword: ['', [Validators.required, Validators.minLength(6)]],
      },
      { validator: this.passwordMatchValidator }
    );
  }

  passwordMatchValidator(control: AbstractControl): { [key: string]: boolean } | null {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;

    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  get confirmPasswordError(): string | null {
    const confirmPasswordControl = this.credentialForm.get('confirmPassword');
    if (confirmPasswordControl?.hasError('minlength')) {
      return 'Password must be at least 6 characters long';
    }
    if (this.credentialForm.errors?.['passwordMismatch']) {
      return 'Passwords do not match';
    }
    return null;
  }

  register(): void {
    this.submitted = true;
    if (this.credentialForm.invalid) {
      this.credentialForm.markAllAsTouched();
      return;
    }
    if (this.credentialForm.valid) {
      const { email, password, confirmPassword } = this.credentialForm.value;

      this.authService.register(email as string, password as string, confirmPassword as string).subscribe({
        next: (_) => {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Register Successful'
          });
          this.router.navigateByUrl('/login');
        },
        error: (error) => {
          console.error('Register Failed:', error)
          let error_message = error.message; 
          switch (error.status) {
            case 409:
              error_message = 'Email Already Exists';
              break;
          }

          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: error_message
          });
        }
      });
      this.credentialForm.markAsUntouched();
    }
  }
}
