# Node Positioning & Structure Logic - Current vs. Needed

## Current Positioning Logic (How It Works Now)

### Backend: `/app/backend/eroad_style_enhancer.py`

**Sequential Processing (Lines 251-298):**
```python
y_position = 40  # Start with top padding
processed_ids = set()

for node in nodes:
    if node['id'] in processed_ids:
        continue
    
    parallel_with = node.get('parallelWith', [])
    
    if parallel_with:
        # PARALLEL FLOW
        # Position nodes side-by-side at same Y
        if len(parallel_nodes) == 2:
            parallel_nodes[0]['x'] = 200  # Left
            parallel_nodes[1]['x'] = 460  # Right
            # Both get same Y
        y_position += 170  # Move down for next group
    else:
        # SEQUENTIAL FLOW
        node['x'] = 330  # Center
        node['y'] = y_position
        y_position += 150  # Move down
```

**AI's Role:**
- Phase 1: Extract steps from document
- Phase 2: Group into 8-13 nodes
- Phase 3: Detect parallel with keywords ("meanwhile", "at the same time")
- Phase 4: Mark with `parallelWith: ["other_node_id"]`

**Connection Logic:**
- Simple: node A connects to node B based on `connections: ["node_B_id"]`
- No merge point detection
- No consideration of visual clarity

---

## Problems with Current Logic

### 1. **Parallel Flow Confusion**
**Issue**: When 2+ parallel paths merge back, the logic doesn't handle it well
```
Example:
Node 1 (Y=40, X=330)
   ↓
Node 2 (Y=190, X=200) ← Parallel Left
Node 3 (Y=190, X=460) ← Parallel Right
   ↓ ← PROBLEM: Both connect to Node 4
Node 4 (Y=360, X=330) ← Merge point

Current code creates 2 lines from Node 2 and Node 3 to Node 4
But doesn't indicate this is a MERGE POINT visually
```

### 2. **AI Misses Parallel Flows**
**Issue**: AI only detects keywords, misses logical parallelism
```
Document: "Contact Auckland Council. Contact CRS Support."
AI thinks: Sequential (no "meanwhile" keyword)
Should be: Parallel (both happen at same time)
```

### 3. **No Layout Optimization**
**Issue**: Positions are calculated sequentially, no global optimization
```
Current: Goes node-by-node (Y = Y + 150)
Needed: Consider entire graph, minimize line crossings
```

### 4. **Decision Branches Poorly Positioned**
**Issue**: YES/NO branches position based on `parallelWith`, not decision logic
```
Decision Node (Y=100, X=330)
  ↙ NO        ↘ YES
Node A        Node B
(Y=250,       (Y=250,
 X=200)        X=460)

Problem: If YES path is longer (5 steps) and NO path is shorter (2 steps),
they still get same vertical spacing, causing overlap later
```

---

## How It SHOULD Work (Ideal Logic)

### 1. **Graph-Based Layout Algorithm**
```python
# Step 1: Build directed graph
graph = {
    'node_1': ['node_2', 'node_3'],  # Branches
    'node_2': ['node_4'],
    'node_3': ['node_4'],  # Merge
    'node_4': ['node_5']
}

# Step 2: Detect graph patterns
- Parallel flows (common ancestor, common descendant)
- Decision diamonds (1 input, 2+ outputs)
- Merge points (2+ inputs, 1 output)
- Loops (cycle detection)

# Step 3: Assign layers (Y coordinates)
layer_0 = [node_1]  # Y = 40
layer_1 = [node_2, node_3]  # Y = 190 (parallel)
layer_2 = [node_4]  # Y = 360 (merge)
layer_3 = [node_5]  # Y = 510

# Step 4: Minimize crossings (X coordinates)
- Sort nodes within each layer to minimize line crossings
- Apply "barycenter heuristic" or "median heuristic"

# Step 5: Position merge points intelligently
- Merge point gets X = average of inputs
- Draw converging lines
```

### 2. **Smarter AI Parallel Detection**
```python
# Beyond keywords, analyze:
1. Same-level bullet points in document
2. "Both teams", "concurrently", "simultaneously"
3. Actions with no sequential dependency
4. Time markers ("at hour 1, at hour 1")

Example:
"Contact Auckland Council" (no "after" or "then")
"Contact CRS Support"
→ AI infers: PARALLEL (no dependency chain)
```

### 3. **Visual Merge Indicators**
```
     Node A
        ↓
     Node B ←―――――┐
        ↓        │
     Node C      │
        ↓     Node D (parallel)
        ↓        │
     [MERGE]←―――――┘
        ↓
     Node E

[MERGE] could be:
- Diamond shape (merge point)
- Thicker node border
- Different color
```

---

## Can We Learn from Examples? (Your Question)

### Short Answer: **YES**, with two approaches:

### Approach A: **Prompt Engineering with Examples** (Faster, No Code Change)

**How it works:**
1. You provide 3-5 examples: PDF → Ideal Flowchart screenshot
2. We extract positioning rules from those examples
3. Update AI prompt with those rules

**Example:**
```
You provided:
- PDF: "GDS Outage BCP"
- Flowchart: Shows decision diamond at Y=200, parallel nodes at X=150/330/510

We extract rule:
"For BCPs with outage detection, place decision diamond after initial alert,
then branch to parallel response teams (left/center/right spacing: 150/330/510)"

Add to prompt:
"For Business Continuity Plans:
- First node: Trigger/alert (Y=40, X=330)
- Second node: Decision (Y=190, X=330, diamond shape)
- YES branch: 2-3 parallel response nodes (X=150/330/510)
- NO branch: Monitoring loop (X=330, Y increases)
- Merge at recovery verification (X=330)"
```

**Implementation:**
- Takes 1-2 hours per example to extract rules
- Update `eroad_style_enhancer.py` prompt
- No architecture change needed

**Limitations:**
- Only works for document types you've seen
- Can't generalize to completely new structures
- Requires manual rule extraction

---

### Approach B: **Few-Shot Learning / RAG** (Better, More Effort)

**How it works:**
1. Create a database of examples (PDF + Ideal Layout JSON)
2. When new document comes in, find similar example
3. Use that example's layout strategy

**Example:**
```python
# Database entry
{
  "document_type": "Business Continuity Plan",
  "structure": {
    "trigger": {"y": 40, "x": 330},
    "decision": {"y": 190, "x": 330, "shape": "diamond"},
    "parallel_responses": {
      "count": 3,
      "x_positions": [150, 330, 510],
      "y": 340
    },
    "merge": {"y": 510, "x": 330}
  }
}

# When processing new BCP:
1. AI detects document type: "Business Continuity Plan"
2. Retrieve example structure from database
3. Apply same layout strategy
4. Adjust Y spacing based on actual node count
```

**Implementation:**
- Requires vector database (store document embeddings)
- Add "template matching" before positioning
- ~2-3 days development

**Benefits:**
- Generalizes better to similar documents
- Can improve over time with more examples
- More consistent results

---

## What I Recommend

### Phase 1: **Fix Current Issues** (Immediate, ~2 hours)
1. Better merge point detection
2. Adjust Y spacing based on path length
3. Add visual merge indicators

### Phase 2: **Simple Learning** (This week, ~4 hours)
1. You provide 3-5 example pairs (PDF + ideal flowchart)
2. I extract positioning rules manually
3. Update AI prompt with those patterns
4. Test with similar documents

### Phase 3: **Advanced Learning** (Future, ~1 week)
1. Build example database
2. Implement template matching
3. RAG-based layout retrieval
4. Continuous improvement from user edits

---

## Immediate Action Items

### For You:
1. **Collect 3-5 Example Pairs:**
   - PDF documents (different types: BCP, SOP, Incident Response)
   - Corresponding "ideal" flowchart layouts (screenshots or descriptions)
   - Note what makes each layout "good"

2. **Provide Feedback on Current Output:**
   - Which specific positioning decisions are confusing?
   - What would you change?

### For Me:
1. **Fix Merge Point Logic** (today)
2. **Add Path Length Awareness** (today)
3. **Implement Phase 2 Learning** (once you provide examples)

---

## Technical Details: How to Provide Examples

### Format Option 1: Screenshots + Annotations
```
1. Upload PDF
2. Upload screenshot of ideal layout
3. Annotate: "This is parallel", "This is merge", "Decision branch spacing: 260px"
```

### Format Option 2: JSON Description
```json
{
  "document": "GDS_Outage_BCP.pdf",
  "layout_rules": {
    "node_spacing_vertical": 150,
    "parallel_spacing_horizontal": [200, 460],
    "decision_branches": {
      "yes_path_x": 460,
      "no_path_x": 200
    },
    "merge_points": [
      {"after_nodes": ["node_2", "node_3"], "merge_at": "node_4"}
    ]
  }
}
```

### Format Option 3: Interactive Review
```
1. Generate flowchart with current logic
2. You drag/reposition nodes to ideal locations
3. I capture your changes
4. Extract rules from your edits
```

---

## Summary

**Current Logic:**
- Sequential Y positioning (Y = Y + 150)
- Parallel nodes based on keywords
- No merge point awareness
- No layout optimization

**Why It's Confusing:**
- Parallel flows don't merge cleanly
- No visual indicators for structure
- Position calculation is naive

**Can We Learn?**
- **Yes! Two ways:**
  1. Prompt engineering (fast, manual)
  2. RAG/template matching (better, more effort)

**Next Steps:**
1. I fix immediate issues (merge points, path awareness)
2. You provide 3-5 example layouts
3. I extract rules and improve AI
4. We iterate until positioning is intelligent

Ready to start with Phase 1 fixes now, then Phase 2 once you share examples?
