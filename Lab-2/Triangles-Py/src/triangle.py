#!/usr/bin/env python3
################################################################################
#
# triangle.py computes the area of a triangle using Heron's algorithm
#
# The function area(points) expects points to be a tuple of 3 2-D
# Cartesian coordinates. It computes the area of the triangle created by
# these points and returns that.
#
# main() will accept these numbers from the command-line and then invoke
# triangleArea() and output the result iff there are exactly six input numbers.
# 

import math
import sys

EXPECTED_ARG_COUNT = 6

################################################################################
#
# processInputs() accepts an array of floats.  It verifies that the array size
# is 6 and raises an error if not.  If it is, it converts the inputs to floats
# and returns the values as a triple of Cartestian points.
# 

def processInputs(name, args):
    if len(args) != EXPECTED_ARG_COUNT:
        raise ValueError(f"{name}: Expected {EXPECTED_ARG_COUNT} inputs; received {len(args)}")

    x1, y1, x2, y2, x3, y3 = map(float, args)
    return ((x1, y1), (x2, y2), (x3, y3))

################################################################################
#
# outputMessage() outputs the area of the triangle

def outputMessage(points, triangleArea):
    print(f"The area of the triangle formed by points {points[0]}, {points[1]}, and {points[2]} is: {triangleArea:.3f}")

################################################################################
#
# distance() computes the Pythagorean distance between two Cartesian points
#

def distance(p1, p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

################################################################################
#
# area() accepts a tuple of three Cartesian points and computes the area of the
# triangle created by those points using Heron's formula.
#

def area(points):
    s1 = distance(points[0], points[1])
    s2 = distance(points[0], points[2])
    s3 = distance(points[1], points[2])
    s = 0.5 * (s1 + s2 + s3)
    return math.sqrt(s * (s - s1) * (s - s2) * (s - s3))

################################################################################
#
#

def triangle(points):
    try:
        points = processInputs(sys.argv[0], points)
    except ValueError as e:
        print(e)
        return

    triangleArea = area(points)
    outputMessage(points, triangleArea)

if __name__ == "__main__":
    triangle(sys.argv[1:])

