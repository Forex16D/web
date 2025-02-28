from psycopg2.extras import RealDictCursor # type: ignore
import shutil
import uuid
import zipfile
from pathlib import Path
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

  def create_models(self, files):
    models_dir = Path("./models")
    models_dir.mkdir(parents=True, exist_ok=True)  # Ensure base directory exists

    saved_files = []  # Track saved files for rollback
    extracted_dirs = []  # Track extracted directories for rollback

    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      for file in files:
        model_id = str(uuid.uuid4())
        filename = file.filename
        file_ext = Path(filename).suffix.lower()
        save_path = models_dir / f"{model_id}_temp"  # Path to save uploaded file

        ServerLogHelper().log(f"Received file: {filename}")

        file.save(save_path)  # Save the uploaded file
        saved_files.append(save_path)  # Track saved file
        ServerLogHelper().log(f"File saved to: {save_path}")

        if file_ext == ".zip":
          extract_dir = models_dir / model_id   # Folder name
          extract_dir.mkdir(parents=True, exist_ok=True)
          extracted_dirs.append(extract_dir)  # Track extracted directory

          with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)  # Extract contents

          ServerLogHelper().log(f"Extracted {filename} to {extract_dir}")

          # Ensure extracted folder contains at least one .py file
          py_files = list(extract_dir.rglob("*.py"))
          if not py_files:
            raise ValueError("Extracted archive does not contain any .py files.")

          save_path.unlink()  # Delete the zip file after successful extraction
          saved_files.remove(save_path)  # Remove from rollback list
          ServerLogHelper().log(f"Deleted compressed file: {save_path}")

          cursor.execute("""
                         INSERT INTO models (model_id, name, file_path) 
                         VALUES (%s, %s, %s)
                         """, 
                         (model_id, filename.replace(".zip", ""), str(extract_dir)))
          conn.commit()

      return {"message": "Model(s) created successfully!"}

    except Exception as e:
      ServerLogHelper().error(f"Error processing files: {str(e)}")

      # Rollback changes
      for file in saved_files:
        if file.exists():
          file.unlink()
          ServerLogHelper().log(f"Rolled back: Deleted file {file}")

      for directory in extracted_dirs:
        if directory.exists():
          shutil.rmtree(directory)  # Delete entire extracted directory
          ServerLogHelper().log(f"Rolled back: Deleted extracted directory {directory}")

      raise Exception("Internal server error while processing files. Rollback completed.")
    
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
    
  def delete_model(self, model_id):
    conn = self.db_pool.get_connection()
    cursor = conn.cursor()

    try:
      path = Path(f"./models/{model_id}")
      if path.exists():
        shutil.rmtree(path)
        ServerLogHelper().log(f"Deleted model directory: {path}")

      cursor.execute("DELETE FROM models WHERE model_id = %s", (model_id,))
      conn.commit()
      return {"message": "Model deleted successfully!"}
    except Exception as e:
      ServerLogHelper().error(f"Error deleting model: {str(e)}")
      conn.rollback()
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
