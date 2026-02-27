#!/usr/bin/env python3
"""
Entry point del bot - Ejecutar desde aquí

Uso:
    uv run python main.py

O en background:
    nohup uv run python main.py > bot.log 2>&1 &
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
root = Path(__file__).parent
sys.path.insert(0, str(root))

from bot.main import run_bot

if __name__ == "__main__":
    run_bot()
