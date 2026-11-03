from pathlib import Path
from huggingface_hub import snapshot_download
root = Path(__file__).resolve().parent
snapshot_download('Systran/faster-whisper-small', local_dir=str(root / 'model'), allow_patterns=['model.bin','config.json','tokenizer.json','vocabulary.json','vocabulary.txt'])
print('Modèle multilingue disponible localement.')
