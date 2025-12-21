# 🎯 DETAILED EXECUTION PLAN - Week 1

## PHILOSOPHY: Build Like a 10x Engineer

**Principles:**
1. **Test Before Moving Forward** - Never assume, always validate
2. **Think Dependencies** - What breaks if I change this?
3. **Measure Impact** - How does this affect accuracy?
4. **User-First** - Will users notice this improvement?
5. **No Technical Debt** - Leave code better than I found it

---

## WEEK 1: FOUNDATION BUILD

### PHASE 1: CRITICAL BUG FIXES (Day 1-2)

---

#### 🔧 TASK 1: Fix OCR (poppler-utils)

**Time Estimate:** 1 hour  
**Priority:** P0 - CRITICAL  
**Impact:** Enables 30% of documents (scanned PDFs)

**Current State:**
```bash
$ which pdftoppm
# Not found - poppler-utils missing
Result: All scanned PDFs fail silently
```

**Root Cause:**
- `poppler-utils` installed via `apt-get` during runtime
- Not baked into Docker image
- Container restart wipes installation

**Solution:**
```bash
# Option A: Add to supervisor startup script
# /etc/supervisor/conf.d/backend.conf
[program:backend]
command=bash -c "apt-get update && apt-get install -y poppler-utils tesseract-ocr && uvicorn server:app --host 0.0.0.0 --port 8001"
```

**Implementation Steps:**
1. Check if poppler-utils can be added to startup
2. Test with scanned PDF
3. Verify OCR works after container restart
4. Add logging for OCR success/failure

**Testing:**
- Upload scanned PDF
- Verify text extracted
- Check backend logs for success message
- Restart backend, test again

**Success Criteria:**
- ✅ Scanned PDFs extract text successfully
- ✅ Works after backend restart
- ✅ Error logged if OCR fails

**Dependencies:**
- None - standalone fix

**What This Unlocks:**
- 30% more documents work
- Users can upload scanned documents
- Competitive advantage (many competitors don't do OCR)

---

#### 🔧 TASK 2: Test & Fix Multi-Process Detection

**Time Estimate:** 4 hours  
**Priority:** P0 - CRITICAL  
**Impact:** Fixes flowchart fragmentation issue

**Current State:**
- Recently "fixed" syntax error
- Logic untested
- May treat steps as separate processes
- May not detect multiple processes at all

**Root Cause:**
- Over-complicated detection prompt
- Not tested after fixes

**Solution Approach:**
1. **First: TEST with real document**
   - Upload Welfare First SOP (has 3 processes)
   - See what it detects
   - Document actual behavior

2. **Then: Debug based on actual behavior**
   - If treats steps as processes → simplify logic
   - If doesn't detect multiple → improve detection
   - If works → validate and move on

**Implementation Steps:**
1. Create test: Welfare First SOP (3 processes expected)
2. Upload and check detection result
3. Read backend logs for detection reasoning
4. If broken, simplify prompt to:
   ```
   Does document have sections like:
   - "## Process A"
   - "## Process B"
   - "## Process C"
   
   If yes → multiple processes
   If no → single process
   ```
5. Re-test until detection is 90%+ accurate

**Testing:**
- Test document with 1 process (should detect 1)
- Test document with 3 processes (should detect 3)
- Test document with 10 steps in 1 process (should detect 1, not 10)

**Success Criteria:**
- ✅ Correctly identifies single vs multiple processes
- ✅ Doesn't treat individual steps as processes
- ✅ Logs clear reasoning

**Dependencies:**
- Task 1 (need working system to test)

**What This Unlocks:**
- Proper flowchart structure
- No more fragmented outputs
- Users can upload multi-process documents

---

#### 🔧 TASK 3: Add Comprehensive Error Handling

**Time Estimate:** 8 hours  
**Priority:** P0 - CRITICAL  
**Impact:** Eliminates 30% of user frustration

**Current State:**
```python
# Current code (BAD):
try:
    text = extract_text(document)
except:
    text = ""  # Silent failure!

# User sees: Loading spinner forever OR empty result
```

**Solution: Three-Layer Error Handling**

**Layer 1: Input Validation (Fail Fast)**
```python
# Before processing
if file.size == 0:
    raise HTTPException(400, "File is empty")
if file.size > 10_000_000:
    raise HTTPException(400, "File too large (max 10MB)")
if file.content_type not in SUPPORTED_TYPES:
    raise HTTPException(400, f"Unsupported file type: {file.content_type}")
```

**Layer 2: Processing Errors (Specific Messages)**
```python
# During processing
try:
    text = extract_text(document)
    if not text or len(text) < 100:
        raise HTTPException(422, 
            "Unable to extract text. Please ensure document is readable and not password-protected.")
except OCRError:
    raise HTTPException(422,
        "Unable to read scanned document. OCR processing failed. Please try a text-based PDF.")
except TimeoutError:
    raise HTTPException(504,
        "Processing taking too long. Please try a shorter document or contact support.")
```

**Layer 3: Graceful Degradation (Partial Results)**
```python
# If AI fails but text extracted
if ai_failed:
    return {
        "status": "partial",
        "message": "AI processing failed but text was extracted. You can retry or contact support.",
        "extracted_text": text[:1000]  # Show preview
    }
```

**Implementation Steps:**
1. Map all error scenarios (20 minutes)
2. Create error message dictionary (30 minutes)
3. Add input validation to upload endpoint (1 hour)
4. Add specific error handling to text extraction (2 hours)
5. Add specific error handling to AI processing (2 hours)
6. Add frontend error display (2 hours)
7. Test all error paths (30 minutes)

**Error Scenarios to Handle:**
1. Empty file
2. File too large
3. Wrong file type
4. Text extraction fails
5. OCR fails
6. AI timeout
7. AI returns invalid JSON
8. MongoDB connection fails
9. Out of API credits

**Frontend Changes:**
```javascript
// Instead of generic "Error occurred"
{error.code === 422 && (
  <ErrorCard
    title="Couldn't Read Document"
    message={error.detail}
    suggestions={[
      "Ensure document is text-based (not scanned)",
      "Check file is not password-protected",
      "Try converting to PDF if using Word"
    ]}
    action={<Button onClick={retry}>Try Again</Button>}
  />
)}
```

**Testing:**
- Upload empty file → Should get clear error
- Upload .exe file → Should reject with message
- Upload 100MB file → Should reject with size limit
- Upload password-protected PDF → Should get specific error
- Simulate AI timeout → Should get clear message + retry option

**Success Criteria:**
- ✅ Every error has clear, actionable message
- ✅ User knows what went wrong
- ✅ User knows what to do next (retry, fix document, contact support)
- ✅ No silent failures

**Dependencies:**
- Task 1 (OCR errors need specific messages)

**What This Unlocks:**
- Users no longer stuck on errors
- Support burden reduced (self-service)
- Trust increased (transparency)

---

#### 🔧 TASK 4: Increase Character Limit

**Time Estimate:** 5 minutes  
**Priority:** P1 - HIGH  
**Impact:** Handles longer documents

**Current State:**
```python
# Line 205 in adaptive_flowchart_processor.py
DOCUMENT:
{doc_text[:20000]}  # Only using 3% of Claude's capacity!
```

**Solution:**
```python
# Use 100K chars (still under Claude's 200K token limit)
DOCUMENT:
{doc_text[:100000]}
```

**Implementation:**
1. Change limit from 20K to 100K
2. Add warning if document > 100K
3. Test with 50-page document

**Testing:**
- Upload 20-page document → Should process fully
- Upload 60-page document → Should process fully
- Upload 300-page document → Should warn about truncation

**Success Criteria:**
- ✅ Documents up to ~40-50 pages process fully
- ✅ User warned if document truncated

**Dependencies:**
- None

**What This Unlocks:**
- 15% more documents work (those between 15-50 pages)
- Competitive advantage (can handle complex BCPs)

---

#### 🔧 TASK 5: Add Truncation Warning

**Time Estimate:** 1 hour  
**Priority:** P1 - HIGH  
**Impact:** User transparency

**Current State:**
- Documents >50 pages truncated silently
- User gets incomplete flowchart
- User thinks AI is bad

**Solution:**
```javascript
// Frontend: After upload, before processing
if (documentLength > 100000) {
  showWarning({
    title: "Document Exceeds Limit",
    message: "Your document is very long. Only the first ~40 pages will be processed.",
    options: [
      { label: "Process First 40 Pages", action: "proceed" },
      { label: "Split Into Sections", action: "guide" },
      { label: "Cancel", action: "cancel" }
    ]
  });
}
```

**Implementation:**
1. Backend returns document length in upload response
2. Frontend checks length
3. Show modal if > 100K chars
4. User can proceed or cancel
5. Log truncation events

**Testing:**
- Upload 30-page doc → No warning
- Upload 80-page doc → Shows warning
- User clicks "proceed" → Continues with warning acknowledged
- User clicks "cancel" → Stops processing

**Success Criteria:**
- ✅ User knows document will be truncated
- ✅ User can make informed decision
- ✅ No surprise incomplete results

**Dependencies:**
- Task 4 (character limit change)

**What This Unlocks:**
- User trust (transparency)
- No surprise bad results

---

#### 🔧 TASK 6: Add Loading States

**Time Estimate:** 2 hours  
**Priority:** P1 - HIGH  
**Impact:** User experience

**Current State:**
```javascript
// Just shows: "Processing..."
<Spinner />
```

**Solution:**
```javascript
// Show actual progress
<LoadingState>
  <Step completed={uploadComplete}>
    ✅ Document uploaded
  </Step>
  <Step active={extractingText}>
    ⏳ Extracting text... (5-10 seconds)
  </Step>
  <Step pending={!aiStarted}>
    ⏳ Analyzing structure... (10-15 seconds)
  </Step>
  <Step pending={!aiComplete}>
    ⏳ Generating flowchart... (5-10 seconds)
  </Step>
  <Step pending={!renderComplete}>
    ⏳ Rendering visualization...
  </Step>
</LoadingState>

<ProgressBar value={progress} max={100} />
<EstimatedTime>~{remainingTime} seconds remaining</EstimatedTime>
```

**Implementation:**
1. Backend emits progress events (WebSocket or polling)
2. Frontend tracks state machine:
   - UPLOADING → EXTRACTING → ANALYZING → GENERATING → RENDERING
3. Show current step + estimated time
4. Add cancel button (optional)

**Testing:**
- Upload simple doc → Should show all steps smoothly
- Upload complex doc → Estimated time should be accurate
- If step takes too long → Show "taking longer than expected"

**Success Criteria:**
- ✅ User sees what's happening
- ✅ Estimated time is within 20% accuracy
- ✅ No "stuck" feeling

**Dependencies:**
- None (improves UX of existing flow)

**What This Unlocks:**
- User confidence (know it's working)
- Reduced abandonment (clear progress)

---

### PHASE 1 SUMMARY

**Total Time:** 16 hours  
**Impact:** Foundation solid, critical bugs fixed  
**User Experience:** Transformed from frustrating to acceptable  

**After Phase 1:**
- ✅ OCR works (30% more documents)
- ✅ Multi-process detection works (no fragmentation)
- ✅ Clear error messages (no confusion)
- ✅ Longer documents work (15% more documents)
- ✅ User knows what's happening (transparency)

**Before moving to Phase 2:**
- [ ] Test all fixes end-to-end
- [ ] Verify no regressions
- [ ] Update BUILD_TRACKER.md

---

## PHASE 2: ACCURACY IMPROVEMENTS (Day 3-4)

---

#### 🎯 TASK 7: Create Test Suite

**Time Estimate:** 8 hours  
**Priority:** P0 - CRITICAL  
**Impact:** Can measure accuracy objectively

**Why This First:**
- Can't improve what we can't measure
- Need baseline before making changes
- Prevents regressions

**Implementation:**

**Step 1: Select Test Documents (1 hour)**
Create 3 test cases representing different complexity levels:

1. **Simple Linear SOP** (Expected: 90% accuracy)
   ```
   Title: "Customer Onboarding"
   Steps:
   1. Receive inquiry
   2. Send welcome email
   3. Schedule onboarding call
   4. Complete paperwork
   5. Grant system access
   
   Expected Nodes: 5
   Expected Decisions: 0
   Expected Connections: 4
   ```

2. **Medium Complexity** (Expected: 80% accuracy)
   ```
   Title: "Panic Alert Response" (from Welfare First SOP)
   Steps: 10
   Expected Nodes: 10
   Expected Decisions: 2 (Can speak freely? Satisfied with response?)
   Expected Connections: ~12
   ```

3. **Complex BCP** (Expected: 70% accuracy)
   ```
   Title: "Server Outage Response"
   Steps: 20+
   Expected Decisions: 4-5
   Expected Tables: 1 (escalation matrix)
   Expected Connections: ~25
   ```

**Step 2: Define Expected Outputs (2 hours)**

```python
# /app/backend/tests/test_data.py

TEST_CASES = [
    {
        "name": "Simple_Customer_Onboarding",
        "document_path": "tests/docs/simple_onboarding.pdf",
        "expected": {
            "processName": "Customer Onboarding",
            "node_count": 5,
            "decision_count": 0,
            "nodes": [
                {"title": "Receive Inquiry", "type": "process"},
                {"title": "Send Welcome Email", "type": "process"},
                {"title": "Schedule Onboarding Call", "type": "process"},
                {"title": "Complete Paperwork", "type": "process"},
                {"title": "Grant System Access", "type": "process"},
            ],
            "connections": [
                ("node-1", "node-2"),
                ("node-2", "node-3"),
                ("node-3", "node-4"),
                ("node-4", "node-5"),
            ]
        },
        "min_accuracy": 0.90
    },
    # ... more test cases
]
```

**Step 3: Implement Accuracy Calculation (3 hours)**

```python
# /app/backend/tests/test_accuracy.py

def calculate_node_accuracy(actual_nodes, expected_nodes):
    """
    Calculate what % of expected nodes are present in actual output.
    Uses fuzzy matching (0.8 threshold) to account for slight wording differences.
    """
    from difflib import SequenceMatcher
    
    matched = 0
    for expected_node in expected_nodes:
        for actual_node in actual_nodes:
            similarity = SequenceMatcher(
                None, 
                expected_node["title"].lower(), 
                actual_node["title"].lower()
            ).ratio()
            
            if similarity > 0.8:
                matched += 1
                break
    
    return matched / len(expected_nodes) if expected_nodes else 0

def calculate_connection_accuracy(actual_edges, expected_connections):
    """Calculate what % of expected connections are present."""
    matched = 0
    for expected_conn in expected_connections:
        for actual_edge in actual_edges:
            if (actual_edge["source"], actual_edge["target"]) == expected_conn:
                matched += 1
                break
    
    return matched / len(expected_connections) if expected_connections else 0

def calculate_decision_accuracy(actual_nodes, expected_decision_count):
    """Calculate if correct number of decisions identified."""
    actual_decisions = [n for n in actual_nodes if n.get("isDecisionPoint")]
    return min(1.0, len(actual_decisions) / expected_decision_count) if expected_decision_count else 1.0

def calculate_overall_accuracy(test_case, actual_output):
    """
    Overall accuracy = weighted average of:
    - Node accuracy (40%)
    - Connection accuracy (30%)
    - Decision accuracy (20%)
    - Hallucination penalty (10%)
    """
    node_acc = calculate_node_accuracy(
        actual_output["nodes"], 
        test_case["expected"]["nodes"]
    )
    
    conn_acc = calculate_connection_accuracy(
        actual_output["edges"],
        test_case["expected"]["connections"]
    )
    
    decision_acc = calculate_decision_accuracy(
        actual_output["nodes"],
        test_case["expected"]["decision_count"]
    )
    
    # Hallucination penalty: extra nodes not in expected
    extra_nodes = len(actual_output["nodes"]) - len(test_case["expected"]["nodes"])
    hallucination_penalty = max(0, extra_nodes) * 0.1
    
    overall = (
        node_acc * 0.4 +
        conn_acc * 0.3 +
        decision_acc * 0.2 +
        (1 - hallucination_penalty) * 0.1
    )
    
    return {
        "overall": overall,
        "node_accuracy": node_acc,
        "connection_accuracy": conn_acc,
        "decision_accuracy": decision_acc,
        "hallucination_count": max(0, extra_nodes)
    }
```

**Step 4: Create Test Runner (2 hours)**

```python
# /app/backend/tests/run_accuracy_tests.py

import asyncio
from test_data import TEST_CASES
from test_accuracy import calculate_overall_accuracy

async def run_test_suite():
    """Run all accuracy tests and generate report."""
    results = []
    
    for test_case in TEST_CASES:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        # Generate flowchart
        actual_output = await generate_flowchart(test_case["document_path"])
        
        # Calculate accuracy
        accuracy = calculate_overall_accuracy(test_case, actual_output)
        
        # Store results
        results.append({
            "test": test_case["name"],
            "expected_min": test_case["min_accuracy"],
            "actual": accuracy["overall"],
            "passed": accuracy["overall"] >= test_case["min_accuracy"],
            "details": accuracy
        })
        
        # Print results
        status = "✅ PASS" if results[-1]["passed"] else "❌ FAIL"
        print(f"{status} - {accuracy['overall']:.1%} (target: {test_case['min_accuracy']:.0%})")
    
    # Generate report
    generate_report(results)
    
    return results

def generate_report(results):
    """Generate markdown report with results."""
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_accuracy = sum(r["actual"] for r in results) / total
    
    report = f"""# Accuracy Test Results
    
## Summary
- Tests Passed: {passed}/{total}
- Average Accuracy: {avg_accuracy:.1%}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Detailed Results

| Test | Target | Actual | Status |
|------|--------|--------|--------|
"""
    
    for r in results:
        status = "✅" if r["passed"] else "❌"
        report += f"| {r['test']} | {r['expected_min']:.0%} | {r['actual']:.1%} | {status} |\n"
    
    report += f"""
## Breakdown by Metric

| Test | Nodes | Connections | Decisions | Hallucinations |
|------|-------|-------------|-----------|----------------|
"""
    
    for r in results:
        d = r["details"]
        report += f"| {r['test']} | {d['node_accuracy']:.1%} | {d['connection_accuracy']:.1%} | {d['decision_accuracy']:.1%} | {d['hallucination_count']} |\n"
    
    with open("/app/ACCURACY_REPORT.md", "w") as f:
        f.write(report)
    
    print(f"\n📊 Report saved to: /app/ACCURACY_REPORT.md")

if __name__ == "__main__":
    asyncio.run(run_test_suite())
```

**Testing:**
- Run test suite
- Verify it completes without errors
- Check ACCURACY_REPORT.md is generated
- Validate accuracy calculations make sense

**Success Criteria:**
- ✅ Test suite runs automatically
- ✅ Generates clear accuracy report
- ✅ Can run before/after changes to measure impact
- ✅ Identifies which metrics need improvement

**Dependencies:**
- Phase 1 complete (need stable system to test)

**What This Unlocks:**
- Objective accuracy measurement
- Can prove improvements
- Prevents regressions
- Data-driven decisions

---

#### 🎯 TASK 8: Add Few-Shot Learning

**Time Estimate:** 6 hours  
**Priority:** P0 - CRITICAL  
**Impact:** +15-20% accuracy improvement

**Why This Works:**
- Shows AI what "good" looks like
- Reduces hallucinations
- Improves decision point detection
- Industry standard for prompt engineering

**Implementation:**

**Step 1: Create High-Quality Examples (3 hours)**

Manual create 3 perfect SOP → flowchart examples:

```python
# Example 1: Simple Linear Process
EXAMPLE_1 = """
DOCUMENT:
"Equipment Maintenance SOP
1. Inspect equipment daily
2. Log any issues found
3. Report to supervisor
4. Schedule repairs if needed
5. Complete maintenance log"

OUTPUT:
{
  "processName": "Equipment Maintenance",
  "nodes": [
    {
      "id": "node-1",
      "title": "Inspect Equipment Daily",
      "type": "process",
      "connections": ["node-2"]
    },
    {
      "id": "node-2",
      "title": "Log Any Issues Found",
      "type": "process",
      "connections": ["node-3"]
    },
    {
      "id": "node-3",
      "title": "Report to Supervisor",
      "type": "process",
      "connections": ["node-4"]
    },
    {
      "id": "node-4",
      "title": "Schedule Repairs if Needed",
      "type": "process",
      "connections": ["node-5"]
    },
    {
      "id": "node-5",
      "title": "Complete Maintenance Log",
      "type": "process",
      "connections": []
    }
  ]
}
"""

# Example 2: Process with Decision Point
EXAMPLE_2 = """
DOCUMENT:
"Customer Complaint Handling
1. Receive complaint
2. Assess severity: If high, escalate immediately. If low, handle directly.
3. Document resolution
4. Follow up with customer"

OUTPUT:
{
  "processName": "Customer Complaint Handling",
  "nodes": [
    {
      "id": "node-1",
      "title": "Receive Complaint",
      "type": "process",
      "connections": ["node-2"]
    },
    {
      "id": "node-2",
      "title": "Assess Severity",
      "type": "decision",
      "isDecisionPoint": true,
      "decisionCriteria": "Is severity high or low?",
      "decisionOptions": {"yes": "node-3", "no": "node-4"},
      "connections": ["node-3", "node-4"]
    },
    {
      "id": "node-3",
      "title": "Escalate Immediately",
      "type": "process",
      "connections": ["node-5"]
    },
    {
      "id": "node-4",
      "title": "Handle Directly",
      "type": "process",
      "connections": ["node-5"]
    },
    {
      "id": "node-5",
      "title": "Document Resolution",
      "type": "process",
      "connections": ["node-6"]
    },
    {
      "id": "node-6",
      "title": "Follow Up with Customer",
      "type": "process",
      "connections": []
    }
  ]
}
"""

# Example 3: Complex with Multiple Decisions
EXAMPLE_3 = """
[Create based on Panic Alert SOP]
"""
```

**Step 2: Integrate into Prompt (1 hour)**

```python
# adaptive_flowchart_processor.py

def _build_generate_prompt(self, doc_text: str, estimated_nodes: int) -> str:
    return f"""Extract a flowchart from this SOP document. Be accurate and use exact terminology.

Here are 3 examples of CORRECT conversions:

{EXAMPLE_1}

{EXAMPLE_2}

{EXAMPLE_3}

Now convert THIS document using the same approach:

DOCUMENT:
{doc_text[:100000]}

INSTRUCTIONS:
[... rest of current prompt ...]
"""
```

**Step 3: Test Impact (2 hours)**

```bash
# Run test suite BEFORE few-shot
python tests/run_accuracy_tests.py
# Save results

# Add few-shot examples
# Run test suite AFTER few-shot
python tests/run_accuracy_tests.py
# Compare results

# Expected improvement: +15-20%
```

**Testing:**
- Run test suite before change
- Add few-shot examples
- Run test suite after change
- Verify accuracy improved
- Check no regressions on any test case

**Success Criteria:**
- ✅ Accuracy improves by 10-20%
- ✅ Hallucinations reduced
- ✅ Decision points detected more accurately
- ✅ No test cases regress

**Dependencies:**
- Task 7 (need test suite to measure)

**What This Unlocks:**
- Major accuracy improvement
- More consistent outputs
- Fewer edge cases

---

#### 🎯 TASK 9: Add Validation UI

**Time Estimate:** 2 hours  
**Priority:** P2 - MEDIUM  
**Impact:** User can spot low-confidence nodes

**Current State:**
- Backend calculates `_validationScore` for each node
- Frontend doesn't show it
- Users can't tell which nodes are questionable

**Solution:**

```javascript
// ProcessNode.jsx

function ProcessNode({ data }) {
  const validationScore = data._validationScore || 1.0;
  
  const confidenceColor = 
    validationScore >= 0.7 ? 'green' :
    validationScore >= 0.5 ? 'yellow' : 'red';
  
  const confidenceLabel =
    validationScore >= 0.7 ? 'High Confidence' :
    validationScore >= 0.5 ? 'Medium Confidence' : 'Low Confidence - Please Review';
  
  return (
    <div className="process-node">
      <div className="node-header">
        <span className="node-title">{data.title}</span>
        {validationScore < 1.0 && (
          <Tooltip content={`Confidence: ${(validationScore * 100).toFixed(0)}% - ${confidenceLabel}`}>
            <Badge color={confidenceColor}>
              {confidenceLabel}
            </Badge>
          </Tooltip>
        )}
      </div>
      {/* ... rest of node */}
    </div>
  );
}
```

**Implementation:**
1. Add confidence badge to nodes
2. Color code by score (green/yellow/red)
3. Show tooltip on hover with explanation
4. Add filter to show only low-confidence nodes

**Testing:**
- Generate flowchart
- Verify confidence badges appear
- Check colors match scores
- Hover to see tooltip

**Success Criteria:**
- ✅ Users can visually identify questionable nodes
- ✅ Color coding is clear
- ✅ Tooltip provides helpful context

**Dependencies:**
- None (backend already calculates scores)

**What This Unlocks:**
- Users can focus review on problem areas
- Transparency builds trust
- Users know what to double-check

---

### PHASE 2 SUMMARY

**Total Time:** 16 hours  
**Impact:** Accuracy improves 15-20%  
**Measurable:** Can prove improvement with test suite

**After Phase 2:**
- ✅ Test suite validates accuracy objectively
- ✅ Few-shot learning reduces hallucinations
- ✅ Users can see confidence scores
- ✅ Accuracy: 65-70% (from 50%)

**Before moving to Phase 3:**
- [ ] Run full test suite
- [ ] Document accuracy improvements
- [ ] Update BUILD_TRACKER.md

---

## PHASE 3: MONITORING & FEEDBACK (Day 5)

---

#### 📊 TASK 10: Add Monitoring System

**Time Estimate:** 4 hours  
**Priority:** P0 - CRITICAL  
**Impact:** Know when things break

**Why Critical:**
- Can't improve what we can't see
- Need to know error rates
- Track accuracy over time
- Catch issues before users report

**Implementation:**

**Step 1: Add Structured Logging (1 hour)**

```python
# /app/backend/monitoring.py

import logging
import json
from datetime import datetime

class MetricsLogger:
    def __init__(self):
        self.logger = logging.getLogger("metrics")
        handler = logging.FileHandler("/var/log/metrics.log")
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event_type, data):
        """Log structured event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "data": data
        }
        self.logger.info(json.dumps(event))
    
    def log_document_processed(self, success, duration, accuracy=None, error=None):
        self.log_event("document_processed", {
            "success": success,
            "duration_seconds": duration,
            "accuracy": accuracy,
            "error": error
        })
    
    def log_error(self, error_type, message, context=None):
        self.log_event("error", {
            "error_type": error_type,
            "message": message,
            "context": context
        })

metrics = MetricsLogger()
```

**Step 2: Instrument Code (2 hours)**

```python
# In server.py and other files

from monitoring import metrics

@app.post("/api/process")
async def process_document():
    start_time = time.time()
    
    try:
        result = await generate_flowchart(document)
        duration = time.time() - start_time
        
        metrics.log_document_processed(
            success=True,
            duration=duration,
            accuracy=result.get("_accuracy")
        )
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        
        metrics.log_document_processed(
            success=False,
            duration=duration,
            error=str(e)
        )
        
        metrics.log_error(
            error_type=type(e).__name__,
            message=str(e),
            context={"document_size": len(document)}
        )
        
        raise
```

**Step 3: Create Daily Digest Script (1 hour)**

```python
# /app/backend/daily_digest.py

import json
from datetime import datetime, timedelta
from collections import Counter

def generate_daily_digest():
    """Parse metrics.log and generate summary."""
    
    # Read last 24 hours of logs
    events = []
    with open("/var/log/metrics.log", "r") as f:
        for line in f:
            event = json.loads(line)
            event_time = datetime.fromisoformat(event["timestamp"])
            if event_time > datetime.utcnow() - timedelta(days=1):
                events.append(event)
    
    # Calculate metrics
    processed = [e for e in events if e["event"] == "document_processed"]
    errors = [e for e in events if e["event"] == "error"]
    
    total_processed = len(processed)
    successful = len([e for e in processed if e["data"]["success"]])
    failed = total_processed - successful
    
    success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
    avg_duration = sum(e["data"]["duration_seconds"] for e in processed) / len(processed) if processed else 0
    
    error_types = Counter(e["data"]["error_type"] for e in errors)
    
    # Generate report
    report = f"""# Daily Metrics Report - {datetime.utcnow().strftime('%Y-%m-%d')}

## Processing Stats
- Total Documents: {total_processed}
- Successful: {successful} ({success_rate:.1f}%)
- Failed: {failed}
- Average Duration: {avg_duration:.1f}s

## Error Breakdown
"""
    for error_type, count in error_types.most_common():
        report += f"- {error_type}: {count}\n"
    
    report += f"""
## Action Items
"""
    
    if success_rate < 80:
        report += "- ⚠️ Success rate below 80% - investigate!\n"
    if avg_duration > 30:
        report += "- ⚠️ Average duration over 30s - optimize!\n"
    if error_types:
        report += f"- ⚠️ Top error: {error_types.most_common(1)[0][0]} - fix!\n"
    
    return report

if __name__ == "__main__":
    print(generate_daily_digest())
```

**Testing:**
- Process 10 documents
- Check metrics.log has entries
- Run daily_digest.py
- Verify report is accurate

**Success Criteria:**
- ✅ All events logged
- ✅ Daily digest runs successfully
- ✅ Can track success rate, duration, errors

**Dependencies:**
- None

**What This Unlocks:**
- Know when accuracy drops
- Identify problem areas
- Track improvements over time

---

#### 💬 TASK 11: Add Feedback Mechanism

**Time Estimate:** 4 hours  
**Priority:** P1 - HIGH  
**Impact:** Can collect user corrections

**Why Important:**
- Users want to report issues
- Corrections = training data
- Shows we care about quality

**Implementation:**

**Step 1: Backend Endpoint (1 hour)**

```python
# In server.py

@app.post("/api/feedback")
async def submit_feedback(
    node_id: str,
    issue_type: str,  # "incorrect", "missing", "hallucination"
    message: str,
    process_id: str,
    user: User = Depends(get_current_user)
):
    """Store user feedback for a node."""
    
    feedback = {
        "id": str(uuid4()),
        "user_id": user.id,
        "process_id": process_id,
        "node_id": node_id,
        "issue_type": issue_type,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    
    await db.feedback.insert_one(feedback)
    
    # Also log for monitoring
    metrics.log_event("user_feedback", {
        "issue_type": issue_type,
        "process_id": process_id
    })
    
    return {"success": True}
```

**Step 2: Frontend UI (3 hours)**

```javascript
// ProcessNode.jsx

function ProcessNode({ data }) {
  const [showFeedback, setShowFeedback] = useState(false);
  
  return (
    <div className="process-node">
      {/* ... node content ... */}
      
      <button 
        onClick={() => setShowFeedback(true)}
        className="feedback-button"
        title="Report issue with this node"
      >
        ⚠️ Report Issue
      </button>
      
      {showFeedback && (
        <FeedbackModal
          nodeId={data.id}
          nodeTitle={data.title}
          onClose={() => setShowFeedback(false)}
        />
      )}
    </div>
  );
}

function FeedbackModal({ nodeId, nodeTitle, onClose }) {
  const [issueType, setIssueType] = useState("");
  const [message, setMessage] = useState("");
  
  const submitFeedback = async () => {
    await api.post("/api/feedback", {
      node_id: nodeId,
      issue_type: issueType,
      message: message,
      process_id: currentProcessId
    });
    
    toast.success("Thank you for your feedback!");
    onClose();
  };
  
  return (
    <Modal>
      <h3>Report Issue: "{nodeTitle}"</h3>
      
      <label>What's wrong?</label>
      <select onChange={(e) => setIssueType(e.target.value)}>
        <option value="">Select issue type...</option>
        <option value="incorrect">This step is incorrect</option>
        <option value="missing">There's a missing step before/after</option>
        <option value="hallucination">This step doesn't exist in my document</option>
        <option value="decision">This should be a decision point</option>
        <option value="connection">The connections are wrong</option>
        <option value="other">Other issue</option>
      </select>
      
      <label>Details (optional):</label>
      <textarea 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="What should it be? Any additional context?"
      />
      
      <button onClick={submitFeedback}>Submit Feedback</button>
      <button onClick={onClose}>Cancel</button>
    </Modal>
  );
}
```

**Testing:**
- Generate flowchart
- Click "Report Issue" on a node
- Fill out form
- Submit
- Verify saved to database
- Check metrics.log has entry

**Success Criteria:**
- ✅ Users can report issues easily
- ✅ Feedback stored in database
- ✅ Can analyze feedback patterns
- ✅ Shows commitment to quality

**Dependencies:**
- None

**What This Unlocks:**
- User satisfaction (being heard)
- Training data for future improvements
- Identify common issues

---

### PHASE 3 SUMMARY

**Total Time:** 8 hours  
**Impact:** Visibility and improvement loop

**After Phase 3:**
- ✅ Monitoring tracks all metrics
- ✅ Daily digest shows health
- ✅ Users can report issues
- ✅ Can measure improvements over time

---

## WEEK 1 COMPLETE CHECKLIST

**Before declaring Week 1 done:**

- [ ] All Phase 1 tasks complete (OCR, errors, loading)
- [ ] All Phase 2 tasks complete (test suite, few-shot, validation UI)
- [ ] All Phase 3 tasks complete (monitoring, feedback)
- [ ] Full end-to-end test passes
- [ ] No regressions from previous functionality
- [ ] BUILD_TRACKER.md updated
- [ ] ACCURACY_REPORT.md generated
- [ ] Ready for Week 2 (beta testing)

**Expected State After Week 1:**
- Accuracy: 65-75% (up from 50%)
- Error handling: Good (clear messages)
- Monitoring: Active
- OCR: Working
- Test suite: Complete
- Ready for 10 beta users

---

*This is the DETAILED execution plan. Follow this exactly. Test at each step. Update BUILD_TRACKER.md after each task.*
