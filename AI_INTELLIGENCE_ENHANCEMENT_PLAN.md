# SuperHumanly - AI Intelligence Enhancement Plan
## Based on Your 4 BCP Documents Analysis

**Date:** November 2, 2025  
**Priority:** CRITICAL  
**Timeline:** 2-3 weeks

---

## Executive Summary

After analyzing your 4 BCP documents (Wilsar, GDS, Internet, RingCentral Outages), I've identified **specific patterns** your AI is missing. This plan will teach the AI to recognize BCP-specific structures.

---

## Key Findings from Your BCPs

### Pattern #1: Swim Lane / Column Structure ⚠️

**Your Documents Use:**
```
┌─────────────────────────────────────────────────────────┐
│ IDENTIFY       │ ONSHORE ACTIONS  │ OFFSHORE ACTIONS   │
├────────────────┼──────────────────┼────────────────────┤
│ [Decision]     │ Step 1           │ Step A             │
│                │ Step 2           │ Step B             │
│                │ Step 3           │ Step C             │
└─────────────────────────────────────────────────────────┘
```

**What AI Currently Does:** Merges all into single sequential flow

**What AI Should Do:** Detect column headers and create 3 parallel swim lanes

**Detection Keywords:**
- "Onshore Actions", "Offshore Actions"
- "FSC / DSC ACTIONS"
- "IDENTIFY", "ASSESS", "MITIGATE"
- Section headers with different team responsibilities

---

### Pattern #2: BCP-Specific Decision Points ⚠️

**Your Documents Use:**
```
Decision: "Has Wilsar Outage?"
  ├─ YES → Proceed to BCP steps
  └─ NO → Resume BAU services

Decision: "GDS down"
  ├─ YES → Launch BCP
  └─ NO → Resume BAU

Decision: "Job received?"
  ├─ YES → Resume services
  └─ NO → Escalate to supervisor
```

**Current AI Detection:** Only catches generic "if", "check if"

**Your BCP Language:**
- "[System Name] down" (e.g., "Wilsar down", "GDS down")
- "[System Name] outage"
- "[X] received?"
- "Has [X] occurred?"
- Diamond shapes in flowchart

---

### Pattern #3: Time-Based Monitoring Loops ⚠️

**Your Documents Use:**
```
Loop: "Check in with Wilson IT every 30 minutes until services restored"
Loop: "Check in with Andrew from CRS every 30 minutes until..."
Loop: "Monitor every [X] minutes"
```

**Current AI Detection:** Misses frequency-based loops

**Your BCP Language:**
- "Check every [X] minutes"
- "Check in with [Person] every [X] minutes until [condition]"
- "Monitor until [condition]"

---

### Pattern #4: Parallel Activities by Team/Location ⚠️

**Your Documents Show:**
```
Parallel:
├─ Onshore: Notify teams, Email councils, Send Modica
└─ Offshore: Reallocate tasks, Begin timeline, Email monitoring
    (Both happening simultaneously at same time)
```

**Current AI Detection:** Treats as sequential

**Your BCP Indicators:**
- Different column headers (Onshore | Offshore)
- Same vertical level in flowchart
- Different actors/locations
- No dependency between them

---

## Implementation Plan

### Phase 1: Enhance Extraction Prompt (Week 1)

**File:** `/app/backend/superintelligent_ai_service.py`

**Add BCP-Specific Patterns:**

```python
EXTRACTION_PROMPT_V2 = """
EXTRACT THE FOLLOWING FROM THIS BCP DOCUMENT:

1. SWIM LANES / COLUMNS (Critical for BCPs):
   Pattern Detection:
   - Look for: "Onshore Actions", "Offshore Actions", "FSC Actions", "DSC Actions"
   - Look for: "IDENTIFY", "ASSESS", "MITIGATE" (3-lane structure)
   - Look for: Visual columns in flowchart layout
   - Look for: Section headers indicating different team responsibilities
   
   Output:
   {
     "swimLanes": [
       {"id": "identify", "title": "IDENTIFY", "team": "Dispatch"},
       {"id": "onshore", "title": "ONSHORE ACTIONS", "team": "Onshore Supervisor"},
       {"id": "offshore", "title": "OFFSHORE ACTIONS", "team": "Offshore Team"}
     ]
   }

2. BCP DECISION POINTS (Enhanced Detection):
   Pattern Detection:
   - "[System Name] down" → YES/NO decision
   - "[System Name] outage" → YES/NO decision
   - "Has [X] occurred?" → YES/NO decision
   - "[X] received?" → YES/NO decision
   - "Check if [condition]" → Decision branch
   - Diamond shapes in flowchart
   
   Output:
   {
     "isDecisionPoint": true,
     "decisionText": "Has Wilsar Outage?",
     "branches": {
       "yes": {
         "description": "Proceed to BCP response",
         "nextSteps": ["notify_teams", "email_councils"]
       },
       "no": {
         "description": "Resume BAU services",
         "nextSteps": ["resume_bau"]
       }
     }
   }

3. MONITORING LOOPS (Time-Based):
   Pattern Detection:
   - "Check every [X] minutes"
   - "Check in with [Person] every [X] minutes until [condition]"
   - "Monitor [X] until [condition]"
   - "Repeat until [condition]"
   
   Output:
   {
     "isLoop": true,
     "loopType": "monitoring",
     "frequency": "every 30 minutes",
     "condition": "until services restored",
     "loopBackTo": "monitor_status_node_id",
     "exitCondition": "Services restored"
   }

4. PARALLEL ACTIVITIES (Team-Based):
   Pattern Detection:
   - Steps in different swim lanes at same level
   - Different actors with no dependency
   - Simultaneous actions indicated by:
     * "Meanwhile"
     * "At the same time"
     * "Simultaneously"
     * Different column headers
   
   Output:
   {
     "parallelActivities": [
       {
         "swimLane": "onshore",
         "steps": ["notify_teams", "email_councils", "send_modica"]
       },
       {
         "swimLane": "offshore",
         "steps": ["reallocate_tasks", "begin_timeline", "email_monitoring"]
       }
     ],
     "synchronizationPoint": "services_restored"  // Where parallel paths merge
   }

5. CONTACTS & EMERGENCY INFO:
   Extract all:
   - Emergency contacts with phone numbers
   - Escalation contacts
   - System contacts (e.g., Wilson IT: 0061 8 9415 2888 ext. 8088)
   - Include in quickReference.emergencyContacts

OUTPUT STRUCTURE:
{
  "documentType": "BCP",
  "title": "Wilsar Outage Response",
  "swimLanes": [...],
  "steps": [
    {
      "swimLane": "identify",
      "level": 1,
      "isDecisionPoint": true,
      "decisionText": "Has Wilsar Outage?",
      "branches": {...}
    },
    {
      "swimLane": "onshore",
      "level": 2,
      "parallelWith": ["offshore_1"],
      "actor": "Onshore Supervisor",
      "title": "Notify Teams",
      ...
    }
  ],
  "loops": [...],
  "emergencyContacts": {...}
}
"""
```

### Phase 2: Enhance Positioning Logic (Week 2)

**File:** `/app/backend/eroad_style_enhancer.py`

**Add Multi-Lane Positioning:**

```python
def position_swim_lanes(nodes, swim_lanes):
    """
    Position nodes across multiple swim lanes
    Supports 2-4 lanes
    """
    if not swim_lanes:
        # Fallback to single center lane
        return position_single_lane(nodes)
    
    # Calculate lane positions
    canvas_width = 900
    lane_count = len(swim_lanes)
    lane_width = canvas_width / lane_count
    
    # Assign X position to each lane
    lane_positions = {}
    for i, lane in enumerate(swim_lanes):
        lane_center = (i * lane_width) + (lane_width / 2)
        lane_positions[lane['id']] = {
            'x': lane_center - 120,  # Center of 240px node
            'title': lane['title']
        }
    
    # Position nodes by swim lane
    lane_nodes = {}
    for node in nodes:
        lane_id = node.get('swimLane', 'default')
        if lane_id not in lane_nodes:
            lane_nodes[lane_id] = []
        lane_nodes[lane_id].append(node)
    
    # Assign positions
    y_position = 40
    levels = {}  # Track Y levels for parallel detection
    
    for node in nodes:
        lane_id = node.get('swimLane', 'default')
        level = node.get('level', 0)
        
        if level not in levels:
            levels[level] = y_position
            y_position += 150
        
        node['x'] = lane_positions[lane_id]['x']
        node['y'] = levels[level]
    
    return nodes

def detect_merge_points(nodes):
    """
    Detect where parallel paths converge
    """
    # Count incoming connections per node
    incoming = {}
    for node in nodes:
        for target_id in node.get('connections', []):
            if target_id not in incoming:
                incoming[target_id] = []
            incoming[target_id].append(node['id'])
    
    # Mark merge points
    for node in nodes:
        if node['id'] in incoming and len(incoming[node['id']]) > 1:
            node['isMergePoint'] = True
            # Center merge points
            node['x'] = 330
```

### Phase 3: Add Visual Verification UI (Week 3)

**New Component:** `/app/frontend/src/components/StructureVerification.js`

**Purpose:** Show detected structure BEFORE generating flowchart

```javascript
const StructureVerification = ({ analysis, onConfirm, onEdit }) => {
  const [swimLanes, setSwimLanes] = useState(analysis.swimLanes);
  const [decisions, setDecisions] = useState(analysis.decisions);
  const [parallels, setParallels] = useState(analysis.parallels);
  const [loops, setLoops] = useState(analysis.loops);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold mb-6">
        Verify Document Structure
      </h2>
      
      {/* Swim Lanes */}
      <section className="mb-6">
        <h3 className="text-lg font-semibold mb-3">
          📊 Detected Swim Lanes ({swimLanes.length})
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {swimLanes.map(lane => (
            <div key={lane.id} className="p-4 border rounded-lg">
              <div className="font-bold">{lane.title}</div>
              <div className="text-sm text-slate-600">{lane.team}</div>
              <div className="text-xs text-slate-500 mt-2">
                {lane.stepCount} steps
              </div>
            </div>
          ))}
        </div>
        <button className="mt-2 text-sm text-blue-600">
          ✏️ Edit swim lanes
        </button>
      </section>

      {/* Decision Points */}
      <section className="mb-6">
        <h3 className="text-lg font-semibold mb-3">
          ◊ Detected Decision Points ({decisions.length})
        </h3>
        {decisions.map(decision => (
          <div key={decision.id} className="p-4 bg-amber-50 border border-amber-200 rounded-lg mb-2">
            <div className="font-bold">{decision.text}</div>
            <div className="flex gap-4 mt-2">
              <div className="text-sm">
                <span className="font-semibold text-green-600">✓ YES:</span> {decision.branches.yes.description}
              </div>
              <div className="text-sm">
                <span className="font-semibold text-red-600">✗ NO:</span> {decision.branches.no.description}
              </div>
            </div>
          </div>
        ))}
      </section>

      {/* Parallel Activities */}
      <section className="mb-6">
        <h3 className="text-lg font-semibold mb-3">
          ⇄ Detected Parallel Activities ({parallels.length} groups)
        </h3>
        {parallels.map((group, i) => (
          <div key={i} className="p-4 bg-blue-50 border border-blue-200 rounded-lg mb-2">
            <div className="font-semibold mb-2">Group {i + 1} (Simultaneous)</div>
            <div className="grid grid-cols-2 gap-4">
              {group.activities.map(activity => (
                <div key={activity.id} className="text-sm">
                  <span className="font-medium">{activity.swimLane}:</span> {activity.title}
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>

      {/* Monitoring Loops */}
      <section className="mb-6">
        <h3 className="text-lg font-semibold mb-3">
          ↻ Detected Monitoring Loops ({loops.length})
        </h3>
        {loops.map(loop => (
          <div key={loop.id} className="p-4 bg-purple-50 border border-purple-200 rounded-lg mb-2">
            <div className="font-bold">{loop.title}</div>
            <div className="text-sm text-slate-600 mt-1">
              Frequency: {loop.frequency}
            </div>
            <div className="text-sm text-slate-600">
              Until: {loop.exitCondition}
            </div>
          </div>
        ))}
      </section>

      {/* Actions */}
      <div className="flex gap-4 mt-8">
        <button 
          onClick={onConfirm}
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
        >
          ✓ Looks Good - Generate Flowchart
        </button>
        <button 
          onClick={onEdit}
          className="px-6 py-3 border border-slate-300 rounded-lg font-semibold hover:bg-slate-50"
        >
          ✏️ Edit Structure
        </button>
      </div>
    </div>
  );
};
```

---

## Testing Plan

### Test Documents
Your 4 BCPs serve as test cases:

**Test Case 1: Wilsar Outage**
- Expected: 3 swim lanes (Identify, Onshore, Offshore)
- Expected: Decision "Has Wilsar Outage?" (YES/NO)
- Expected: Parallel onshore/offshore actions
- Expected: Loop "Check every 30 minutes"

**Test Case 2: GDS Outage**
- Expected: 2 swim lanes (FSC/DSC, Main flow)
- Expected: Decision "GDS down" (YES/NO)
- Expected: Loop monitoring

**Test Case 3: Internet Outage**
- Expected: 3 swim lanes (Identify, Assess, Mitigate)
- Expected: Decision "All applications affected?"
- Expected: Parallel onshore/offshore tasks

**Test Case 4: RingCentral Outage**
- Similar structure validation

### Success Metrics
- ✅ AI detects 100% of swim lanes
- ✅ AI detects 100% of decision points
- ✅ AI detects 90%+ of parallel activities
- ✅ AI detects 90%+ of monitoring loops
- ✅ User verification UI shows all structures correctly
- ✅ Generated flowchart matches your BCP layout

---

## Next Steps

1. **Your Action:** Review this plan and approve
2. **My Action:** Implement Phase 1 (Week 1) - Enhanced extraction prompts
3. **Your Action:** Test with your 4 BCPs
4. **My Action:** Iterate based on your feedback
5. **My Action:** Implement Phase 2 (Week 2) - Multi-lane positioning
6. **Your Action:** Test visual verification UI
7. **My Action:** Implement Phase 3 (Week 3) - User verification step
8. **Your Action:** Final approval and production deployment

---

## Timeline Summary

**Week 1:** Enhanced AI prompts with BCP patterns
**Week 2:** Multi-lane positioning logic
**Week 3:** Visual verification UI + testing
**Week 4:** Polish and production deployment

**Total: 4 weeks to production-ready BCP intelligence**

---

## Questions for You

1. Are these the primary BCP patterns you need? Any others?
2. Do your BCPs follow this structure consistently, or are there variations?
3. Would you like to see a live demo of the enhanced AI on one of your BCPs?
4. Any specific BCP language/terminology I should add to detection patterns?

Please approve this plan so I can begin implementation! 🚀
