export interface PortfolioResponse {
  connected: boolean
  created_at: string
  login: string
  model_id: string | null
  model_name: string | null
  name: string
  portfolio_id: string
  access_token: string
  user_id: string
  is_expert: boolean
  expert_id: string | null
  total_profit: number | null
  monthly_pnl: number | null
  winrate: number | null
  commission: number
}