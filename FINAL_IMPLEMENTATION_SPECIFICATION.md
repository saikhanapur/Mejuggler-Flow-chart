# Combined Implementation Plan - Final Specification

**Date:** November 2, 2025  
**Scope:** Multi-Process Detection + BCP Intelligence + Version Snapshots  
**Timeline:** 8-10 hours  
**Test Documents:** 6 provided (BCPs, Recruitment, Product Recall, IT DR)

---

## Document Analysis Summary

### Test Document Set:

**1. Wilsar BCP** (Your existing)
- Structure: 3 swim lanes (Identify, Onshore, Offshore)
- Decisions: "Has Wilsar Outage?" (YES/NO)
- Loops: "Check every 30 minutes"
- Parallel: Onshore + Offshore simultaneous actions

**2. GDS BCP** (Your existing)
- Structure: 2 swim lanes (FSC/DSC, Main)
- Decisions: "GDS down" (YES/NO)
- Loops: Monitoring cycles

**3. Recruitment Process Maps** (Your existing)
- Structure: 9 separate processes in one document
- Complexity: Collection of independent workflows

**4. Product Recall SOP** (NEW - Just provided)
- Structure: Single process with branches
- Key patterns:
  - Parallel notifications (QA, Supply Chain, Customer Service)
  - Decisions: "If Supplier Issue", "If Manufacturing Error"
  - Loops: "RCA validated until accepted", "CAPA effectiveness check"
  - RACI table: Role-based responsibilities
  - Referenced sub-processes: RCA, Supplier Deviation, Field Recovery, CAPA

**5. IT Disaster Recovery SOP** (NEW - Just provided, 20+ pages)
- Structure: 7 phases (linear progression)
- Complexity: HIGH
  - Multiple parallel activities per phase
  - Decision matrix for triggers
  - RACI matrix
  - Role-based sections (DR Manager, Incident Commander, Platform Owners)
  - Nested sub-processes (Network, DB, App, Data Stores)
  - Gates/Approvals (G3, G6)
  - Contact lists and escalation paths

---

## Implementation Strategy

### Core Requirements (From Analysis):

**Must Handle:**
1. ✅ Multiple processes in one document (Recruitment: 9 processes)
2. ✅ Swim lanes (BCPs: 2-3 lanes)
3. ✅ Decision points (BCPs, Product Recall, DR SOP)
4. ✅ Monitoring loops (BCPs, Product Recall)
5. ✅ Parallel activities (All documents)
6. ✅ Role-based sections (DR SOP, Product Recall)
7. ✅ RACI tables (Product Recall, DR SOP)
8. ✅ Phased processes (DR SOP: 7 phases)
9. ✅ Referenced sub-processes (Product Recall)
10. ✅ Long documents (DR SOP: 20+ pages)

**User Requirements:**
- Decide automatically (no user confirmation for variations)
- Support up to 50 pages
- Use best judgment for table detection

---

## Phase-by-Phase Implementation

### PHASE 1: Enhanced Multi-Process Detection (3 hours)

**File:** `/app/backend/superintelligent_ai_service.py`

**Add method `detect_multiple_processes_and_structure`:**

```python
async def detect_multiple_processes_and_structure(self, document_text: str) -> Dict[str, Any]:
    """
    STAGE 0.5: Comprehensive Document Analysis
    
    Detects:
    1. Multiple processes (like Recruitment: 9 processes)
    2. Swim lanes/role sections (like BCPs: Onshore/Offshore)
    3. Phased structures (like DR SOP: 7 phases)
    4. Decision points (if/then branches)
    5. Monitoring loops (every X minutes)
    6. Parallel activities (simultaneous actions)
    7. RACI tables (role matrices)
    
    Returns comprehensive structure for AI to use
    """
    logger.info("🔍 Comprehensive document structure detection...")
    
    try:
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"detect_{uuid.uuid4()}",
            system_message="""You are an enterprise process intelligence expert. Analyze documents from:
- Manufacturing (Quality Control, Product Recall, Safety)
- Healthcare (Clinical pathways, Emergency protocols)
- Finance (KYC, Transaction processing, Approval chains)
- IT (Incident management, Disaster Recovery, Change management)
- HR (Recruitment, Onboarding, Performance, Offboarding)

Your job: Identify ALL structural patterns in the document."""
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        prompt = f"""COMPREHENSIVE DOCUMENT STRUCTURE ANALYSIS

DOCUMENT (first 25,000 chars):
{document_text[:25000]}

ANALYZE FOR ALL PATTERNS:

1. MULTIPLE PROCESSES:
   - Are there 2+ distinct processes in this document?
   - Look for: Numbered sections (Process 1, 2, 3), Separate workflows
   - Example: "Recruitment Process Maps" with 9 separate processes
   - If found, list each process title

2. SWIM LANES / ROLE SECTIONS:
   - Are there parallel columns/sections by role or team?
   - Look for: "Onshore Actions", "Offshore Actions", "IDENTIFY", "ASSESS", "MITIGATE"
   - Look for: Role-based headers (QA Manager, DR Manager, Platform Owner)
   - Example: BCP with "Identify | Onshore | Offshore" columns

3. PHASED STRUCTURE:
   - Is the process divided into phases/stages?
   - Look for: "Phase 1", "Phase 2", "Stage 1", "Step 1"
   - Example: DR SOP with "Phase 0: Preparedness, Phase 1: Incident Declaration..."
   - If found, list phase names

4. DECISION POINTS:
   - Look for if/then/else logic, branching
   - Patterns: "If [condition]", "[System] down?", "Has [X] occurred?"
   - Example: "If Supplier Issue → Trigger SD-07"
   - Example: "Has Wilsar Outage? YES/NO"
   - List all decision criteria found

5. MONITORING LOOPS:
   - Look for recurring checks/validations
   - Patterns: "Check every [X] minutes", "Monitor until [condition]"
   - Example: "Check in with Wilson IT every 30 minutes until services restored"
   - Example: "RCA validated until accepted by QA Director"
   - List all loops with frequency

6. PARALLEL ACTIVITIES:
   - Look for simultaneous actions by different teams
   - Patterns: "Meanwhile", "At the same time", "Parallel", actions in same row
   - Example: "QA notifies Regulatory, Supply Chain halts distribution, Customer Service drafts notice"
   - Look for: Same timing/level but different actors
   - List parallel activity groups

7. RACI TABLES / ROLE MATRICES:
   - Look for tables showing Responsible, Accountable, Consulted, Informed
   - Look for: Role columns (Manager, Employee, HR, IT)
   - Example: RACI matrix in Product Recall SOP
   - If found, note presence

8. REFERENCED SUB-PROCESSES:
   - Look for references to other procedures
   - Patterns: "SOP-XXX", "Refer to [Procedure]", "Trigger [Sub-Process]"
   - Example: "Trigger Supplier Deviation Procedure SD-07"
   - List referenced procedures

9. GATES / APPROVALS:
   - Look for approval points or gates
   - Patterns: "Gate G3", "Approval required", "Sign-off"
   - Example: "Gate G6: Steering Committee approval required"
   - List all gates

10. DOCUMENT COMPLEXITY:
    - Simple (3-10 steps, linear)
    - Medium (10-20 steps, some branching)
    - Complex (20+ steps, multiple branches/phases)
    - Very Complex (30+ steps, nested processes, tables)

RETURN JSON (VALID JSON ONLY, NO MARKDOWN):
{{
  "multipleProcesses": true/false,
  "processCount": 1 to 20,
  "processTitles": ["Process 1 title", "Process 2 title", ...],
  
  "swimLanes": [
    {{"id": "identify", "title": "IDENTIFY", "team": "Dispatch"}},
    {{"id": "onshore", "title": "ONSHORE ACTIONS", "team": "Onshore Supervisor"}},
    ...
  ],
  
  "phases": [
    {{"number": 0, "title": "Preparedness", "description": "Pre-incident"}},
    {{"number": 1, "title": "Incident Declaration", "description": "Initial response"}},
    ...
  ],
  
  "decisionPoints": [
    {{"condition": "Has Wilsar Outage?", "branches": ["YES", "NO"], "location": "section 2"}},
    {{"condition": "If Supplier Issue", "branches": ["Trigger SD-07", "Continue"], "location": "step 5"}},
    ...
  ],
  
  "monitoringLoops": [
    {{"action": "Check with Wilson IT", "frequency": "every 30 minutes", "until": "services restored"}},
    {{"action": "RCA validation", "frequency": "iterative", "until": "accepted by QA Director"}},
    ...
  ],
  
  "parallelActivities": [
    {{"level": "notification", "activities": ["QA notifies Regulatory", "Supply Chain halts", "Customer Service drafts"]}},
    ...
  ],
  
  "hasRACITable": true/false,
  "referencedProcedures": ["SOP-RCA-001", "SD-07", "FR-05", "CAPA-04", ...],
  "gates": ["Gate G3", "Gate G6", ...],
  
  "complexity": "simple|medium|complex|very_complex",
  "reasoning": "Why this structure?",
  "recommendation": "single_flowchart|multiple_flowcharts|phased_flowcharts",
  "pageEstimate": 1-50
}}

CRITICAL:
- If processCount >= 2, set multipleProcesses: true
- If swimLanes found, list ALL swim lanes with their teams
- If phases found, list ALL phases
- Return ONLY valid JSON, no explanatory text before/after
- Be thorough - capture ALL patterns

Analyze now:"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        detection = self._parse_json_response(response)
        
        # Auto-decide based on detection
        if detection.get("multipleProcesses") and detection.get("processCount", 0) >= 2:
            # AUTO-DECIDE: Multiple processes → Create separately
            detection["recommendation"] = "multiple_flowcharts"
            detection["autoDecision"] = "Create each process as a separate flowchart"
        elif detection.get("phases") and len(detection.get("phases", [])) >= 3:
            # AUTO-DECIDE: Phased process → Keep as one with phases
            detection["recommendation"] = "phased_single_flowchart"
            detection["autoDecision"] = "Create one flowchart with phase stages"
        elif detection.get("swimLanes") and len(detection.get("swimLanes", [])) >= 2:
            # AUTO-DECIDE: Swim lanes → Keep as one with lanes
            detection["recommendation"] = "swimlane_single_flowchart"
            detection["autoDecision"] = "Create one flowchart with swim lanes"
        else:
            # AUTO-DECIDE: Simple process → Standard flowchart
            detection["recommendation"] = "single_flowchart"
            detection["autoDecision"] = "Create standard flowchart"
        
        logger.info(f"✅ Detection complete: {detection.get('processCount')} process(es)")
        logger.info(f"   Auto-decision: {detection.get('autoDecision')}")
        logger.info(f"   Swim lanes: {len(detection.get('swimLanes', []))}")
        logger.info(f"   Phases: {len(detection.get('phases', []))}")
        logger.info(f"   Decisions: {len(detection.get('decisionPoints', []))}")
        logger.info(f"   Loops: {len(detection.get('monitoringLoops', []))}")
        
        return detection
        
    except Exception as e:
        logger.error(f"❌ Detection failed: {e}", exc_info=True)
        return {
            "multipleProcesses": False,
            "processCount": 1,
            "swimLanes": [],
            "phases": [],
            "decisionPoints": [],
            "monitoringLoops": [],
            "parallelActivities": [],
            "hasRACITable": False,
            "complexity": "unknown",
            "recommendation": "single_flowchart",
            "autoDecision": "Create standard flowchart (detection failed)"
        }
```

**Update `generate_eroad_style_flowchart`:**

```python
async def generate_eroad_style_flowchart(
    self,
    document_text: str,
    input_type: str,
    user_id: str = None
) -> Dict[str, Any]:
    """
    HYBRID APPROACH: Detect → Extract → Enhance → Return
    
    NEW: Comprehensive structure detection!
    """
    logger.info("🚀 EROAD-Style with Comprehensive Detection")
    
    try:
        # PHASE 0: Comprehensive structure detection
        detection = await self.detect_multiple_processes_and_structure(document_text)
        
        # AUTO-DECIDE based on detection
        if detection.get("multipleProcesses") and detection.get("processCount", 0) >= 2:
            logger.info(f"🔍 {detection['processCount']} processes detected - creating separately")
            
            # Return for multi-process handling
            return {
                "multipleProcesses": True,
                "processCount": detection["processCount"],
                "processTitles": detection["processTitles"],
                "detection": detection,  # Include full detection for reference
                "autoDecision": detection["autoDecision"],
                "processes": []  # Will be created individually
            }
        
        # PHASE 1: Single process (but with detected structure)
        logger.info(f"📄 Single process - using detected structure")
        logger.info(f"   Swim lanes: {len(detection.get('swimLanes', []))}")
        logger.info(f"   Phases: {len(detection.get('phases', []))}")
        
        # Pass detection to extraction for context
        extracted = await self.analyze_document_with_structure(
            document_text, 
            input_type, 
            user_id,
            detection  # NEW: Pass detected structure
        )
        
        # PHASE 2: Enhance with structure awareness
        from eroad_style_enhancer import EROADStyleEnhancer
        
        enhancer = EROADStyleEnhancer(self.api_key)
        enhanced = await enhancer.enhance_with_detected_structure(
            extracted, 
            document_text,
            detection  # NEW: Pass detected structure
        )
        
        # Continue with existing mapping...
        # (rest of existing code)
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}", exc_info=True)
        raise
```

---

### PHASE 2: Enhanced EROAD Style Enhancer (3 hours)

**File:** `/app/backend/eroad_style_enhancer.py`

**Update `enhance_for_visualization` to `enhance_with_detected_structure`:**

```python
async def enhance_with_detected_structure(
    self,
    extracted_data: Dict[str, Any],
    document_text: str,
    detection: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhanced EROAD-style with structure awareness
    
    Uses detected patterns:
    - Swim lanes
    - Phases
    - Decision points
    - Monitoring loops
    - Parallel activities
    """
    logger.info("🎨 EROAD Enhancement with Structure Awareness")
    
    # Build context from detection
    structure_context = self._build_structure_context(detection)
    
    prompt = f"""TRANSFORM TO EROAD-STYLE FLOWCHART

DETECTED STRUCTURE:
{structure_context}

EXTRACTED DATA:
{json.dumps(extracted_data, indent=2)[:10000]}

DOCUMENT EXCERPT:
{document_text[:15000]}

TRANSFORMATION RULES:

1. SWIM LANES (if detected):
   {{
     "swimLanes": {detection.get('swimLanes', [])}
   }}
   - Position nodes in correct swim lane
   - X-coordinates: Lane 1=150, Lane 2=380, Lane 3=610
   - Parallel nodes in different lanes at same Y level

2. PHASES (if detected):
   {{
     "phases": {detection.get('phases', [])}
   }}
   - Group nodes by phase
   - Add phase progress badges at Y positions

3. DECISION POINTS (detected):
   {json.dumps(detection.get('decisionPoints', []), indent=2)}
   - Mark as: isDecisionPoint: true
   - Create diamond shape
   - Add decisionOptions: {{"yes": "node_id", "no": "node_id"}}

4. MONITORING LOOPS (detected):
   {json.dumps(detection.get('monitoringLoops', []), indent=2)}
   - Mark as: isLoop: true
   - Add loopBackTo: "node_id"
   - Add dashed connection line

5. PARALLEL ACTIVITIES (detected):
   {json.dumps(detection.get('parallelActivities', []), indent=2)}
   - Same Y position
   - Different X positions (different lanes)
   - Mark with parallelWith: ["node_id_1", "node_id_2"]

6. GROUPING (8-13 nodes total):
   - Combine related sequential steps
   - Keep decision points separate
   - Keep parallel activities as individual nodes
   - Merge trivial steps into parent node's subSteps

RETURN VALID JSON:
{{
  "processName": "Process Title",
  "swimLanes": [...],  // If detected
  "phases": [...],      // If detected
  "nodes": [
    {{
      "id": "node_1",
      "title": "Step Title (max 50 chars)",
      "details": "Brief description",
      "purpose": "WHY this step exists (value-add)",
      "status": "trigger|critical|action|communication|monitoring|verification|recovery",
      "x": 150,  // Based on swim lane
      "y": 40,
      "swimLane": "onshore",  // If swim lanes detected
      "phase": 1,             // If phases detected
      "isDecisionPoint": false,
      "decisionCriteria": null,
      "decisionOptions": {{}},
      "isLoop": false,
      "loopBackTo": null,
      "parallelWith": [],
      "connections": ["node_2"],
      "contacts": ["Role: Name (phone)"],
      "systems": ["System1", "System2"],
      "timing": "5 minutes",
      "actions": ["Specific action 1", "Specific action 2"],
      "currentState": "How it's done now",
      "idealState": "How it should be done",
      "gap": "What's wrong/missing"
    }}
  ]
}}

CRITICAL:
- Use detected structure (swim lanes, phases, decisions, loops)
- Position nodes correctly based on swim lanes
- Mark decision points and loops explicitly
- Create connections for branches (YES/NO)
- Return ONLY valid JSON

Generate now:"""
    
    # ... rest of enhancement logic
```

**Add helper method:**

```python
def _build_structure_context(self, detection: Dict[str, Any]) -> str:
    """Build human-readable context from detection"""
    context = []
    
    if detection.get("swimLanes"):
        lanes = [f"{lane['title']} ({lane['team']})" for lane in detection['swimLanes']]
        context.append(f"SWIM LANES: {', '.join(lanes)}")
    
    if detection.get("phases"):
        phases = [f"Phase {p['number']}: {p['title']}" for p in detection['phases']]
        context.append(f"PHASES: {', '.join(phases)}")
    
    if detection.get("decisionPoints"):
        context.append(f"DECISIONS: {len(detection['decisionPoints'])} decision points detected")
    
    if detection.get("monitoringLoops"):
        context.append(f"LOOPS: {len(detection['monitoringLoops'])} monitoring loops detected")
    
    if detection.get("hasRACITable"):
        context.append("RACI TABLE: Role-based responsibilities detected")
    
    return "\n".join(context)
```

---

### PHASE 3: Long Document Handling (1 hour)

**Add chunking strategy for 20+ page documents:**

```python
async def process_long_document(self, document_text: str, input_type: str) -> Dict[str, Any]:
    """
    Handle documents longer than 20 pages
    
    Strategy:
    1. Detect structure first (full document)
    2. Chunk document by sections
    3. Process each chunk
    4. Merge results
    """
    doc_length = len(document_text)
    
    if doc_length < 50000:  # ~25 pages
        # Process normally
        return await self.generate_eroad_style_flowchart(document_text, input_type)
    
    logger.info(f"📚 Long document detected ({doc_length} chars) - using chunking strategy")
    
    # Step 1: Detect structure (use first 25K chars)
    detection = await self.detect_multiple_processes_and_structure(document_text[:25000])
    
    # Step 2: Chunk by phases or sections
    if detection.get("phases"):
        chunks = self._chunk_by_phases(document_text, detection["phases"])
    else:
        chunks = self._chunk_by_size(document_text, chunk_size=20000)
    
    # Step 3: Process each chunk
    all_nodes = []
    for i, chunk in enumerate(chunks):
        logger.info(f"   Processing chunk {i+1}/{len(chunks)}")
        result = await self.analyze_document(chunk, input_type, None)
        all_nodes.extend(result.get("steps", []))
    
    # Step 4: Merge and enhance
    merged_data = {
        "documentSummary": f"Complex process with {len(all_nodes)} steps",
        "steps": all_nodes,
        "detection": detection
    }
    
    # Continue with enhancement
    from eroad_style_enhancer import EROADStyleEnhancer
    enhancer = EROADStyleEnhancer(self.api_key)
    return await enhancer.enhance_with_detected_structure(merged_data, document_text, detection)
```

---

### PHASE 4: Basic Version Snapshots (2 hours)

**Add version snapshot on publish:**

**File:** `/app/backend/server.py`

```python
@api_router.patch("/process/{id}/publish")
async def publish_process(id: str, request: Request):
    """Publish process + create version snapshot"""
    try:
        user = await require_auth(request)
        
        # Get process
        process = await db.processes.find_one({"id": id}, {"_id": 0})
        if not process or process.get("userId") != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Create version snapshot
        version_snapshot = {
            "id": str(uuid.uuid4()),
            "processId": id,
            "versionNumber": process.get("version", 1),
            "snapshot": process,  # Full process data
            "createdBy": user["id"],
            "createdByName": user["name"],
            "createdAt": datetime.now(timezone.utc),
            "changeType": "publish",
            "description": f"Published version {process.get('version', 1)}"
        }
        
        await db.process_versions.insert_one(version_snapshot)
        logger.info(f"📸 Version snapshot created: v{version_snapshot['versionNumber']}")
        
        # Publish process
        await db.processes.update_one(
            {"id": id},
            {"$set": {
                "status": "published",
                "publishedAt": datetime.now(timezone.utc),
                "version": process.get("version", 1) + 1  # Increment for next edit
            }}
        )
        
        return {"message": "Process published", "version": version_snapshot['versionNumber']}
        
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/process/{id}/versions")
async def get_version_history(id: str, request: Request):
    """Get version history for a process"""
    try:
        user = await require_auth(request)
        
        versions = await db.process_versions.find(
            {"processId": id},
            {"_id": 0, "snapshot": 0}  # Exclude full snapshot from list
        ).sort("versionNumber", -1).to_list(100)
        
        return versions
        
    except Exception as e:
        logger.error(f"Version history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing Plan

### Test Matrix:

| Document | Expected Detection | Expected Output |
|----------|-------------------|-----------------|
| **Wilsar BCP** | 1 process, 3 swim lanes, decisions, loops | Single flowchart with 3 lanes |
| **GDS BCP** | 1 process, 2 swim lanes, decisions | Single flowchart with 2 lanes |
| **Recruitment** | 9 processes | 9 separate flowcharts |
| **Product Recall** | 1 process, parallel, decisions, loops, RACI | Single flowchart with branches |
| **IT DR SOP** | 1 process, 7 phases, roles, gates, complex | Single phased flowchart |

### Success Criteria:

✅ **Wilsar BCP:** 3 swim lanes detected, decision diamond at "Has Wilsar Outage?", loop for "every 30 min"  
✅ **Recruitment:** 9 processes detected, user sees "Creating 9 flowcharts..."  
✅ **Product Recall:** Parallel notifications shown, "If Supplier Issue" branch, RCA loop  
✅ **IT DR SOP:** 7 phases detected, role sections, gates shown, no truncation despite 20+ pages

---

## Timeline:

- **Phase 1:** Detection logic - 3 hours
- **Phase 2:** EROAD enhancer - 3 hours
- **Phase 3:** Long docs - 1 hour
- **Phase 4:** Version snapshots - 2 hours
- **Testing:** 1 hour

**Total: 10 hours**

---

## Ready to Implement?

All specifications are complete. Shall I proceed with Phase 1 (Detection logic) first?
