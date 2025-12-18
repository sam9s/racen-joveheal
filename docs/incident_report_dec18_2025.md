# Production Incident Report - December 18, 2025

## Incident Summary

| Field | Details |
|-------|---------|
| **Incident Date** | December 18, 2025 |
| **Duration** | ~3+ hours |
| **Severity** | Critical (Complete production outage) |
| **Affected Systems** | External production deployment (https://jove-heal-chatbot--sam9s.replit.app) |
| **Impact** | Client demo failed, all public-facing endpoints returned 404 |
| **Resolution Time** | 20:53 UTC |
| **Status** | RESOLVED |

---

## 1. Root Cause Analysis

### The Core Problem
The production deployment script (`start_production.sh`) was running Next.js as a **background process** using `&`, which caused the main shell process (PID 1) to exit immediately after spawning the services.

### WHY This Core Problem Occurred (The TRUE Root Cause)

**This is critical to understand:** The backgrounding bug was introduced by the AI Agent in an earlier session (commit `907d8a1` - "Improve application deployment and startup configurations") as part of a "fast cold start" optimization.

**Why it wasn't noticed earlier:**
1. The change was made to speed up startup by running Flask and Next.js in parallel
2. **Internal development environment continued to work** because Replit's workflow runner keeps background processes alive differently than Autoscale
3. **Production was still running the OLD deployment** - Autoscale doesn't automatically redeploy when code changes; it only redeploys when you explicitly publish
4. So the old (working) version continued serving traffic, masking the bug

**What triggered the failure:**
1. When you attempted to switch from Autoscale → Reserved VM → back to Autoscale
2. This forced Replit to **tear down the old deployment** and create a fresh one
3. The fresh deployment used the **new (broken) script** for the first time
4. That's when the 404s started

**In summary:** The bug was a latent defect introduced by the Agent. It was hidden because the old deployment kept running. The deployment type switch exposed the bug by forcing a fresh deployment.

### Why This Caused 404 Errors
Replit Autoscale monitors **PID 1** (the main process). When PID 1 exits:
1. Autoscale interprets this as "the app has finished running"
2. The container is torn down
3. The load balancer has no backend to route to
4. All requests return 404

### The Broken Code Pattern
```bash
# BROKEN: Shell spawns Next.js in background, then exits
npx next start -p "$APP_PORT" -H 0.0.0.0 &
NEXT_PID=$!
# ... shell script ends, PID 1 dies, container torn down
```

### The Fixed Code Pattern
```bash
# FIXED: Shell replaces itself with Next.js process (PID 1 stays alive)
exec npx next start -p "$APP_PORT" -H 0.0.0.0
```

### Why Internal Development Worked
The internal development environment uses Replit's **workflow system**, which:
- Manages processes differently than Autoscale
- Keeps services running via its own process supervision
- Is not affected by how the startup script handles backgrounding

---

## 2. Timeline of Events

| Time (Approx) | Event |
|---------------|-------|
| T-7 hours | App working correctly on Autoscale deployment |
| T-6 hours | User attempted to switch from Autoscale to Reserved VM |
| T-6 hours | User switched back to Autoscale |
| T-6 hours | Production started returning 404 on all endpoints |
| T-3 hours | Troubleshooting began |
| T-2 hours | Multiple attempts: removing [[ports]], updating script |
| T-1 hour | Identified root cause: background process issue |
| T-0 | Fixed start_production.sh with `exec` in foreground |
| T+5 min | Production confirmed working |

---

## 3. Why Previous Troubleshooting Attempts Failed

| Attempt | Why It Didn't Work |
|---------|-------------------|
| Removing `[[ports]]` sections | Autoscale **ignores** these entirely - they only affect development routing |
| Adding `[[ports]]` back | Same reason - irrelevant to Autoscale |
| Using `npx` instead of `node` path | Didn't change process lifecycle behavior |
| Multiple republishes | Republishing recreated the same broken state |
| Checking `.next` folder | The build existed and was valid |

**Key Insight**: The issue was never about port configuration or build artifacts - it was purely about **process lifecycle management**.

---

## 4. Prevention Plan

### Immediate Actions (Complete by Dec 19)
- [x] Fix start_production.sh to use `exec` for foreground process
- [ ] Set up UptimeRobot monitoring (see Section 6)
- [ ] Document Autoscale requirements in replit.md

### Ongoing Practices
1. **Never background the main service** in production startup scripts
2. **Always use `exec`** for the primary service to replace the shell process
3. **Test deployment changes in a staging environment first** (if possible)
4. **Check deployment logs immediately** after any publish

---

## 5. Monitoring Recommendations

### UptimeRobot Setup (Free Tier - 50 monitors, 5-min checks)

| Monitor | URL | Check Interval |
|---------|-----|----------------|
| Homepage | https://jove-heal-chatbot--sam9s.replit.app/ | 5 minutes |
| Health Endpoint | https://jove-heal-chatbot--sam9s.replit.app/health | 5 minutes |
| Widget.js | https://jove-heal-chatbot--sam9s.replit.app/widget.js | 5 minutes |

**Alert Configuration:**
- Email alerts: Immediate
- SMS alerts (optional): After 2 consecutive failures
- Alert contacts: sam27sep@gmail.com, shaveta@joveheal.com

### Internal Health Checks
Add to deployment verification:
```bash
# Post-deployment smoke test
curl -f https://jove-heal-chatbot--sam9s.replit.app/health || echo "ALERT: Health check failed!"
```

---

## 6. Disaster Recovery Plan

### If Production Goes Down Again

**Step 1: Verify the Issue (2 minutes)**
```bash
# Check if it's really down
curl -I https://jove-heal-chatbot--sam9s.replit.app/
curl -I https://jove-heal-chatbot--sam9s.replit.app/health
```

**Step 2: Check Internal Environment (1 minute)**
- Open Replit project
- Verify Frontend and Webhook Server workflows are running
- Test: `curl http://localhost:5000/` and `curl http://localhost:8080/health`

**Step 3: Check Deployment Logs (2 minutes)**
- Go to Publishing tab → Logs
- Look for error messages during startup
- Common issues: missing `.next` folder, Python errors, port binding failures

**Step 4: Quick Fix Options**

| If You See... | Do This |
|---------------|---------|
| Process exiting immediately | Check start_production.sh uses `exec` for main service |
| `.next` folder missing | Run `npx next build` locally, then republish |
| Python/Flask errors | Check webhook_server.py for import or startup errors |
| Port already in use | Wait 2 minutes, republish (previous instance may still be shutting down) |

**Step 5: Rollback Option**
- Use Replit Checkpoints to roll back to last known working state
- Look for commits with "Published your App" that had working production

**Step 6: Manual Republish**
- Make any necessary fixes
- Click Publish
- Wait 2-3 minutes for cold start
- Verify with health check

---

## 7. Pre-Deployment Checklist

Before making ANY deployment configuration changes:

### Code Verification
- [ ] Run `npx next build` locally - verify `.next` folder created
- [ ] Test `python webhook_server.py` starts without errors
- [ ] Verify both services respond on their ports locally

### Configuration Verification
- [ ] `start_production.sh` uses `exec` for the main foreground process
- [ ] `start_production.sh` uses `$PORT` or `${PORT:-5000}` for the app port
- [ ] `.replit` has correct `[deployment]` section with `deploymentTarget = "autoscale"`

### Post-Publish Verification
- [ ] Wait 2-3 minutes for cold start
- [ ] Check `/health` endpoint returns 200
- [ ] Check homepage loads correctly
- [ ] Test widget.js loads
- [ ] Test a chat message flows through

---

## 8. Safe Deployment Testing Protocol

### For Future Deployment Type Changes

**DO NOT** switch deployment types (Autoscale ↔ Reserved VM) without:

1. **Creating a checkpoint first** - Use Replit's checkpoint feature
2. **Documenting current working configuration** - Screenshot or copy .replit and start_production.sh
3. **Testing during low-traffic hours** - Not before client demos
4. **Having rollback plan ready** - Know exactly how to restore

### Recommended Testing Approach

1. **Fork the project** to a test environment
2. Make deployment changes in the fork
3. Verify the fork works correctly
4. Apply the same changes to production
5. Monitor for 15 minutes after deploy

---

## 9. Key Lessons Learned

1. **Autoscale has specific process requirements** - The main process (PID 1) must stay running
2. **Internal dev ≠ Production** - They use different process management - a change that works in dev may break production
3. **[[ports]] sections are irrelevant to Autoscale** - Don't waste time on them for Autoscale issues
4. **Deployment logs are critical** - Check them first, not last
5. **Monitoring prevents surprises** - Set up UptimeRobot immediately
6. **Document everything** - This RCA should prevent future incidents
7. **Agent-introduced bugs can be latent** - Changes made by AI agents may not be immediately visible if old deployments keep running
8. **Always republish after script changes** - Any change to start_production.sh should trigger an immediate publish and verification
9. **Test deployment behavior, not just functionality** - A feature working in dev doesn't mean the deployment script works correctly

---

## 10. Action Items

| Priority | Action | Owner | Due Date |
|----------|--------|-------|----------|
| P0 | Set up UptimeRobot monitoring | User | Dec 19, 2025 |
| P0 | Verify start_production.sh is correct | Agent | Complete |
| P1 | Add deployment checklist to replit.md | Agent | Dec 19, 2025 |
| P1 | Consider Reserved VM upgrade ($20/mo) to eliminate cold starts | User | Dec 20, 2025 |
| P2 | Create staging environment for testing | User | Jan 2026 |

---

## Appendix: Current Working Configuration

### start_production.sh (WORKING)
```bash
#!/bin/bash
# Production startup script for Replit Autoscale
# Next.js MUST run in foreground to keep deployment alive

set -e

APP_PORT="${PORT:-5000}"

echo "[Startup] PORT=$APP_PORT"

if [ ! -d ".next" ]; then
    echo "[ERROR] .next folder missing! Build required before deploy."
    exit 1
fi

# Start Flask in BACKGROUND first
python webhook_server.py &

sleep 2

# Start Next.js in FOREGROUND (CRITICAL - keeps deployment alive)
exec npx next start -p "$APP_PORT" -H 0.0.0.0
```

### .replit [deployment] section (WORKING)
```toml
[deployment]
deploymentTarget = "autoscale"
run = ["sh", "-c", "bash start_production.sh"]
build = ["sh", "-c", "npx next build"]
```

---

**Report Generated:** December 18, 2025
**Report Author:** Replit Agent
**Status:** INCIDENT RESOLVED
