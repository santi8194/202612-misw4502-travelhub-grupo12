import sys
import os

# Ensure the notification root directory is in the Python path so that
# modules like `api`, `config`, and `modules` can be imported directly.
sys.path.insert(0, os.path.dirname(__file__))
