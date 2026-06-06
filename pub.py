"""
pub.py - wrapper, delega a infra/pub.py
Uso: python pub.py <topic> <mensaje>
"""
import subprocess, sys, os

infra_dir = os.path.join(os.path.dirname(__file__), "infra")
venv_python = os.path.join(infra_dir, "venv", "Scripts", "python.exe")
script = os.path.join(infra_dir, "pub.py")

result = subprocess.run([venv_python, script] + sys.argv[1:], cwd=infra_dir)
sys.exit(result.returncode)