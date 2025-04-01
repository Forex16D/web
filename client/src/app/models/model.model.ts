import { WeeklyProfit } from "./weekly-profit.model"

export interface Model {
  model_id: string
  name: string
  symbol: string
  commission: number | null
  running: boolean
  created_at: string
  updated_at: string | null
  file_path: string
  monthly_pnl: number | null
  winrate: number | null
  auto_train: boolean
  weekly_profits: WeeklyProfit[]
}