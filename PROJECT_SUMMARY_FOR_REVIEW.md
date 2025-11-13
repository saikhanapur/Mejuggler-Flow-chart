# SOP-to-Flowchart Application - Technical Summary

## Business Context
Transform complex Standard Operating Procedure documents (BCPs, SOPs) into accurate, interactive AI-generated flowcharts. Target users: Operations teams managing business continuity procedures.

**Core Value Proposition:** Simplify complex processes through visual flowcharts that correctly identify decision points, loops, swim lanes, and parallel workflows - NOT simple linear diagrams.

---

## Tech Stack
- **Frontend:** React, TailwindCSS
- **Backend:** FastAPI (Python), Pydantic models
- **Database:** MongoDB
- **AI:** Claude Sonnet 4 via Emergent LLM integration
- **Architecture:** React frontend → FastAPI → SuperintelligentAIService (extraction) → EROADStyleEnhancer (visualization) → MongoDB → Frontend rendering

---

## What's Been Built

### Working Components:
1. **Document Upload & Processing** - PDF/text parsing working
2. **AI Extraction Pipeline** - Extracts steps, contacts, timings from documents
3. **Node Generation** - Creates 10-15 consolidated flowchart nodes
4. **Frontend Rendering** - FlowNode.js renders regular nodes, decision diamonds, loop badges
5. **Basic Flowchart Display** - Nodes, edges, connections render correctly

### Recently Fixed (Current Session):
1. **Swim Lane Detection** - Now extracts role-based sections (Onshore/Offshore/FSC)
2. **Swim Lane Assignment** - Nodes matched to lanes via content scoring algorithm
3. **Loop Connections** - Auto-fixes `loopBackTo` target if missing
4. **Edge Generation** - Converts node `connections` array to `edges` array
5. **Decision Detection** - More conservative (only real branches, not verifications)
6. **Frontend Swim Lane Rendering** - Colored horizontal bands with headers

---

## Critical Shortcomings

### Issue 1: Swim Lane Assignment Not Working in Production
**Symptom:** User uploads through UI → swim lanes created but nodes NOT assigned (0/10)
**Root Cause:** Code reads swim lanes from `extracted_data.get('swimLanes')`, but UI passes data in `detection` object. Fixed with fallback: `extracted_data.get('swimLanes', []) or detection.get('swimLanes', [])`
**Status:** Fixed in code, backend restarted, AWAITING user test

### Issue 2: Parallel Processes Hidden
**Problem:** Document has 5+ simultaneous communications (SMS, Email, Calls) but rendered as single sequential node "Stakeholder Communications"
**Impact:** Loses critical timing information - appears sequential when it's parallel
**Not Yet Implemented**

### Issue 3: Context Gathering Feature Missing
**Problem:** Frontend has `SmartQuestionPanel` and `ContextAdder` components, but backend never generates `suggested_questions`
**User Expectation:** AI asks clarifying questions post-upload, user adds context (voice/chat/docs), then enhanced flowchart generated
**Status:** UI exists, backend logic missing

### Issue 4: Over-Consolidation
**Problem:** 30-40 procedural steps → 10 nodes (too aggressive grouping)
**Example:** RingCentral doc has 38 steps → only 10 nodes generated
**Impact:** Loses procedural granularity

### Issue 5: Share/Export Buttons Non-Functional
**Problem:** Share, PDF Export, HTML Export buttons exist but don't work
**Status:** Not implemented

---

## Current Challenge: Verification Deadlock

**Timeline:**
1. User reported swim lanes not showing (multiple uploads)
2. Agent implemented fixes, tested in isolation → works perfectly
3. Generated test process directly via Python → database shows 10/10 nodes assigned to lanes
4. User uploads via UI → swim lanes created but 0/10 nodes assigned
5. Agent identified data source mismatch, fixed code, restarted backend
6. **NOW:** Awaiting user to upload again to verify fix works in production

**The Problem:** Can't verify fixes work through UI upload until user tests. User frustrated by repeated failures. Agent can't test UI upload flow directly (no file upload mechanism in testing).

---

## What Needs to Be Built (Priority Order)

### P0 - Critical (Blocks Core Functionality):
1. **Verify swim lane fix works through UI upload** (in progress)
2. **Implement parallel process detection & rendering**
   - Detect simultaneous activities from text cues
   - Position nodes at same Y-coordinate in different lanes
   - Visual indicator for "happens simultaneously"

3. **Implement Context Gathering backend logic**
   - Generate `suggested_questions` from initial analysis
   - Create endpoint to receive user context additions
   - Re-run enhancement with added context

### P1 - High (Quality Issues):
4. **Fix decision diamond positioning** - Y-coordinate calculation causing overlaps
5. **Detect 2nd decision point** - Time-based decisions (e.g., "If no response in 15 min") missed
6. **Reduce consolidation aggression** - Keep more procedural detail (aim for 15-20 nodes from 30-40 steps)

### P2 - Medium (Feature Completion):
7. **Implement Share feature** - Generate shareable link
8. **Implement PDF Export** - Convert flowchart to PDF
9. **Implement HTML Export** - Standalone HTML file

---

## Key Files to Review

### Backend Core:
- `/app/backend/server.py` - API endpoints, Pydantic models (lines 160-210 for ProcessNode model)
- `/app/backend/superintelligent_ai_service.py` - AI extraction logic, prompts (lines 75-150 for structure detection)
- `/app/backend/eroad_style_enhancer.py` - Visualization enhancement, swim lane assignment (lines 405-470)

### Frontend Core:
- `/app/frontend/src/components/flowchart/FlowchartDisplay.js` - Main rendering, swim lane backgrounds
- `/app/frontend/src/components/flowchart/FlowNode.js` - Individual node rendering (diamond logic lines 121-221)
- `/app/frontend/src/components/ProcessCreator.js` - Upload flow, SmartQuestionPanel integration (lines 525-590)

### Critical Data Flow:
```
Document Upload 
  → POST /api/process/eroad-style (server.py:3130)
  → SuperintelligentAIService.generate_eroad_style_flowchart() (line 1087)
  → analyze_document() (extraction)
  → EROADStyleEnhancer.enhance_for_visualization() (line 28)
  → [Swim lane creation lines 405-470]
  → [Node assignment lines 431-468]
  → [Edge conversion lines 675-696]
  → MongoDB save
  → Frontend render
```

---

## Testing Notes

**Isolated testing works:** Test script shows 12/12 nodes assigned to lanes, proper loops, edges.
**UI upload broken:** User uploads → 0/10 nodes assigned (until recent fix).
**Root cause identified:** Data source mismatch between test environment and production UI endpoint.
**Fix applied:** Line 407-410 in eroad_style_enhancer.py now reads from both sources.
**Status:** Backend restarted, awaiting user verification.

---

## Questions for Reviewing Agent

1. **Is the swim lane data source fix correct?** (line 407-410 in eroad_style_enhancer.py)
2. **How to detect parallel processes from text?** Need algorithm to identify simultaneous activities
3. **Best approach for context gathering?** Generate questions before or after initial flowchart?
4. **How to reduce over-consolidation?** Current logic: 30 steps → 10 nodes (too aggressive)
5. **Any architectural issues in data flow?** Current: Analysis → Enhancement → Save → Render

---

## Success Criteria

✅ **Swim lanes:** Visible colored bands, nodes assigned to correct lanes
✅ **Loops:** Purple dashed arrows going back to target
✅ **Decisions:** Yellow diamonds only at real branch points (not verifications)
✅ **Parallel processes:** Simultaneous activities shown at same Y-coordinate
✅ **Context gathering:** Smart questions displayed, user can add context
✅ **Granularity:** 15-20 nodes from 30-40 step documents (not 10)

Current Status: First 3 items fixed in code, awaiting user confirmation via new upload.
