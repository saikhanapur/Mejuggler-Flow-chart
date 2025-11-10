# Existing Sharing, Publishing & Version Control Features - Status Report

**Date:** November 2, 2025  
**Purpose:** Document what features exist for sharing, publishing, and version control

---

## ✅ WHAT EXISTS (Fully Implemented)

### 1. Publishing Feature ✅

**Status:** FULLY FUNCTIONAL

**Backend Endpoints:**
- `PATCH /api/process/{id}/publish` - Publish a process
- `PATCH /api/process/{id}/unpublish` - Unpublish a process

**Database Fields (Process model):**
```python
class Process(BaseModel):
    status: str = "draft"  # draft, published, archived
    publishedAt: Optional[datetime] = None
    version: int = 1  # Simple version counter
```

**How It Works:**
1. Process starts as "draft"
2. User clicks "Publish" → Status changes to "published", publishedAt timestamp added
3. User clicks "Unpublish" → Status changes back to "draft"
4. Version counter increments on significant changes

**Guest Mode Gating:**
- Guest users CANNOT publish (returns 403)
- Error message: "Guest users cannot publish. Sign up to share your flowchart!"

**Files:**
- Backend: `/app/backend/server.py` lines 1971-2010
- Frontend: Dashboard shows "Draft" or "Published" badge

---

### 2. Sharing Feature ✅

**Status:** FULLY FUNCTIONAL

**Backend Endpoints:**
- `POST /api/process/{process_id}/share` - Create share link
- `GET /api/process/{process_id}/shares` - List all shares for a process
- `DELETE /api/share/{token}` - Revoke a share
- `GET /api/view/{token}` - View shared process (public endpoint)
- `POST /api/view/{token}/comment` - Add comment to shared process
- `PATCH /api/view/{token}/access` - Track access

**Database Collection:** `shares`

**Share Model:**
```python
class Share(BaseModel):
    id: str  # UUID
    token: str  # Unique encrypted token (secrets.token_urlsafe(32))
    processId: str
    accessLevel: str  # "view", "comment", "edit"
    
    # Owner tracking
    createdBy: str  # userId of share creator
    createdByName: str
    
    # Expiration
    expiresAt: Optional[datetime] = None  # None = never expires
    isActive: bool = True  # Can be revoked
    
    # Usage tracking
    accessCount: int = 0
    lastAccessedAt: Optional[datetime] = None
    
    # Timestamps
    createdAt: datetime
    updatedAt: datetime
    revokedAt: Optional[datetime] = None
```

**Access Levels:**
1. **View Only** 👁️
   - Can view the flowchart
   - Cannot edit or comment
   - Read-only access

2. **Can Comment** 💬
   - Can view the flowchart
   - Can add comments to nodes
   - Cannot edit the flowchart

3. **Can Suggest Edits** ✏️
   - Can view the flowchart
   - Can add comments
   - Can suggest edits (requires owner approval)
   - Cannot directly edit

**Expiration Options:**
- 7 days
- 30 days
- 90 days
- Never expires (null)

**How It Works:**
1. User publishes process
2. User opens "Share" modal
3. User selects access level and expiration
4. Backend generates encrypted token: `secrets.token_urlsafe(32)`
5. Share link created: `https://app.com/view/{token}`
6. Recipients can access via unique link
7. Owner can revoke any share (soft delete - sets isActive=false)
8. Expired shares are automatically blocked

**Frontend Component:**
- `ShareModal.js` - Full-featured sharing UI with:
  - Create share tab
  - Manage shares tab
  - Copy link button
  - Revoke share button
  - View access statistics

**Security:**
- Only published processes can be shared
- Only process owner can create/revoke shares
- Token is cryptographically secure (32 bytes, URL-safe)
- Access tracking (count, last accessed)
- Soft delete (revocation doesn't delete, just deactivates)

---

### 3. Version Control ⚠️

**Status:** PARTIAL (Basic Version Counter Only)

**What EXISTS:**
- `version: int = 1` field in Process model
- Version increments on major changes
- No version history/snapshots
- No version comparison
- No version revert

**What's MISSING:**
- ❌ Version history (list of all versions)
- ❌ Version snapshots (full process data per version)
- ❌ Version comparison (diff between v1 and v2)
- ❌ Version revert (restore to previous version)
- ❌ Version branching
- ❌ Version metadata (who changed what, when, why)

**Current Implementation:**
```python
# In Process model
version: int = 1

# In update endpoint (line 3007)
"version": process.get('version', 1) + 1  # Increment version

# In another endpoint (line 3577)
process.version += 1
```

**What Would Be Needed for Full Version Control:**

```python
# New collection: process_versions
class ProcessVersion(BaseModel):
    id: str
    processId: str
    versionNumber: int
    snapshot: Dict[str, Any]  # Full process data
    createdBy: str
    createdAt: datetime
    changeDescription: str
    changeType: str  # "minor_edit", "major_change", "publish"

# Endpoints needed:
GET /api/process/{id}/versions          # List all versions
GET /api/process/{id}/versions/{version} # Get specific version
POST /api/process/{id}/versions/compare  # Compare two versions
POST /api/process/{id}/versions/{version}/restore  # Revert to version
```

---

## 📊 Feature Comparison Matrix

| Feature | Status | Implementation | Files |
|---------|--------|----------------|-------|
| **Publishing** | ✅ Complete | Draft → Published workflow | `server.py` lines 1971-2010 |
| **Unpublishing** | ✅ Complete | Published → Draft | `server.py` lines 1971-2010 |
| **Share Links** | ✅ Complete | Encrypted tokens (32 bytes) | `server.py` lines 4269-4420 |
| **Access Levels** | ✅ Complete | View, Comment, Edit | `ShareModal.js` |
| **Expiration** | ✅ Complete | 7/30/90 days or never | `Share` model |
| **Revoke Share** | ✅ Complete | Soft delete (isActive=false) | `server.py` line 4374 |
| **Access Tracking** | ✅ Complete | Count + last accessed | `Share` model |
| **Guest Gating** | ✅ Complete | Guests cannot publish/share | `server.py` line 1974 |
| **Version Counter** | ⚠️ Partial | Simple integer counter | `Process.version` |
| **Version History** | ❌ Missing | Not implemented | - |
| **Version Snapshots** | ❌ Missing | Not implemented | - |
| **Version Compare** | ❌ Missing | Not implemented | - |
| **Version Revert** | ❌ Missing | Not implemented | - |

---

## 🎯 Summary

### ✅ Fully Working:
1. **Publishing System**
   - Draft/Published status
   - Publish/Unpublish actions
   - Guest users blocked from publishing

2. **Sharing System**
   - Unique encrypted tokens
   - 3 access levels (view, comment, edit)
   - Expiration options
   - Revocation (soft delete)
   - Access tracking
   - Full UI in ShareModal.js

### ⚠️ Partially Working:
3. **Version Control**
   - Simple version counter exists
   - No history, snapshots, comparison, or revert

---

## 🔧 Implementation Status by Component

### Backend (server.py)

**Publishing:**
- ✅ Lines 1971-2010: Publish/Unpublish endpoints
- ✅ Guest gating (line 1974)
- ✅ Status field in Process model (line 214)
- ✅ publishedAt timestamp (line 212)

**Sharing:**
- ✅ Lines 4269-4330: Create share endpoint
- ✅ Lines 4337-4372: List shares endpoint
- ✅ Lines 4374-4420: Revoke share endpoint
- ✅ Lines 283-314: Share model + validation
- ✅ Encrypted token generation (line 287)

**Version Control:**
- ⚠️ Line 213: Version field (int)
- ⚠️ Line 3007: Version increment (basic)
- ❌ No version history collection
- ❌ No version snapshots
- ❌ No version comparison logic

### Frontend

**Publishing:**
- ✅ Dashboard: Shows "Draft" or "Published" badge
- ✅ FlowchartEditor: Publish/Unpublish buttons

**Sharing:**
- ✅ ShareModal.js (300+ lines):
  - Create share tab with access level selector
  - Manage shares tab with list of active shares
  - Copy link functionality
  - Revoke share functionality
  - Access statistics display
  - Expiration date display

**Version Control:**
- ❌ No version history UI
- ❌ No version comparison UI
- ❌ No version revert UI

### Database Collections

**processes** ✅
- All process data
- status: "draft" or "published"
- publishedAt: timestamp
- version: integer counter

**shares** ✅
- All share links
- Encrypted tokens
- Access levels
- Expiration dates
- Usage tracking

**process_versions** ❌
- Does NOT exist
- Would store version snapshots

---

## 🚀 What Can Be Done NOW

### User Workflows That Work:

**Workflow 1: Publish a Process**
```
1. Create flowchart → Status: "draft"
2. Click "Publish" button
3. Status changes to "published"
4. publishedAt timestamp recorded
5. Process appears in "Published" filter on dashboard
```

**Workflow 2: Share a Published Process**
```
1. Open published process
2. Click "Share" button
3. Select access level: View / Comment / Edit
4. Select expiration: 7 days / 30 days / 90 days / Never
5. Click "Create Share Link"
6. Backend generates encrypted token (e.g., "xK9mP2nQ...")
7. Share URL: https://app.com/view/xK9mP2nQ...
8. Copy link and share with team
9. Recipients access via unique link
10. Owner can revoke access anytime
```

**Workflow 3: Manage Shares**
```
1. Click "Share" → "Manage" tab
2. See list of all active shares:
   - Access level badge
   - Expiration date
   - Access count
   - Last accessed time
3. Click "Revoke" to deactivate a share
4. Revoked shares show "Revoked" badge
```

---

## 🔴 What DOES NOT Work (Missing Features)

### Version Control (Not Implemented)

**What Users CANNOT Do:**
1. ❌ View version history ("Version 1, Version 2, Version 3...")
2. ❌ See who made changes and when
3. ❌ Compare two versions (diff view)
4. ❌ Revert to a previous version
5. ❌ Branch from a version
6. ❌ Add version notes/descriptions

**What Would Be Needed:**

```javascript
// Desired UI (not implemented):
<VersionHistory processId={id}>
  <VersionItem
    version={3}
    date="2025-11-02 14:30"
    author="john@company.com"
    description="Added emergency contacts"
    changes={"+5 nodes, -2 nodes, 3 modified"}
    onView={() => viewVersion(3)}
    onRestore={() => restoreVersion(3)}
    onCompare={() => compareVersions(2, 3)}
  />
  <VersionItem version={2} ... />
  <VersionItem version={1} ... />
</VersionHistory>

// Comparison view (not implemented):
<VersionDiff oldVersion={2} newVersion={3}>
  <ChangeItem type="added" node={{...}} />
  <ChangeItem type="modified" node={{...}} field="title" />
  <ChangeItem type="deleted" node={{...}} />
</VersionDiff>
```

**Backend Requirements (not implemented):**
```python
# New collection needed:
db.process_versions

# New endpoints needed:
GET    /api/process/{id}/versions           # List all versions
GET    /api/process/{id}/versions/{version}  # Get specific version
POST   /api/process/{id}/versions/compare    # Compare versions
POST   /api/process/{id}/versions/{version}/restore  # Revert
POST   /api/process/{id}/versions/create     # Manual version creation

# Version snapshot on save:
async def create_version_snapshot(process_id: str, user_id: str, description: str):
    current_process = await db.processes.find_one({"id": process_id})
    
    version = ProcessVersion(
        processId=process_id,
        versionNumber=current_process['version'],
        snapshot=current_process,  # Full process data
        createdBy=user_id,
        changeDescription=description
    )
    
    await db.process_versions.insert_one(version.dict())
```

---

## 💡 Recommendations

### For Your Current Implementation:

**1. Keep Using Published/Share System ✅**
- It's fully functional
- Secure encrypted tokens
- Comprehensive access control
- UI is polished and working

**2. Version Control - Two Options:**

**Option A: Implement Full Version Control (8-10 hours)**
- Create `process_versions` collection
- Snapshot process on every save
- Build version history UI
- Add version comparison
- Add version revert
- **Benefit:** Full enterprise-grade version control
- **Cost:** Additional development time

**Option B: Use Simple Version Counter (Current State)**
- Keep existing version integer
- Manual version bumps on major changes
- No history, just counter
- **Benefit:** Already working, no additional work
- **Cost:** Limited version tracking

**Recommendation:** **Option A** if you need enterprise features (audit trail, compliance, rollback). **Option B** if you want to focus on multi-process detection and BCP intelligence first.

### For Combined Implementation:

Since you asked about not duplicating effort, here's what to do:

✅ **Keep:**
- Publishing system (fully working)
- Sharing system (fully working)
- Simple version counter (working)

🚧 **Add in Parallel with Multi-Process Work:**
- Version snapshots when process is published
- Version history UI (simple list)
- **Why:** Saves time, no duplication

❌ **Defer:**
- Version comparison (complex diff algorithm)
- Version branching (complex)
- **Why:** Not critical for MVP, add in Phase 2

---

## 🎯 Action Plan for Your Session

### What to Implement Together:

**Phase 1: Multi-Process + BCP Intelligence (6-8 hours)**
- Multi-process detection
- BCP patterns (swim lanes, decisions, loops)
- Long document handling

**Phase 2: Basic Version Snapshots (2 hours)**
- Create version snapshot on publish
- Store in `process_versions` collection
- Simple version history UI (list only)
- **Benefit:** Captures important milestones without full complexity

**Total:** 8-10 hours for comprehensive solution

**Not Including:**
- Version comparison (defer)
- Version revert (defer)
- Version branching (defer)

---

## Files Reference

### Backend
- `server.py` lines 1971-2010: Publishing
- `server.py` lines 4269-4420: Sharing
- `server.py` lines 283-314: Share model
- `server.py` line 213: Version field

### Frontend
- `ShareModal.js`: Full sharing UI
- `Dashboard.js`: Draft/Published badges
- `FlowchartEditor.js`: Publish/Unpublish buttons

### Database
- Collection: `processes` (status, publishedAt, version)
- Collection: `shares` (tokens, access levels, tracking)
- Collection: `process_versions` ❌ Does NOT exist

---

## Conclusion

**What You Have:**
- ✅ Fully functional publishing system
- ✅ Fully functional sharing system with encrypted tokens, access levels, and expiration
- ⚠️ Basic version counter (no history or snapshots)

**What You're Missing:**
- ❌ Version history and snapshots
- ❌ Version comparison
- ❌ Version revert

**Recommendation:**
Keep using the existing publishing/sharing system (it's enterprise-ready). Add basic version snapshots during multi-process implementation (minimal effort, high value). Defer complex version features (comparison, branching) to Phase 2.

Ready to proceed with the combined implementation! 🚀
