# Product Steering

## What we're building
HealthTracker: a calorie, water, weight, and activity tracker for individuals — a modern,
voice-first, highly polished web app.

## Priorities, in order
1. **Extremely user friendly.** Every flow should take the fewest taps/words possible.
   Voice logging is the primary input method, not a bolt-on feature.
2. **Exotic, delightful UI.** Not a generic CRUD dashboard — animated, considered, feels
   crafted. Mobile-first (most logging happens on a phone).
3. **Correctness of health data.** Calorie/macro estimates and logs must be traceable —
   store the raw model output alongside the parsed structured result.
4. **Analytics dashboard** (trends, macro breakdown) comes after solo tracking is solid.

## Core user flow (voice-first)
1. User taps one big mic button (any time of day).
2. User speaks freely about their day: meals eaten, water drunk, activity, weight,
   in any order, in natural language.
3. App transcribes + extracts structured entries (meal/water/weight/activity, each with
   its own fields) and shows them as an editable confirmation card before saving.
4. User taps confirm (or edits a field) and everything routes to the right tables.
5. Manual entry (typing/tapping) remains available for every log type as a fallback.

## Users
- Individual trying to track calories/water/weight with minimal daily effort.

## Non-goals (for now)
- Native mobile app (web app, mobile-responsive/PWA is enough).
- Wearable integrations.
- Meal recommendation engine (future enhancement, stays future for now).
