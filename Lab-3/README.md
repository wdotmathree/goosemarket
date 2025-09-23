# Lab 3 Requirements

In Lab 3 we will define the initial requirements for the To-Do application, and
learn some very basic MySQL so as to provide a persistent storage solution for
the To-Do data.

If you can see this, it means you have successfully fetched the upstream, merged
it with your main and (possibly) pushed to your repo on git.uwaterloo.ca.  If
you can see this and someone near you looks confused, show them how to fetch
this in their own repo.

You will find in your repo a Lab-3 directory which contains this README and two
subdirectories, MySQLSamples and To-Do-App.  The MySQLSamples directory contains
a few examples of the use of MySQL, both Command-Line Interface (CLI) examples
(ending in .sql) and Python examples.  The To-DO-App directory contains three
subdirectories, src, tests, and docs, together with a README for what is
expected to be done for the To-Do application for Lab-3.

Before you can do any work with MySQL you will first need to install some
software to enable you to do this work.

1. Create a task issue with appropriate severity, priority, and description
(*e.g.*, setup MySQL).
2. The MySQL server is riku.shoshin.uwaterloo.ca and you will have received an
email telling you that you have an account on that server and how to change your
password there. To change the password you will need to use the Command-Line
Interface (CLI).  You can get this by installing the appropriate packages from
the [MySQL Downloads Page](https://dev.mysql.com/downloads/) or by "apt install"
or "port install" depending on whether you have a Mac or Windows machine.
3. To log into the MySQL you issue the command:

      `mysql -u <userid> -p -h riku.shoshin.uwaterloo.ca`

   where `<userid>` is your userid as sent to you in the email giving you the
   password for the account.  It will prompt you for the password (please note
   that there are special charaters in the password so if you have a non-ASCII
   email reader if may not give you the correct password; ask your email client
   to show you the raw email if you have problems with your password).
4. Some basic commands you will want to play with are:

   	`show databases;`
	
	`use SE101;`
	
	`show tables;`
	
	`select * from Grades;`
	
   which will show you the databases you have access to, select the SE101 (case
   sensitive) database for use, show the tables in the SE101 database (there is
   only one), and show you the contents of the Grades table in the SE101
   database.  You only have read permission on the SE101 database.
   The commands are contained in the `cmds.sql` file in the MySQLSamples
   subdirectory. You can execute them all at once by using the command:

   `source MySQLSamples/cmds.sql`

   assuming you are in the Lab-3 directory.
5. You have your own dedicated database with the name `se101_<userid>` where
   `<userid>` is your userid.  You can create tables in that database.  You
   should select this database for use with the

   	  `use se101_<userid>;`

   command.
6. Create a table Foo with two columns, A and B, where A is a 10-character string and
   the B should be an integer, as follows:

   `CREATE TABLE Foo(A CHAR(10), B INT);`

7. Show that there is no data in the Foo table:

   `SELECT * FROM Foo;`

8. Insert some data into Foo:

   `INSERT INTO Foo Values ("Fred", 23),("George", 14);`

9. Select the data from Foo to satisfy yourself that you have inserted the data
   into the Foo table.

10. Update the integer for George to 47:

    `UPDATE Foo SET B = 47 where A = "George";`

11.Select the data from Foo to satisfy yourself that you have updated the data
   in the Foo table.

12. You should look at the gpa1.py and gpa3.py code and run it to satisfy
    yourself that you can connect to the database using python.

When you have completed this, you are ready to move on to README.md in the
To-Do-App directory.
