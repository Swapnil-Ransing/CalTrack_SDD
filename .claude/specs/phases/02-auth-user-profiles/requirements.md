# Phase 02 — Requirements: Auth & User Profiles

## Context
HealthTracker is single-user-per-account: each person signs up once, logs in, and every
later log (meals, water, weight, activity) belongs to their account. This phase adds that
account layer and the one-time health-metrics profile that later phases (calorie calc,
analytics) will read. No logging features exist yet — this phase only makes accounts work.

## User stories

### 1. Sign up
As a new user, I want to create an account with my email, a password, and my basic health
metrics, so the app can personalize calorie/macro math later and I can start logging.

- Given I'm on the signup form, when I submit a valid email, a password meeting the
  strength rule, a matching confirmation, and all required profile fields, then a new
  account is created, my password is stored hashed (never plaintext), and I'm signed in
  immediately.
- Given I submit an email that's already registered, when I submit the form, then I see a
  clear error ("An account with this email already exists.") and no duplicate row is
  created.
- Given I submit a password under 8 characters, or a password/confirmation mismatch, or
  leave a required profile field empty, when I submit the form, then I see a specific
  validation error per field and no account is created.
- Given I submit an email in an invalid format, when I submit the form, then I see a
  validation error and no account is created.

### 2. Profile fields captured at signup
As a user, I want to provide the metrics the app needs to personalize my tracking, in one
short form, so I don't have to fill out a separate step later.

- Fields: date of birth, biological sex (male / female / other), height (cm), current
  weight (kg), activity level (sedentary / light / moderate / active / very active), goal
  (lose weight / maintain weight / gain weight).
- Given I select "other" for sex, when later phases compute BMR/calorie targets, then the
  app must not crash — exact formula choice for "other" is deferred to the phase that
  builds calorie calculation (open question noted in design.md).

### 3. Log in
As a returning user, I want to log in with my email and password, so I can access my data.

- Given I enter the correct email and password, when I submit the login form, then I'm
  signed in and taken to the home page.
- Given I enter a wrong password or an unregistered email, when I submit the login form,
  then I see one generic error ("Invalid email or password.") that does not reveal which
  field was wrong.
- Given I leave either field empty, when I submit the login form, then I see a validation
  error and no login attempt is made against the database.

### 4. Stay logged in across a browser refresh
As a user, I want my session to survive a page refresh or closing/reopening the tab, so I
don't have to log in every time I open the app.

- Given I'm logged in, when I refresh the browser or reopen the app in the same browser
  within the session lifetime, then I remain logged in without re-entering credentials.
- Given my session has expired (past its lifetime) or the signing secret has changed, when
  I load the app, then I'm treated as logged out and shown the login/signup screen.

### 5. Log out
As a user, I want to log out, so my session doesn't stay active on a shared device.

- Given I'm logged in, when I click "Log out", then my session is cleared (both server-side
  state and the persisted session token) and I'm returned to the login/signup screen.

### 6. Auth gate on every page
As a user, I should not be able to reach any logged-in-only page or feature without a valid
session.

- Given I'm not logged in, when I try to load any page other than the login/signup screen
  (directly via URL or sidebar), then I'm redirected to the login/signup screen.
- Given I'm logged in, when I load the app, then I see the home page, not the login form.

### 7. View and edit my profile
As a user, I want to view and update my health metrics after signup, so I can correct
mistakes or reflect changes (e.g. new weight, changed activity level, changed goal).

- Given I'm logged in and open the Profile page, when the page loads, then I see my current
  profile values pre-filled.
- Given I change one or more fields and save, when the update succeeds, then the new values
  are persisted and I see a confirmation.
- Given I submit an invalid value (e.g. empty height), when I save, then I see a validation
  error and the previous values are unchanged in the database.
- Given I try to change my email to one already used by another account, when I save, then
  I see an error and no change is made.

## Explicit non-goals for this phase
- Email verification / confirmation emails (no email-sending service wired up yet).
- Password reset / "forgot password" flow.
- Social login (Google/etc.).
- Multi-factor auth.
- Account deletion.
- Any nutrition/water/weight/activity logging (later phases).
