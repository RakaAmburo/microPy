"""
pyping.py -- wrapper, delega a infra/pyping.py usando el venv de infra.

Uso:
    python pyping.py [--timeout 3]
"""
import subprocess, sys, os

infra_dir = os.path.join(os.path.dirname(__file__), "infra")
venv_python = os.path.join(infra_dir, "venv", "Scripts", "python.exe")
script = os.path.join(infra_dir, "pyping.py")

result = subprocess.run([venv_python, script] + sys.argv[1:], cwd=infra_dir)
sys.exit(result.returncode)