# To-Do Application

We would like to create a To-Do application.  At a fairly high level, this
application is intended to keep track of things we have to do, when we started
the item (based on when we added it to the To-Do list), when it is due, what it
is, what type of thing it is, and when it was done (assuming it is done).  An
task in the To-Do list would then be a tuple

     (item, type, started, due, done)

Item is string that is the item to be done.  Some examples of items are:
"Math 115 Assignment 3", "Buy groceries", "Phone Home", *etc*. Each item string
should be unique.

Type is likewise a string, but it will categorize things.  In the case of the
above examples, they might be "Schoolwork", "Shopping", and "Personal",
respectively.

The remaining three elements of the tuple are Python datetime values.

You should create an issue to start the work on this To-Do application, and
create a brach for that work.  
You should create a subdirectory in Lab-2 called "To-Do" within which you will
develop code and pytest code for the following functions for this To-Do
application:

	add(task): item within task must be unique
	update(task): item within task must exist
	delete(task): item within task must exist
	next(): returns the next task based on the due dates of tasks
	today(): returns an array of tasks due today
	tomorrow(): returns an array of tasks due tomorrow

Create approrpiate test cases for these six functions.  You should create issues
for each these functions (six in total), with branches for those issues, but do
so as branches of the branch where this To-Do application is being developed,
not as branches off of main.  As you complete those functions, merge the
branches back to you application branch, and then issue a Merge Request for the
To-Do application.

	
