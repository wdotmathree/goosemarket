# To-Do Requirements

For the To-Do application we wish to more formally start to define the
requirements, together with working toward having a persistent storage solution.

For this initial set of requirements you must create user stories for the
`add()`, `update()`, and `next()` functions, with the assumption that there is a
MySQL database where data will be stored for the application, both as data is
added, and reloaded when the application is restarted.  The user stories should
be written in `user_stories.md` in the docs directory.

You should then create use cases based on the user stories and document them in
`docs/use_cases.md`.

Finally, you should implement the `add()`, `update()`, and `next()` functions
with the MySQL backend.  In doing this implementation you are expected to:

1. Create an issue and branch for the application as a whole, with all
   appropriate descriptors and labels.

2. Create an issue and branch for the individual functions, where these are
   branches of the branch you created for this application.  

3. Create tests cases for your functions.

4. Create a merge request and approve that request, with comments as necessary,
   for you code and tests.  Likely you need to implement `add()` first amd then
   the other two functions after `add()` is meregd into the ToDo branch.

5. Create a merge request when you have completed all of this work, assigning it
   to `d3feng` to review.

To enable effective grading, we require the following:

1. The database table should be called `ToDoData` and have the columns:

   `item     varchar(255)`
   
   `type     varchar(255)`
   
   `started  datetime`
   
   `due	     datetime`

   `done     datetime`

2. The main python code should be called `todo.py`.
