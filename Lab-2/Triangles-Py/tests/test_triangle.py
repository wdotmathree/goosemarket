#!/usr/bin/env python3
################################################################################
#
# Tests for triangle.py
# 

import math
import sys
import re                      # Needed for regexp tests
import pytest
from pytest import approx      # Needed to perform float comparison

# What we are testing

from src.triangle import processInputs, outputMessage, distance, area, triangle, EXPECTED_ARG_COUNT

################################################################################
#
#

def test_processInputs_t1():
    assert(processInputs("DontCare", [1, 2, 3, 4, 5, 6]) == ((1,2),(3,4),(5,6)))

def test_processInputs_t2():
    args = []
    with pytest.raises(ValueError, match=f"Expected {EXPECTED_ARG_COUNT} inputs; received {len(args)}"):
        processInputs("triangle.py", args)

################################################################################
#
#

def test_outputMessage_t1(capsys):
    outputMessage(((1,2),(3,4),(5,6)),7)
    captured = capsys.readouterr()  # Capture stdout and stderr
    assert captured.out.strip() == "The area of the triangle formed by points (1, 2), (3, 4), and (5, 6) is: 7.000"
    
################################################################################
#
#

def test_distance_t1():
    assert distance((0, 0), (0, 1)) == 1

def test_distance_t2():
    assert distance((0, 0), (1, 1)) == approx(1.414213, rel=1e-6)

def test_distance_t3():
    assert distance((0, 0), (0, 0)) == 0

################################################################################
#
#

def test_area_t1():
    assert area(((0, 0), (0, 1), (1, 0))) == approx(0.5, rel=1e-6)

def test_area_t2():
    assert area(((0,0),(0,1.6),(10,0))) == approx(8.0, rel=1e-6)

def test_area_t3():
    assert area(((1.2, 1.2), (-7.4, 6.4), (17, 123.24))) == approx(565.852173, rel=1e-6)

################################################################################
#
#

def test_triangle_t1(capsys):
    triangle([0, 0, 0, 1, 1, 0])
    captured = capsys.readouterr()
    output = captured.out.strip()  # Strip trailing whitespace/newlines
    pattern = r".*The area of the triangle.*0.5.*"
    assert re.match(pattern, output), f"Text '{output}' does not match pattern '{pattern}'"

def test_triangle_t2(capsys):
    triangle([])
    captured = capsys.readouterr()
    output = captured.out.strip()  # Strip trailing whitespace/newlines
    pattern = r".*Expected 6 inputs; received.*"
    assert re.match(pattern, output), f"Text '{output}' does not match pattern '{pattern}'"

def test_triangle_t3(capsys):
    triangle([0,2.5,2.5,0,2.5,2.5])
    captured = capsys.readouterr()
    output = captured.out.strip()  # Strip trailing whitespace/newlines
    pattern = r".*The area of the triangle.*3\.125.*"
    assert re.match(pattern, output), f"Text '{output}' does not match pattern '{pattern}'"
