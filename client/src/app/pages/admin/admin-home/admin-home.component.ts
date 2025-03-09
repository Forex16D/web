import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { BarChart, LineChart } from 'echarts/charts';
import { SkeletonModule } from 'primeng/skeleton';
import { catchError } from 'rxjs/operators';
import * as echarts from 'echarts/core';
import { forkJoin, of } from 'rxjs';
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
  modelUsage: { value: number; name: string }[] = [];

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
      this.initProfitChart();
      this.initUsageChart();
    });
  }

  fetchDashboardData(): Promise<void> {
    return new Promise((resolve) => {
      forkJoin({
        dashboard: this.apiService.get<any>('/v1/admin/dashboard').pipe(
          catchError((error) => {
            this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load dashboard data' });
            return of({ total_users: 0, total_models: 0, total_revenue: 0, active_subscriptions: 0 }); // Default values
          })
        ),
        revenue: this.apiService.get<any>('/v1/admin/revenue').pipe(
          catchError((error) => {
            this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load revenue data' });
            return of({ revenue_by_month: [] }); // Default value
          })
        ),
        modelUsage: this.apiService.get<any>('/v1/admin/model-usage').pipe(
          catchError((error) => {
            this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load model usage data' });
            return of({ model_usage: [] }); // Default value
          })
        )
      }).subscribe(({ dashboard, revenue, modelUsage }) => {
        this.totalUsers = dashboard.total_users;
        this.totalModels = dashboard.total_models;
        this.totalRevenue = dashboard.total_revenue;
        this.activeSubscriptions = dashboard.active_subscriptions;

        this.revenueData = revenue.revenue_by_month;
        this.modelUsage = modelUsage.model_usage;

        this.loading = false;
        resolve(); // Resolve the promise even if some APIs failed
      });
    });
  }

  initProfitChart(): void {
    if (this.profitChartElement && this.profitChartElement.nativeElement) {
      this.profitChart = echarts.init(this.profitChartElement.nativeElement);

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
      // Dispose existing chart instance to prevent duplicate initialization
      if (this.usageChart) {
        this.usageChart.dispose();
      }

      this.usageChart = echarts.init(this.usageChartElement.nativeElement);

      // Define a dynamic color palette
      const colorPalette = ['#4ade80', '#60a5fa', '#f97316', '#a78bfa', '#facc15', '#ef4444', '#14b8a6'];

      // Map colors dynamically to model usage data
      const chartData = this.modelUsage.map((item, index) => ({
        ...item,
        itemStyle: { color: colorPalette[index % colorPalette.length] } // Assign color from palette
      }));

      console.log(chartData);
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
            data: chartData // Use dynamically colored data
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
    this.fetchDashboardData().then(() => {
      this.initProfitChart();
      this.initUsageChart();
    })
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