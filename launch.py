import subprocess
from pathlib import Path
from service import ensure_running, URL
ensure_running()
chrome=Path('/Applications/Google Chrome.app');edge=Path('/Applications/Microsoft Edge.app')
if chrome.exists():subprocess.run(['/usr/bin/open','-a',str(chrome),URL],check=True)
elif edge.exists():subprocess.run(['/usr/bin/open','-a',str(edge),URL],check=True)
else:subprocess.run(['/usr/bin/open',URL],check=True)
