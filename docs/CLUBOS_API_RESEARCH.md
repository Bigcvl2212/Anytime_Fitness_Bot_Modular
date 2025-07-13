# ClubOS API Research & Development Plan

## Executive Summary

Based on comprehensive research of the Gym-Bot codebase and ClubOS system, I've identified multiple API endpoints and authentication methods that can be leveraged to replace Selenium automation with direct API calls. This document outlines the research findings and provides a detailed development plan.

## Current State Analysis

### 1. ClubOS Web Interface Structure
- **Base URL**: `https://anytime.club-os.com`
- **Key Endpoints Identified**:
  - `/action/Login/view` - Authentication
  - `/action/Dashboard/view` - Main dashboard
  - `/action/Calendar` - Calendar management
  - `/action/Dashboard/messages` - Messaging system
  - `/action/Dashboard/PersonalTraining` - Training management

### 2. ClubHub API Integration (Already Implemented)
- **Base URL**: `https://clubhub-ios-api.anytimefitness.com`
- **Authentication**: Bearer token + session cookies
- **Endpoints Available**:
  - `/api/v1.0/clubs/1156/members` - Member data
  - `/api/v1.0/clubs/1156/prospects` - Prospect data
  - `/api/members/{member_id}/agreement` - Billing details

### 3. Authentication Methods Discovered

#### ClubHub API Authentication
```python
# Current implementation in constants.py
CLUBHUB_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "API-version": "1",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Cookie": "incap_ses_132_434694=...; dtCookie=..."
}
```

#### ClubOS Web Authentication
- Session-based authentication via cookies
- Form-based login with CSRF tokens
- Access token pattern: `eyJhbGciOiJIUzI1NiJ9...`

## API Endpoints Identified

### 1. ClubHub API (Mobile App Backend)
**Status**: ✅ Already implemented and working
- **Members**: `GET /api/v1.0/clubs/1156/members`
- **Prospects**: `GET /api/v1.0/clubs/1156/prospects`
- **Agreements**: `GET /api/members/{member_id}/agreement`
- **Authentication**: Bearer token + session cookies

### 2. ClubOS Web API (Potential)
**Status**: 🔍 Research needed
- **Calendar**: `GET /action/Calendar` (AJAX endpoints likely)
- **Messages**: `GET /action/Dashboard/messages`
- **Training**: `GET /action/Dashboard/PersonalTraining`
- **Authentication**: Session cookies + CSRF tokens

### 3. ClubOS API Discovery
**Status**: 🚧 Development needed
Based on web interface analysis, potential REST endpoints:
- `/api/calendar/sessions`
- `/api/members/search`
- `/api/messages/send`
- `/api/training/sessions`

## Development Plan

### Phase 1: ClubOS Web API Discovery (Week 1-2)

#### 1.1 Network Traffic Analysis
- **Tool**: Charles Proxy + Selenium DevTools
- **Goal**: Capture all AJAX requests during ClubOS operations
- **Focus Areas**:
  - Calendar session creation/management
  - Member search and lookup
  - Message sending
  - Training session management

#### 1.2 API Endpoint Mapping
```python
# Target endpoints to discover
CLUBOS_API_ENDPOINTS = {
    "calendar": {
        "sessions": "/api/calendar/sessions",
        "create": "/api/calendar/sessions/create",
        "update": "/api/calendar/sessions/{id}/update",
        "delete": "/api/calendar/sessions/{id}/delete"
    },
    "members": {
        "search": "/api/members/search",
        "details": "/api/members/{id}",
        "agreements": "/api/members/{id}/agreements"
    },
    "messages": {
        "send": "/api/messages/send",
        "history": "/api/messages/history",
        "templates": "/api/messages/templates"
    },
    "training": {
        "sessions": "/api/training/sessions",
        "clients": "/api/training/clients",
        "packages": "/api/training/packages"
    }
}
```

#### 1.3 Authentication Research
- **Session Management**: Analyze cookie patterns
- **CSRF Protection**: Identify token requirements
- **Rate Limiting**: Understand API constraints

### Phase 2: ClubOS API Client Development (Week 3-4)

#### 2.1 Authentication Service
```python
class ClubOSAPIAuthentication:
    """Handles ClubOS web API authentication"""
    
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.access_token = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate with ClubOS web interface"""
        # Implementation based on discovered patterns
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-CSRF-Token": self.csrf_token,
            "Cookie": self.session.cookies.get_dict()
        }
```

#### 2.2 API Client Service
```python
class ClubOSAPIClient:
    """ClubOS web API client"""
    
    def __init__(self, auth_service: ClubOSAPIAuthentication):
        self.auth = auth_service
        self.base_url = "https://anytime.club-os.com"
    
    def get_calendar_sessions(self, date: str) -> List[Dict]:
        """Get calendar sessions for a date"""
        # Implementation
    
    def create_calendar_session(self, session_data: Dict) -> bool:
        """Create a new calendar session"""
        # Implementation
    
    def search_members(self, query: str) -> List[Dict]:
        """Search members by name/email"""
        # Implementation
    
    def send_message(self, member_id: str, message: str) -> bool:
        """Send message to member"""
        # Implementation
```

### Phase 3: Integration & Migration (Week 5-6)

#### 3.1 Hybrid API Service
```python
class EnhancedGymBotAPIService:
    """Combines ClubHub and ClubOS APIs"""
    
    def __init__(self):
        self.clubhub_api = EnhancedClubHubAPIService()
        self.clubos_api = ClubOSAPIClient()
    
    def get_comprehensive_member_data(self, member_name: str) -> Dict:
        """Get member data from both APIs"""
        # Combine ClubHub member data with ClubOS billing data
    
    def create_training_session(self, session_data: Dict) -> bool:
        """Create training session via ClubOS API"""
        # Use ClubOS calendar API instead of Selenium
    
    def send_payment_reminder(self, member_id: str, amount: float) -> bool:
        """Send payment reminder via ClubOS messaging"""
        # Use ClubOS messaging API instead of Selenium
```

#### 3.2 Migration Strategy
1. **Parallel Implementation**: Run API and Selenium versions simultaneously
2. **Feature-by-Feature**: Migrate one workflow at a time
3. **Fallback Mechanism**: Keep Selenium as backup for critical operations
4. **Performance Monitoring**: Compare response times and reliability

### Phase 4: Advanced Features (Week 7-8)

#### 4.1 Real-time Data Sync
- **WebSocket Integration**: Real-time calendar updates
- **Event-driven Architecture**: Automatic notifications
- **Data Consistency**: Sync between ClubHub and ClubOS

#### 4.2 Advanced Analytics
- **API Metrics**: Response times, success rates
- **Usage Analytics**: Most used endpoints
- **Error Tracking**: Comprehensive error handling

## Implementation Priority

### High Priority (Replace Selenium)
1. **Calendar Management**: Session creation/updates
2. **Member Search**: Quick member lookups
3. **Message Sending**: Payment reminders
4. **Training Management**: Session scheduling

### Medium Priority (Enhance Functionality)
1. **Real-time Updates**: WebSocket integration
2. **Batch Operations**: Bulk member updates
3. **Advanced Search**: Filtering and sorting
4. **Data Export**: Automated reporting

### Low Priority (Nice to Have)
1. **Mobile App Integration**: Direct ClubHub app API
2. **Third-party Integrations**: Payment processors
3. **Advanced Analytics**: Business intelligence
4. **Multi-location Support**: Scale to multiple clubs

## Technical Requirements

### Development Environment
- **Charles Proxy**: Network traffic analysis
- **Selenium DevTools**: Browser network monitoring
- **Postman/Insomnia**: API testing
- **Python Requests**: HTTP client library

### Security Considerations
- **Token Management**: Secure storage and rotation
- **Rate Limiting**: Respect API constraints
- **Error Handling**: Graceful degradation
- **Logging**: Comprehensive audit trail

### Performance Optimization
- **Connection Pooling**: Reuse HTTP connections
- **Caching**: Cache frequently accessed data
- **Async Operations**: Non-blocking API calls
- **Batch Processing**: Reduce API calls

## Success Metrics

### Performance Improvements
- **Response Time**: 90% reduction in operation time
- **Reliability**: 99.9% success rate
- **Scalability**: Handle 10x more operations
- **Maintenance**: 80% reduction in maintenance overhead

### Business Impact
- **Automation Efficiency**: 24/7 operation capability
- **Error Reduction**: 95% fewer manual errors
- **Cost Savings**: 70% reduction in manual work
- **User Experience**: Faster response times

## Next Steps

### Immediate Actions (This Week)
1. **Set up Charles Proxy**: Configure for ClubOS traffic capture
2. **Create API Discovery Script**: Automated endpoint detection
3. **Document Current Selenium Workflows**: Map all operations
4. **Establish Testing Environment**: Isolated development setup

### Week 1 Deliverables
1. **API Endpoint Map**: Complete list of discovered endpoints
2. **Authentication Flow**: Documented login process
3. **Proof of Concept**: Basic API client implementation
4. **Migration Plan**: Detailed feature-by-feature migration

### Week 2 Deliverables
1. **Core API Client**: Functional ClubOS API client
2. **Integration Tests**: Verify API functionality
3. **Performance Benchmarks**: Compare with Selenium
4. **Security Review**: Token management and security

## Conclusion

The research reveals significant opportunities to replace Selenium automation with direct API calls. The combination of ClubHub API (already working) and ClubOS web API (to be discovered) provides a comprehensive solution for all Gym-Bot operations.

The phased approach ensures minimal disruption while maximizing performance improvements. The hybrid architecture allows for gradual migration while maintaining system reliability.

**Estimated Timeline**: 8 weeks for complete implementation
**Expected ROI**: 90% performance improvement, 70% cost reduction
**Risk Level**: Low (with proper fallback mechanisms) 