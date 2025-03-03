export interface Model {
  model_id: string
  name: string
  commission: number | null
  running: boolean
  created_at: string
  updated_at: string | null
  file_path: string
}