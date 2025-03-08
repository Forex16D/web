from psycopg2.extras import RealDictCursor # type: ignore
from pathlib import Path
import subprocess
import threading
import tempfile
import zipfile
import shutil
import uuid
import time
import json
import os

from application.helpers.server_log_helper import ServerLogHelper

class ModelService:
  def __init__(self, db_pool):
    self.db_pool = db_pool
    self.evaluation_process = None
    self.current_evaluation_model = None
    self.stop_event = threading.Event()

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

  def get_active_models(self):

    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM models WHERE active = true")
      models = cursor.fetchall()

      cursor.close()
      return {"models": models}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      self.db_pool.release_connection(conn)

  def get_model_detail(self, model_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM models WHERE model_id = %s", (model_id, ))
      model = cursor.fetchone()

      cursor.close()
      return {"model": model}
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
            for file in zip_ref.namelist():
              if not file.endswith('/'):  # Skip directories
                destination = os.path.join(extract_dir, os.path.basename(file))
                with zip_ref.open(file) as source, open(destination, 'wb') as target:
                  target.write(source.read())


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
  
  def update_model(self, request, model_id):
    name = request.json.get("name")
    commission = request.json.get("commission")
    symbol = request.json.get("symbol").upper()
    
    if not name or not commission:
      raise ValueError("Missing required fields.")
    
    conn = self.db_pool.get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)


    try:
      cursor.execute(""" UPDATE models 
        SET name = %s, commission = %s, symbol = %s, updated_at = NOW()
        WHERE model_id = %s 
      """, (name, commission, symbol, model_id))
      conn.commit()
      return {"message": "Model updated successfully!"}
    except Exception as e:
      ServerLogHelper().error(f"Error updating model: {str(e)}")
      conn.rollback()
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
      
  def train_model(self, model_id):
    try:
      path = Path(f"./models/{model_id}")
      if not path.exists():
        raise ValueError("Model directory not found.")

      module_path = Path(f"models.{model_id}.trainer")

      # Load model and train
      subprocess.run(["python3", str(module_path)], check=True)

      return {"message": "Model trained successfully!"}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")

  def train_model(self, model_id, start_date, bars=100000):
    try:
      path = Path(f"./models/{model_id}")
      if not path.exists():
        raise ValueError("Model directory not found.")

      conn = self.db_pool.get_connection()
      cursor = conn.cursor()

      if start_date is None:
        raise ValueError("start_date must be specified.")
      
      if self.evaluation_process is not None and self.evaluation_process.poll() is None:
        raise ValueError(f"A training is already running for model {self.current_evaluation_model}. Please stop it before starting a new one.")

      ServerLogHelper().log(f"Start training for model {model_id}")


      # Fetch data from DB
      cursor.execute("SELECT * FROM market_data WHERE timestamp < %s LIMIT %s", (start_date, bars))
      data = cursor.fetchall()
      columns = [desc[0] for desc in cursor.description]  # Get column names

      # Convert to JSON
      dataset = [dict(zip(columns, row)) for row in data]

      with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as tmp_file:
        json.dump(dataset, tmp_file, default=str)
        temp_path = tmp_file.name

      module_path = f"models.{model_id}.trainer"

      # Call subprocess with data file path
      self.evaluation_process = subprocess.Popen(["python3", "-m", module_path, temp_path])
      self.current_evaluation_model = model_id

      return {"message": "Model trained successfully!"}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def backtest_model(self, model_id):
    try:
      path = Path(f"./models/{model_id}")
      if not path.exists():
        raise ValueError("Model directory not found.")

      module_path = f"models.{model_id}.publisher"

      if self.evaluation_process is not None and self.evaluation_process.poll() is None:
        raise ValueError(f"A backtest is already running for model {self.current_evaluation_model}. Please stop it before starting a new one.")

      ServerLogHelper().log(f"Starting backtest for model {model_id}")

      self.evaluation_process = subprocess.Popen(["python3", "-m", module_path])
      self.current_evaluation_model = model_id  # Track the running model

      return {"message": f"Backtest started for model {model_id}!"}
    except ValueError as e:
      raise ValueError(str(e))
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
  
  def stop_evaluate(self):
    if self.evaluation_process is not None:
      if self.evaluation_process.poll() is None:  # Check if running
        self.evaluation_process.terminate()  # Gracefully terminate
        self.evaluation_process.wait()  # Ensure it stops
        ServerLogHelper().log(f"Backtest for model {self.current_evaluation_model} stopped.")

      self.evaluation_process = None  # Reset tracking variable
      self.current_evaluation_model = None  # Reset the tracking model

      self.stop_event.set() 

      return {"message": "Backtest stopped successfully."}

    raise ValueError("No backtest process running.")

  def get_process_status(self):
    """Returns the current model being backtested or None if no backtest is running."""
    if self.evaluation_process is not None and self.evaluation_process.poll() is None:
      return {"running": True, "model_id": self.current_evaluation_model}
    return {"running": False, "model_id": None}

  def stream_backtest_status(self):
    """Streams the backtest status continuously until stopped."""
    self.stop_event.clear()  # Reset stop event before streaming

    def generate():
      while not self.stop_event.is_set():
        if not self.get_process_status()["running"]:
          yield "completed"
          break
        yield "running"
        time.sleep(2)  # Adjust based on how often you want updates

    return generate()
    
  def get_processes_status(self):
    status = {}
    for model_id, process in self.processes.items():
      status[model_id] = process.poll()  # Get process status
    return status
  
  def copy_trade(self, portfolio_id, model_id, user_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      cursor.execute(
          "UPDATE portfolios SET model_id = %s WHERE portfolio_id = %s AND user_id = %s",
          (model_id, portfolio_id, user_id)
      )
      conn.commit()
      
      return {"message": "Copy trade successfully!"}
    except Exception as e:
      ServerLogHelper().error(f"Error updating model: {str(e)}")
      conn.rollback()
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)