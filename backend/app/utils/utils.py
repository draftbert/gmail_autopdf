import os
import requests
import subprocess

ONEDRIVE_REMOTE    = os.getenv("ONEDRIVE_REMOTE")
ONEDRIVE_BASE_PATH = os.getenv("ONEDRIVE_BASE_PATH")

def telegram(aviso = 'Ejecutions has finalized'):
    
    ida    = os.getenv("TELEGRAM_IDA")
    token  = os.getenv("TELEGRAM_TOKEN")
    
    url    = "https://api.telegram.org/bot" + token + "/sendMessage"
    params = {'chat_id': ida, 'text' : aviso}
    
    requests.post(url, params = params)
    
    
def upload_to_onedrive(local_path):
    """
    Upload de file to the onedrive folder
    """
    try:
        path_parts = local_path.split(os.sep)
        year_folder = next((p for p in path_parts if p.isdigit() and len(p) == 4), None)
        
        if year_folder:
            remote_dest = f"{ONEDRIVE_REMOTE}:{ONEDRIVE_BASE_PATH}/{year_folder}"
        else:
            remote_dest = f"{ONEDRIVE_REMOTE}:{ONEDRIVE_BASE_PATH}"

        filename = os.path.basename(local_path)
        print(f"[INFO] Uploading {filename} to OneDrive: {remote_dest}")
        
        subprocess.run([
            "rclone", "copy", 
            local_path, 
            remote_dest
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        print(f"[SUCCESS] Upload complete: {filename}")
        telegram(f"[SUCCESS] Upload complete: {filename}")
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Rclone failed for {local_path}: {e.stderr.decode().strip()}")
        telegram(f"[ERROR] Rclone failed for {local_path}: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"[ERROR] Unexpected error uploading {local_path}: {str(e)}")
        telegram(f"[ERROR] Unexpected error uploading {local_path}: {str(e)}")
