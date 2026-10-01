@echo off
setlocal
cd /d "%~dp0"
echo Abriendo el editor local de contenido.
echo Manten esta ventana abierta mientras trabajas. Para cerrar el editor, presiona Ctrl+C.
python tools\content_editor.py
endlocal
