# Revenue Display Restructuring TODO

## ✅ COMPLETED TASKS

### 1. Dashboard Changes
- [x] Move monthly revenue display from members page to dashboard
- [x] Add revenue card to dashboard showing total monthly revenue
- [x] Ensure dashboard shows comprehensive revenue overview

### 2. Members Page Changes  
- [x] Remove monthly revenue display from members page
- [x] Add membership-specific revenue card
- [x] Add membership-specific past due card
- [x] Filter revenue calculations to only include membership data

### 3. Training Clients Page Changes
- [x] Add training-specific revenue card
- [x] Add training-specific past due card
- [x] Calculate revenue from training packages/agreements only
- [x] Calculate past due from training agreements only

### 4. Backend API Changes
- [x] Create separate revenue calculation methods:
  - [x] `get_membership_revenue()` - for members page
  - [x] `get_training_revenue()` - for training clients page  
  - [x] `get_total_monthly_revenue()` - for dashboard
- [x] Create separate past due calculation methods:
  - [x] `get_membership_past_due()` - for members page
  - [x] `get_training_past_due()` - for training clients page

### 5. Frontend Template Changes
- [x] Update dashboard.html to include revenue card
- [x] Update members.html to show membership-specific cards
- [x] Update training_clients.html to add revenue/past due cards
- [x] Ensure consistent card styling across all pages

## 🎯 IMPLEMENTATION SUMMARY

### Dashboard
- Shows **total monthly revenue** (members + training)
- Displays comprehensive revenue overview
- Uses `/api/members/monthly-revenue` endpoint

### Members Page
- Shows **membership revenue only** (excludes training)
- Shows **membership past due only**
- Uses `/api/members/membership-revenue` endpoint
- Updated card labels to "Membership Revenue"

### Training Clients Page
- Shows **training revenue only** (excludes memberships)
- Shows **training past due only**
- Uses `/api/training/training-revenue` endpoint
- Added new revenue and past due cards

## ✅ ALL TASKS COMPLETED

The revenue display has been successfully restructured:
- Dashboard shows total revenue overview
- Members page shows membership-specific revenue
- Training clients page shows training-specific revenue
- All calculations are properly separated
- API endpoints are created and functional
