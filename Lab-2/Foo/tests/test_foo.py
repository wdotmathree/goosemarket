#!/usr/bin/env python3
# tests/test_foo.py
import pytest
from src.foo import EXPECTED_ARG_COUNT, process_args

def test_expected_arg_count():
    assert EXPECTED_ARG_COUNT == 6, "Expected argument count should be 6"

def test_process_args_valid():
    args = ["a", "b", "c", "d", "e", "f"]
    process_args(args)  # Should not raise

def test_process_args_invalid():
    args = ["a", "b", "c"]
    with pytest.raises(ValueError, match=f"Expected {EXPECTED_ARG_COUNT} arguments"):
        process_args(args)
