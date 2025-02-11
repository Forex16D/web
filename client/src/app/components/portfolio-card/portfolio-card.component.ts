import { Component, Input, Output, EventEmitter } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CurrencyPipe, NgIf } from '@angular/common';
import { NgClass } from '@angular/common';
import { TagModule } from 'primeng/tag';
import { MenuModule } from 'primeng/menu';
import { RippleModule } from 'primeng/ripple';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { RouterLink } from '@angular/router';
import { Router, ActivatedRoute } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { FormsModule, ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { MessageModule } from 'primeng/message';
import { MessageService } from 'primeng/api';
import { ConfirmationService } from 'primeng/api';
import { MenuItem, MenuItemCommandEvent } from 'primeng/api';

@Component({
  selector: 'app-portfolio-card',
  imports: [
    ButtonModule,
    NgClass,
    TagModule,
    MenuModule,
    RippleModule,
    DialogModule,
    InputTextModule,
    RouterLink,
    ReactiveFormsModule,
    MessageModule,
    NgIf,
    FormsModule,
  ],
  templateUrl: './portfolio-card.component.html',
  styleUrl: './portfolio-card.component.css',
  providers: [CurrencyPipe]
})
export class PortfolioCardComponent {
  @Input() credential = {
    portfolio_id: '0',
    name: 'Portfolio',
    login: 'login',
  }

  @Input() data = {
    pnl: '',
    winrate: '',
    roi: '',
    balance: '',
  };

  @Output() portfolioDeleted = new EventEmitter<string>();

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  roiFormatted: string = '-';
  balanceFormatted: string = '-';
  pnlTextColor: string = 'text-white';

  isEditVisible = false;

  portfolioEditForm = new FormGroup({
    name: new FormControl('', [Validators.required, Validators.minLength(1), Validators.maxLength(20)]),
    login: new FormControl('', [Validators.required, Validators.pattern('[0-9]*')]),
  });

  menuItems: MenuItem[] = [
    { label: 'Detail', icon: 'pi pi-info-circle', command: () => this.detailItem() },
    { label: 'Edit', icon: 'pi pi-cog', command: () => this.showEditDialog() },
    { label: 'Delete', icon: 'pi pi-trash', command: (event) => this.deleteItem(event) },
  ];

  constructor(
    private currency: CurrencyPipe,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService,
  ) { }

  ngOnChanges(): void {
    this.transformData();
  }

  transformData(): void {
    const pnlValue = parseFloat(this.data.pnl);
    const winrateValue = parseFloat(this.data.winrate);
    const roiValue = parseFloat(this.data.roi);
    const balanceValue = parseFloat(this.data.balance);

    this.pnlTextColor = pnlValue > 0 ? 'text-green-400' : pnlValue < 0 ? 'text-red-400' : 'text-white';
    this.pnlFormatted = isNaN(pnlValue) ? '-' : pnlValue >= 0 ? `+$${pnlValue}` : `-$${Math.abs(pnlValue)}`;
    this.winrateFormatted = isNaN(winrateValue) ? '-' : `${winrateValue}%`;
    this.roiFormatted = isNaN(roiValue) ? '-' : `${roiValue}%`;
    this.balanceFormatted = isNaN(balanceValue)
      ? '-'
      : this.currency.transform(balanceValue, 'USD', 'symbol', '.2-2') || '-';
  }

  deleteItem(event: MenuItemCommandEvent): void {
    this.confirmationService.confirm({
      target: event.originalEvent?.target as EventTarget,
      message: 'Are you sure you want to delete this portfolio?',
      header: 'Delete Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Delete',
      rejectLabel: 'Cancel',
      closeOnEscape: true,
      closable: true,
      rejectButtonStyleClass: 'p-button-secondary p-button-text',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.apiService.delete(`v1/portfolios/${this.credential.portfolio_id}`).subscribe({
          next: (response) => {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Portfolio Deleted Successfully'
            });
            this.portfolioDeleted.emit(this.credential.portfolio_id);
          },
          error: (error) => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Error Deleting Portfolio'
            });
          }
        });
      }
    });
  }

  showEditDialog(): void {
    this.portfolioEditForm.setValue({
      name: this.credential.name,
      login: this.credential.login,
    });
    this.isEditVisible = true;
  }

  editItem(): void {
    const data = this.portfolioEditForm.value;
    this.apiService.put(`v1/portfolios/${this.credential.portfolio_id}`, data).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Portfolio Updated Successfully'
        })
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Error Updating Portfolio'
        })
      }
    })
  }

  detailItem(): void {
    this.router.navigate([`/portfolio/${this.credential.portfolio_id}`])
  }
}