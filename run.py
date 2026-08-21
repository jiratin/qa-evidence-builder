from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from qa_evidence.app import main

main()
