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
        """
        return f"""TASK: Create a flowchart structure from this text-based SOP document.

DOCUMENT:
{doc_text[:20000]}

TASK: Analyze the document and create an intelligent flowchart structure.

RULES:
1. Identify ALL decision points (questions, if/then statements, conditional logic)
2. Identify ALL action steps (things that must be done)
3. Determine the logical flow and connections
4. Based on analysis, this document likely needs around {estimated_nodes} nodes
5. Create EXACTLY the number of nodes needed - no arbitrary padding
6. Group related sub-actions into single nodes (they'll become expandable sub-steps)
7. DO NOT create artificial complexity

For EACH logical step:
- Create a clear, concise title (3-6 words)
- Determine if it's a decision or action
- Identify what connects to what
- Note which role/actor is responsible

Return JSON:
{{
  "processName": "Descriptive process name",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "Clear action or question (3-6 words)",
      "description": "Brief description",
      "status": "critical|action|operational|communication",
      "swimLane": "Role/Team",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question if decision",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Lane Name", "color": "#3B82F6"}}
  ]
}}

Expected range: {max(3, estimated_nodes-5)} to {estimated_nodes+5} nodes based on content.
Create EXACTLY what the document requires - no more, no less.
Return ONLY JSON."""
    
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
Return ONLY JSON.
        
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
                # Fallback: basic sub-steps
                node["subSteps"] = [node.get("description", "Execute step")]
                node["operationalDetails"] = {
                    "specificActions": [node.get("description", "")],
                    "estimatedDuration": "",
                    "gap": False
                }
        
        logger.info(f"✅ Merged: {len(result['nodes'])} nodes")
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
