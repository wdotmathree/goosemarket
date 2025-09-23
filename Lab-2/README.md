# Lab 2 Requirements

In Lab 2 we will learn some basic Python together with one of the standard
Python test systems, pytest, learn a little bit about repo structure, practice
issues, branches, *etc.*, and start working on a To-Do application.

If you can see this, it means you have successfully fetched the upstream, merged
it with your main and (possibly) pushed to your repo on git.uwaterloo.ca.  If
you can see this and someone near you looks confused, show them how to fetch
this in their own repo.

You will find in your repo a Lab-2 directory which contains this,
Requirements.md, and two subdirectories: Triangle-Py and Foo.  Those directories
illustrate the use of the pytest system.  To use pytest, you will first need to
install pytest.  **Don't just install pytest**.  Remember: we want visibility
into work done and we need to record things that are done so we can look them up
later. 

1. Create a task issue with appropriate severity, priority, and description.
2. Install pytest.  Feel free to ask your favourite LLM how to do this if you do
not know how.
3. Given the way the subdirectories have been structured in Lab-2, there is a
simple way and a (mildly) more complex way to run pytest.  
4. You may notice that the tests for distance() in test_triangle.py only use one
quadrant of the Cartesian plane and only have integer inputs.  We would like to create two
additional tests, following the naming convention for these tests.  However, in
keeping with the visibility and branches for new code approach, open a bug
issue, with appropriate priority, severity, and description.  Create a branch
following the appropriate naming convention.  Add the code for these two
additional tests, verifying that it works.  Create a merge request, documenting
what you did in the MR.
5. Close the initial task issue, documenting what you needed to do to install
pytest and ensure it was working.  Also document the two methods to invoke
pytest. 

When you have completed this, you are ready to move on to Requirements.md
