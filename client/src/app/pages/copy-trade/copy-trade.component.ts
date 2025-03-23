import { Component, OnInit } from '@angular/core';
import { CommonModule, NgFor } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BotCardComponent } from '../../components/bot-card/bot-card.component';
import { ApiService } from '../../core/services/api.service';
import { Model } from '../../models/model.model';

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
    BotCardComponent,
    NgFor,
    DropdownModule,
    SelectButtonModule,
    FormsModule,
    InputTextModule,
    PaginatorModule
  ],
  templateUrl: './copy-trade.component.html',
  styleUrl: './copy-trade.component.css'
})
export class CopyTradeComponent implements OnInit {
  models: Model[] = [];
  filteredModels: Model[] = [];
  
  // UI state
  selectedView: any = { label: 'All', value: 'all' };
  searchQuery: string = '';
  symbolFilter: string = 'all';
  
  // Stats data 
  stats = {
    activeBots: 0,
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
    this.getModels();
    this.getStats(); // New method to fetch platform stats
  }

  getModels(): void {
    this.apiService.get('v1/models/user').subscribe({
      next: (response: any) => {
        this.models = response.models;
        this.filteredModels = [...this.models]; // Initialize filtered list
        this.applyFilters(); // Apply any active filters
        this.totalRecords = this.models.length;
        this.stats.activeBots = this.models.length; // Update active bots count
      },
      error: (error) => console.error('Failed to fetch models:', error),
    });
  }

  // New method to get platform statistics
  getStats(): void {
    // This would be replaced with an actual API call in production
    this.apiService.get('v1/stats').subscribe({
      next: (response: any) => {
        // Using placeholder data since the actual API endpoint might not exist yet
        this.stats = {
          activeBots: this.models.length,
          performance: '+2.8%', // Placeholder
          activeTraders: 428,   // Placeholder
          volume: '$1.2M'       // Placeholder
        };
      },
      error: (error) => {
        // Fallback to placeholder data if endpoint doesn't exist
        console.info('Stats endpoint not available, using placeholder data');
        this.stats = {
          activeBots: this.models.length,
          performance: '+2.8%',
          activeTraders: 428,
          volume: '$1.2M'
        };
      }
    });
  }

  // Method to handle search and filtering
  applyFilters(): void {
    let filtered = [...this.models];
    
    // Apply search filter
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(model => 
        model.name.toLowerCase().includes(query) || 
        model.symbol.toLowerCase().includes(query)
      );
    }
    
    // Apply symbol filter
    if (this.symbolFilter !== 'all') {
      filtered = filtered.filter(model => {
        // This is an example - adjust based on how your symbols are categorized
        const symbolType = this.getSymbolType(model.symbol);
        return symbolType === this.symbolFilter;
      });
    }
    
    // Apply performance filter
    if (this.selectedView.value === 'top') {
      // Sort by ROI or winrate descending
      filtered.sort((a, b) => parseFloat(b.roi) - parseFloat(a.roi));
      filtered = filtered.slice(0, 10); // Top 10 performers
    } else if (this.selectedView.value === 'new') {
      // Assuming there's a created_at field or similar
      // This is a placeholder and should be adjusted based on your model structure
      filtered.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
    }
    
    this.filteredModels = filtered;
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