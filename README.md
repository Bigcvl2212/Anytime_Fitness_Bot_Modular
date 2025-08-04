# Gym Bot Automation System

## Production Invoice Processing Script

### Purpose
The `send_live_invoices_and_messages.py` script is designed to automatically process overdue gym memberships and generate Square invoices for past-due payments. This script:

- Reads member data from a CSV contact list
- Identifies members with overdue payments (past due amount > $0)
- Calculates late fees based on missed payments ($19.50 per missed payment)
- Creates and sends Square invoices directly to members via email
- Generates a comprehensive CSV report of all processed invoices

**Last Verified in Production**: ~2 weeks ago (Early January 2025)

### Quick Start - Production Run

To run the script in production mode:

```bash
SQUARE_ENVIRONMENT=production python send_live_invoices_and_messages.py
```

### Prerequisites

1. **Environment Setup**:
   - Ensure `SQUARE_ENVIRONMENT=production` is set
   - Verify all required secrets are available in Google Secret Manager
   - Confirm the master contact list CSV file exists and is up-to-date

2. **Required Secrets**:
   - `square-production-access-token`
   - `square-production-location-id`
   - `clubos-username`
   - `clubos-password`

3. **Data Dependencies**:
   - `master_contact_list_with_agreements_20250722_180712.csv` (or latest version)

### Safety Guidelines ⚠️

**CRITICAL - READ BEFORE RUNNING IN PRODUCTION:**

1. **Double-check recipient data**: Review the contact list CSV to ensure:
   - Email addresses are valid and current
   - Member information is accurate
   - No test/dummy data is included

2. **Environment verification**:
   ```bash
   # MUST set this before running
   export SQUARE_ENVIRONMENT=production
   ```
   
3. **Dry run recommendation**: Always test with a small subset first:
   - Temporarily modify the script to process only 1-2 test members
   - Verify invoices are created correctly in Square
   - Check that emails are sent to the correct recipients

4. **Exclusions**: The script automatically excludes:
   - Members with no overdue amount ($0 or less)
   - Members without valid email addresses
   - Connor Ratzke (already paid - hardcoded exclusion)

5. **Financial verification**:
   - Late fees are automatically calculated: $19.50 per missed payment
   - Total amount = Past due amount + (Number of missed payments × $19.50)
   - Review the generated CSV report before any follow-up actions

### Output Files

The script generates:
- `overdue_members_for_square_invoices_YYYYMMDD_HHMMSS.csv` - Complete processing report
- Console output with detailed status for each member processed

### Post-Execution Steps

1. **Review the output CSV** for any failed invoice creations
2. **Verify invoices in Square Dashboard** - check that all invoices were created successfully
3. **Monitor email delivery** - ensure members receive their invoice emails
4. **Follow up on failures** - manually address any members where invoice creation failed

### Troubleshooting

**Common Issues:**
- `SQUARE_ENVIRONMENT` not set to production → invoices go to sandbox
- Missing or expired Square credentials → invoice creation fails
- Invalid email addresses → automatic skip with logged warning
- Network connectivity issues → retry after checking internet connection

**Error Codes in CSV Output:**
- `PENDING` - Ready to process but not yet attempted
- `INVOICE_SENT` - Successfully created and sent
- `SQUARE_FAILED` - Square API returned error
- `SQUARE_ERROR` - Exception during Square API call

### Support

For issues with this script, check:
1. Google Secret Manager for credential status
2. Square Dashboard for invoice creation status
3. ClubOS system for member data accuracy
4. Console output and generated CSV for specific error details
