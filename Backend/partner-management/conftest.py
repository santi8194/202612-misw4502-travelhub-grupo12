import sys
import os

# Ensure the partner-management root is on the path so that
# `config`, `modules` etc. can be imported directly in tests.
sys.path.insert(0, os.path.dirname(__file__))
