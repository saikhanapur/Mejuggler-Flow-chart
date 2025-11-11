# Visual Intelligence Implementation Plan
## Enterprise-Grade Flowchart Visualization

### CURRENT STATE ANALYSIS

**✅ Frontend (FlowNode.js) - READY**
- Decision diamonds implemented (lines 122-180)
- Different status colors configured
- Icons for each status type
- Merge point indicators

**❌ Backend (eroad_style_enhancer.py) - NEEDS FIX**
- Prompt asks for isDecisionPoint, but AI not reliably setting it
- Need stronger detection logic
- Need explicit examples in prompt

**❌ Missing Features**
- Loop visualization (curved arrows)
- Gap highlighting (red/amber borders)
- Parallel process indicators
- Critical path highlighting

---

### PHASE 1: DECISION POINT DETECTION (Priority 1)

**Problem**: AI receives prompt to detect decisions but doesn't always set `isDecisionPoint: true`

**Solution**: Enhanced prompt with explicit patterns + post-processing validation

**Implementation**:
1. Strengthen prompt with explicit examples
2. Add decision pattern detection
3. Post-process nodes to force isDecisionPoint based on keywords
4. Validate decisionCriteria is human-readable

**Patterns to detect**:
- "if", "check if", "verify whether"
- "has [X] happened?", "is [Y] true?"
- "YES/NO", "true/false" branches
- "depends on", "conditional"

---

### PHASE 2: LOOP VISUALIZATION (Priority 2)

**Current**: isLoop flag exists but no visual indicator

**Solution**:
1. Add curved arrow component (SVG path)
2. Connect looping node back to loopBackTo target
3. Add "↻" icon on looping nodes
4. Label with loop condition ("Until X" or "Every 30 min")

---

### PHASE 3: GAP HIGHLIGHTING (Priority 3)

**Current**: Gaps stored in `operationalDetails.gap` but not visually highlighted

**Solution**:
1. Add left border indicator (4px amber/red)
2. Add gap count badge ("⚠️ 2 gaps")
3. Pulsing animation for critical gaps
4. Gap severity levels (info/warning/critical)

---

### PHASE 4: PARALLEL PROCESS INDICATORS (Priority 4)

**Current**: parallelWith exists but no clear visual

**Solution**:
1. Horizontal line connecting parallel nodes
2. "PARALLEL" label
3. Same Y-position enforcement
4. Visual grouping box (optional)

---

### PHASE 5: ENHANCED STATUS DIFFERENTIATION (Priority 5)

**Current**: All statuses have colors, but could be clearer

**Solution**:
1. Size variation (critical = larger)
2. Animation (critical = pulse)
3. Icon prominence
4. Shadow intensity

---

### FILES TO MODIFY

1. `/app/backend/eroad_style_enhancer.py`
   - Strengthen decision detection prompt
   - Add post-processing validation
   - Better loop detection

2. `/app/frontend/src/components/flowchart/FlowNode.js`
   - Add gap indicator
   - Add loop icon
   - Enhance decision diamond

3. `/app/frontend/src/components/flowchart/ConnectionLine.js`
   - Add loop arrows (curved)
   - Add parallel indicators

4. `/app/frontend/src/components/flowchart/FlowchartDisplay.js` or `FlowchartCanvas.js`
   - Overall layout logic
   - Gap summary banner

---

### SUCCESS CRITERIA

✅ Decision nodes render as yellow diamonds
✅ Loop nodes show curved arrow back
✅ Nodes with gaps have amber/red left border
✅ Parallel nodes visually grouped
✅ Clear visual hierarchy (critical > action > monitoring)
✅ Mobile-responsive (field worker ready)
✅ Tesla/SpaceX quality level

---

### TESTING DOCUMENTS

1. **Wilsar BCP** - Has decisions ("Has Wilsar Outage? YES/NO")
2. **System Incident** - Has loops ("Check every 30 minutes")
3. **Recruitment** - Linear process (control case)
4. **Product Recall** - Parallel activities + decisions
