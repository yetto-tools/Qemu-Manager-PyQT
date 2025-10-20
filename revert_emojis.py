# revert_emojis.py
"""
Script para revertir texto a emojis
Ejecutar en la raíz del proyecto para deshacer los cambios de cleanup_emojis.py
"""

import os
from pathlib import Path

# Mapeo inverso de texto a emojis
TEXT_TO_EMOJI_MAP = {
    '[OK]': '✓',
    '[ERROR]': '❌',
    '[WARN]': '⚠️',
    '[OFF]': '🔴',
    '[ON]': '🟢',
    '[FILE]': '📁',
    '[NOTE]': '📝',
    '[SAVE]': '💾',
    '[SEARCH]': '🔍',
    '[FOLDER]': '📂',
    '[TOOL]': '🔧',
    '[CONFIG]': '⚙️',
    '[INFO]': '📋',
    '[HELP]': '❓',
    '[DOCS]': '📖',
    '[VIDEO]': '🎬',
    '[NETWORK]': '🌐',
    '[DEVICE]': '🔌',
    '[DISK]': '💿',
    '[PRINTER]': '🖨️',
    '[IMPORT]': '📥',
    '[EXPORT]': '📤',
    '[EDIT]': '✏️',
    '[DELETE]': '🗑️',
    '[ADD]': '➕',
    '[PLAY]': '▶',
    '[STOP]': '⏹',
    '[REFRESH]': '🔄',
    '[CREDITS]': '👥',
    '[LICENSE]': '📜',
    '[FEATURES]': '✨',
    '[LAUNCH]': '🚀',
    '[IDEA]': '💡',
    '[STATS]': '📊',
    '[COMPUTER]': '💻',
    '[BACK]': '⬅️',
    '[NEXT]': '➡️',
    '[CHECKED]': '☑️',
    '[UNCHECKED]': '☐',
}

def revert_file(filepath):
    """Revierte emojis en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar texto a emojis
        # IMPORTANTE: Revertir en orden para evitar conflictos
        # Primero los más específicos
        replacements = sorted(TEXT_TO_EMOJI_MAP.items(), key=lambda x: -len(x[0]))
        
        for text, emoji in replacements:
            content = content.replace(text, emoji)
        
        # Si hubo cambios, guardar
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[REVERTED] {filepath}")
            return True
        
        return False
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def main():
    """Script principal"""
    print("=" * 60)
    print("Revirtiendo emojis en archivos Python...")
    print("=" * 60)
    print()
    
    # Archivos a revertir
    python_files = list(Path('.').rglob('*.py'))
    
    reverted_count = 0
    total_count = 0
    skipped_count = 0
    
    for py_file in python_files:
        # Ignorar venv y este script
        if 'venv' in str(py_file) or py_file.name == 'revert_emojis.py':
            skipped_count += 1
            continue
        
        total_count += 1
        if revert_file(str(py_file)):
            reverted_count += 1
    
    print()
    print("=" * 60)
    print(f"Total de archivos procesados: {total_count}")
    print(f"Archivos revertidos: {reverted_count}")
    print(f"Archivos omitidos (venv): {skipped_count}")
    print("=" * 60)
    print()
    print("[OK] Reversión completada")
    print()
    print("Ahora ejecuta: python main.py")
    print()

if __name__ == '__main__':
    main()


# ==================== ALTERNATIVA: Sin ejecutar script ====================

"""
Si quieres revertir manualmente, busca y reemplaza:

[OK] → ✓
[ERROR] → ❌
[WARN] → ⚠️
[SEARCH] → 🔍
[SAVE] → 💾
[DELETE] → 🗑️
[ADD] → ➕
[PLAY] → ▶
[STOP] → ⏹
[REFRESH] → 🔄
[EDIT] → ✏️
[EXPORT] → 📤
[IMPORT] → 📥
[TOOL] → 🔧
[CONFIG] → ⚙️
[FOLDER] → 📂
[DISK] → 💿
[DEVICE] → 🔌
[NETWORK] → 🌐
[HELP] → ❓
[DOCS] → 📖
[FEATURES] → ✨
[CREDITS] → 👥
[LICENSE] → 📜
[INFO] → ℹ️

En VS Code:
1. Ctrl+H
2. Buscar: \[OK\]
3. Reemplazar: ✓
4. Replace All
5. Repetir para cada reemplazo
"""