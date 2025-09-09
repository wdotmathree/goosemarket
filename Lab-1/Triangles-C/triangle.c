/*******************************************************************************/
/*                                                                             */
/* Program: Triangle                                                           */
/* Input:  Exactly 6 floating point numbers, interpreted as three Cartestian   */
/*         points.                                                             */
/* Output: The area of the triangle formed by the input points is printed on   */
/*         stdout.                                                             */
/*                                                                             */
/* Author: PASW; 17 July 2018                                                  */
/*                                                                             */
/* Change history                                                              */
/* 17 July 2018; PASW: Initial version                                         */
/* 28 Sept 2018; PASW: Added slope output, comments, broke into functions      */
/* 17 Aug  2023; PASW: reduced tojust triangle area; changed to C              */
/*  7 Jan  2025; PASW: cleaned up comments                                     */
/*                                                                             */

#include <stdio.h>                    /* printf */
#include <math.h>                     /* sqrt   */
#include <stdlib.h>                   /* atoi   */

/*******************************************************************************/
/*                                                                             */
/* outputMessage()                                                             */
/*                                                                             */

void outputMessage(const float x1, const float y1,
                   const float x2, const float y2,
                   const float x3, const float y3,
                   const float area) {

  printf("The area of the triangle formed by points (%f,%f), (%f,%f), and (%f,%f) is: %f\n",
	 x1, y1,
	 x2, y2,
	 x3, y3,
	 area);

  return;
}

/*******************************************************************************/
/*                                                                             */
/* distance()                                                                  */
/* Inputs:                                                                     */
/* (x1,y1), (x2,y2): unvalidated Cartesian coordinates                         */
/* Output:                                                                     */

// The distance between said coordinates.
//

float distance(const float x1, const float y1,
               const float x2, const float y2) {
  return sqrt(pow((x1-x2),2)+pow((y1-y2),2));
}

/*******************************************************************************/
/*                                                                             */
/* triangleArea()                                                              */
/* Inputs:                                                                     */
/* s1, s2, s3: lengths of the three sides                                      */
/* Output:                                                                     */
/* The area of the triangles.                                                  */
/*                                                                             */

float triangleArea(const float s1, const float s2, const float s3) {
  float s = 0.5*(s1+s2+s3);
  float area = sqrt(s*(s-s1)*(s-s2)*(s-s3));
  return area;
}

/*******************************************************************************/
/*                                                                             */
/* main()                                                                      */
/*                                                                             */

int main(const int argc, const char* const argv[]) {

  /* Cartesian coordinates */
  
  float x1;
  float y1;
  float x2;
  float y2;
  float x3;
  float y3;

  /* Process inputs */
  x1 = atoi(argv[1]);
  y1 = atoi(argv[2]);
  x2 = atoi(argv[3]);
  y2 = atoi(argv[4]);
  x3 = atoi(argv[5]);
  y3 = atoi(argv[6]);

  /* Compute lengths s1, s2, and s3 */
  float s12 = distance(x1,y1,x2,y2);
  float s23 = distance(x2,y2,x3,y3);
  float s13 = distance(x1,y1,x3,y3);

  /* Compute area per problem description */
  float area = triangleArea(s12, s23, s13);

  /* Output area */
  outputMessage(x1,y1,x2,y2,x3,y3,area);

  return 0;
}
