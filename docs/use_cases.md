# GooseMarket Use Cases


## Student Use Cases

⸻

Use Case: Sign Up

Actor: Student
Goal: Create account using @uwaterloo.ca email
Preconditions: User not already registered

Main Flow:
	1.	Student opens Sign-Up page
	2.	System prompts for @uwaterloo.ca email
	3.	Student submits registration form
	4.	System validates email domain
	5.	System sends verification link

Postconditions: Account created, pending verification
Exceptions: Invalid email domain → registration denied

⸻

Use Case: Verify Email

Actor: Student
Goal: Confirm account ownership
Preconditions: Verification email sent

Main Flow:
	1.	Student opens verification email
	2.	Student clicks verification link
	3.	System validates token
	4.	System activates account

Postconditions: Account verified
Exceptions: Expired or invalid link → resend verification

⸻

Use Case: Secure Login

Actor: Student
Goal: Access GooseMarket securely
Preconditions: Account verified

Main Flow:
	1.	Student enters credentials
	2.	System authenticates
	3.	System logs student in

Postconditions: Session active
Exceptions: Invalid credentials → show error

⸻

Use Case: Receive Login Bonus

Actor: Student
Goal: Earn Goose Dollars for logging in
Preconditions: Successful login

Main Flow:
	1.	System checks last login time
	2.	System awards bonus if eligible
	3.	System updates balance

Postconditions: Balance increased
Exceptions: Already rewarded today → no bonus

⸻

Use Case: Earn Participation Rewards

Actor: Student
Goal: Earn Goose Dollars from platform participation
Preconditions: Account active

Main Flow:
	1.	Student performs platform activities
	2.	System tracks participation
	3.	System grants reward when threshold met

Postconditions: Additional Goose Dollars awarded
Exceptions: Suspicious activity → reward withheld

⸻

Use Case: Browse Events

Actor: Student
Goal: View open prediction events
Preconditions: Logged in

Main Flow:
	1.	Student opens events page
	2.	System displays open events

Postconditions: Events visible
Exceptions: No events → show placeholder

⸻

Use Case: Filter Events

Actor: Student
Goal: Find events by category or name
Preconditions: Events available

Main Flow:
	1.	Student selects filters
	2.	System refines event list

Postconditions: Relevant events shown
Exceptions: No matches → show “no results”

⸻

Use Case: View Event Details

Actor: Student
Goal: Review an event before predicting
Preconditions: Event selected

Main Flow:
	1.	System loads event details
	2.	System shows description, odds, activity

Postconditions: Student informed
Exceptions: Event unavailable → error

⸻

Use Case: Create Prediction Event

Actor: Student
Goal: Create new prediction event
Preconditions: Logged in

Main Flow:
	1.	Student opens “Create Event”
	2.	Student enters title, options, details
	3.	System validates submission
	4.	System forwards event to admin review

Postconditions: Event pending approval
Exceptions: Invalid data → show error

⸻

Use Case: Buy/Sell Shares

Actor: Student
Goal: Participate in the prediction market
Preconditions: Event open; adequate balance

Main Flow:
	1.	Student selects option
	2.	Student enters purchase amount
	3.	System processes trade
	4.	System updates holdings and balance

Postconditions: Position updated
Exceptions: Insufficient balance → denied

⸻

Use Case: View Positions

Actor: Student
Goal: Track current market positions
Preconditions: Student has trades

Main Flow:
	1.	Student opens portfolio
	2.	System displays positions and metrics

Postconditions: Holdings visible
Exceptions: No positions → empty state

⸻

Use Case: Quick Access to Event from Position

Actor: Student
Goal: Navigate to an event from portfolio
Preconditions: Active positions exist

Main Flow:
	1.	Student clicks a position
	2.	System opens event details

Postconditions: Event page loaded
Exceptions: Event resolved → show notice

⸻

Use Case: View Profile

Actor: Student
Goal: See account stats and history
Preconditions: Logged in

Main Flow:
	1.	Student opens profile
	2.	System loads stats, balance, history

Postconditions: Profile displayed
Exceptions: Data error → retry

⸻

Use Case: View Leaderboard

Actor: Student
Goal: Compare performance to peers
Preconditions: Leaderboard data exists

Main Flow:
	1.	Student opens leaderboard
	2.	System ranks users
	3.	System displays ranking

Postconditions: Leaderboard visible
Exceptions: No data → placeholder

⸻

Use Case: Login Streak Bonuses

Actor: Student
Goal: Earn streak-based rewards
Preconditions: Logged in

Main Flow:
	1.	System tracks consecutive login days
	2.	System calculates streak bonus
	3.	System updates balance

Postconditions: Bonus awarded
Exceptions: Streak broken → reset

⸻

## Admin / Moderator Use Cases

⸻

Use Case: Moderator Login

Actor: Moderator
Goal: Access admin tools securely
Preconditions: Moderator account exists

Main Flow:
	1.	Moderator enters credentials
	2.	System authenticates
	3.	System loads dashboard

Postconditions: Access granted
Exceptions: Invalid credentials → denied

⸻

Use Case: Approve or Reject Events

Actor: Moderator
Goal: Control which student events go live
Preconditions: Event submitted

Main Flow:
	1.	Moderator views pending list
	2.	Moderator reviews event
	3.	Moderator approves or rejects
	4.	System updates status

Postconditions: Event published or denied
Exceptions: Missing info → request edits

⸻

Use Case: Edit Events Before Approval

Actor: Moderator
Goal: Fix unclear/inappropriate details
Preconditions: Event pending review

Main Flow:
	1.	Moderator edits title/description
	2.	System saves changes
	3.	Moderator finalizes approval

Postconditions: Event updated
Exceptions: Invalid edit → show error

⸻

Use Case: Resolve Event Outcomes

Actor: Moderator
Goal: Finalize results and trigger payouts
Preconditions: Event concluded

Main Flow:
	1.	Moderator reviews evidence
	2.	Moderator selects correct outcome
	3.	System processes payouts

Postconditions: Winners paid
Exceptions: Unclear result → delay

⸻

## System-Level Use Case

⸻

Use Case: Maintain Security and Fairness

Actor: Platform
Goal: Protect data and ensure fair play
Preconditions: System operational

Main Flow:
	1.	System enforces authentication
	2.	System prevents abuse
	3.	System monitors suspicious activity
	4.	System processes payouts accurately

Postconditions: Platform integrity maintained
Exceptions: Security breach → trigger response