import { Component, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { FormBuilder, FormGroup, FormControl, ReactiveFormsModule, Validators, AbstractControl, FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { LogoComponent } from '../../components/logo/logo.component';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';

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
    MessageModule,
    CheckboxModule,
  ],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  credentialForm: FormGroup;
  submitted = false;

  constructor(
    private authService: AuthService,
    private fb: FormBuilder,
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
    if (this.credentialForm.value.email && this.credentialForm.value.password && this.credentialForm.value.confirmPassword) {
      this.authService.register();
      console.log('Form Values:', this.credentialForm.value);
      this.credentialForm.markAsUntouched();
      // this.credentialForm.reset();
    }
  }
}
