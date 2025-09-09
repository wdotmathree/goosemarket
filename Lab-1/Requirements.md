# Lab 1 Requirements

If you are reading this it means you have succesfully set yopur upstream and
should have access to a number of additional files and subdirectories.

In the directory Triangles-C you will see four files.  The README.md describes
the setup.  You will need to install the Gnu C compiler.  There are various ways
to do this but in this case rather than provide directions you are asked to seek
out methods to do so yourself.  Given the prior setup of WSL or MacPorts,
something along the lines of

	  `apt install gcc`

or
	  `sudo port install gcc`

is likely the correct thing to do.

After compiling the triangle code, you should run the driver.py testcase driver.
The testcases are defined in testCaseInputs.txt and are briefly described in the
README.

Given that the code has defects in it (one testcase does not currently pass
because of one of the defects) you are required to

1. Create an issue because of a defect in the code.
2. Create a branch for resolving the issue.  The branch name should follow the
Gitlab naming convention of `issue-#<issueNumber>-description`
3. Solving the defects, including creating a testcase for the defect that does
not currently have a testcase for it.
4. Add the code to your git repo.
5. Commit your code, with a commit message that includes `(#<issueNumber>`
6. Push your code.
7. Do a merge request which will then be assessed by the SE101 instruction team
