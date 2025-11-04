# GooseMarket Backlog

---

## Story: User sign in
- Create database 
- Create login/signup pages
- Implement authentication
- Create account schema in database

---

## Story: Create a poll
- Add poll schema to database
- API for creating poll
- Frontend for creating poll

---

## Story: View events
- Homepage to view all events
- Sort events by tag
- View individual event pages

---

## Story: Buying and selling event shares
- Database schema for storing trades/shares
- UI for buying and selling shares on event pages
- API for buying and selling
- Automatic market making system for handling prices

---

## Story: View your own current positions
- UI for viewing positions (click to access event page to trade)
- API call for looking at all open positions

---

## Story: View user pages
- UI for displaying user pages with trades and statistics
- API call for getting the user information and trades

---

## Story: Conclude events
- UX for when an event concludes
- API for handling payouts and concluding event

---

## Story: Subscribe to tags
- UI for subscribing to tags
- API for subscribing to tags
- Subscribed tags viewing page

---

## Story: View leaderboard
- Sort users by current balance
- Page to display the top X users by balance, PNL

---

## Story: Login bonus
- UI for displaying a login bonus for user login streaks
- API for handling user login bonuses

---

# END OF MVP

---

## Story: Moderator approval for events
- Implement moderator accounts and login
- Require moderator approval for making events (through API)
- Admin panel for approving/editing events

---

## Story: Email verification (Missing from MVP)
- Add email verification token system
- Send verification email on signup
- Verification endpoint to validate token
- UI flow for "verify your email"
- Restrict access until verified

---

## Story: Fake currency earnings (non-login tasks)
- Logic for earning Goose Dollars (login streak, predictions, activity)
- Anti-abuse / bot detection rules
- Database table for tracking currency rewards
- Notification UI for earned Goose Dollars

---

## Story: Security protections
- Implement SQL injection prevention
- XSS filtering & sanitization
- Rate limiting (login, event creation, trading)
- Error logging and security alerts

---

## Story: Help & onboarding guide
- Create help page explaining prediction system
- Add examples of events, payouts, and trading
- Add FAQ for rules, ethics, campus guidelines
- Onboarding tutorial for new users

---

## Story: Dispute resolution
- Admin interface to review event disputes
- API endpoint to file disputes
- UI allowing users to request review of resolved event
- Admin tools to reverse payouts if needed

---

## Story: Group / Faculty support (e.g. SE, MATH, ENG)
- Ability to join groups
- Group-based event filtering
- Group leaderboard display
- API for group membership & stats

---

## Story: Abuse / Cheating Prevention
- Spam protection for event creation
- Duplicate account mitigation (email / device checks)
- Reporting system for suspicious events/users
- Admin tools to flag & restrict accounts

---
