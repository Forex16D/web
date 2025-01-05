import { Component, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { FormBuilder, FormGroup, FormControl, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { LogoComponent } from '../../components/logo/logo.component';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { ApiService } from '../../core/services/api.service';

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
  ],
})

export class LoginComponent {
  credentialForm: FormGroup;
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
    private fb: FormBuilder,
    private apiService: ApiService
  ) {
    
    this.credentialForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: '',
    });
  }

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
      const data = {
        email: this.credentialForm.value.email,
        password: this.credentialForm.value.password,
      };
    
      console.log('Form Values:', data);
    
      this.apiService.postData('v1/login', data).subscribe({
        next: (response) => {
          console.log('Login Successful:', response);

          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
          this.router.navigateByUrl(returnUrl);
        },
        error: (error) => {
          console.error('Login Failed:', error);
        },
      });
    } else {
      console.error('Invalid form submission');
    }
  }
}
