import sys
from pathlib import Path

# Add ai-service root to sys.path so tests can run from project root or ai-service/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
