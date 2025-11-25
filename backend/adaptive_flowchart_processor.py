"""
Adaptive Flowchart Processor

Uses document analysis to apply the RIGHT processing strategy:
- EXTRACT mode: For documents already containing flowcharts
- GENERATE mode: For text-based SOPs that need structuring
- HYBRID mode: For mixed documents

The key insight: AI must ADAPT to the document, not force the document into a template.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class AdaptiveFlowchartProcessor:
    """
    Processes documents intelligently based on their analyzed structure.
    NO MORE "create 15-25 nodes" - we create EXACTLY what's in the document.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_document(
        self, 
        document_text: str,
        analysis: Dict[str, Any],
        document_name: str = "Document"
    ) -> Dict[str, Any]:
        """
        Process document using the strategy determined by analysis.
        """
        
        strategy = analysis.get("processingStrategy", "generate")
        estimated_nodes = analysis.get("existingStructure", {}).get("estimatedNodes", 15)
        
        logger.info(f"⚡ Processing with strategy: {strategy}")
        logger.info(f"📊 Expected nodes: ~{estimated_nodes}")
        
        # Truncate if too long
        doc_text = document_text[:50000]
        
        # Launch THREE parallel calls with ADAPTIVE prompts
        structure_task = self._extract_structure(
            doc_text, document_name, analysis
        )
        content_task = self._extract_content(
            doc_text, document_name, analysis
        )
        references_task = self._extract_references(
            doc_text, document_name
        )
        
        # Wait for all three to complete
        structure, content, references = await asyncio.gather(
            structure_task,
            content_task,
            references_task,
            return_exceptions=True
        )
        
        # Check for failures
        if isinstance(structure, Exception):
            logger.error(f"❌ Structure extraction failed: {structure}")
            structure = {"nodes": [], "swimLanes": []}
        if isinstance(content, Exception):
            logger.error(f"❌ Content extraction failed: {content}")
            content = {}
        if isinstance(references, Exception):
            logger.error(f"❌ References extraction failed: {references}")
            references = {"contacts": [], "templates": []}
        
        # MERGE the results
        result = self._merge_results(structure, content, references, analysis)
        
        # Validate
        result = self._validate_and_fix(result)
        
        # Apply intelligent grouping post-processing
        result = self._apply_intelligent_grouping(result)
        
        logger.info(f"✅ Processing complete: {len(result['nodes'])} nodes (expected ~{estimated_nodes})")
        
        return result
    
    async def _extract_structure(
        self, 
        doc_text: str, 
        doc_name: str,
        analysis: Dict[str, Any]
    ) -> Dict:
        """
        Extract flowchart structure with ADAPTIVE prompts based on analysis.
        """
        
        strategy = analysis.get("processingStrategy", "generate")
        estimated_nodes = analysis.get("existingStructure", {}).get("estimatedNodes", 15)
        doc_type = analysis.get("documentType", "text_sop")
        fidelity = analysis.get("fidelityRequirement", "medium")
        
        logger.info(f"📊 [Call 1/3] Extracting structure (strategy: {strategy})...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="adaptive_structure",
            system_message="Extract flowchart structure with PERFECT FIDELITY. Never hallucinate steps."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=8000)
        
        # Build adaptive prompt based on strategy
        if strategy == "extract":
            instruction = self._build_extract_prompt(doc_text, estimated_nodes, doc_type)
        elif strategy == "generate":
            instruction = self._build_generate_prompt(doc_text, estimated_nodes)
        else:
            instruction = self._build_hybrid_prompt(doc_text, estimated_nodes)
        
        message = UserMessage(text=instruction)
        response = await chat.send_message(message)
        return self._parse_json(response)
    
    def _build_extract_prompt(self, doc_text: str, estimated_nodes: int, doc_type: str) -> str:
        """
        Build prompt for EXTRACTION mode (document already has flowchart).
        """
        return f"""CRITICAL TASK: This document describes an EXISTING flowchart. Your job is to EXTRACT it EXACTLY as described.

DOCUMENT:
{doc_text[:20000]}

TASK: Extract the EXACT flowchart structure described in this document.

RULES (CRITICAL - THIS IS EMERGENCY SERVICES):
1. This document describes approximately {estimated_nodes} nodes. Extract EXACTLY what's described.
2. DO NOT add steps that aren't explicitly mentioned.
3. DO NOT skip any steps that ARE mentioned.
4. DO NOT "improve" or "reorganize" - preserve EXACTLY.
5. Look for explicit node descriptions like "Step 1:", "Decision Node:", "Action Node:", diamond shapes, rectangle shapes, etc.

DECISION NODE IDENTIFICATION:
- Any node with "?" in the title is a DECISION (e.g., "User Contacted?")
- Any node labeled "Decision Node" or "Diamond shape" is a DECISION
- Any node with YES/NO branches is a DECISION
- Set isDecisionPoint: true and provide decisionOptions

ACTION NODE IDENTIFICATION:
- Nodes labeled "Action Node", "Process Node", or "Rectangle shape" are ACTIONS
- Nodes with imperative verbs ("Call", "Dispatch", "Contact") are ACTIONS
- Start and End nodes (Ovals) are ACTIONS
- Set isDecisionPoint: false

NODE CONSOLIDATION:
- If "Start" and first action are essentially the same (e.g., "Panic Triggered" → "Call User"), keep them separate only if both are explicitly described as distinct nodes
- Do NOT create intermediate nodes between clearly connected steps

For EACH node mentioned, extract:
- The EXACT title/name given in the document
- Correct type based on shape or context (decision vs action)
- Exact connections as described
- Roles if mentioned

Return JSON:
{{
  "processName": "Exact process name from document",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "EXACT title from document",
      "description": "Brief description if provided",
      "status": "critical|action|operational|communication",
      "swimLane": "Role if mentioned, otherwise 'Operations'",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question for decision nodes",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Operations", "color": "#3B82F6"}}
  ]
}}

Target: EXACTLY {estimated_nodes} nodes (±1 acceptable).
PERFECT FIDELITY to source. NO hallucinations.
Return ONLY JSON."""
    
    def _build_generate_prompt(self, doc_text: str, estimated_nodes: int) -> str:
        """
        Build prompt for GENERATION mode (text SOP needs flowchart).
        PRIORITY: 100% ACCURACY - Zero hallucinations.
        """
        
        return f"""You are an expert at analyzing Standard Operating Procedures (SOPs) and creating accurate flowcharts.

CRITICAL MISSION: Create a flowchart that is 100% ACCURATE to the source document. ZERO hallucinations allowed.

DOCUMENT TO ANALYZE:
{doc_text[:20000]}

═══════════════════════════════════════════════════════════════════════════

🎯 CORE PRINCIPLES (NEVER VIOLATE):

1. **ACCURACY OVER EVERYTHING**
   - Every node MUST come directly from the document
   - Every node title MUST be traceable to specific text in the document
   - If you're unsure about something, use the EXACT wording from the document
   - NEVER invent, assume, or "improve" steps that aren't explicitly mentioned

2. **ZERO HALLUCINATION RULE**
   - ❌ FORBIDDEN: Creating nodes like "Extended Monitoring Protocol" if it's not in the document
   - ❌ FORBIDDEN: Inventing technical terms that aren't in the source
   - ❌ FORBIDDEN: Adding "best practice" steps not mentioned in the SOP
   - ✅ REQUIRED: Use only steps, decisions, and terminology FROM THE DOCUMENT

3. **DECISION POINT DETECTION**
   - Look for explicit decision language:
     * "Check if...", "Ask if...", "Determine whether..."
     * "If X, then Y, else Z"
     * Questions in the text (e.g., "Is the user able to speak?")
   - Create a decision node with:
     * isDecisionPoint: true
     * Clear YES/NO branches
     * Explicit decisionCriteria from the document

4. **SEQUENTIAL ACCURACY**
   - Follow the EXACT sequence in the document
   - If SOP says "Step 1, Step 2, Step 3", your flowchart must follow that order
   - Don't reorder steps to "improve" the flow

5. **CONTEXT UNDERSTANDING**
   - Read the ENTIRE document first to understand:
     * What is the main process? (e.g., "Panic Alert Response")
     * Who are the actors? (e.g., "Operator", "Emergency Services", "Supervisor")
     * What is the goal? (e.g., "Ensure user safety")
   - Use this context to guide node creation, but DON'T add context that isn't there

═══════════════════════════════════════════════════════════════════════════

📖 STEP-BY-STEP ANALYSIS PROCESS:

**STEP 1: Identify the Process**
- What is this SOP about? Extract the process name from section headers or document title
- Example: If document says "## Panic Alert", process name is "Panic Alert"

**STEP 2: Find All Actions**
- Look for numbered steps (1., 2., 3.) or bullet points
- Look for imperative verbs: "Contact", "Check", "Call", "Ask", "Wait"
- Each distinct action = potential node

**STEP 3: Find All Decisions**
- Look for:
  * "If X then Y" statements
  * Questions (e.g., "Is the user able to speak freely?")
  * Decision language: "Check whether", "Determine if", "Ask if"
- Each decision = decision node with YES/NO branches

**STEP 4: Map the Flow**
- Follow the document's sequence
- Connect nodes in the order they appear
- For decisions, trace both YES and NO paths

**STEP 5: Validate Against Source**
- For each node you create, ask yourself:
  * "Can I point to the exact sentence in the document that mentions this?"
  * "Am I using the same terminology as the document?"
  * "Have I added anything that isn't explicitly stated?"

═══════════════════════════════════════════════════════════════════════════

🔍 NODE CREATION RULES:

**For Process Nodes:**
- Title: Use wording from the document (e.g., if SOP says "Contact Emergency Services", title is "Contact Emergency Services")
- Description: Brief summary of what happens
- subSteps: Break down the details if the document provides them
- Do NOT create summary nodes that don't exist (e.g., don't create "Initial Assessment" unless document explicitly has that phase)

**For Decision Nodes:**
- Title: The question being asked (e.g., "Can User Speak Freely?")
- isDecisionPoint: true
- decisionCriteria: The exact question from the document
- decisionOptions: {{"yes": "node-id-for-yes-path", "no": "node-id-for-no-path"}}
- Both YES and NO paths MUST be defined

**Grouping Rules (Use Sparingly):**
- ONLY group actions if they are:
  1. Truly repetitive (e.g., "Call Contact 1", "Call Contact 2", "Call Contact 3" → "Escalate Through Contacts")
  2. Explicitly grouped in the document (e.g., document says "Perform the following steps: a, b, c")
- When in doubt, keep actions separate

═══════════════════════════════════════════════════════════════════════════

📋 OUTPUT FORMAT:

Return ONLY valid JSON in this exact structure:

{{
  "processName": "Exact process name from document",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process",
      "title": "Exact action from document",
      "description": "Brief description",
      "status": "critical|action|operational|communication",
      "swimLane": "Actor/Role from document",
      "connections": ["node-2"],
      "isDecisionPoint": false,
      "actors": ["Operator"],
      "subSteps": ["Detailed step 1", "Detailed step 2"]
    }},
    {{
      "id": "node-2",
      "type": "decision",
      "title": "Question from document",
      "description": "Decision point description",
      "status": "critical",
      "swimLane": "Actor",
      "connections": ["node-3", "node-4"],
      "isDecisionPoint": true,
      "decisionCriteria": "The question being asked",
      "decisionOptions": {{"yes": "node-3", "no": "node-4"}},
      "actors": ["Operator"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Operator", "color": "#3B82F6"}}
  ]
}}

═══════════════════════════════════════════════════════════════════════════

⚠️ FINAL CHECKLIST BEFORE RETURNING:

1. ✅ Every node title can be traced to specific text in the document
2. ✅ No invented terminology or concepts
3. ✅ All decision nodes have YES and NO branches defined
4. ✅ Flow sequence matches document order
5. ✅ No steps are missing from the document
6. ✅ No extra steps added that aren't in the document

If you cannot meet ALL these criteria with 100% confidence, return fewer nodes but ensure those you create are PERFECT.

ACCURACY > COMPLETENESS. Better to have 5 perfect nodes than 15 nodes with hallucinations.

Now analyze the document and return ONLY the JSON."""
    
    def _build_hybrid_prompt(self, doc_text: str, estimated_nodes: int) -> str:
        """
        Build prompt for HYBRID mode (mixed structure).
        """
        return f"""TASK: Process this document which has SOME flowchart structure but needs organization.

DOCUMENT:
{doc_text[:20000]}

TASK: Extract existing structure and intelligently organize any unstructured parts.

RULES:
1. Where flowchart structure is clearly described, EXTRACT it exactly
2. Where text is unstructured, intelligently organize it
3. Estimated complexity: ~{estimated_nodes} nodes
4. Maintain fidelity to source material
5. Do not over-complicate or under-simplify

Return JSON:
{{
  "processName": "Process name",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "Node title",
      "description": "Description",
      "status": "critical|action|operational|communication",
      "swimLane": "Role",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Lane Name", "color": "#3B82F6"}}
  ]
}}

Expected range: {max(3, estimated_nodes-3)} to {estimated_nodes+3} nodes.
Return ONLY JSON."""
    
    async def _extract_content(
        self, 
        doc_text: str, 
        doc_name: str,
        analysis: Dict[str, Any]
    ) -> Dict:
        """
        Extract detailed content for each node.
        """
        logger.info("📝 [Call 2/3] Extracting content...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="adaptive_content",
            system_message="Extract detailed content accurately. No hallucination."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=8000)
        
        prompt = f"""Extract ACTIONABLE, DIFFERENTIATED CONTENT from this document for interactive flowchart nodes:

{doc_text[:20000]}

CRITICAL: For each major step, provide DIFFERENT types of information:
1. subSteps: Concrete action items someone would DO (not just restating the step name)
2. operationalDetails: Specific how-to information, checklists, timing, tools

EXAMPLES OF GOOD vs BAD:

❌ BAD (Duplication):
  Step: "Call First Contact"
  subSteps: ["Call the first contact person"]  <-- Just repeating the title!

✅ GOOD (Actionable):
  Step: "Call First Contact" 
  subSteps: [
    "Locate contact phone number in escalation list",
    "Prepare incident summary before calling",
    "Make call and document response time"
  ]

For each major step/action, extract:
- 2-5 SPECIFIC sub-actions (what to actually DO, not just restate the step)
- Timing/duration if mentioned
- Systems/tools/documents to use
- Any checklists or verification steps

Return JSON:
{{
  "contentByStep": {{
    "step-name-1": {{
      "subSteps": ["Specific action 1", "Specific action 2", "Specific action 3"],
      "operationalDetails": {{
        "specificActions": ["How-to detail 1", "Checklist item 2"],
        "estimatedDuration": "X minutes if mentioned",
        "gap": false,
        "toolsRequired": ["System names", "Documents needed"]
      }},
      "timing": "When/how long if mentioned",
      "systems": ["System names if mentioned"]
    }}
  }}
}}

Extract ONLY what's in the document. If document lacks detail, generate logical sub-steps based on context.
Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return self._parse_json(response)
    
    async def _extract_references(self, doc_text: str, doc_name: str) -> Dict:
        """
        Extract critical reference information.
        """
        logger.info("📚 [Call 3/3] Extracting references...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="adaptive_references",
            system_message="Extract critical reference info only."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=6000)
        
        prompt = f"""Extract CRITICAL REFERENCE INFORMATION ONLY:

{doc_text[:30000]}

Extract ONLY:
1. Emergency contacts (name, phone, when to call)
2. Key scripts/templates (SUMMARY only, 1-2 sentences)
3. Critical timings (e.g., "Wait 5 minutes", "Check every 30 min")

Return JSON:
{{
  "contacts": [
    {{
      "name": "Contact name",
      "phone": "Phone",
      "role": "When to call"
    }}
  ],
  "keyScripts": [
    {{
      "name": "Script name",
      "summary": "1-sentence summary"
    }}
  ],
  "criticalTimings": [
    "Timing guideline"
  ]
}}

Keep CONCISE. Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return self._parse_json(response)
    
    def _merge_results(
        self, 
        structure: Dict, 
        content: Dict, 
        references: Dict,
        analysis: Dict[str, Any]
    ) -> Dict:
        """
        Merge the three parallel results.
        """
        logger.info("🔗 Merging structure + content + references...")
        
        # Start with structure
        result = {
            "processName": structure.get("processName", "Process Flowchart"),
            "nodes": structure.get("nodes", []),
            "swimLanes": structure.get("swimLanes", []),
            "contacts": references.get("contacts", []),
            "keyScripts": references.get("keyScripts", []),
            "criticalTimings": references.get("criticalTimings", [])
        }
        
        # Enhance nodes with detailed content
        content_map = content.get("contentByStep", {})
        
        for node in result["nodes"]:
            title = node.get("title", "")
            
            # Try to find matching content
            matching_content = None
            for step_name, step_content in content_map.items():
                if step_name.lower() in title.lower() or title.lower() in step_name.lower():
                    matching_content = step_content
                    break
            
            if matching_content:
                node["subSteps"] = matching_content.get("subSteps", [])
                node["operationalDetails"] = matching_content.get("operationalDetails", {})
                if "timing" in matching_content:
                    node["timing"] = matching_content["timing"]
                if "systems" in matching_content:
                    node["systems"] = matching_content["systems"]
            else:
                # Fallback: Generate meaningful sub-steps from title
                title_lower = title.lower()
                desc = node.get("description", "")
                
                # Create actionable sub-steps based on common patterns
                if "call" in title_lower or "contact" in title_lower:
                    node["subSteps"] = [
                        f"Locate contact information",
                        f"Make the call and document the attempt",
                        f"Record response or no-answer status"
                    ]
                elif "review" in title_lower or "check" in title_lower:
                    node["subSteps"] = [
                        f"Access the relevant system or document",
                        f"Verify key details and indicators",
                        f"Document findings"
                    ]
                elif "escalate" in title_lower or "notify" in title_lower:
                    node["subSteps"] = [
                        f"Prepare incident summary",
                        f"Contact appropriate party",
                        f"Confirm handover"
                    ]
                elif desc and len(desc) > 10:
                    # Use description as single substep if it's meaningful
                    node["subSteps"] = [desc]
                else:
                    # Generic fallback
                    node["subSteps"] = [f"Complete {title.lower()} as documented"]
                
                node["operationalDetails"] = {
                    "specificActions": node["subSteps"][:],
                    "estimatedDuration": "",
                    "gap": False
                }
        
        # POST-PROCESSING: Deduplicate content
        for node in result["nodes"]:
            title = node.get("title", "").lower()
            desc = node.get("description", "").lower()
            substeps = node.get("subSteps", [])
            
            # If substeps just repeat the description, make them more actionable
            if substeps and len(substeps) == 1:
                substep_lower = substeps[0].lower()
                # Check if substep is essentially the same as description
                if desc and (substep_lower == desc or (len(desc) > 20 and substep_lower in desc)):
                    # Replace with more actionable steps
                    logger.info(f"⚠️ Deduplicating substeps for: {node.get('title')}")
                    if "call" in title or "contact" in title:
                        node["subSteps"] = [
                            "Retrieve contact information from escalation list",
                            "Place call and document attempt time",
                            "Record outcome (answered/no answer)"
                        ]
                    elif "review" in title or "evaluate" in title or "check" in title:
                        node["subSteps"] = [
                            "Access relevant information or system",
                            "Examine key indicators or details",
                            "Document findings and next steps"
                        ]
                    elif "record" in title or "log" in title or "document" in title:
                        node["subSteps"] = [
                            "Gather all relevant information",
                            "Enter data into system",
                            "Verify entry accuracy"
                        ]
                    else:
                        # Keep the original but add context
                        node["subSteps"] = [
                            substeps[0],
                            "Document completion",
                            "Proceed to next step"
                        ]
        
        logger.info(f"✅ Merged and deduplicated: {len(result['nodes'])} nodes")
        return result
    

    def _apply_intelligent_grouping(self, result: Dict) -> Dict:
        """
        Post-process nodes to detect and group repetitive patterns.
        
        Patterns to detect:
        1. Sequential "Call Contact" nodes → Group into "Contact Escalation"
        2. Sequential similar actions → Group into single node
        3. Preserve decision nodes (never group these)
        """
        nodes = result.get("nodes", [])
        if len(nodes) <= 5:
            logger.info("⏭️ Skipping grouping - already concise")
            return result
        
        logger.info(f"🔍 Analyzing {len(nodes)} nodes for grouping opportunities...")
        
        # Detect repetitive "Call X Contact" pattern
        grouped_nodes = []
        i = 0
        while i < len(nodes):
            node = nodes[i]
            title_lower = node.get("title", "").lower()
            
            # Pattern 1: Detect "Call First/Second/Third Contact" sequence
            if "call" in title_lower and "contact" in title_lower:
                # Look ahead for similar patterns
                contact_sequence = [node]
                j = i + 1
                while j < len(nodes) and j < i + 5:  # Look up to 5 nodes ahead
                    next_node = nodes[j]
                    next_title_lower = next_node.get("title", "").lower()
                    if "call" in next_title_lower and "contact" in next_title_lower:
                        contact_sequence.append(next_node)
                        j += 1
                    elif next_node.get("isDecisionPoint"):
                        # Stop at decision nodes, but include them
                        j += 1
                        break
                    else:
                        break
                
                # If we found 2+ contact calls, group them
                if len(contact_sequence) >= 2:
                    logger.info(f"📦 Grouping {len(contact_sequence)} contact escalation nodes")
                    
                    # Create grouped node
                    grouped_node = {
                        "id": contact_sequence[0]["id"],
                        "type": "process",
                        "title": "Escalate Through Contacts",
                        "description": f"Attempt to reach escalation contacts (up to {len(contact_sequence)} attempts)",
                        "status": "critical",
                        "swimLane": contact_sequence[0].get("swimLane", "Operations"),
                        "connections": [],
                        "isDecisionPoint": False,
                        "actors": contact_sequence[0].get("actors", []),
                        "subSteps": []
                    }
                    
                    # Collect all sub-steps from grouped nodes
                    for seq_node in contact_sequence:
                        if not seq_node.get("isDecisionPoint"):
                            grouped_node["subSteps"].extend([
                                f"{seq_node.get('title')}: {step}"
                                for step in seq_node.get("subSteps", [seq_node.get("description", "")])[:2]
                            ])
                    
                    # Find the final connection (skip intermediary decision nodes)
                    for seq_node in reversed(contact_sequence):
                        if seq_node.get("connections"):
                            grouped_node["connections"] = seq_node["connections"][:1]
                            break
                    
                    grouped_nodes.append(grouped_node)
                    i = j  # Skip past all grouped nodes
                    continue
            
            # No grouping applied, keep node as-is
            grouped_nodes.append(node)
            i += 1
        
        if len(grouped_nodes) < len(nodes):
            logger.info(f"✅ Reduced nodes from {len(nodes)} → {len(grouped_nodes)}")
            result["nodes"] = grouped_nodes
        else:
            logger.info("ℹ️ No grouping opportunities found")
        
        return result

    def _parse_json(self, response: str) -> Dict:
        """Parse AI response to JSON."""
        try:
            return json.loads(response)
        except:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            logger.warning("⚠️ Could not parse JSON, returning empty dict")
            return {}
    
    def _validate_and_fix(self, data: Dict) -> Dict:
        """Validate and fix the merged data."""
        
        # Ensure required fields
        if "nodes" not in data:
            data["nodes"] = []
        if "swimLanes" not in data:
            data["swimLanes"] = []
        if "contacts" not in data:
            data["contacts"] = []
        
        # Validate nodes
        valid_node_ids = set()
        for i, node in enumerate(data["nodes"]):
            if "id" not in node:
                node["id"] = f"node-{i+1}"
            valid_node_ids.add(node["id"])
            
            # Smart decision point detection
            title = node.get("title", "")
            conns = node.get("connections", [])
            
            # Auto-detect decision nodes by title pattern or connection count
            if not node.get("isDecisionPoint"):
                # Questions ending with "?" are decisions
                if "?" in title:
                    logger.info(f"🔍 Auto-detected decision node: {title}")
                    node["isDecisionPoint"] = True
                    node["type"] = "decision"
                # Nodes with exactly 2 connections are likely decisions
                elif len(conns) == 2 and "decision" in title.lower():
                    logger.info(f"🔍 Auto-detected decision node: {title}")
                    node["isDecisionPoint"] = True
                    node["type"] = "decision"
            
            if "type" not in node:
                node["type"] = "decision" if node.get("isDecisionPoint") else "process"
            
            if "connections" not in node:
                node["connections"] = []
            
            # Fix decision points
            if node.get("isDecisionPoint"):
                opts = node.get("decisionOptions", {})
                conns = node.get("connections", [])
                
                if len(conns) == 2:
                    if not opts or opts.get("yes") not in conns:
                        node["decisionOptions"] = {"yes": conns[0], "no": conns[1]}
                elif len(conns) != 2:
                    # Not a valid decision if it doesn't have exactly 2 connections
                    node["isDecisionPoint"] = False
                    node["decisionOptions"] = {}
                    node["type"] = "process"
            
            # Ensure sub-steps exist
            if "subSteps" not in node or not node["subSteps"]:
                node["subSteps"] = [node.get("description", "Execute step")]
        
        # Validate connections
        for node in data["nodes"]:
            node["connections"] = [c for c in node.get("connections", []) if c in valid_node_ids]
        
        return data
