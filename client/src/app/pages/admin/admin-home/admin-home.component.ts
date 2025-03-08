import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import * as echarts from 'echarts/core';
import { BarChart, LineChart } from 'echarts/charts';
import { provideEchartsCore } from 'ngx-echarts';
import { SkeletonModule } from 'primeng/skeleton';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DecimalPipe, NgClass, NgIf } from '@angular/common';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TableModule } from 'primeng/table';
import { ApiService } from '../../../core/services/api.service';
import { PieChart } from 'echarts/charts';
import { ActivatedRoute, Router } from '@angular/router';

// Register the required components
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  LineChart,
  CanvasRenderer,
  PieChart
]);

@Component({
  selector: 'app-admin-home',
  templateUrl: './admin-home.component.html',
  styleUrls: ['./admin-home.component.css'],
  imports: [
    ButtonModule,
    DecimalPipe,
    SkeletonModule,
    ProgressSpinnerModule,
    TableModule,
    NgClass,
    NgIf,
  ],
  providers: [
    provideEchartsCore({ echarts }),
  ],

})
export class AdminHomeComponent implements OnInit {
  @ViewChild('profitChart') profitChartElement!: ElementRef;
  @ViewChild('usageChart') usageChartElement!: ElementRef;

  // Stats summary
  totalUsers: number = 0;
  totalModels: number = 0;
  totalRevenue: number = 0;
  activeSubscriptions: number = 0;
  revenueData: { month: string; total_revenue: number }[] = [];

  // Charts
  profitChart: any;
  usageChart: any;

  // Loading states
  loading: boolean = true;

  constructor(
    private messageService: MessageService,
    private apiService: ApiService,
    public activatedRoute: ActivatedRoute,
    public router: Router,
  ) { }

  ngOnInit(): void {
    this.fetchDashboardData().then(() => {
      // Initialize charts after data is fetched
      this.initProfitChart();
      this.initUsageChart();
    });
  }

  fetchDashboardData(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Simulate API call with setTimeout
      setTimeout(() => {
        // Demo data - Replace with actual API calls
        this.totalUsers = 1254;
        this.totalModels = 18;
        this.totalRevenue = 58750;
        this.activeSubscriptions = 867;

        this.loading = false;

        this.messageService.add({
          severity: 'success',
          summary: 'Data Loaded',
          detail: 'Dashboard data has been updated'
        });

        this.apiService.get('/v1/admin/dashboard').subscribe({
          next: (response: any) => {
            this.totalUsers = response.total_users;
            this.totalModels = response.total_models;
            this.totalRevenue = response.total_revenue;
            this.activeSubscriptions = response.active_subscriptions;
            this.loading = false;
          },
          error: (error) => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to load dashboard data'
            });
            this.loading = false;
          }
        });

        this.apiService.get('/v1/admin/revenue').subscribe({
          next: (response: any) => {
            // Assuming response.revenue_by_month has the necessary structure
            this.revenueData = response.revenue_by_month;
            this.loading = false;
            resolve();  // Resolve the promise when data fetching is complete
          },
          error: (error) => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to load revenue data'
            });
            this.loading = false;
            reject(error); // Reject the promise if there's an error
          }
        });
      }, 1000);
    });
  }


  initProfitChart(): void {
    if (this.profitChartElement && this.profitChartElement.nativeElement) {
      this.profitChart = echarts.init(this.profitChartElement.nativeElement);

      // Demo data for profit chart
      const revenueData = [
        { month: "Sat, 01 Mar 2025 00:00:00 GMT", total_revenue: 417.08 },
        { month: "Sat, 01 Feb 2025 00:00:00 GMT", total_revenue: 500 }
      ];

      // Map the revenue data to months and revenue values
      const months = this.revenueData.map(item => new Date(item.month).toLocaleString('en-US', { month: 'short' }));
      const revenue = this.revenueData.map(item => item.total_revenue);

      // const expenses = [6000, 6300, 6500, 6200, 6800, 7400, 7900, 8300, 8800];
      // const profit = months.map((_, i) => revenue[i] - expenses[i]);

      const option = {
        title: {
          text: 'Monthly Revenue & Profit',
          left: 'center',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['Revenue'],
          top: 'bottom',
          textStyle: {
            color: '#fff'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: months,
          axisLabel: {
            color: '#fff'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '${value}',
            color: '#fff'
          }
        },
        series: [
          {
            name: 'Revenue',
            type: 'bar',
            data: revenue,
            itemStyle: {
              color: '#4ade80'
            }
          },
          // {
          //   name: 'Expenses',
          //   type: 'bar',
          //   data: expenses,
          //   itemStyle: {
          //     color: '#f87171'
          //   }
          // },
          // {
          //   name: 'Profit',
          //   type: 'line',
          //   data: profit,
          //   symbolSize: 8,
          //   itemStyle: {
          //     color: '#60a5fa'
          //   },
          //   lineStyle: {
          //     width: 3
          //   }
          // }
        ]
      };

      this.profitChart.setOption(option);

      // Handle window resize
      window.addEventListener('resize', () => {
        this.profitChart.resize();
      });
    }
  }

  initUsageChart(): void {
    if (this.usageChartElement && this.usageChartElement.nativeElement) {
      this.usageChart = echarts.init(this.usageChartElement.nativeElement);

      // Demo data for model usage chart
      const option = {
        title: {
          text: 'Model Usage Distribution',
          left: 'center',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 'bottom',
          textStyle: {
            color: '#fff'
          }
        },
        series: [
          {
            name: 'Model Usage',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#1f2937',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 48, name: 'GPT-4', itemStyle: { color: '#4ade80' } },
              { value: 32, name: 'Claude', itemStyle: { color: '#60a5fa' } },
              { value: 15, name: 'Llama 3', itemStyle: { color: '#f97316' } },
              { value: 5, name: 'Other', itemStyle: { color: '#a78bfa' } }
            ]
          }
        ]
      };

      this.usageChart.setOption(option);

      // Handle window resize
      window.addEventListener('resize', () => {
        this.usageChart.resize();
      });
    }
  }

  refresh(): void {
    this.loading = true;
    this.fetchDashboardData();

    // Refresh charts with new data
    setTimeout(() => {
      this.initProfitChart();
      this.initUsageChart();
    }, 1100);
  }

  updateQueryParams(value: string) {
    this.router.navigate(
      [],
      {
        relativeTo: this.activatedRoute,
        queryParams: { view: value },
        queryParamsHandling: 'replace'
      }
    );
  }

}