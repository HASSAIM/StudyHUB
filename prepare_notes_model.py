from pathlib import Path
from huggingface_hub import snapshot_download
root = Path(__file__).resolve().parent
snapshot_download('mlx-community/Qwen3-4B-Instruct-2507-4bit', local_dir=str(root / 'notes-model'), allow_patterns=['*.json','*.safetensors','*.txt','*.jinja'])
print('Modèle de comptes rendus disponible localement.')
