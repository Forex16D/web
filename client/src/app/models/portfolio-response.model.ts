export interface PortfolioResponse {
  connected: boolean
  created_at: string
  login: string
  model_id: string | null
  model_name: string | null
  name: string
  portfolio_id: string
  token_id: string | null
  user_id: string
  is_expert: boolean
  total_profit: number | null
  monthly_pnl: number | null
  winrate: number | null
  commission: number
}