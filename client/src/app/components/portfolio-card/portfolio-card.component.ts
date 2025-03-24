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
    if (this.portfolioEditForm.invalid) return;

    const updatedData = this.portfolioEditForm.value;
    const newPortfolioData = {
      ...this.portfolioData,
      name: updatedData.name ?? this.portfolioData.name,
      login: updatedData.login ?? this.portfolioData.login,
      is_expert: updatedData.is_expert ?? this.portfolioData.is_expert,
      commission: updatedData.commission ?? this.portfolioData.commission,
    };

    // User is becoming an expert
    if (newPortfolioData.is_expert && !this.portfolioData.is_expert) {
      this.confirmationService.confirm({
        header: "Become a Trading Expert",
        message: `
          <div class="p-3">
            <div class="flex align-items-center gap-3 mb-3">
              <i class="pi pi-star text-yellow-500" style="font-size: 2rem;"></i>
              <h2 class="text-xl font-medium m-0">Expert Status Benefits & Responsibilities</h2>
            </div>
            
            <div class="mb-4 p-3 border border-1 border-left-3 border-yellow-500 bg-yellow-600">
              <p class="mb-2 font-medium">Becoming an expert costs <b>$10 monthly</b> and includes:</p>
              <ul class="m-0 pl-4">
                <li>- Your portfolio visible in the Experts marketplace</li>
                <li>- Performance metrics and ranking</li>
                <li>- Ability to earn ${(newPortfolioData.commission * 100).toFixed(0)}% commission on subscriber profits</li>
                <li>- Expert badge on your profile</li>
              </ul>
            </div>
            
            <p class="mb-0">By proceeding, you agree to our <a href="/terms-and-conditions" target="_blank" class="text-primary font-medium">Terms & Conditions</a> for Expert Traders.</p>
          </div>
        `,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Yes, Become an Expert',
        rejectLabel: 'Not Now',
        closeOnEscape: true,
        closable: true,
        rejectButtonStyleClass: 'p-button-secondary p-button-text',
        acceptButtonStyleClass: 'p-button-primary',
        accept: () => {
          this.updatePortfolio(newPortfolioData);
        },
        reject: () => {
          // Revert the form control value without submitting
          this.portfolioEditForm.patchValue({
            is_expert: false
          });
        }
      });
    }
    // User is revoking expert status
    else if (!newPortfolioData.is_expert && this.portfolioData.is_expert) {
      this.confirmationService.confirm({
        header: "Disable Expert Status",
        message: `
          <div class="p-3">
            <div class="flex align-items-center gap-3 mb-3">
              <i class="pi pi-info-circle text-blue-500" style="font-size: 2rem;"></i>
              <h2 class="text-xl font-medium m-0">Disable Expert Status</h2>
            </div>

            <div class="mb-4 p-3 border-1 border-left-3 border-blue-500 bg-blue-600">
              <p class="font-medium mb-2">By disabling your expert status:</p>
              <ul class="m-0 pl-4">
                <li>- Your portfolio will be removed from the Experts marketplace</li>
                <li>- All current subscriber connections will be terminated</li>
                <li>- Monthly expert fee will no longer be charged</li>
              </ul>
            </div>
            
            <p class="mb-0">You can always become an expert again in the future.</p>
          </div>
        `,
        icon: 'pi pi-info-circle',
        acceptLabel: 'Yes, Disable Expert Status',
        rejectLabel: 'Keep Expert Status',
        closeOnEscape: true,
        closable: true,
        rejectButtonStyleClass: 'p-button-secondary p-button-text',
        acceptButtonStyleClass: 'p-button-danger',
        accept: () => {
          this.updatePortfolio(newPortfolioData);
        },
        reject: () => {
          // Revert the form control value without submitting
          this.portfolioEditForm.patchValue({
            is_expert: true
          });
        }
      });
    }
    // Other changes (not related to expert status)
    else {
      this.updatePortfolio(newPortfolioData);
    }
  }

  updatePortfolio(data: any): void {
    this.apiService.put(`v1/portfolios/${this.portfolioData.portfolio_id}`, data).subscribe({
      next: () => {
        this.portfolioData = data;
        this.transformData();

        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Portfolio Updated Successfully'
        });

        this.isEditVisible = false;
      },
      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Error Updating Portfolio'
        });
      }
    });
  }


  detailItem(): void {
    this.router.navigate([`/portfolio/${this.portfolioData.portfolio_id}`]);
  }

}
