# Complete AI Logic - How SuperHumanly Processes Documents

## Overview: The AI Pipeline

Our AI system uses a **3-Phase Processing Pipeline**:
```
Phase 1: Document Intelligence (superintelligent_ai_service.py)
    ↓ Extracts raw structure + operational details
Phase 2: Enhancement & Grouping (eroad_style_enhancer.py)
    ↓ Groups into 8-13 nodes, enriches with purpose/gap analysis
Phase 3: Positioning & Visualization (Backend + Frontend)
    ↓ Calculates coordinates, renders flowchart
```

Let's go deep into each phase.

---

## Phase 1: Document Intelligence (The Brain)

**File**: `/app/backend/superintelligent_ai_service.py`  
**AI Model**: Claude Sonnet 4 (Anthropic)  
**Purpose**: Extract meaning, not just text

### Step 1A: Document Analysis (Lines 120-250)
```python
# AI reads the document and creates a "skeleton" - high-level process overview

PROMPT:
"Analyze this document. What is the main process? What are the key phases?"

AI RESPONSE:
{
  "processName": "GDS Outage Business Continuity Plan",
  "processType": "incident_response",
  "phases": [
    "Detection & Alert",
    "Initial Response",
    "Monitoring & Communication",
    "Recovery Verification"
  ]
}
```

**What AI Assesses:**
- Document type (BCP, SOP, Policy, Incident Response)
- Main goal/purpose
- High-level phases
- Time-criticality

### Step 1B: Step Extraction (Lines 300-450)
```python
# AI extracts individual steps with context

PROMPT:
"Extract EVERY distinct step. For each, identify:
1. What happens (action)
2. Who does it (role/system)
3. When it happens (sequence/timing)
4. Why it matters (purpose)
5. What's needed (inputs/data)
6. What could go wrong (gaps/risks)"

AI RESPONSE (per step):
{
  "step_number": 3,
  "action": "Alert Field Operations Teams",
  "actor": "Incident Manager",
  "trigger": "After confirming GDS outage",
  "purpose": "Ensure field teams are aware and can adjust operations",
  "systems": ["Email", "Slack"],
  "contacts": ["Operations Manager: 0800-123-456"],
  "timing": "Within 5 minutes of confirmation"
}
```

**How AI Determines Importance:**
1. **Keywords**: "critical", "urgent", "immediately", "within X minutes"
2. **Position**: First/last steps are usually important
3. **Dependencies**: Steps that many others depend on
4. **Consequences**: Steps with "if not done, X will fail"
5. **Stakeholders**: More stakeholders = more important

### Step 1C: Operational Details Extraction (Lines 500-650)
```python
# AI digs DEEP into each step to find actionable details

PROMPT (for each step):
"Extract operational specifics:
- Specific actions (HOW-TO steps)
- Required data fields
- Contact information
- Systems/tools
- Timelines
- Email templates
- Decision criteria"

AI RESPONSE:
{
  "step_3_details": {
    "specificActions": [
      "Open Slack channel #ops-emergency",
      "Send pre-approved template message",
      "Call operations manager",
      "Log notification in incident tracker"
    ],
    "requiredData": ["Outage start time", "Affected areas", "Expected duration"],
    "contactInfo": {
      "Operations Manager": "John Smith: 0800-123-456",
      "Backup Contact": "Jane Doe: 0800-789-012"
    },
    "systems": ["Slack", "Incident Tracker", "Email"],
    "timeline": "Within 5 minutes",
    "emailTemplates": ["URGENT: GDS Outage - Manual Operations Required..."]
  }
}
```

**This is where AI adds REAL VALUE** - it doesn't just copy text, it understands context.

---

## Phase 2: Enhancement & Grouping (The Intelligence)

**File**: `/app/backend/eroad_style_enhancer.py`  
**Purpose**: Transform 20 steps into 8-13 intelligent nodes

### Step 2A: Intelligent Grouping (Lines 100-200)
```python
# AI groups steps that belong together

PROMPT:
"You have 20 steps. Group them into 8-13 logical nodes.
Rules:
1. Each node = one strategic decision or action group
2. Don't over-group - preserve important details
3. Group only if steps are:
   - Same phase (e.g., all 'monitoring' steps)
   - Same actor (e.g., all 'Field Team' actions)
   - Happen simultaneously
   - Are sub-tasks of same parent action"

EXAMPLE:
Original Steps:
1. Open email client
2. Select template "Outage Alert"
3. Add recipients from distribution list
4. Send email
5. Log send confirmation

Grouped Node:
"Notify Stakeholders via Email"
  purpose: "Ensure awareness across organization"
  specificActions: [original steps 1-5]
```

**Grouping Logic:**
```python
# Pseudo-code of how AI thinks

def should_group(step_a, step_b):
    if same_phase(step_a, step_b) and same_actor(step_a, step_b):
        if delta_time(step_a, step_b) < 5_minutes:
            return True  # Group them
    
    if step_b.action.startswith("Log") and step_a has_primary_action:
        return True  # Logging is a sub-task
    
    if step_a.timing == step_b.timing and "simultaneously" in document:
        return True  # Parallel actions
    
    return False  # Keep separate
```

### Step 2B: Purpose Extraction (Lines 150-180)
```python
# AI identifies WHY each node exists (not just WHAT it does)

PROMPT:
"For each node, explain the PURPOSE - the goal, not the process.
Think: Why does this step exist? What problem does it solve?"

EXAMPLES:
❌ BAD: "Send emails to stakeholders"
✅ GOOD: "Ensure all parties are aware of the outage and can adjust operations"

❌ BAD: "Check system status every 30 minutes"
✅ GOOD: "Maintain situational awareness and detect resolution"

❌ BAD: "Create manual dispatch jobs"
✅ GOOD: "Ensure business continuity when automated systems are down"
```

**Why This Matters:**
- Users understand the "why" at a glance
- Helps identify if steps are actually needed
- Reveals gaps ("We do X but there's no purpose for it")

### Step 2C: Gap Analysis (Lines 170-190)
```python
# AI compares current state vs. ideal state

PROMPT:
"For each node, analyze:
1. Current State: How is this done now? (from document)
2. Ideal State: How SHOULD it be done? (best practices)
3. Gap: What's missing, broken, or risky?"

EXAMPLE:
Node: "Monitor System Restoration"
Current State: "Manual checks every 30 minutes via dashboard"
Ideal State: "Automated alerts when thresholds are met"
Gap: "No automation - relies on human remembering to check"
```

**How AI Identifies Gaps:**
1. **Manual vs. Automated**: "Manual X" → Gap: "Should be automated"
2. **Time-based**: "Check every 30 min" → Gap: "Should be real-time alerts"
3. **Single point of failure**: "Only manager can approve" → Gap: "No backup process"
4. **Missing information**: "Contact support" (no number) → Gap: "Missing contact details"
5. **Implicit assumptions**: "Team will coordinate" → Gap: "No defined coordination method"

### Step 2D: Connection Logic (Lines 240-340)
```python
# How AI determines which nodes connect to which

LOGIC:
1. SEQUENTIAL: Node A → Node B if:
   - B happens after A chronologically
   - B depends on A's output
   - Document says "then", "after", "next"

2. PARALLEL: Node A → [Node B, Node C] if:
   - B and C both follow A
   - Document says "meanwhile", "simultaneously", "at the same time"
   - B and C have same trigger but different actors

3. DECISION: Node A → [Node B (YES), Node C (NO)] if:
   - Document says "if", "check if", "verify whether"
   - Two distinct paths based on condition

4. MERGE: [Node A, Node B] → Node C if:
   - Both A and B connect to C
   - C is mentioned after both A and B complete
   - Document says "after both", "once all teams", "when complete"

5. LOOP: Node A → Node B → Node A if:
   - Document says "repeat until", "check every X minutes"
   - Condition-based cycling
```

**CRITICAL ISSUE (Why Connections Can Be Missing):**
```python
# Current logic relies on AI explicitly specifying connections

Node: {
  "id": "node_3",
  "connections": ["node_4", "node_5"]  # ← AI MUST LIST THESE
}

# If AI doesn't list a connection, it won't exist!
# This happens when:
1. Document doesn't explicitly state "then do X"
2. AI over-simplifies the flow
3. Implicit connections (obvious to humans, not to AI)
```

---

## Phase 3: Positioning & Visualization

**File**: `/app/backend/eroad_style_enhancer.py` (Lines 250-310)  
**Purpose**: Calculate X, Y coordinates for visual layout

### Positioning Algorithm
```python
y_position = 40  # Start position
processed_ids = set()

# Step 1: Detect merge points (multiple nodes → one node)
merge_points = detect_merge_points(nodes)

# Step 2: Position each node
for node in nodes:
    if node.id in processed_ids:
        continue
    
    # Check if this is part of a parallel group
    if node.parallelWith:
        # Position side-by-side
        parallel_nodes = get_parallel_group(node)
        if len(parallel_nodes) == 2:
            parallel_nodes[0].x = 200  # Left
            parallel_nodes[1].x = 460  # Right
        elif len(parallel_nodes) == 3:
            parallel_nodes[0].x = 150  # Left
            parallel_nodes[1].x = 330  # Center
            parallel_nodes[2].x = 510  # Right
        
        # Same Y for all parallel
        for pnode in parallel_nodes:
            pnode.y = y_position
        
        y_position += 170  # Extra spacing for parallel
    
    elif node.id in merge_points:
        # Merge point - add extra spacing
        y_position += 30
        node.x = 330  # Center
        node.y = y_position
        node.isMergePoint = True
        y_position += 150
    
    else:
        # Sequential node
        node.x = 330  # Center
        node.y = y_position
        y_position += 150
```

---

## What's Missing: Why Connections Fail

### Problem 1: AI Doesn't Always Specify Connections
```python
# AI might output:
{
  "id": "handle_jobs_manually",
  "title": "Handle Incoming Council Jobs Manually",
  "connections": []  # ← EMPTY! Missing next step
}

# Should be:
{
  "id": "handle_jobs_manually",
  "connections": ["verify_recovery"]  # ← Explicit connection
}
```

**Why This Happens:**
1. **Document ambiguity**: "Teams handle jobs manually" (doesn't say "then what?")
2. **AI assumes implied flow**: AI thinks it's obvious next step
3. **Parallel path confusion**: AI knows parallel paths should merge but forgets to connect

### Problem 2: Missing Validation
```python
# We don't currently validate that ALL nodes have outgoing connections
# (except the final node)

# Should add:
for node in nodes:
    if node != final_node and len(node.connections) == 0:
        logger.warning(f"Node {node.id} has no outgoing connections!")
        # Auto-connect to next sequential node
        node.connections.append(next_node.id)
```

---

## Is the AI "Learning"?

### Short Answer: **No, not in the traditional sense**

**What it DOES:**
- ✅ Follows rules in prompts
- ✅ Uses pattern matching (similar docs → similar structures)
- ✅ Improves when we update prompts with new rules

**What it DOESN'T do:**
- ❌ Remember previous documents
- ❌ Self-correct based on user edits
- ❌ Improve automatically over time

### How We Can Make It "Learn"

**Option 1: Prompt Engineering (Current)**
```python
# When user says "connection missing", we update prompt:

OLD PROMPT:
"Generate nodes with connections"

NEW PROMPT:
"Generate nodes with connections. CRITICAL:
- Every non-final node MUST have at least one outgoing connection
- Parallel paths MUST converge to a merge point
- Decision branches MUST have both YES and NO paths defined"
```

**Option 2: Feedback Loop (Future)**
```python
# Capture user edits and feed back to AI

user_edits = {
  "added_connection": {
    "from": "handle_jobs_manually",
    "to": "verify_recovery"
  }
}

# Next generation, AI sees:
"Previous similar document had these corrections:
- Added connection from manual handling to recovery verification
- This suggests parallel paths should merge at recovery verification"
```

**Option 3: Fine-Tuning (Advanced)**
```python
# Train AI on examples of:
# Input: Document
# Output: Perfect flowchart with all connections

# Requires 50+ examples to be effective
```

---

## Immediate Fix: Connection Validation

### What I'll Implement Now:
```python
# In eroad_style_enhancer.py, after AI generates nodes:

# Step 1: Identify terminal node (no more steps after it)
terminal_nodes = [node for node in nodes if 'recovery' in node.title.lower() or 'complete' in node.title.lower()]

# Step 2: Validate all non-terminal nodes have connections
for i, node in enumerate(nodes):
    if node in terminal_nodes:
        continue  # Final node, OK to have no connections
    
    if not node.get('connections') or len(node['connections']) == 0:
        # Missing connection! Auto-fix:
        # Option A: Connect to next node in sequence
        if i + 1 < len(nodes):
            node['connections'] = [nodes[i + 1]['id']]
            logger.info(f"Auto-connected {node['id']} → {nodes[i + 1]['id']}")
        
        # Option B: If parallel, connect to common merge point
        elif node.get('parallelWith'):
            # Find merge point (next node that's not parallel)
            for future_node in nodes[i+1:]:
                if not future_node.get('parallelWith'):
                    node['connections'] = [future_node['id']]
                    logger.info(f"Auto-connected parallel {node['id']} → merge {future_node['id']}")
                    break
```

---

## Summary: Current AI Intelligence

### What AI Does Well:
✅ Extracts operational details (contacts, systems, timings)
✅ Identifies purpose (WHY, not just WHAT)
✅ Detects parallel flows (keywords: "meanwhile", "simultaneously")
✅ Recognizes decision points (keywords: "if", "check if")
✅ Groups related steps intelligently
✅ Performs gap analysis (current vs. ideal state)

### What AI Struggles With:
❌ **Implicit connections** (obvious to humans, not stated in document)
❌ **Merge point connections** (parallel paths should converge)
❌ **Loop back connections** (repeat until X)
❌ **Cross-reference connections** (Step 5 refers back to Step 2)

### How We're Improving:
1. **Better prompts** (more explicit rules)
2. **Validation logic** (catch missing connections)
3. **Learning from examples** (you provide ideal layouts, we extract patterns)
4. **Feedback loops** (capture user edits, teach AI)

---

## Your Specific Case: Missing Connection

**What Happened:**
```
Node: "Handle Incoming Council Jobs Manually"
  connections: []  ← EMPTY!

AI thought: "This is ongoing, no clear next step in document"
Should be: connections: ["verify_recovery"] or ["monitor_restoration"]
```

**Why:**
- Document likely says "Teams handle jobs manually" (period)
- Doesn't explicitly say "then verify recovery"
- AI doesn't infer the logical flow

**Fix:** I'll implement connection validation that auto-connects orphaned nodes.

---

Ready to implement the connection validation fix?
