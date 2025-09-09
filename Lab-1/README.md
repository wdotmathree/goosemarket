# Lab 1 Requirements


Lab 1 is setting up the environment for SE101, learning a little bit about
python and testing, and doing some basic git work.

### Step 1:

Install git and python on your machine.  How you do this will likely be machine
dependent.  For Windows machines, you should probably set up WSL (Windows
Subsystem for Linux) via the command:

	  wsl --install

This will allow you to run an ubuntu terminal where you can do the standard
Linux things.  In particular, you will want to do:

      sudo apt update && sudo apt upgrade -y	

though this may be best left for later as it may take some time to run.  To
install python and pip, execute the commands:

	sudo apt install python3 python3-pip -y
	sudo apt install git -y

On a Mac you will want to install MacPorts from macports.org.  In a
terminal you can then execute the commands

	 sudo port selfupdate

though as with the WSL system, you are better to leave this to later.  To
install python and pip, execute the commands:

	sudo port install python313 py313-pip
	sudo port install git -y

A somewhat more detailed version of these instructions is available from
[Grok](https://grok.com/share/c2hhcmQtMg%3D%3D_8f0cd6ef-6f65-4c69-a6ac-7e8acd378292)
and you are advised to continue the conversation with Grok, or use ChatGPT,
Claude, Copilot, ..., if you are needincg additional information.  You may also
wish to consult with a TA.

### Step 2:

Log in to [Git](https://git.uwaterloo.ca/) where you should see that you are now
a member of the Labs project.  More specifically, a project has been created
called `userid` where `userid` is your UW userID and also your git userid,
within the group `SE101-Fall2025/Labs for which you have Maintainer access.
However, there is very little in that project currently.  Specifically, all you
should see is this README.md file.  You will need to set the upstream for that
project and then pull the current version of that.  When you have achieved that
you will find additional files that will tell you what else you need to do for
Lab 1.

To set the upstream, you need to do the following:

1. (Optional) Set up git ssh credentials so that you do not need to give you
   password for every usage.
2. Create an issue, type task, with appropriate severity and priority, and a
   suitable description.
3. clone the project that has been created for you:

   	 `git clone https://git.uwaterloo.ca/se101-fall2025/students/<userid>.git`

   where `<userid>` is your git/uw userid.
4. Connect your repository to the SE 101 labs upstream:

   	  `git remote add upstream https://git.uwaterloo.ca/se101-fall2025/labs.git`
5. Fetch the remote repository:

   	 `git fetch upstream`
	 
6. Whenever you need to get an up-to-date version of the labs repo, do an upstream
   merge:	    

          git merge upstream/main
	  
7. Update your remote GitLab repository with the new content by pushing all of
   your code changes for this: 	

   	  git push origin main

