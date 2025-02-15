from psycopg2.extras import RealDictCursor # type: ignore
import uuid
from application.helpers.server_log_helper import ServerLogHelper

class ModelService:
  def __init__(self, db_pool):
    self.db_pool = db_pool
    
  def get_all_models(self, request):
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)

    offset = (page - 1) * limit
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM models LIMIT %s OFFSET %s", (limit, offset))
      models = cursor.fetchall()

      cursor.close()
      return {"models": models}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      self.db_pool.release_connection(conn)

  def create_models(self, form_data, files):
    model_name = form_data.get("model_name")

    for file in files:
      filename = file.filename

      if not filename.endswith('.py'):
        raise ValueError("Only .py files are allowed.")

      ServerLogHelper().log(f"Received Python file: {filename}")

      try:
        save_path = f"./models/{filename}"
        file.save(save_path)

        ServerLogHelper().log(f"File saved to: {save_path}")

      except Exception as e:
        ServerLogHelper().error(f"Error saving file {filename}: {str(e)}")
        raise Exception("Internal server error while saving files.")

    return {"message": "Model(s) created successfully!"}
