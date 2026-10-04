"""
Convenience entrypoint script to execute synthetic dataset generation.
Usage:
    python generate_data.py --profile medium
    python generate_data.py --profile small
    python generate_data.py --customers 10000 --transactions 50000 --seed 42
"""

import sys
from src.data_generator.generate_data import main

if __name__ == "__main__":
    sys.exit(main())
