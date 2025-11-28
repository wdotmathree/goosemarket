## Domain model for GooseApp

### Entities
- User
  - Email
  - Username
  - Password
  - Balance
  - Streak
  - Admin?
  - Active?
  - Last Bonus
- Poll
  - Title
  - Description
  - Creator
  - Creation date
  - End date
  - Public?
  - Outcome
- Trade
  - User
  - Poll
  - Number of shares
  - Share price
  - Outcome
- Tag
  - Name

### Relationships
- Users create polls
- Users participate in polls by making trades
- Users follow tags
- Polls have tags
