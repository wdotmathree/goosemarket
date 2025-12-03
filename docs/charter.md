# GooseMarket Project Charter

## Title
**GooseMarket: UWaterloo Campus Prediction Market Platform**

---

## Description (Concise Overview)
GooseMarket is a prediction market web platform for University of Waterloo students, using a fake currency called *Goose Dollars*. Students create and predict outcomes on real campus-related events (e.g., midterm averages, election results) and compete via a leaderboard. No real money is involved — users earn currency through platform activity such as logging in and participation.

---

## Objectives and Goals
- Deliver an engaging and competitive student prediction platform
- Allow users to create, predict, and resolve events tied to campus life
- Provide group/Faculty-based communities (e.g., SE, Math, Eng groups)
- Encourage friendly competition through leaderboards and stats
- Offer a safe, secure, and policy-compliant web experience

---

## Scope

### In Scope
- Web app for account creation & fake balance system
- uWaterloo-only email signup & verification
- Create & predict Yes/No campus-related events
- Sorting & categories/groups for event discovery
- Leaderboards, stats, user progression/rewards
- Event resolution (automatic or admin-based)
- Admin panel for moderation
- Security: safe authentication, XSS/SQLi protections
- Backend API + database for users, events, predictions, groups

### Out of Scope
- Real money or cryptocurrency integration
- Multi-outcome events (>2 outcomes)
- Native mobile apps (web-only experience)

---

## Stakeholders
- **Sponsors:** Student-run team & course/project stakeholders
- **Users:** UWaterloo students
- **Developers:** GooseMarket team
- **Admins:** Selected moderators with event approval rights

---

## Assumptions
- All users have a valid `@uwaterloo.ca` email
- Platform will operate for entertainment and academic/club purposes only
- Students are motivated by friendly competition and leaderboard status
- Adequate campus event data exists for meaningful predictions

---

## Constraints
- No real-world financial value or gambling connections
- Must follow UWaterloo policy and ethical guidelines
- Limited moderation and development resources
- Web-only product (desktop + mobile browser)

---

## High-Level Risks
- **User Abuse / Cheating:** Manipulating outcomes or spam events  
- **Security Issues:** Bot accounts, SQLi, XSS, unauthorized access  
- **Scalability:** High traffic during peak campus events  
- **Ethical Concerns:** Misinterpretation as gambling platform  
- **Moderation Load:** Limited admin resources  

---

## Roles & Responsibilities

### Moosa
- Frontend (User & admin panels)
- Authentication & email verification

### William
- DB security & SQLi/XSS prevention
- Rollback logic for bets
- Moderation/admin tooling

### Cole
- Leaderboard logic
- Token economy modeling

### Adam
- Event management (create, predict, resolve)
- Groups/tags system

### Bryan
- User analytics
- Token economy balancing

---

## Deliverables

### Frontend Web App
- Login / Signup
- Dashboard with current events
- Event creation & prediction interface
- Groups/Categories page
- Leaderboard

### Backend API
- Auth + email verification
- Event creation, predictions, resolution logic
- Admin moderation tools
- User stats & token tracking

### Database
- Users
- Events
- Predictions
- Groups

---

## Success Criteria
- Only `@uwaterloo.ca` users can sign up
- Users can:
  - Create accounts
  - Earn/spend Goose Dollars
  - Create and predict events
  - View leaderboards & stats
- Admins can approve/resolve events and handle disputes
- Token balances update correctly for bets and payouts
- Platform meets basic security protections
- A simple user guide/help section exists

---

## Authority & Sign-Off
This project charter is agreed upon by the GooseMarket development team.  
All major scope changes require team discussion and approval.

**Sign-Off:**  
✔ GooseMarket Team  
✔ Course Instructor 
