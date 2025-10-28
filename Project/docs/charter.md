# GooseMarket

## Scope
GooseMarket is a prediction market platform (using fake currency) designed for University of Waterloo students. It allows users to create, predict, and resolve events on real campus-related events — from midterm averages to student elections.

Instead of using cryptocurrencies like other similar sites, we will create our own custom Goose Dollars that are not backed by real money. Users will have the ability to receive more Goose Dollars by consistently logging in, and other tasks. A leaderboard will be displayed with the users with the highest balances (as well as other fun stats like highest losses). Users will be able to join groups (e.g. SE30) to receive more tailored predictions.

In scope:

* Web app for account creation and fake balance management

* Accounts email verification, only allowing uWaterloo emails

* Ability to create and predict events on campus-related questions (Yes/No events)

* Sorting of events by category to show users relevant events

* Automatic or admin-based event resolution

* Leaderboard and stats system to encourage engagement

* Admin panel for site moderation and management

* Secure backend & frontend

Out of scope:

* Real currency or crypto integration

* Multi outcome events (more than two possible outcomes)

## Objective
GooseMarket's objective is to create a fun and competitive web application that allows users across UWaterloo to spend points on predictions about campus-related events, and compete with their friends for the top step of the leaderboard.

## Deliverables
* Frontend Web App
    * Login / Signup
    * Dashboard with current events
    * Event creation and prediction interface
    * Groups/Categories page
    * Leaderboard
* Backend API
    * User management & Authentication (email verification)
    * Event management (create, predict, resolve)
    * Prediction resolution logic (payouts)
    * Admin panel for moderation (e.g. approving events)
    * User statistic tracking (for leaderboard)
* Database
    * Users, events, predictions, groups

## Roles
* Moosa
    * Frontend (User & admin panels)
    * Authentication & email verification
* William
    * DB security
    * XSS and SQL injection prevention
    * Rolling back bets after event ends
    * Moderation/Admin panel
* Cole
    * Leaderboard
    * Token economy
* Adam
    * Managing events (creating, placing predictions, closing, resolving)
    * Groups / tags for events
* Bryan
    * User analytics
    * Balancing token economy