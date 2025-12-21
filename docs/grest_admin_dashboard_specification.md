# GREST Admin Dashboard - Complete Specification

## Overview
Create an admin dashboard for GREST (refurbished phone e-commerce chatbot) with four tabs: Analytics, Conversations, Monitoring, and Shopify Sync. This dashboard should follow the same authentication and UI patterns as the JoveHeal admin dashboard.

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    GREST Admin Dashboard                     │
│  (Next.js 14 + TypeScript + Tailwind CSS)                   │
├───────────┬───────────┬──────────────┬─────────────────────┤
│ Analytics │ Convers.  │  Monitoring  │   Shopify Sync      │
└───────────┴───────────┴──────────────┴─────────────────────┘
                              │
                              ▼
                    Flask Backend (Port 8080)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         PostgreSQL      Shopify API     UptimeRobot
         (Products,      (Source of      (Health
          Sessions,       truth)          monitoring)
          Sync Logs)
```

---

## Tab 1: Analytics

### Features
- Total conversations count
- Unique sessions count
- Message volume over time (line chart)
- Filter by date range: Last 24h, Last 7 days, Last 30 days
- Top query intents breakdown (price queries, product info, comparison, etc.)

### API Endpoints
```
GET /api/admin/stats?range=7d
Response: {
  totalConversations: number,
  uniqueSessions: number,
  avgMessagesPerSession: number,
  dailyStats: [{ date: string, conversations: number, messages: number }],
  intentBreakdown: { priceQuery: number, productInfo: number, comparison: number, general: number }
}
```

---

## Tab 2: Conversations

### Features
- List of chat sessions with pagination
- Show: session ID, first message preview, message count, timestamp, channel
- Click to expand full conversation
- Filter by intent type (price, product, comparison)
- Search functionality

### API Endpoints
```
GET /api/admin/conversations?range=7d&page=1&limit=50
Response: {
  sessions: [{
    sessionId: string,
    firstMessage: string,
    messageCount: number,
    createdAt: string,
    channel: string
  }],
  total: number
}

GET /api/admin/conversations/:sessionId
Response: {
  sessionId: string,
  messages: [{
    role: "user" | "assistant",
    content: string,
    timestamp: string
  }]
}
```

---

## Tab 3: Monitoring

### Features
- Service health status cards (Website, API, Chatbot)
- UptimeRobot integration (reuse JoveHeal pattern)
- Sync service heartbeat indicator
- Last successful sync timestamp
- Alert if last sync > 8 hours ago

### API Endpoints
```
GET /api/admin/monitoring
Response: {
  services: [{
    name: string,
    status: "up" | "down" | "unknown",
    uptime: number,
    lastCheck: string
  }],
  syncHealth: {
    lastSuccessfulSync: string,
    hoursAgo: number,
    isHealthy: boolean
  }
}
```

---

## Tab 4: Shopify Sync (NEW - Most Important)

### Features

#### 4.1 Sync Status Card
- Current sync status: Idle / In Progress / Last run succeeded / Last run failed
- Last sync timestamp with "X hours ago" display
- Next scheduled sync time
- Products synced count

#### 4.2 Manual Sync Button
- "Sync Now" button to trigger manual sync
- Button disabled while sync in progress
- Shows spinner and progress during sync
- Confirmation dialog before running

#### 4.3 Sync Verification Panel
- Side-by-side comparison:
  - Shopify product count (from API)
  - Database product count (from PostgreSQL)
  - Match status: ✅ Matched / ⚠️ Mismatch (difference count)
- "Verify Now" button to refresh counts

#### 4.4 Sync History Table
- List of last 20 sync runs
- Columns: Date/Time, Trigger (Manual/Scheduled), Duration, Status, Products Updated, Actions
- Expandable row for error details if failed
- Export to CSV option

#### 4.5 Sync Details Timeline
- When a sync is clicked, show step-by-step timeline:
  1. Started fetch from Shopify
  2. Retrieved X products
  3. Comparing with database
  4. Updated X, Created Y, Deleted Z
  5. Verification passed/failed
  6. Completed

### Database Schema for Sync Logging

```sql
-- Table: sync_runs
CREATE TABLE sync_runs (
    id SERIAL PRIMARY KEY,
    trigger_source VARCHAR(20) NOT NULL, -- 'manual' | 'scheduled'
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'running', -- 'running' | 'success' | 'failed' | 'warning'
    products_created INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_deleted INTEGER DEFAULT 0,
    shopify_product_count INTEGER,
    db_product_count INTEGER,
    error_log TEXT,
    triggered_by VARCHAR(100) -- admin email or 'scheduler'
);

-- Table: sync_run_events (for detailed timeline)
CREATE TABLE sync_run_events (
    id SERIAL PRIMARY KEY,
    sync_run_id INTEGER REFERENCES sync_runs(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'fetch_start', 'fetch_complete', 'compare_start', 'update_complete', 'verify_complete'
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_sync_runs_started_at ON sync_runs(started_at DESC);
CREATE INDEX idx_sync_run_events_run_id ON sync_run_events(sync_run_id);
```

### API Endpoints for Sync

```
POST /api/admin/sync/run
Headers: X-Internal-Api-Key: <key>
Body: { triggeredBy: "admin@example.com" }
Response: { 
  syncRunId: number, 
  status: "started",
  message: "Sync initiated"
}

GET /api/admin/sync/status
Response: {
  isRunning: boolean,
  currentRunId: number | null,
  lastRun: {
    id: number,
    status: string,
    startedAt: string,
    finishedAt: string,
    productsUpdated: number
  }
}

GET /api/admin/sync/history?limit=20
Response: {
  runs: [{
    id: number,
    triggerSource: string,
    startedAt: string,
    finishedAt: string,
    status: string,
    productsCreated: number,
    productsUpdated: number,
    productsDeleted: number,
    duration: string,
    errorLog: string | null
  }]
}

GET /api/admin/sync/run/:runId/events
Response: {
  events: [{
    eventType: string,
    message: string,
    createdAt: string
  }]
}

GET /api/admin/sync/verification
Response: {
  shopifyCount: number,
  databaseCount: number,
  isMatched: boolean,
  difference: number,
  lastChecked: string
}
```

### Sync Script Integration

The existing sync script should be modified to:

1. **Create sync_run record at start:**
```python
def start_sync(trigger_source, triggered_by):
    with get_db_session() as db:
        run = SyncRun(
            trigger_source=trigger_source,
            triggered_by=triggered_by,
            status='running'
        )
        db.add(run)
        db.commit()
        return run.id
```

2. **Log events during sync:**
```python
def log_sync_event(run_id, event_type, message):
    with get_db_session() as db:
        event = SyncRunEvent(
            sync_run_id=run_id,
            event_type=event_type,
            message=message
        )
        db.add(event)
        db.commit()
```

3. **Update sync_run on completion:**
```python
def complete_sync(run_id, products_created, products_updated, products_deleted, 
                  shopify_count, db_count, status='success', error=None):
    with get_db_session() as db:
        run = db.query(SyncRun).filter(SyncRun.id == run_id).first()
        run.finished_at = datetime.utcnow()
        run.status = status
        run.products_created = products_created
        run.products_updated = products_updated
        run.products_deleted = products_deleted
        run.shopify_product_count = shopify_count
        run.db_product_count = db_count
        run.error_log = error
        db.commit()
```

4. **Verification routine:**
```python
def verify_sync():
    # Get Shopify count
    shopify_count = get_shopify_product_count()  # Call Shopify API
    
    # Get database count
    with get_db_session() as db:
        db_count = db.query(func.count(Product.id)).scalar()
    
    is_matched = abs(shopify_count - db_count) <= 2  # Allow ±2 tolerance
    
    return {
        'shopify_count': shopify_count,
        'db_count': db_count,
        'is_matched': is_matched,
        'difference': abs(shopify_count - db_count)
    }
```

### Auto-Sync Scheduling

The sync should run automatically every 6 hours. Implementation options:

**Option A: Python APScheduler (Recommended for Replit)**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=run_scheduled_sync,
    trigger='interval',
    hours=6,
    id='shopify_sync',
    name='Shopify Product Sync'
)
scheduler.start()
```

**Option B: Workflow-based cron**
Create a separate workflow that runs the sync script on schedule.

---

## Authentication

Use the same authentication pattern as JoveHeal:

1. **Admin Login Page** at `/admin/login`
   - Email/password authentication
   - Store session in cookie (`admin_token`)

2. **Authorization Check**
```typescript
async function isAuthorized(): Promise<boolean> {
  // Check admin_token cookie
  const cookieStore = await cookies();
  const adminToken = cookieStore.get('admin_token');
  if (adminToken?.value) {
    const decoded = Buffer.from(adminToken.value, 'base64').toString();
    const [email] = decoded.split(':');
    if (email.toLowerCase() === DASHBOARD_EMAIL.toLowerCase()) {
      return true;
    }
  }
  return false;
}
```

3. **Internal API Key** for Flask communication
   - All admin API calls include `X-Internal-Api-Key` header
   - Flask validates this key before processing

---

## Frontend Component Structure

```
src/app/admin/
├── login/
│   └── page.tsx              # Login page
├── dashboard/
│   └── page.tsx              # Main dashboard with tabs
└── components/
    ├── AnalyticsTab.tsx      # Analytics charts and stats
    ├── ConversationsTab.tsx  # Conversation list and viewer
    ├── MonitoringTab.tsx     # Health status cards
    ├── SyncTab.tsx           # Shopify sync interface
    ├── SyncStatusCard.tsx    # Current sync status
    ├── SyncHistoryTable.tsx  # Sync run history
    ├── SyncVerification.tsx  # Count comparison widget
    └── SyncTimeline.tsx      # Step-by-step sync events
```

---

## UI/UX Guidelines

### Theme
- Dark theme similar to JoveHeal dashboard
- Background: `#0f172a` (slate-900)
- Cards: `#1e293b` (slate-800)
- Accent: `#22d3ee` (cyan-400) for primary actions
- Success: `#22c55e` (green-500)
- Warning: `#eab308` (yellow-500)
- Error: `#ef4444` (red-500)

### Sync Tab Specific
- Use pulsing animation for "In Progress" status
- Show countdown timer for next scheduled sync
- Use toast notifications for sync completion
- Disable "Sync Now" button with tooltip when sync running

---

## Error Handling

1. **Sync Failures**
   - Capture full error in `sync_runs.error_log`
   - Show user-friendly error message in UI
   - Log detailed error for debugging

2. **Verification Mismatches**
   - If mismatch > 2 products, set status to 'warning'
   - Show warning banner in Sync tab
   - Include in monitoring health check

3. **API Timeouts**
   - Shopify API calls should have 30-second timeout
   - Retry logic: 3 attempts with exponential backoff
   - If all retries fail, mark sync as failed

---

## Environment Variables Required

```
# Database
DATABASE_URL=postgresql://...

# Shopify
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxx

# Admin Auth
DASHBOARD_EMAIL=admin@example.com
DASHBOARD_PASSWORD=secure_password
INTERNAL_API_KEY=random_secure_key

# Monitoring (optional)
UPTIMEROBOT_API_KEY=ur_xxxxx
```

---

## Implementation Checklist

### Backend (Flask)
- [ ] Create `sync_runs` and `sync_run_events` database tables
- [ ] Add SQLAlchemy models for sync tables
- [ ] Implement `/api/admin/stats` endpoint
- [ ] Implement `/api/admin/conversations` endpoints
- [ ] Implement `/api/admin/monitoring` endpoint
- [ ] Implement `/api/admin/sync/run` endpoint (triggers sync)
- [ ] Implement `/api/admin/sync/status` endpoint
- [ ] Implement `/api/admin/sync/history` endpoint
- [ ] Implement `/api/admin/sync/verification` endpoint
- [ ] Modify existing sync script to log to sync_runs table
- [ ] Add APScheduler for 6-hour auto-sync
- [ ] Add sync verification routine

### Frontend (Next.js)
- [ ] Create admin login page
- [ ] Create dashboard layout with 4 tabs
- [ ] Implement AnalyticsTab component
- [ ] Implement ConversationsTab component
- [ ] Implement MonitoringTab component
- [ ] Implement SyncTab component with all sub-components
- [ ] Add polling for sync status updates
- [ ] Add toast notifications
- [ ] Style with dark theme

### Testing
- [ ] Test manual sync trigger
- [ ] Test sync verification
- [ ] Test sync history display
- [ ] Test error handling (simulate Shopify API failure)
- [ ] Test auto-sync scheduling
- [ ] Verify admin authentication works

---

## Reference: JoveHeal Dashboard Files

For implementation reference, examine these files from JoveHeal:
- `src/app/admin/dashboard/page.tsx` - Main dashboard structure
- `src/app/api/admin/stats/route.ts` - Stats API pattern
- `src/app/api/admin/conversations/route.ts` - Conversations API pattern
- `webhook_server.py` - Flask admin endpoints pattern

---

## Notes

1. **Do NOT include Transcription tab** - GREST doesn't need audio/video transcription
2. **Focus on Sync reliability** - This is the most critical feature for GREST
3. **Shopify API rate limits** - Be mindful of Shopify's 40 requests/second limit
4. **Idempotency** - Ensure sync can be safely re-run without duplicating products
