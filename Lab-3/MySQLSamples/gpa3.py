#!/usr/bin/env python3
################################################################################
#
# GPA3PyMySQL
# Compute the GPA either for a specific student, using a single SQL statement,
# or for all students in the Grades table in the SE101 database
# Print the GPA(s), if any.
# This version used the PyMySQL module rather than the older mysql.connector.
# It is worth noting the performance difference, since it is otherwise identical
# to gpa3.py
#
# Revision history:
# 16 Oct 2024; PASW; Initial version
#

# Optional debugging statements can be printed

DEBUG = False;

# There are various ways to connect to MySQL with Python.  This code uses
import pymysql

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

def parseInput(defaultHost, defaultDatabase, defaultUser, defaultPassword):    
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Parse command-line arguments.")

    # Add the arguments for hostname, database, and username
    parser.add_argument('-H', '--hostname', default=defaultHost, help="Hostname")
    parser.add_argument('-d', '--database', default=defaultDatabase, help="Database")
    parser.add_argument('-u', '--username', default=defaultUser, help="Username")
    parser.add_argument('-s', '--studentID', help="StudentID")
    
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
# queryDatabase() executes the query and returns the cursor with the results.
# This version of the query computes the GPA for the student at the database
# server rather than have the slow python code compute it.
#

def queryDatabase(connection, studentID):
    try:
        cursor = connection.cursor()

        query = "SELECT studentID, sum(grade * weight)/sum(weight) as GPA "
        query += "FROM Grades "
        if studentID is not None:
            query += f"WHERE studentID = '{studentID}'; "
        else:
            query += "GROUP BY studentID;"

        if DEBUG:
            print(f"Query: {query}")
        
        cursor.execute(query)
        return cursor
        
    except pymysql.Error as err:
        print(f"Query Error: {err}")
        return None
         
################################################################################
#
# computeGPA() uses the cursor to get get the rows of results and post-process
# them.  In this case, the result should be a single value, the GPA for the
# given student, and we are fetching it.
#

def computeGPA(cursor, studentID):
    try:
        results = cursor.fetchall()
        if DEBUG:
            print(f"Results: {results}")
        return results

    except pymysql.Error as err:
        print(f"Query Error: {err}")
    finally:
        cursor.close()

################################################################################
#

def main():
    args = parseInput("riku.shoshin.uwaterloo.ca","SE101","pasward","");
   
    connection = connect2DB(args)

    if connection:
        cursor = queryDatabase(connection, args.studentID)
        if cursor is not None:
            results = computeGPA(cursor, args.studentID);
            for id, gpa in results:
                if args.studentID is not None and gpa is None:
                    print(f"Student ID: {args.studentID} has no recorded grades")
                else:
                    print(f"Student ID: {id}: GPA: {gpa:.2f}")

        connection.close()
    else:
        print("Unable to connect to database")
        exit(-1)
        
if __name__ == "__main__":
    main()
