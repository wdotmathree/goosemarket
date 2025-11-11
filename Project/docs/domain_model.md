## Domain model for GooseApp

### Entities
- User
  - Email
  - Password
  - Balance
  - Streak
- Poll
  - Title
  - Description
  - Creator
  - Creation date
  - End date
  - Public?
- Trade
  - User
  - Poll
  - Amount
- Tag
  - Name

### Relationships
- Users create polls
- Users participate in polls by making trades
- Users follow tags
- Polls have tags
