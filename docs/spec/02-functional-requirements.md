# 2. Functional Requirements

## 2.1 Match List

- Display upcoming football matches.
- Each match shows:
  - home team vs away team
  - kickoff date/time label
  - three selectable odds buttons: `1`, `X`, `2`
- Selecting a new odds button replaces the previous selection.
- User clicks on odds to select outcome for betting
- Clicking new odds replaces previous selection

## 2.2 Bet Slip

- Right-side fixed bet slip.
- Shows one active selection at a time.
- Shows entered stake, available balance, and computed potential payout.
- Includes:
  - `Place Bet`
  - `Remove All`
  - per-selection remove (`x`)

## 2.3 Place Bet Interaction

- On submit, button enters loading state (`Placing...`).
- After submit, the UI must show an in-progress state and resolve to one final outcome
  (success or failure).
- On success:
  - stake is deducted
  - success receipt modal appears
- On failure:
  - error modal appears with retry option

## 2.4 Success Receipt

Receipt must show:

- Bet ID
- Match details
- Selection
- Stake
- Odds at placement
- Potential payout
- Placement timestamp

Closing receipt returns user to main flow without active selection.

## 2.5 Error Modal

- Modal title: `Something went wrong`.
- Modal body explains that the bet could not be processed and suggests trying again.
- Actions:
  - `Rebet` (primary): on click it closes the modal and retries placement.
  - `Close` (secondary): closes modal and clears current selection/stake.
  - top-right `X`: same behavior as `Close`.

## 2.6 Filters

- Date filter supports single day or date range (inclusive).
- Odds filter supports min/max range (inclusive) and must reject invalid ranges with clear
  feedback.
