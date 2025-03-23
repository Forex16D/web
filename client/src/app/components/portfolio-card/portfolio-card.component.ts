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
import { DropdownModule } from 'primeng/dropdown';
import { SliderModule } from 'primeng/slider';

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
    DropdownModule,
    SliderModule,
  ],
  templateUrl: './portfolio-card.component.html',
  styleUrls: ['./portfolio-card.component.css'],
  providers: [CurrencyPipe]
})
export class PortfolioCardComponent {
  @Input() portfolioData: {
    portfolio_id: string;
    name: string;
    login: string;
    model_name: string | null;
    is_expert: boolean;
    connected: boolean;
    total_profit: number | null;
    monthly_pnl: number | null;
    winrate: number | null;
    commission: number;
  } = {
      portfolio_id: '0',
      name: 'Portfolio',
      login: 'login',
      model_name: null,
      is_expert: false,
      connected: false,
      total_profit: null,
      monthly_pnl: 0,
      winrate: 0,
      commission: 0,
    };

  @Output() portfolioDeleted = new EventEmitter<string>();

  pnlFormatted: string = '-';
  winrateFormatted: string = '-';
  roiFormatted: string = '-';
  profitFormatted: string = '-'; // Renamed from balanceFormatted
  pnlTextColor: string = 'text-white';

  isEditVisible = false;

  expertOptions = [
    { label: 'Yes', value: true },
    { label: 'No', value: false },
  ];

  portfolioEditForm = new FormGroup({
    name: new FormControl('', [Validators.required, Validators.minLength(1), Validators.maxLength(20)]),
    login: new FormControl('', [Validators.required, Validators.pattern('[0-9]*')]),
    is_expert: new FormControl(false, [Validators.required]),
    commission: new FormControl(0.0, [Validators.required, Validators.min(0.0), Validators.max(100.0)]),
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
    const totalProfitValue = this.portfolioData.total_profit !== null ? parseFloat(this.portfolioData.total_profit.toString()) : 0;
    const monthlyPnlValue = this.portfolioData.monthly_pnl !== null ? parseFloat(this.portfolioData.monthly_pnl.toString()) : 0;
    const winrateValue = this.portfolioData.winrate !== null ? parseFloat(this.portfolioData.winrate.toString()) : 0;

    // Formatting total profit
    this.profitFormatted = isNaN(totalProfitValue)
      ? '-'
      : this.currency.transform(totalProfitValue, 'USD', 'symbol', '.2-2') || '-';

    // Formatting monthly PnL
    this.pnlFormatted = isNaN(monthlyPnlValue) ? '-' : monthlyPnlValue >= 0 ? `+$${monthlyPnlValue}` : `-$${Math.abs(monthlyPnlValue)}`;

    // Formatting winrate
    this.winrateFormatted = isNaN(winrateValue) ? '-' : `${winrateValue}%`;

    // Formatting PnL text color based on monthly PnL
    this.pnlTextColor = monthlyPnlValue > 0 ? 'text-green-400' : monthlyPnlValue < 0 ? 'text-red-400' : 'text-white';
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
        this.apiService.delete(`v1/portfolios/${this.portfolioData.portfolio_id}`).subscribe({
          next: (response) => {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Portfolio Deleted Successfully'
            });
            this.portfolioDeleted.emit(this.portfolioData.portfolio_id);
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
      name: this.portfolioData.name,
      login: this.portfolioData.login,
      is_expert: this.portfolioData.is_expert,
      commission: this.portfolioData.commission,
    });
    this.isEditVisible = true;
  }

  editItem(): void {
    const data = this.portfolioEditForm.value;
    if (this.portfolioEditForm.invalid) return;
    this.apiService.put(`v1/portfolios/${this.portfolioData.portfolio_id}`, data).subscribe({
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
    this.isEditVisible = false;
  }

  detailItem(): void {
    this.router.navigate([`/portfolio/${this.portfolioData.portfolio_id}`]);
  }
  
}
