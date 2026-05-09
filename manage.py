#!/usr/bin/env python
"""Repository-level shim to run Django management from root."""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Set working directory to repo root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add repo root to path so taskflow module is importable
sys.path.insert(0, os.getcwd())

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow.settings')

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
