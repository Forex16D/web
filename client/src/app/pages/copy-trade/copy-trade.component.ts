import { Component, OnInit } from '@angular/core';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExpertCardComponent } from '../../components/expert-card/expert-card.component';
import { ApiService } from '../../core/services/api.service';
import { PortfolioResponse } from '../../models/portfolio-response.model';

// PrimeNG Imports
import { DropdownModule } from 'primeng/dropdown';
import { SelectButtonModule } from 'primeng/selectbutton';
import { InputTextModule } from 'primeng/inputtext';
import { PaginatorModule } from 'primeng/paginator';

@Component({
  selector: 'app-copy-trade',
  standalone: true,
  imports: [
    CommonModule,
    NgFor,
    DropdownModule,
    SelectButtonModule,
    FormsModule,
    InputTextModule,
    PaginatorModule,
    ExpertCardComponent,
    NgIf,
  ],
  templateUrl: './copy-trade.component.html',
  styleUrl: './copy-trade.component.css'
})
export class CopyTradeComponent implements OnInit {
  experts: PortfolioResponse[] = [];
  filteredExperts: PortfolioResponse[] = [];
  
  // UI state
  selectedView: any = { label: 'All', value: 'all' };
  searchQuery: string = '';
  symbolFilter: string = 'all';
  
  // Stats data 
  stats = {
    activeExperts: 0,
    performance: '+0.0%',
    activeTraders: 0,
    volume: '$0'
  };
  
  // Pagination
  first: number = 0;
  rows: number = 9;
  totalRecords: number = 0;

  constructor(
    private apiService: ApiService,
  ) {}

  ngOnInit(): void {
    this.getExperts();
    this.getStats();
  }

  getExperts(): void {
    this.apiService.get('v1/expert-portfolios').subscribe({
      next: (response: any) => {
        this.experts = response.portfolios;
        this.filteredExperts = [...this.experts]; 
        this.applyFilters(); 
        this.totalRecords = this.experts.length;
        this.stats.activeExperts = this.experts.length;
      },
      error: (error) => {
        console.error('Failed to fetch experts:', error);
        this.experts = [];
      },
    });
  }
  

  // New method to get platform statistics
  getStats(): void {
    // This would be replaced with an actual API call in production
    this.apiService.get('v1/stats').subscribe({
      next: (response: any) => {
        // Using placeholder data since the actual API endpoint might not exist yet
        this.stats = {
          activeExperts: this.experts.length,
          performance: '+2.8%', // Placeholder
          activeTraders: 428,   // Placeholder
          volume: '$1.2M'       // Placeholder
        };
      },
      error: (error) => {
        // Fallback to placeholder data if endpoint doesn't exist
        console.info('Stats endpoint not available, using placeholder data');
        this.stats = {
          activeExperts: this.experts.length,
          performance: '+2.8%',
          activeTraders: 428,
          volume: '$1.2M'
        };
      }
    });
  }

  // Method to handle search and filtering
  applyFilters(): void {
    let filtered = [...this.experts];
    
    // Apply search filter
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(model => 
        model.name.toLowerCase().includes(query)
      );
    }
    
    if (this.selectedView.value === 'top') {
      // filtered.sort((a, b) => parseFloat(b.roi) - parseFloat(a.roi));
      filtered = filtered.slice(0, 10);
    } else if (this.selectedView.value === 'new') {
      filtered.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
    }
    
    this.filteredExperts = filtered;
    this.totalRecords = filtered.length;
  }
  
  // Helper method to categorize symbols
  private getSymbolType(symbol: string): string {
    // This is a simple example - implement your own logic
    if (symbol.includes('USD') || symbol.includes('EUR') || symbol.includes('JPY')) {
      return 'forex';
    } else if (symbol.includes('BTC') || symbol.includes('ETH') || symbol.includes('USDT')) {
      return 'crypto';
    } else if (symbol.includes('XAU') || symbol.includes('OIL') || symbol.includes('GOLD')) {
      return 'commodities';
    }
    return 'other';
  }
  
  // Pagination event handler
  onPageChange(event: any): void {
    this.first = event.first;
    this.rows = event.rows;
  }
  
  // Search handler
  onSearch(): void {
    this.applyFilters();
  }
  
  // Filter by symbol handler
  onSymbolFilterChange(event: any): void {
    this.symbolFilter = event.value;
    this.applyFilters();
  }
  
  // View type handler
  onViewTypeChange(event: any): void {
    this.selectedView = event.value;
    this.applyFilters();
  }
}