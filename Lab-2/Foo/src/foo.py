#!/usr/bin/env python3
# src/foo.py
EXPECTED_ARG_COUNT = 6

def process_args(args):
    """Process arguments and validate count."""
    if len(args) != EXPECTED_ARG_COUNT:
        raise ValueError(f"Expected {EXPECTED_ARG_COUNT} arguments, got {len(args)}")
    print(f"Processing {len(args)} arguments: {args}")

if __name__ == "__main__":
    import sys
    try:
        process_args(sys.argv[1:])  # Pass command-line args (excluding script name)
    except ValueError as e:
        print(e)
        sys.exit(-1)
