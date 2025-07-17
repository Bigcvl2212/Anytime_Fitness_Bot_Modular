# Business Policies: Late Payment and Waiver

## Late Payment Policy
- A late payment fee of $19.50 is applied to every biweekly payment that is missed.
- To calculate total late fees: `late_fees = floor(amountPastDue / recurringCost.total) * 19.50`
- If a member is behind by 2 or more payments (i.e., missed_payments >= 2), include a note:
  - “You must respond within 7 days or your account will be sent to collections. If you pay today in full, we can offer a one-time late fee waiver.”
- If a member receives a late fee waiver, add them to a “late fee waived” list and do not allow another waiver for 1 year.

## Implementation Notes
- The `late_fee_waived` status is tracked in the master contact list as a date (or blank if not waived).
- All invoice calculations and notes are included in the master contact list for audit and review. 