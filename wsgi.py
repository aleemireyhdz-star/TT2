#!/usr/bin/env python
"""
Script para ejecutar la aplicación en modo producción.
Requiere gunicorn instalado: pip install gunicorn
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path
src_dir = Path(__file__).resolve().parent / 'src'
sys.path.insert(0, str(src_dir))

from src.Flask_Server import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
