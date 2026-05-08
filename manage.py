#!/usr/bin/env python
"""Repository-level shim to run the real manage.py inside the taskflow folder."""
import runpy
import os
import sys

# Ensure working directory is repository root
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Execute inner manage.py
runpy.run_path(os.path.join('taskflow', 'manage.py'), run_name='__main__')
