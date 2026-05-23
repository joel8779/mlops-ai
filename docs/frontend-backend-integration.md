# Frontend/Backend Integration - PHASE 16

**Date**: 2026-05-23
**Phase**: STEP 7 - FRONTEND/BACKEND INTEGRATION

## Frontend Structure

### Next.js Application
**Location**: `apps/web/`
**Framework**: Next.js 15
**UI Library**: React 18, TailwindCSS
**State Management**: React hooks

### Available Pages
- `/` - Dashboard
- `/sign-in` - Authentication
- `/candidates` - Candidate management
- `/resumes` - Resume upload
- `/jobs` - Job descriptions
- `/search` - Semantic search
- `/copilot` - AI copilot
- `/analytics` - Executive analytics

## Integration Points

### 1. Auth Flows
**Frontend**: `/sign-in`
**Backend**: `/api/v1/auth/*`

**Required Integration**:
- Register form → POST /api/v1/auth/register
- Login form → POST /api/v1/auth/login
- Token refresh → POST /api/v1/auth/refresh
- Token storage (localStorage/httpOnly cookie)
- Protected route guards
- Token propagation to API calls

**Status**: ⚠️ Needs Implementation

### 2. Recruiter Dashboard
**Frontend**: `/`
**Backend**: `/api/v1/analytics/executive`

**Required Integration**:
- Fetch executive dashboard data
- Display hiring funnel
- Display top skills
- Display recruiter efficiency
- Display ranking accuracy

**Status**: ⚠️ Needs Implementation

### 3. Candidate Tables
**Frontend**: `/candidates`
**Backend**: `/api/v1/resumes/*`, `/api/v1/matching/*`

**Required Integration**:
- List candidates
- Upload resume
- View candidate details
- Bookmark candidates
- Add notes
- Update stage

**Status**: ⚠️ Needs Implementation

### 4. Semantic Search UI
**Frontend**: `/search`
**Backend**: `/api/v1/search/candidates`

**Required Integration**:
- Search input
- Skill filters
- Location filter
- Results display
- Pagination
- Score visualization

**Status**: ⚠️ Needs Implementation

### 5. Copilot UI
**Frontend**: `/copilot`
**Backend**: `/api/v1/ai/copilot`, `/api/v1/ai/copilot-2`

**Required Integration**:
- Chat interface
- Message history
- Citations display
- Artifact rendering
- Confidence visualization

**Status**: ⚠️ Needs Implementation

### 6. Analytics UI
**Frontend**: `/analytics`
**Backend**: `/api/v1/analytics/executive`

**Required Integration**:
- Dashboard visualization
- Charts and graphs
- Time series data
- Funnel visualization
- Skill trends

**Status**: ⚠️ Needs Implementation

## CORS Configuration

### Backend CORS
**File**: `app/main.py`
**Current Config**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Default Origins**: `["http://localhost:3000"]`

**Status**: ✅ Configured

### Frontend API Client
**Required**:
- Base URL configuration
- Token injection
- Error handling
- Request/response interceptors

**Status**: ⚠️ Needs Implementation

## Token Propagation

### Required Implementation
1. Store access token after login
2. Store refresh token
3. Inject Bearer token in API calls
4. Handle token expiry
5. Auto-refresh tokens
6. Clear tokens on logout

**Status**: ⚠️ Needs Implementation

## Loading States

### Required Implementation
1. Global loading indicator
2. Per-component loading states
3. Skeleton screens
4. Optimistic updates
5. Error boundaries

**Status**: ⚠️ Needs Implementation

## Error Handling

### Required Implementation
1. Global error handler
2. API error parsing
3. User-friendly error messages
4. Retry logic
5. Error logging

**Status**: ⚠️ Needs Implementation

## Integration Checklist

### Authentication
- [ ] Login form implementation
- [ ] Register form implementation
- [ ] Token storage
- [ ] Token refresh logic
- [ ] Protected route guards
- [ ] Logout functionality

### API Client
- [ ] Base URL configuration
- [ ] Token injection
- [ ] Request interceptors
- [ ] Response interceptors
- [ ] Error handling
- [ ] Retry logic

### Dashboard
- [ ] Fetch executive data
- [ ] Display hiring funnel
- [ ] Display top skills
- [ ] Display efficiency metrics
- [ ] Display accuracy metrics

### Candidates
- [ ] List candidates
- [ ] Upload resume
- [ ] View candidate details
- [ ] Bookmark functionality
- [ ] Add notes
- [ ] Update stage

### Search
- [ ] Search input
- [ ] Skill filters
- [ ] Location filter
- [ ] Results display
- [ ] Pagination
- [ ] Score visualization

### Copilot
- [ ] Chat interface
- [ ] Message history
- [ ] Citations display
- [ ] Artifact rendering
- [ ] Confidence visualization

### Analytics
- [ ] Dashboard visualization
- [ ] Charts and graphs
- [ ] Time series data
- [ ] Funnel visualization
- [ ] Skill trends

## Environment Variables

### Frontend
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend
```
backend_cors_origins=http://localhost:3000
```

## Status

**Backend API**: ✅ Complete
**Frontend Pages**: ⚠️ Skeleton exists
**Integration**: ⚠️ Needs Implementation
**CORS**: ✅ Configured
**Auth**: ⚠️ Needs Implementation

## Recommendations

1. **API Client**: Create a centralized API client with token management
2. **State Management**: Consider using Zustand or React Query for state
3. **Error Handling**: Implement global error boundary and error handler
4. **Loading States**: Use React Query for automatic loading states
5. **Type Safety**: Ensure TypeScript types match backend schemas
6. **Testing**: Add integration tests for critical flows

## Next Steps

To complete frontend/backend integration:
1. Implement authentication flow
2. Create API client with token management
3. Implement dashboard data fetching
4. Implement candidate management UI
5. Implement semantic search UI
6. Implement copilot chat interface
7. Implement analytics visualization
8. Test all integration points

The backend is complete and ready for frontend integration. The frontend has page skeletons but needs full implementation of API integration, authentication, and state management.
