"""Wrapper — delega a infra/upload.py usando el venv de infra."""
import subprocess, sys, os

venv_python = os.path.join(os.path.dirname(__file__), "infra", "venv", "Scripts", "python.exe")
script      = os.path.join(os.path.dirname(__file__), "infra", "upload.py")

sys.exit(subprocess.call([venv_python, script] + sys.argv[1:]))