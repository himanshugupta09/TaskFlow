#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow.settings')

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
