# conftest.py
import os
import sys
# Calculate the absolute path for src directory
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, src_path)