#!/usr/bin/env python3
################################################################################
#
# GPA1
# Get the course grades and weights for a specific student
# Compute the GPA for that student
# Print the GPA
#
# Revision history:
#  7 Oct 2024; PASW; Initial version
#  9 Oct 2024; PASW; Comment the code; add /usr/bin/env startup
# 14 Oct 2024; PASW; Decompose functions; add command-line parsing

# There are various ways to connect to MySQL with Python.  This code uses

import pymysql

# Alternate method with be shown elsewhere
# import pymysql

# For getting command-line arguments, and prompting for a password
import getpass
import argparse

################################################################################
#
# Parse command-line arguments using Python argparse
#
# Optional arguments are as follows:
#
# -h: prints usage
#
# -u <username>: username on MySQL database
# -H <hostname>: hostname of MySQL server
# -d <database>: name of MySQL database
# -p [password]: if present with a password, that password is used
#                if present without a password, a password prompt will be used
# -s <studentID>: studentID for which the query is being done
#
# Default values are passed to the function and used if any flag is omitted.
#

# Helper class for parsing

class OptionalPassword(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # If no value is provided, set the password to True (flag-like behavior)
        if values is None:
            setattr(namespace, self.dest, True)
        else:
            setattr(namespace, self.dest, values)

# parse function

def parseInput(defaultHost, defaultDatabase, defaultUser, defaultPassword,defaultID):    
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Parse command-line arguments.")

    # Add the arguments for hostname, database, and username
    parser.add_argument('-H', '--hostname', default=defaultHost, help="Hostname")
    parser.add_argument('-d', '--database', default=defaultDatabase, help="Database")
    parser.add_argument('-u', '--username', default=defaultUser, help="Username")
    parser.add_argument('-s', '--studentID', default=defaultID, help="StudentID")
    
    # Add the password argument which may or may not take a parameter
    parser.add_argument('-p', '--password', nargs='?', action=OptionalPassword, help="Password (optional)")
    
    # Parse the arguments
    args = parser.parse_args()

    # Prompt if -p with no parameter
    # Set to default if no -p
    if args.password is None:
        args.password = defaultPassword
    elif args.password is True:
        args.password = getpass.getpass(
            prompt=f"Enter MySQL password for user '{args.username}' on host '{args.hostname}': ")

    return args

################################################################################
#
# connect2DB connects to the database server with passed parameters
#

def connect2DB(args):
    try:
        # Establishing the connection
        connection = pymysql.connect(
            host     = args.hostname,
            user     = args.username,
            database = args.database,
            password = args.password)
        
        return connection

    except pymysql.Error as err:
        print(f"Error: {err}")
        return None

################################################################################
#
# queryDatabase() executes the query and returns the cursor with the results
#

def queryDatabase(connection, studentID):
    try:
        cursor = connection.cursor()

        query = f"SELECT grade, weight FROM Grades WHERE studentID = '{studentID}'"
        
        cursor.execute(query)
        return cursor
        
    except pymysql.connector.Error as err:
        print(f"Query Error: {err}")
        return None
         
################################################################################
#
# computeGPA() uses the cursor to get get the rows of results and post-process
# them.  In this case, the post-processing is computing the GPA, which really
# should be done in the database server.  That query will be shown in a future
# python script.
#

def computeGPA(cursor):
    try:
        results = cursor.fetchall()
        
        total_points = 0
        total_weight = 0
        
        # GPA is weighted sum of grades divided by total weight
        for grade, weight in results:
            total_points += grade * weight
            total_weight += weight

        # Calculate GPA
        if total_weight > 0:
            gpa = total_points / total_weight
            return gpa
        else:
            return None

    except pymysql.connector.Error as err:
        print(f"Query Error: {err}")
    finally:
        cursor.close()

################################################################################
#

def main():
    args = parseInput("riku.shoshin.uwaterloo.ca","SE101","pasward","",12345678);
   
    connection = connect2DB(args)

    if connection:
        cursor = queryDatabase(connection, args.studentID)
        if cursor is not None:
            gpa = computeGPA(cursor);
            if gpa is None:
                print(f"Student ID: {args.studentID} has no recorded grades")
            else:
                print(f"Student ID: {args.studentID}: GPA: {gpa:.2f}")

        connection.close()
    else:
        print("Unable to connect to database")
        exit(-1)
        
if __name__ == "__main__":
    main()
