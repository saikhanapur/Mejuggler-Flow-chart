# SUPERHUMANLY - FLOWCHART APP BUILD PROMPT
# Copy this entire prompt to a new Emergent AI agent

---

## 🎯 PROJECT MISSION

Build **SuperHumanly** - an enterprise SaaS that converts complex SOP documents into **beautiful, interactive flowcharts** that match this exact reference design: https://saikhanapur.github.io/Complex-SOP/

**Core Value:** "Turn process chaos into clarity. Instantly."

**Success Criteria:** When a user uploads a document and says "WOW, this is EXACTLY what I needed!"

---

## 🎨 DESIGN-FIRST APPROACH (CRITICAL!)

### The #1 Rule: Match the Reference Design EXACTLY

**Reference URL:** https://saikhanapur.github.io/Complex-SOP/
**Attached HTML:** index.html (I will provide)

**What makes this design special:**
1. **Clean & Simple:** No clutter, pure focus on the process
2. **Color-Coded Status:** Red for critical, blue for action, purple for communication, etc.
3. **Perfect Layout:** Nodes positioned at X=330 (center), Y spacing of 150px
4. **Visual Hierarchy:** Critical steps immediately stand out
5. **Quick Reference:** 3 cards at bottom (Critical Actions, Key Timings, Recovery Steps)
6. **Emergency Contacts:** Full-width blue gradient section
7. **Grid Background:** Subtle dot pattern (30px spacing)
8. **Connection Lines:** Color-coded arrows between steps
9. **Progress Badges:** Stage indicators (⚠️ IMMEDIATE, 🔄 ONGOING, ✅ COMPLETE)

**DO NOT DEVIATE FROM THIS DESIGN.** Every pixel matters.

---

## 📋 TECH STACK (Fixed)

**Frontend:**
- React 18
- TailwindCSS
- React Router
- **NO GRAPH LIBRARIES** (no Reactflow, no Dagre) - Pure HTML/CSS positioning

**Backend:**
- FastAPI (Python)
- MongoDB (UUID-based, NO ObjectID)
- Claude Sonnet 4 (via Emergent LLM Key)

**Deployment:**
- Emergent platform (Kubernetes, pre-configured)

---

## 🏗️ ARCHITECTURE OVERVIEW

```
User uploads PDF/DOCX/Voice
    ↓
Backend: AI analyzes document
    ↓
Extract: steps, contacts, systems, timings, decisions, parallel processes
    ↓
Enhance: Simplify to 10-13 nodes with status classification
    ↓
Position: X=330 (center), Y=index*150, parallel nodes side-by-side
    ↓
Frontend: Render using reference HTML structure
    ↓
User: Clicks node → Side panel with operational details
    ↓
User: Edits via AI chat, exports to PDF/PNG/HTML
```

---

## 🎨 FRONTEND IMPLEMENTATION

### Phase 1: Component Structure (Pure HTML/CSS)

**Directory:** `/app/frontend/src/components/flowchart/`

#### Component 1: FlowchartDisplay.js (Main Visual)
**Purpose:** Render the entire flowchart matching reference design

**Structure:**
```jsx
<div className="w-full">
  {/* Legend Bar */}
  <Legend statuses={uniqueStatuses} />
  
  {/* Flowchart Canvas */}
  <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-12 relative"
       style={{minHeight: canvasHeight}}>
    
    {/* Grid Background */}
    <div style={{
      backgroundImage: 'radial-gradient(circle, rgb(226, 232, 240) 1px, transparent 1px)',
      backgroundSize: '30px 30px'
    }} />
    
    {/* Connection Lines (z-index: 1) */}
    {edges.map(edge => <ConnectionLine from={fromNode} to={toNode} />)}
    
    {/* Nodes (z-index: 2) */}
    {nodes.map(node => <FlowNode node={node} onClick={onNodeClick} />)}
    
    {/* Progress Badges (z-index: 3) */}
    {progressStages.map(stage => <ProgressBadge {...stage} />)}
  </div>
  
  {/* Quick Reference Panels */}
  <QuickReference criticalActions={...} keyTimings={...} recoverySteps={...} />
  
  {/* Emergency Contacts */}
  <EmergencyContacts contacts={emergencyContacts} />
</div>
```

**Key Requirements:**
- Use backend-provided X, Y coordinates exactly
- NO FORCED POSITIONING in frontend
- Absolute positioning for all nodes
- z-index layering (lines below nodes, badges above)

#### Component 2: FlowNode.js (Individual Node Card)
**Purpose:** Render a single node card with status-based styling

**Status Styles:**
```javascript
const STATUS_STYLES = {
  critical: {
    bg: 'bg-gradient-to-br from-red-500 to-red-600',
    text: 'text-white',
    icon: 'text-white',
  },
  action: {
    bg: 'bg-white',
    border: 'border-blue-400',
    text: 'text-slate-800',
    icon: 'text-blue-600',
  },
  communication: {
    bg: 'bg-white',
    border: 'border-purple-400',
    text: 'text-slate-800',
    icon: 'text-purple-600',
  },
  // ... 7 total status types
}
```

**Card Structure:**
```jsx
<div 
  className={`absolute transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer rounded-xl p-4`}
  style={{
    left: `${node.x}px`,
    top: `${node.y}px`,
    width: '240px',
    minHeight: '80px'
  }}
>
  <div className="flex items-start gap-3">
    <StatusIcon status={node.status} />
    <div>
      <h3 className="font-semibold text-sm">{node.title}</h3>
      <p className="text-xs">{node.description}</p>
    </div>
  </div>
</div>
```

**Critical Node Animation:**
```css
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }
  50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.8); }
}
.critical-highlight {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

#### Component 3: ConnectionLine.js (Lines & Arrows)
**Purpose:** Draw connection lines between nodes

**Logic:**
1. **Vertical Line:** If deltaX < 50 (same X position)
2. **L-Shaped Line:** If deltaX >= 50 (parallel/branching)
3. **Dashed Line:** If edge.type === 'dashed' (loops)

**Styling:**
- Line width: 3px (visible)
- Arrow size: 12px tall, 6px wide (visible)
- Color: Match target node's status color

#### Component 4: ProgressBadge.js
**Purpose:** Stage indicators

**Types:**
- `immediate`: Red background, ⚠️ emoji, "IMMEDIATE ACTION"
- `ongoing`: Amber background, 🔄 emoji, "ONGOING"
- `complete`: Green background, ✅ emoji, "RECOVERY COMPLETE"

**Positioning:** X=630, Y=node.y+5, width=200px

#### Component 5: Legend.js
**Purpose:** Status legend bar at top

**Layout:**
```jsx
<div className="bg-white rounded-xl shadow-sm border p-5 mb-6">
  <div className="flex flex-wrap items-center gap-6 text-sm">
    {statuses.map(status => (
      <div className="flex items-center gap-2">
        <StatusIcon status={status} />
        <span>{STATUS_LABELS[status]}</span>
      </div>
    ))}
  </div>
</div>
```

#### Component 6: QuickReference.js
**Purpose:** 3-column cards at bottom

**Layout:**
```jsx
<div className="grid grid-cols-3 gap-6 mt-6">
  {/* Critical Actions - Red gradient */}
  <div className="bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-300 rounded-xl p-6">
    <h3 className="font-bold text-red-900 mb-4">
      <AlertIcon /> Critical Actions
    </h3>
    {criticalActions.map(action => <li>{action}</li>)}
  </div>
  
  {/* Key Timings - Amber gradient */}
  {/* Recovery Steps - Emerald gradient */}
</div>
```

#### Component 7: EmergencyContacts.js
**Purpose:** Full-width contact section

**Layout:**
```jsx
<div className="mt-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-8">
  <h3 className="font-bold text-blue-900 mb-6 text-2xl">
    <PhoneIcon /> Emergency Contacts Quick Reference
  </h3>
  <div className="grid grid-cols-3 gap-6">
    {Object.entries(contacts).map(([name, contact]) => (
      <div className="bg-white/70 rounded-lg p-5 border border-blue-200">
        <h4 className="font-semibold text-blue-900">{name}</h4>
        <p className="font-mono font-medium">{contact}</p>
      </div>
    ))}
  </div>
</div>
```

---

## 🧠 BACKEND IMPLEMENTATION

### Phase 1: AI Document Analysis

**File:** `/app/backend/superintelligent_ai_service.py`

**Method:** `analyze_document(document_text, input_type)`

**What it does:**
1. Extracts raw data: steps, contacts, systems, timings, decisions
2. Uses Claude Sonnet 4 (Emergent LLM Key)
3. Returns JSON with extracted data

**Prompt Structure:**
```
Analyze this document and extract:
1. All process steps (in order)
2. Contact information (name: phone/email)
3. Systems/tools mentioned
4. Timings (within X minutes, every Y hours)
5. Decision points (if/then)
6. Parallel processes (meanwhile, at same time)

Return ONLY valid JSON.
```

### Phase 2: EROAD-Style Enhancement

**File:** `/app/backend/eroad_style_enhancer.py`

**Method:** `enhance_for_visualization(extracted_data, document_text)`

**What it does:**
1. **Simplifies:** Combines 20 raw steps → 10-13 strategic nodes
2. **Classifies:** Assigns status (critical, action, communication, operational, monitoring, verification, recovery)
3. **Positions:** Calculates X, Y coordinates
4. **Enriches:** Adds purpose, currentState, idealState, gap analysis

**Prompt Structure:**
```
Transform extracted data into 10-13 strategic nodes.

OUTPUT STRUCTURE:
{
  "processName": "...",
  "nodes": [
    {
      "id": "node-1",
      "title": "Short title (max 50 chars)",
      "purpose": "WHY this step exists",
      "details": "Full description",
      "status": "critical|action|communication|operational|monitoring|verification|recovery",
      "actions": ["Specific action 1", "Specific action 2"],
      "currentState": "How this is done now",
      "idealState": "How this could be improved",
      "gap": "What's problematic/missing",
      "contacts": ["Name: Phone/Email"],
      "systems": ["Tool names"],
      "timing": "When/how long",
      "parallelWith": ["node-id-if-parallel"],
      "isDecisionPoint": false,
      "decisionOptions": {"yes": "next_node", "no": "alt_node"},
      "isLoop": false,
      "loopBackTo": "node-id",
      "x": 330,
      "y": 0,
      "connections": ["next_node_id"]
    }
  ]
}

STATUS CLASSIFICATION GUIDE:
- critical: Urgent, time-sensitive, failures (e.g., "Emergency Response", "System Down", "Call 111")
- action: Immediate action/decision (e.g., "Notify Manager", "Initiate BCP")
- communication: Sending info to stakeholders (e.g., "Email Teams", "Broadcast Alert")
- operational: Standard tasks (e.g., "Manual Dispatch", "Create Jobs")
- monitoring: Checking/tracking (e.g., "Check Every 30 Min", "Track Progress")
- verification: Testing/confirming (e.g., "Test Systems", "Verify Resolution")
- recovery: Final restoration (e.g., "Resume Operations", "Return to BAU")

PARALLEL PROCESS DETECTION:
- Keywords: "meanwhile", "at the same time", "simultaneously", "both teams"
- Example: "Onshore team sets up" + "Offshore team sets up" = PARALLEL
- Mark: "parallelWith": ["other_node_id"]

DECISION POINT DETECTION:
- Keywords: "if", "check if", "verify whether", "has X happened?"
- Mark: "isDecisionPoint": true, "decisionOptions": {"yes": "...", "no": "..."}

LOOP DETECTION:
- Keywords: "repeat until", "check every X minutes", "continue monitoring"
- Mark: "isLoop": true, "loopBackTo": "node_id"

GROUPING RULES:
- Combine sequential steps that serve the same purpose
- Example: "Email councils", "Email MCs" → "Stakeholder Communications"
- Keep decision points separate
- Parallel processes = separate nodes, same Y coordinate
```

**Positioning Logic:**
```python
# Process nodes intelligently
nodes = enhanced.get('nodes', [])
y_position = 0
processed_ids = set()

for i, node in enumerate(nodes):
    if node['id'] in processed_ids:
        continue
    
    # Check for parallel companions
    parallel_with = node.get('parallelWith', [])
    
    if parallel_with:
        # Position parallel nodes side-by-side
        parallel_nodes = [node] + [n for n in nodes if n['id'] in parallel_with]
        
        if len(parallel_nodes) == 2:
            parallel_nodes[0]['x'] = 250  # Left
            parallel_nodes[0]['y'] = y_position
            parallel_nodes[1]['x'] = 410  # Right
            parallel_nodes[1]['y'] = y_position
        elif len(parallel_nodes) == 3:
            parallel_nodes[0]['x'] = 180  # Left
            parallel_nodes[1]['x'] = 330  # Center
            parallel_nodes[2]['x'] = 480  # Right
            # All same Y
        
        for pnode in parallel_nodes:
            processed_ids.add(pnode['id'])
        
        y_position += 150
    else:
        # Sequential node - center it
        node['x'] = 330
        node['y'] = y_position
        processed_ids.add(node['id'])
        y_position += 150
```

### Phase 3: API Response Formatting

**File:** `/app/backend/superintelligent_ai_service.py`

**Method:** `generate_eroad_style_flowchart(document_text, input_type)`

**Response Structure:**
```json
{
  "processes": [{
    "name": "Process Name",
    "description": "Brief summary",
    "nodes": [
      {
        "id": "node-1",
        "title": "Step Title",
        "description": "Details",
        "type": "critical",
        "status": "critical",
        "x": 330,
        "y": 0,
        "position": {"x": 330, "y": 0},
        "actors": ["Contact: Phone"],
        "subSteps": ["Action 1", "Action 2"],
        "dependencies": [],
        "parallelWith": [],
        "isDecisionPoint": false,
        "decisionOptions": {},
        "isLoop": false,
        "loopBackTo": null,
        "operationalDetails": {
          "purpose": "Why this step exists",
          "specificActions": ["Action 1", "Action 2"],
          "contactInfo": {"Name": "Phone"},
          "timeline": "Within 5 minutes",
          "systems": ["Tool1", "Tool2"],
          "decisionCriteria": null,
          "currentState": "How it's done now",
          "idealState": "How it could be better",
          "gap": "What's wrong"
        }
      }
    ],
    "edges": [
      {
        "id": "e-node-1-node-2",
        "source": "node-1",
        "target": "node-2",
        "label": null,
        "type": "solid" // or "dashed" for loops
      }
    ],
    "quickReference": {
      "criticalActions": ["Action 1", "Action 2"],
      "keyTimings": ["Within 5 min", "Every 30 min"],
      "emergencyContacts": {
        "IT Support": "0800 123 456",
        "Manager": "0800 789 012"
      }
    },
    "progressStages": [
      {
        "type": "immediate",
        "x": 630,
        "y": 5,
        "title": "IMMEDIATE ACTION",
        "description": "Critical response required"
      }
    ]
  }],
  "multipleProcesses": false
}
```

---

## 🎯 IMPLEMENTATION STEPS

### Day 1: Frontend Foundation (4-6 hours)

**Step 1.1: Analyze Reference HTML (30 min)**
- Download HTML from reference
- Extract exact CSS classes
- Document color values
- Note spacing constants

**Step 1.2: Create Component Structure (1 hour)**
```bash
mkdir -p /app/frontend/src/components/flowchart
```
Create 7 files:
1. FlowchartDisplay.js
2. FlowNode.js
3. ConnectionLine.js
4. ProgressBadge.js
5. Legend.js
6. QuickReference.js
7. EmergencyContacts.js

**Step 1.3: Build FlowNode.js (1 hour)**
- Implement 7 status styles
- Add SVG icons
- Add hover effects
- Add pulse animation for critical

**Step 1.4: Build ConnectionLine.js (1 hour)**
- Vertical line logic
- L-shaped line logic
- Dashed line support
- Arrow rendering

**Step 1.5: Build FlowchartDisplay.js (1.5 hours)**
- Assemble all components
- Grid background
- z-index layering
- Canvas height calculation

**Step 1.6: Build QuickReference + EmergencyContacts (1 hour)**
- 3-column grid layout
- Gradient backgrounds
- Icon integration

### Day 2: Backend Integration (4-6 hours)

**Step 2.1: Test with Mock Data (1 hour)**
- Create sample JSON matching backend response structure
- Verify all components render correctly
- Check positioning, colors, connections

**Step 2.2: Create FlowchartCanvas.js (1 hour)**
- Orchestrator component
- Load process from API
- Handle node clicks → side panel
- Integrate AI chat, export, share buttons

**Step 2.3: Connect to Backend API (1 hour)**
- Verify `/api/process/eroad-style` endpoint
- Test with real document
- Debug any data mismatches

**Step 2.4: Side Panel Integration (1 hour)**
- OperationalDetailsPanel shows on node click
- Display purpose, actions, contacts, systems, timings
- Show currentState vs idealState

**Step 2.5: Verify Backend Logic (1 hour)**
- Check eroad_style_enhancer.py positioning logic
- Verify status mapping in superintelligent_ai_service.py
- Test parallel process detection
- Test decision point detection

**Step 2.6: Integration Testing (1 hour)**
- Upload 3 different documents
- Verify 10-13 nodes generated
- Check status color variety
- Verify Quick Reference panels populate
- Test all connections render

### Day 3: Polish & Testing (2-4 hours)

**Step 3.1: Visual QA (1 hour)**
- Compare side-by-side with reference
- Adjust colors if needed
- Fine-tune spacing
- Check hover effects

**Step 3.2: Responsive Design (1 hour)**
- Test on 1920x1080 (primary)
- Test on 1366x768
- Ensure canvas scrolls properly

**Step 3.3: Edge Case Testing (1 hour)**
- Single node process
- 20+ node process
- Process with no contacts
- Process with no timings

**Step 3.4: Feature Testing (1 hour)**
- AI editing works
- Export to PDF/PNG/HTML
- Sharing generates link
- Workspace management

---

## ✅ ACCEPTANCE CRITERIA

### Visual Match (100% Required)

- [ ] Node cards match reference pixel-perfect
- [ ] All 7 status colors correct (critical=red, action=blue, etc.)
- [ ] Grid background visible (radial dots, 30px spacing)
- [ ] Connection lines render correctly (vertical + L-shaped)
- [ ] Arrows visible (12px tall, color-matched)
- [ ] Progress badges positioned at X=630
- [ ] Legend bar matches reference
- [ ] Quick Reference 3-column layout matches
- [ ] Emergency Contacts section matches
- [ ] Hover effects work (scale-105, shadow-2xl)
- [ ] Critical nodes pulse with red glow

### Functionality (100% Required)

- [ ] Upload PDF → generates 10-13 nodes
- [ ] Upload DOCX → generates 10-13 nodes
- [ ] Upload voice → generates 10-13 nodes
- [ ] All nodes render at correct positions
- [ ] Click node → side panel opens with details
- [ ] Multiple status colors visible (not all same)
- [ ] Parallel processes appear side-by-side (if detected)
- [ ] Decision points show L-shaped connections (if detected)
- [ ] Loops show dashed lines (if detected)
- [ ] AI editing works (chat interface)
- [ ] Export to PDF works
- [ ] Sharing generates public link

### Performance

- [ ] Initial load < 3s
- [ ] Flowchart renders < 500ms
- [ ] No console errors
- [ ] Smooth hover interactions

---

## 🚫 WHAT NOT TO DO

1. **DO NOT use Reactflow or Dagre** - Pure HTML/CSS positioning only
2. **DO NOT deviate from reference design** - Match it exactly
3. **DO NOT over-engineer** - Simple is better
4. **DO NOT force linear positioning in frontend** - Use backend coordinates
5. **DO NOT skip status color mapping** - All 7 types must work
6. **DO NOT ignore parallel/decision detection** - These are critical

---

## 📊 DATA FLOW DIAGRAM

```
1. User uploads document
   ↓
2. ProcessCreator.js → POST /api/process with file
   ↓
3. Backend: superintelligent_ai_service.analyze_document()
   → Extract: steps, contacts, systems, timings
   ↓
4. Backend: eroad_style_enhancer.enhance_for_visualization()
   → Simplify to 10-13 nodes
   → Classify status (critical, action, etc.)
   → Detect parallel processes
   → Detect decision points
   → Calculate positions (X, Y)
   ↓
5. Backend: superintelligent_ai_service.generate_eroad_style_flowchart()
   → Format response (nodes, edges, quickReference, progressStages)
   ↓
6. Backend: POST /api/process creates process in MongoDB
   ↓
7. Frontend: Navigate to /edit/:processId
   ↓
8. FlowchartCanvas.js → GET /api/process/:id
   ↓
9. FlowchartDisplay.js renders:
   → Legend
   → Canvas with grid background
   → Connection lines (from edges array)
   → Nodes (from nodes array)
   → Progress badges
   → Quick Reference panels
   → Emergency Contacts
   ↓
10. User clicks node → OperationalDetailsPanel opens
    ↓
11. User edits via AI → AIRefineChat.js
    ↓
12. User exports → ExportModal.js
```

---

## 🎨 DESIGN CONSTANTS

Copy these exactly:

```javascript
// Node sizing
const NODE_WIDTH = 240;
const NODE_MIN_HEIGHT = 80;
const NODE_X_CENTER = 330;
const NODE_Y_SPACING = 150;

// Parallel node positioning
const PARALLEL_LEFT = 250;
const PARALLEL_CENTER = 330;
const PARALLEL_RIGHT = 410;
const PARALLEL_FAR_LEFT = 180;
const PARALLEL_FAR_RIGHT = 480;

// Progress badge positioning
const BADGE_X = 630;
const BADGE_WIDTH = 200;

// Grid background
const GRID_SIZE = 30;
const GRID_COLOR = 'rgb(226, 232, 240)';

// Connection lines
const LINE_WIDTH = 3;
const ARROW_HEIGHT = 12;
const ARROW_WIDTH = 6;

// Status colors (exact hex values)
const STATUS_COLORS = {
  critical: { primary: '#ef4444', secondary: '#dc2626' },
  action: { primary: '#3b82f6' },
  communication: { primary: '#a855f7' },
  operational: { primary: '#10b981' },
  monitoring: { primary: '#f59e0b' },
  verification: { primary: '#14b8a6' },
  recovery: { primary: '#22c55e' },
};
```

---

## 🧪 TESTING PROTOCOL

### Test Document 1: Simple Linear (6 steps)
```
System Outage Response

1. Detect Outage - Monitor systems
2. Notify Manager - Call on-duty manager
3. Initiate BCP - Activate continuity plan
4. Monitor Status - Check every 30 minutes
5. Test Restoration - Verify systems operational
6. Resume Operations - Return to normal

Contacts:
- IT Support: 0800 123 456
- Manager: 0800 789 012
```

**Expected:** 5-6 nodes, vertical layout, critical=red, monitoring=amber

### Test Document 2: Parallel Processes (Wilsar BCP)
```
Wilsar System Outage BCP

1. Identify Outage
2. Onshore BCP Setup - Team A activates tracking
3. Offshore BCP Setup - Team B activates tracking (at same time)
4. Notify Councils
5. Manual Dispatch
...
```

**Expected:** Nodes 2 and 3 side-by-side (X=250/410)

### Test Document 3: Decision Points
```
Fleet Vehicle Breakdown

1. Receive Call
2. Safety Assessment
3. Check if officer harmed - If YES → Call 111, If NO → Continue
4. Collect Information
...
```

**Expected:** Node 3 has L-shaped connections to two different nodes

---

## 🎯 SUCCESS METRICS

**When you've succeeded:**

1. User uploads Wilsar BCP → Gets 13 nodes with colors matching urgency
2. User uploads Fleet Vehicle → Gets 9-10 nodes with decision branching visible
3. User clicks any node → Sees rich operational details in side panel
4. User shows colleague → Colleague says "WOW, this is exactly what we need!"
5. Side-by-side comparison with reference → 95%+ visual match

**When you've failed:**

1. All nodes same color → Status classification broken
2. Only 1 node visible → Positioning or rendering broken
3. Nodes overlapping → Coordinate calculation broken
4. No arrows visible → Connection line rendering broken
5. Looks nothing like reference → Design implementation wrong

---

## 📝 DEVELOPMENT CHECKLIST

### Phase 1: Frontend (Day 1)
- [ ] Create 7 flowchart components
- [ ] Implement exact status colors from reference
- [ ] Add grid background (radial dots, 30px)
- [ ] Build connection line rendering (vertical + L-shaped)
- [ ] Add larger arrows (12px tall)
- [ ] Implement hover effects (scale-105, shadow-2xl)
- [ ] Add critical node pulse animation
- [ ] Build QuickReference 3-column layout
- [ ] Build EmergencyContacts section
- [ ] Test with mock data

### Phase 2: Integration (Day 2)
- [ ] Create FlowchartCanvas orchestrator
- [ ] Connect to `/api/process/eroad-style` endpoint
- [ ] Verify backend positioning logic (X=330, parallel side-by-side)
- [ ] Verify backend status mapping (all 7 types)
- [ ] Test parallel process detection
- [ ] Test decision point detection
- [ ] Test loop detection (dashed lines)
- [ ] Integrate side panel (OperationalDetailsPanel)
- [ ] Test with 3 real documents

### Phase 3: Polish (Day 3)
- [ ] Visual QA vs reference (pixel-perfect match)
- [ ] Test responsive design (1920x1080, 1366x768)
- [ ] Test edge cases (1 node, 20+ nodes, no contacts)
- [ ] Test all features (AI edit, export, share)
- [ ] Performance check (<3s load, <500ms render)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] No console errors

---

## 🚀 DEPLOYMENT READINESS

**Before marking as complete:**

1. Upload the attached reference HTML and compare side-by-side
2. Test with Wilsar BCP document (should show parallel onshore/offshore)
3. Test with Fleet Vehicle doc (should show decision branching)
4. Verify Quick Reference panels populate correctly
5. Verify Emergency Contacts section appears (if data exists)
6. Check that all 7 status colors appear (not all same)
7. Verify arrows are clearly visible
8. Verify critical nodes pulse with red glow
9. Get user approval: "This matches the reference!"

---

## 💎 THE GOLDEN RULE

**"If it doesn't look like the reference, it's not done."**

The reference design (https://saikhanapur.github.io/Complex-SOP/) is the source of truth. Every component, every color, every spacing must match. This is not negotiable.

The backend logic for AI analysis is solid. The features work. The only job is to **match the visual design exactly**.

---

## 🎓 LESSONS LEARNED FROM PREVIOUS ATTEMPTS

**What didn't work:**
1. Using Reactflow/Dagre (over-engineering)
2. Forcing linear positioning in frontend (ignoring backend coordinates)
3. Collapsing all statuses to "active" (losing color distinctions)
4. Not following the reference HTML structure
5. Making it too complex

**What works:**
1. Pure HTML/CSS absolute positioning
2. Using backend-provided X, Y coordinates
3. Preserving all 7 status types
4. Following reference HTML exactly
5. Keeping it simple

---

## 📞 SUPPORT RESOURCES

**Reference Materials:**
- Design: https://saikhanapur.github.io/Complex-SOP/
- HTML Source: index.html (attached)

**Key Dependencies:**
- React 18
- TailwindCSS
- FastAPI
- MongoDB
- Claude API (Emergent LLM Key - already configured)

**Emergent Platform:**
- Frontend: Port 3000 (auto-configured)
- Backend: Port 8001 (auto-configured)
- MongoDB: localhost:27017 (auto-configured)
- Services: Managed by supervisord

---

## 🎯 FINAL CHECKLIST

Before calling this complete:

- [ ] Visual match: 95%+ to reference design
- [ ] Status colors: All 7 types working
- [ ] Node positioning: X=330 for sequential, side-by-side for parallel
- [ ] Connection lines: Vertical + L-shaped + dashed for loops
- [ ] Arrows: Visible (12px tall)
- [ ] Quick Reference: 3 cards render correctly
- [ ] Emergency Contacts: Section renders if data exists
- [ ] Side panel: Opens on node click with operational details
- [ ] AI editing: Chat interface works
- [ ] Export: PDF/PNG generation works
- [ ] Sharing: Public link generation works
- [ ] Performance: <3s load, <500ms render
- [ ] No console errors
- [ ] User says: "WOW!"

---

**NOW BUILD IT. MATCH THE DESIGN. GET THE WOW FACTOR.** 🚀
