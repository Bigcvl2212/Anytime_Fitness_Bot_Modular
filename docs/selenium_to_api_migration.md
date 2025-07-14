# Selenium to API Migration Documentation

## Overview
This document tracks the migration of all Selenium-based automation features to direct API calls using the ClubOS API and ClubHub API endpoints.

## Current Selenium Workflows Analysis

### 1. ClubOS Messaging (`services/clubos/messaging.py`)

#### Selenium Functions:
- **`send_clubos_message(driver, member_name, subject, body)`**
  - Purpose: Send SMS or email messages to members through ClubOS interface
  - Selenium Actions:
    - Navigate to ClubOS dashboard
    - Search for member by name
    - Open member profile
    - Click "Send Message" button
    - Choose between text/email tabs
    - Fill message content and notes
    - Submit form
  - Fallback Logic: Automatically switches from SMS to email if SMS fails
  - Character Limit: 300 chars for SMS, unlimited for email

- **`get_last_message_sender(driver)`**
  - Purpose: Get the name of the member from the most recent message thread
  - Selenium Actions:
    - Navigate to ClubOS messages page
    - Find first message item in list
    - Extract member name from username link
  - Returns: Member name string

#### API Migration Status:
- ❌ **NOT MIGRATED** - No API equivalent discovered yet
- 🔍 **DISCOVERY NEEDED** - Need to analyze ClubOS messaging endpoints

### 2. Authentication (`core/driver.py`)

#### Selenium Functions:
- **`setup_driver_and_login()`**
  - Purpose: Initialize Chrome WebDriver and login to ClubOS
  - Selenium Actions:
    - Setup Chrome options (anti-detection, proxy, etc.)
    - Navigate to ClubOS login page
    - Fill username and password fields
    - Submit login form
    - Wait for dashboard to load
  - Returns: Authenticated WebDriver instance

- **`login_to_clubos(driver)`**
  - Purpose: Login to ClubOS using existing WebDriver
  - Similar actions to above but uses existing driver

#### API Migration Status:
- ✅ **PARTIALLY MIGRATED** - ClubOS API client exists (`services/api/clubos_api_client.py`)
- 🔧 **NEEDS ENHANCEMENT** - ClubOS API authentication needs completion

### 3. Calendar Operations

#### Selenium Functions (Referenced in network analyzer):
- Calendar session management
- Training session scheduling
- Appointment booking

#### API Migration Status:
- ✅ **PARTIALLY MIGRATED** - ClubOS API client has calendar methods
- 🔧 **NEEDS TESTING** - Calendar API endpoints need validation

### 4. Member Data Operations

#### Current Functionality:
- Member search and profile access
- Agreement management
- Balance checking via ClubHub API

#### API Migration Status:
- ✅ **MIGRATED** - ClubHub API service handles member data
- ✅ **MIGRATED** - Member search via ClubHub API
- 🔧 **NEEDS INTEGRATION** - Connect ClubOS member operations to API

## Existing API Infrastructure

### 1. ClubOS API Client (`services/api/clubos_api_client.py`)
- **Authentication**: Session-based with CSRF tokens
- **Endpoints**: Calendar, members, messages, training
- **Features**: Endpoint discovery, fallback to form submission
- **Status**: Partially implemented, needs completion

### 2. ClubHub API Service (`services/data/clubhub_api.py`)
- **Authentication**: Bearer token with session cookies
- **Endpoints**: Members, prospects, historical data
- **Features**: Pagination, error handling, token refresh
- **Status**: Fully functional

### 3. Token Management (`services/authentication/clubhub_token_capture.py`)
- **Functionality**: Automated token extraction via Charles Proxy
- **Features**: Token validation, secure storage, scheduled refresh
- **Status**: Fully functional

### 4. Network Analyzer (`services/api/network_analyzer.py`)
- **Functionality**: Discover API endpoints via traffic analysis
- **Features**: Pattern recognition, authentication analysis
- **Status**: Ready for endpoint discovery

## Migration Plan

### Phase 1: Discovery and Documentation ✅
- [x] Analyze existing Selenium workflows
- [x] Document current API infrastructure
- [x] Identify migration gaps

### Phase 2: API Endpoint Discovery 🔄
- [ ] Use network analyzer to discover ClubOS messaging APIs
- [ ] Map all ClubOS form submissions to API calls
- [ ] Document authentication requirements for each endpoint
- [ ] Test discovered endpoints with existing token system

### Phase 3: API Enhancement 🔄
- [ ] Complete ClubOS API client implementation
- [ ] Add missing messaging endpoints
- [ ] Implement member search and profile APIs
- [ ] Add calendar and training session APIs

### Phase 4: Migration Implementation 🔄
- [ ] Create API-based messaging service
- [ ] Replace Selenium authentication with API client
- [ ] Migrate calendar operations to API calls
- [ ] Update workflows to use API functions

### Phase 5: Testing and Validation 🔄
- [ ] Test API functions against Selenium equivalents
- [ ] Validate message delivery and formatting
- [ ] Ensure member data accuracy
- [ ] Performance testing and optimization

### Phase 6: Documentation and Deployment 🔄
- [ ] Document all discovered API endpoints
- [ ] Create migration guide for future developers
- [ ] Update workflow configurations
- [ ] Deploy API-based system

## API Endpoint Discovery Results

### ClubOS Messaging Endpoints (To be discovered)
```
Base URL: https://anytime.club-os.com

Potential Endpoints:
- POST /api/messages/send
- GET /api/messages/history
- GET /api/members/search
- GET /api/members/{id}/profile
- POST /api/calendar/sessions
```

### Authentication Requirements
- Session cookies from login
- CSRF tokens for form submissions
- Bearer tokens for API calls (if available)

## Testing Strategy

### Side-by-Side Comparison
1. Run Selenium workflow
2. Run API equivalent
3. Compare results:
   - Message delivery status
   - Member data accuracy
   - Response times
   - Error handling

### Test Scenarios
- Send SMS to member with valid phone
- Send email to member without phone
- Handle member opt-out scenarios
- Process overdue payment notifications
- Search for members by various criteria

## Known Limitations

### Operations That May Not Be Migratable
1. **UI-dependent workflows**: Operations that rely on visual elements
2. **Complex form interactions**: Multi-step wizards without API equivalents
3. **File upload workflows**: If no API endpoint for file uploads
4. **Reporting interfaces**: PDF generation through UI only

### Fallback Strategy
- Keep Selenium implementations as backup
- Use hybrid approach where needed
- Clear documentation of limitations

## Progress Tracking

### Completed
- ✅ Initial analysis and planning
- ✅ Existing API infrastructure review
- ✅ Selenium workflow documentation

### In Progress
- 🔄 API endpoint discovery
- 🔄 ClubOS API client enhancement

### Pending
- ❌ Messaging API implementation
- ❌ Complete migration testing
- ❌ Performance optimization
- ❌ Final documentation

## Notes

### Security Considerations
- Ensure API keys and tokens are securely managed
- Use existing token capture system for authentication
- Implement proper rate limiting for API calls

### Performance Benefits
- Faster execution (no browser overhead)
- More reliable (less prone to UI changes)
- Better error handling and logging
- Reduced resource usage

### Maintenance Benefits
- Single source of truth for data operations
- Easier testing and debugging
- Better integration with other systems
- Reduced dependency on UI stability