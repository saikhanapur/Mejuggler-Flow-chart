# Multi-Process Detection - Restoration Plan

## Problem Analysis

Your recruitment document contains **9 distinct processes**, but the current EROAD-style endpoint generates a single linear flowchart.

**Root Cause:**
1. The `/api/process/eroad-style` endpoint bypasses multi-process detection
2. `superintelligent_ai_service.py` line 911 hardcodes `"multipleProcesses": False`
3. Stage 0 (Document Intelligence) doesn't detect multiple processes
4. The existing multi-process logic exists but isn't connected to the EROAD-style flow

## Solution Overview

**3-Step Fix:**
1. Add multi-process detection to Stage 0 (Document Intelligence)
2. Update EROAD-style endpoint to check for multiple processes
3. Use existing `_parse_multiple_processes` logic when detected

## Your Example Document Analysis

**Document:** Recruitment & Onboarding Process Maps.pdf

**Detected Processes:**
1. Standard Requisition to Hire Process
2. High Volume/High Turnover Casual Roles – Master Requisition Process
3. Raise Standard Job Requisition - Parking & Group
4. Raise Standard Job Requisition - Security
5. Job Posting (All)
6. Manage Applications & Offer – Parking/Group
7. Manage Applications & Offer - Security
8. Younity Onboarding (All)
9. Onboarding – Admin Add New Employee (All)

**Current Output:** Single linear flowchart ❌
**Expected Output:** User prompt showing 9 processes with option to create individually or merge ✅

## Implementation

### Step 1: Enhance Stage 0 to Detect Multiple Processes

**File:** `/app/backend/superintelligent_ai_service.py`

**Add new method after `analyze_document`:**

```python
async def detect_multiple_processes(self, document_text: str) -> Dict[str, Any]:
    """
    STAGE 0.5: Detect if document contains multiple distinct processes
    
    Returns:
    {
        "multipleProcesses": true/false,
        "processCount": N,
        "processTitles": ["Process 1", "Process 2", ...],
        "recommendation": "create_separate" or "create_single"
    }
    """
    logger.info("🔍 Detecting multiple processes in document...")
    
    try:
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"detect_{uuid.uuid4()}",
            system_message="""You are a process intelligence expert. Your job is to identify if a document contains:
1. A single complex process with multiple steps
2. Multiple distinct processes that should be separate flowcharts

CRITERIA FOR MULTIPLE PROCESSES:
- Each has a distinct name/title (e.g., "Process 1: Job Requisition", "Process 2: Onboarding")
- Each can stand alone as a complete workflow
- Each has different start/end points
- Each serves a different primary purpose

CRITERIA FOR SINGLE COMPLEX PROCESS:
- One overarching process with many steps
- Steps are sequential or parallel within one workflow
- Shared start or end point
- One primary purpose with sub-activities"""
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        prompt = f"""ANALYZE THIS DOCUMENT FOR MULTIPLE PROCESSES

DOCUMENT (first 20,000 chars):
{document_text[:20000]}

QUESTIONS TO ANSWER:
1. Does this document contain ONE process or MULTIPLE distinct processes?
2. If multiple, what are their names/titles?
3. Could these processes be standalone flowcharts?
4. What's the best approach: create one flowchart or multiple?

LOOK FOR INDICATORS:
- Process titles in headings (e.g., "Process 1:", "Workflow A:")
- Separate flowchart diagrams
- Different sections with complete workflows
- Distinct start and end points per section

RETURN JSON (valid JSON only, no explanation):
{{
  "multipleProcesses": true or false,
  "processCount": 1 to 20,
  "processTitles": [
    "Full title of process 1",
    "Full title of process 2",
    ...
  ],
  "processDescriptions": [
    "Brief description of process 1 purpose",
    "Brief description of process 2 purpose",
    ...
  ],
  "reasoning": "Why single or multiple",
  "recommendation": "create_separate" or "create_single",
  "complexity": "simple|medium|complex"
}}

CRITICAL:
- If you find 2+ distinct titled processes, set multipleProcesses: true
- processTitles must match the actual titles in the document
- processCount must equal length of processTitles array
- Return ONLY valid JSON, no markdown code blocks

Analyze now:"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        detection = self._parse_json_response(response)
        
        # Validate
        if detection.get("multipleProcesses"):
            if detection.get("processCount", 0) < 2:
                detection["multipleProcesses"] = False
                detection["processCount"] = 1
                logger.warning("⚠️ multipleProcesses=true but processCount<2, forcing single")
        
        logger.info(f"✅ Detection complete: {detection.get('processCount')} process(es) found")
        logger.info(f"   Processes: {detection.get('processTitles', [])}")
        
        return detection
        
    except Exception as e:
        logger.error(f"❌ Process detection failed: {e}", exc_info=True)
        # Default to single process on error
        return {
            "multipleProcesses": False,
            "processCount": 1,
            "processTitles": ["Untitled Process"],
            "reasoning": f"Detection failed: {str(e)}",
            "recommendation": "create_single",
            "complexity": "unknown"
        }
```

### Step 2: Update `generate_eroad_style_flowchart` to Check for Multiple Processes

**File:** `/app/backend/superintelligent_ai_service.py`

**Replace lines 758-911 with:**

```python
async def generate_eroad_style_flowchart(
    self,
    document_text: str,
    input_type: str,
    user_id: str = None
) -> Dict[str, Any]:
    """
    HYBRID APPROACH: Detect → Extract → Enhance → Return
    
    NEW: Now detects multiple processes first!
    
    Phase 0: Detect if document has multiple processes
    Phase 1: Extract structured data (one or many)
    Phase 2: Enhance with EROAD-style grouping and rich details
    
    Returns visualization-ready flowchart(s)
    """
    logger.info("🚀 EROAD-Style Flowchart Generation (Hybrid with Multi-Process Detection)")
    
    try:
        # PHASE 0: Detect multiple processes
        detection = await self.detect_multiple_processes(document_text)
        
        # If multiple processes detected, return early for user confirmation
        if detection.get("multipleProcesses") and detection.get("processCount", 0) >= 2:
            logger.info(f"🔍 Multiple processes detected: {detection['processCount']}")
            
            # Return detection result for frontend to show MultiProcessReview UI
            return {
                "multipleProcesses": True,
                "processCount": detection["processCount"],
                "processTitles": detection["processTitles"],
                "processDescriptions": detection.get("processDescriptions", []),
                "recommendation": detection.get("recommendation"),
                "complexity": detection.get("complexity"),
                "reasoning": detection.get("reasoning"),
                "processes": []  # Empty - user must confirm first
            }
        
        # PHASE 1: Single process - Extract data
        logger.info("📄 Single process detected, proceeding with extraction...")
        extracted = await self.analyze_document(document_text, input_type, user_id)
        
        # PHASE 2: Enhance for visualization
        from eroad_style_enhancer import EROADStyleEnhancer
        
        enhancer = EROADStyleEnhancer(self.api_key)
        enhanced = await enhancer.enhance_for_visualization(extracted, document_text)
        
        # Map to expected format (existing code continues...)
        process = {
            "name": enhanced.get("processName"),
            "description": extracted.get("documentSummary"),
            "nodes": [],
            "edges": [],
            "swimLanes": enhanced.get("swimLanes", []),
            "actors": list(set([
                actor 
                for node in enhanced.get("nodes", []) 
                for actor in node.get("contacts", [])
            ])),
            "quickReference": {
                "criticalActions": [n["title"] for n in enhanced["nodes"] if n.get("status") == "critical"],
                "keyTimings": extracted.get("timings", []),
                "emergencyContacts": extracted.get("contacts", {})
            },
            "progressStages": []
        }
        
        # Process nodes (existing code continues as before...)
        # ... [rest of existing node processing code] ...
        
        # Return single process
        return {"processes": [process], "multipleProcesses": False}
        
    except Exception as e:
        logger.error(f"❌ EROAD-style generation failed: {e}", exc_info=True)
        raise
```

### Step 3: Add Backend Endpoint for Creating Individual Processes

**File:** `/app/backend/server.py`

**Add after the `/process/eroad-style` endpoint (around line 2753):**

```python
@api_router.post("/process/eroad-style/create-selected")
async def eroad_style_create_selected(
    request_data: dict,
    request: Request
):
    """
    Create selected processes from multi-process document
    
    Called after user reviews MultiProcessReview and clicks "Create Selected"
    
    Input:
    {
        "documentText": "full document text",
        "inputType": "document",
        "selectedProcessTitles": ["Process 1", "Process 3", "Process 5"],
        "mergeIntoOne": false
    }
    """
    try:
        from superintelligent_ai_service import SuperintelligentAIService
        
        user = await get_current_user(request)
        user_id = user.get("id") if user else None
        
        document_text = request_data.get("documentText")
        input_type = request_data.get("inputType", "document")
        selected_titles = request_data.get("selectedProcessTitles", [])
        merge_into_one = request_data.get("mergeIntoOne", False)
        
        logger.info(f"🎨 Creating {len(selected_titles)} selected process(es)")
        
        service = SuperintelligentAIService(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            db_client=client
        )
        
        if merge_into_one:
            # User chose to merge all into one flowchart
            logger.info("Merging all processes into single flowchart")
            result = await service.generate_eroad_style_single_merged(
                document_text, input_type, selected_titles, user_id
            )
        else:
            # Create individual flowcharts for each selected process
            logger.info(f"Creating individual flowcharts for {len(selected_titles)} processes")
            
            processes = []
            for i, process_title in enumerate(selected_titles):
                logger.info(f"Creating process {i+1}/{len(selected_titles)}: {process_title}")
                
                # Extract section for this process
                process_text = service._extract_process_section(
                    document_text, 
                    process_title, 
                    selected_titles
                )
                
                # Generate EROAD-style flowchart for this one process
                process_result = await service.generate_eroad_style_single_process(
                    process_text, 
                    process_title, 
                    input_type, 
                    user_id
                )
                
                processes.append(process_result["processes"][0])
            
            result = {
                "multipleProcesses": True,
                "processCount": len(processes),
                "processes": processes
            }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Selected process creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 4: Add Helper Method for Single Process Generation

**File:** `/app/backend/superintelligent_ai_service.py`

**Add after `generate_eroad_style_flowchart`:**

```python
async def generate_eroad_style_single_process(
    self,
    process_text: str,
    process_title: str,
    input_type: str,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Generate EROAD-style flowchart for a SINGLE PROCESS
    
    Used when user selects individual processes from multi-process document
    """
    logger.info(f"🎯 Generating EROAD-style flowchart for: {process_title}")
    
    try:
        # Extract data for this one process
        extracted = await self.analyze_document(process_text, input_type, user_id)
        
        # Override process name with the selected title
        extracted["processName"] = process_title
        
        # Enhance for visualization
        from eroad_style_enhancer import EROADStyleEnhancer
        
        enhancer = EROADStyleEnhancer(self.api_key)
        enhanced = await enhancer.enhance_for_visualization(extracted, process_text)
        
        # Override name again (ensure it's preserved)
        enhanced["processName"] = process_title
        
        # Map to expected format (same as generate_eroad_style_flowchart)
        process = {
            "name": process_title,  # Use selected title
            "description": extracted.get("documentSummary", f"Workflow for {process_title}"),
            "nodes": [],
            "edges": [],
            "swimLanes": enhanced.get("swimLanes", []),
            "actors": list(set([
                actor 
                for node in enhanced.get("nodes", []) 
                for actor in node.get("contacts", [])
            ])),
            "quickReference": {
                "criticalActions": [n["title"] for n in enhanced["nodes"] if n.get("status") == "critical"],
                "keyTimings": extracted.get("timings", []),
                "emergencyContacts": extracted.get("contacts", {})
            },
            "progressStages": []
        }
        
        # Process nodes (same logic as before)
        for node in enhanced.get("nodes", []):
            processed_node = {
                "id": node["id"],
                "title": node["title"],
                "description": node.get("details", ""),
                "type": self._map_status_to_type(node.get("status")),
                "status": node.get("status", "operational"),
                "x": node.get("x", 330),
                "y": node.get("y", 0),
                "position": {"x": node.get("x", 0), "y": node.get("y", 0)},
                "actors": node.get("contacts", []),
                "subSteps": node.get("actions", []),
                "dependencies": node.get("dependencies", []),
                "parallelWith": node.get("parallelWith", []),
                "isDecisionPoint": node.get("isDecisionPoint", False),
                "decisionOptions": node.get("decisionOptions", {}),
                "isLoop": node.get("isLoop", False),
                "loopBackTo": node.get("loopBackTo"),
                "failures": [],
                "blocking": None,
                "impact": "high" if node.get("status") == "critical" else "medium",
                "timeEstimate": node.get("timing"),
                "operationalDetails": {
                    "purpose": node.get("purpose", ""),
                    "specificActions": node.get("actions", []),
                    "requiredData": [],
                    "contactInfo": {c.split(":")[0]: c.split(":")[1].strip() if ":" in c else c for c in node.get("contacts", [])},
                    "timeline": node.get("timing"),
                    "systems": node.get("systems", []),
                    "decisionCriteria": node.get("decisionCriteria") if node.get("isDecisionPoint") else None,
                    "emailTemplates": [],
                    "currentState": node.get("currentState"),
                    "idealState": node.get("idealState"),
                    "gap": node.get("gap"),
                    "sourcePage": None
                }
            }
            process["nodes"].append(processed_node)
            
            # Create edges
            for target_id in node.get("connections", []):
                edge = {
                    "id": f"e-{node['id']}-{target_id}",
                    "source": node['id'],
                    "target": target_id,
                    "label": None
                }
                
                if node.get("isLoop") and target_id == node.get("loopBackTo"):
                    edge["type"] = "dashed"
                
                if node.get("isDecisionPoint") and node.get("decisionOptions"):
                    decision_opts = node.get("decisionOptions", {})
                    if decision_opts.get("yes") == target_id:
                        edge["label"] = "YES"
                    elif decision_opts.get("no") == target_id:
                        edge["label"] = "NO"
                
                process["edges"].append(edge)
        
        logger.info(f"✅ EROAD-style flowchart complete for '{process_title}': {len(process['nodes'])} nodes")
        return {"processes": [process], "multipleProcesses": False}
        
    except Exception as e:
        logger.error(f"❌ Single process generation failed for '{process_title}': {e}", exc_info=True)
        raise
```

### Step 5: Update Frontend ProcessCreator to Handle Detection

**File:** `/app/frontend/src/components/ProcessCreator.js`

**Update the `handleGenerateEROAD` function (around line 350-400):**

```javascript
const handleGenerateEROAD = async () => {
  if (!extractedData.text) {
    toast.error('Please upload and extract a document first');
    return;
  }

  setLoading(true);
  setLoadingMessage('Analyzing document structure...');

  try {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/process/eroad-style`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        text: extractedData.text,
        inputType: extractedData.inputType || 'document'
      })
    });

    if (!response.ok) throw new Error('Generation failed');

    const result = await response.json();

    // NEW: Check if multiple processes detected
    if (result.multipleProcesses && result.processCount >= 2) {
      setLoadingMessage('');
      setLoading(false);
      
      // Show MultiProcessReview UI
      setExtractedData({
        ...extractedData,
        multipleProcesses: true,
        processCount: result.processCount,
        processTitles: result.processTitles,
        processDescriptions: result.processDescriptions,
        recommendation: result.recommendation,
        complexity: result.complexity,
        reasoning: result.reasoning
      });
      
      toast.info(`${result.processCount} processes detected in document!`);
      return;
    }

    // Single process - continue as normal
    setLoadingMessage('Generating flowchart...');
    setFlowchartData(result);
    setCurrentStep('flowchart');
    toast.success('Flowchart generated successfully!');

  } catch (error) {
    console.error('Generation error:', error);
    toast.error('Failed to generate flowchart');
  } finally {
    setLoading(false);
    setLoadingMessage('');
  }
};
```

**Update the render to show MultiProcessReview when needed:**

```javascript
// In the render section, after extraction review
{currentStep === 'extract-review' && extractedData.multipleProcesses && (
  <MultiProcessReview
    processesData={extractedData}
    onBack={() => setCurrentStep('upload')}
    currentWorkspace={currentWorkspace}
    selectedWorkspace={selectedWorkspace}
    documentText={extractedData.text}
    inputType={extractedData.inputType}
  />
)}
```

### Step 6: Update MultiProcessReview to Use New Endpoint

**File:** `/app/frontend/src/components/MultiProcessReview.js`

**Update the `handleCreateSelected` function (around line 120-180):**

```javascript
const handleCreateSelected = async (selectedTitles, mergeIntoOne = false) => {
  if (selectedTitles.length === 0) {
    toast.error('Please select at least one process');
    return;
  }

  setLoading(true);
  setProgress(0);

  try {
    // Call new endpoint for creating selected processes
    const response = await fetch(
      `${process.env.REACT_APP_BACKEND_URL}/api/process/eroad-style/create-selected`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({
          documentText: processesData.text,
          inputType: processesData.inputType || 'document',
          selectedProcessTitles: selectedTitles,
          mergeIntoOne: mergeIntoOne
        })
      }
    );

    if (!response.ok) throw new Error('Failed to create processes');

    const result = await response.json();

    // Create processes in database
    const createdProcesses = [];
    for (let i = 0; i < result.processes.length; i++) {
      const process = result.processes[i];
      
      const createResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/process`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify({
            ...process,
            workspaceId: selectedWorkspace || currentWorkspace?.id
          })
        }
      );

      if (createResponse.ok) {
        const created = await createResponse.json();
        createdProcesses.push(created);
      }

      setProgress(((i + 1) / result.processes.length) * 100);
    }

    toast.success(`Created ${createdProcesses.length} flowchart(s)!`);
    navigate('/dashboard');

  } catch (error) {
    console.error('Error creating processes:', error);
    toast.error('Failed to create processes');
  } finally {
    setLoading(false);
  }
};
```

## Testing Plan

### Test Case 1: Your Recruitment Document (9 Processes)

**Expected Flow:**
1. Upload recruitment PDF
2. Extract text
3. Click "Generate Flowchart"
4. **NEW:** See detection message: "9 processes detected in document!"
5. **NEW:** See MultiProcessReview UI showing:
   - Standard Requisition to Hire Process
   - High Volume/High Turnover Casual Roles
   - Raise Standard Job Requisition - Parking & Group
   - Raise Standard Job Requisition - Security
   - Job Posting (All)
   - Manage Applications & Offer – Parking/Group
   - Manage Applications & Offer - Security
   - Younity Onboarding (All)
   - Onboarding – Admin Add New Employee (All)
6. **NEW:** User can:
   - Select which processes to create (checkboxes)
   - Edit process names
   - Click "Create Selected" → 9 individual flowcharts
   - OR Click "Merge into One" → 1 complex flowchart

### Test Case 2: Single Complex Document (Your BCP)

**Expected Flow:**
1. Upload BCP PDF (Wilsar Outage)
2. Extract text
3. Click "Generate Flowchart"
4. Detection shows: "1 process detected"
5. Continue directly to flowchart generation (no MultiProcessReview)

### Test Case 3: Simple Document (5 steps)

**Expected Flow:**
1. Upload simple procedure
2. Extract text
3. Click "Generate Flowchart"
4. Detection shows: "1 process detected"
5. Generate simple flowchart

## Implementation Timeline

**Phase 1: Core Detection (2 hours)**
- Add `detect_multiple_processes` method
- Update `generate_eroad_style_flowchart`
- Test detection on your recruitment doc

**Phase 2: Backend Endpoints (1 hour)**
- Add `/process/eroad-style/create-selected` endpoint
- Add `generate_eroad_style_single_process` method
- Test API calls with Postman/curl

**Phase 3: Frontend Integration (1 hour)**
- Update ProcessCreator to handle detection
- Update MultiProcessReview to use new endpoint
- Test end-to-end flow

**Phase 4: Testing & Polish (1 hour)**
- Test with your 3 documents (recruitment, BCP, simple)
- Fix any edge cases
- Update error handling

**Total: ~5 hours**

## Success Criteria

✅ Recruitment doc (9 processes) → Shows MultiProcessReview with 9 options
✅ BCP doc (1 complex process) → Generates flowchart directly
✅ Simple doc (5 steps) → Generates flowchart directly
✅ User can select which processes to create individually
✅ User can merge multiple processes into one flowchart
✅ Each created flowchart is EROAD-style enhanced (not linear)

## Next Steps

Ready to implement? Let me know and I'll:
1. Start with Phase 1 (detection logic)
2. Test on your recruitment document
3. Show you the detection output
4. Continue with Phases 2-4 once detection is working

Would you like me to proceed with implementation now?
