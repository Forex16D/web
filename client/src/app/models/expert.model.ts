import { WeeklyProfit } from './weekly-profit.model';

export interface Expert {
  connected: boolean
  created_at: string
  name: string
  portfolio_id: string
  user_id: string
  is_expert: boolean
  total_profit: number | null
  monthly_pnl: number | null
  winrate: number | null
  commission: number
  weekly_profits: WeeklyProfit[]
}