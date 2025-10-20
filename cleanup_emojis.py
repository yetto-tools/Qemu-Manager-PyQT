# cleanup_emojis.py
"""
Script para limpiar todos los emojis de los archivos Python
Ejecutar en la raíz del proyecto
"""

import os
import re
from pathlib import Path

# Mapeo de emojis a texto
EMOJI_MAP = {
    '✓': '✓',
    '✓': '✓',
    '✓': '✓',
    '❌': '❌',
    '⚠️': '⚠️',
    '⚠️': '⚠️',
    '🔴': '🔴',
    '🟢': '🟢',
    '📁': '📁',
    '📝': '📝',
    '💾': '💾',
    '🔍': '🔍',
    '📂': '📂',
    '🔧': '🔧',
    '⚙️': '⚙️',
    '⚙️': '⚙️',
    '✓': '✓',
    '📋': '📋',
    '❓': '❓',
    '📖': '📖',
    '🎬': '🎬',
    '🌐': '🌐',
    '🔌': '🔌',
    '💿': '💿',
    '🖨️': '🖨️',
    '🖨️': '🖨️',
    '📥': '📥',
    '📤': '📤',
    '✏️': '✏️',
    '✏️': '✏️',
    '🗑️': '🗑️',
    '🗑️': '🗑️',
    '➕': '➕',
    '▶': '▶',
    '⏹': '⏹',
    '🔄': '🔄',
    '📋': '📋',
    '👥': '👥',
    '📜': '📜',
    '✨': '✨',
    '🚀': '🚀',
    '💡': '💡',
    '📊': '📊',
    '💻': '💻',
    '⬅️': '⬅️',
    '➡️': '➡️',
    '☑️': '☑️',
    '☐': '☐',
}

def clean_file(filepath):
    """Limpia emojis de un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar emojis
        for emoji, text in EMOJI_MAP.items():
            content = content.replace(emoji, text)
        
        # Si hubo cambios, guardar
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[CLEANED] {filepath}")
            return True
        
        return False
    except Exception as e:
        print(f"❌ {filepath}: {e}")
        return False

def main():
    """Script principal"""
    print("Limpiando emojis de archivos Python...")
    print()
    
    # Archivos a limpiar
    python_files = Path('.').rglob('*.py')
    
    cleaned_count = 0
    total_count = 0
    
    for py_file in python_files:
        # Ignorar venv
        if 'venv' in str(py_file):
            continue
        
        total_count += 1
        if clean_file(str(py_file)):
            cleaned_count += 1
    
    print()
    print(f"Total de archivos: {total_count}")
    print(f"Archivos limpiados: {cleaned_count}")
    print()
    print("✓ Limpieza completada")
    print()
    print("Ahora ejecuta: python main.py")

if __name__ == '__main__':
    main()


# ==================== ALTERNATIVA: Si no quieres ejecutar script ====================

# Edita manualmente estos archivos y reemplaza los emojis:

"""
ARCHIVOS A EDITAR Y REEMPLAZOS:

1. main.py
   - Reemplazar ✓ por ✓
   - Todos los emojis por sus equivalentes en texto

2. utils.py
   - Reemplazar ✓ por ✓
   - Reemplazar ⚠️ por ⚠️
   - Etc.

3. qemu_ui/main_window.py
   - Buscar todos los emojis y reemplazar

4. qemu_ui/dialogs/*.py
   - Buscar todos los emojis y reemplazar

OPCIÓN: Usar buscar y reemplazar en VS Code:
- Ctrl+H para abrir Buscar y Reemplazar
- Habilitar expresiones regulares
- Patrón: ✓|❌|⚠️|🔴|🟢 etc
- Reemplazar con: ✓ o según sea
"""