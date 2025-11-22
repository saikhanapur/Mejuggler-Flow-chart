"""
Lightning Processor - Fast, Reliable Flowchart Generation
Single-pass extraction with all intelligence built in.
NO multi-stage bottlenecks, NO timeouts.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class LightningProcessor:
    """
    Ultra-fast processor that does EVERYTHING in one smart AI call.
    Extracts: steps, decisions, contacts, scripts, swim lanes, loops.
    Returns visualization-ready data - no enhancement needed.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_document(
        self, 
        document_text: str, 
        document_name: str = "Document"
    ) -> Dict[str, Any]:
        """
        Single-pass intelligent extraction.
        Returns complete, visualization-ready flowchart data.
        """
        
        logger.info(f"⚡ Lightning processing: {document_name}")
        
        # Truncate if too long to prevent timeouts
        doc_text = document_text[:50000]
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="lightning_process",
            system_message="""You are an expert at analyzing business process documents and creating clear flowcharts.

Your task: Extract ALL information and structure it for visualization in ONE PASS.

Be comprehensive but efficient. Extract everything needed for a complete flowchart."""
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=16000)
        
        prompt = f"""Analyze this document and extract COMPLETE flowchart data:

DOCUMENT: {document_name}

{doc_text}

Extract and structure ALL of the following:

1. PROCESS STEPS (15-25 nodes):
   - Extract each major step/action
   - Assign clear titles (concise, actionable)
   - Add brief descriptions
   - Classify status: critical|action|communication|operational|monitoring|verification|recovery
   - Identify connections (which step comes next)
   
2. DECISION POINTS:
   - Identify ALL decision/branching points
   - Mark with isDecisionPoint: true
   - Provide clear decision criteria (the question)
   - Map YES and NO paths to node IDs
   
3. SWIM LANES (if applicable):
   - Detect different roles/teams/systems
   - Assign each node to a swim lane
   
4. LOOPS (if applicable):
   - Identify monitoring loops or retry logic
   - Mark which node loops back where
   
5. CONTACTS (full extraction):
   - Extract ALL contacts with phone, email, role
   - Note location (onshore/offshore) if mentioned
   - Include extensions and timing info
   
6. SCRIPTS & TEMPLATES (FULL TEXT):
   - Extract communication scripts (Modica, email, SMS)
   - Get COMPLETE text for outage and restoration messages
   - Extract checklists with ALL items
   - Extract procedures with ALL steps

Return JSON:
{{
  "processName": "Clear process name",
  "nodes": [
    {{
      "id": "node-1",
      "title": "Action Title (concise, 3-6 words)",
      "description": "What happens and why (1-2 sentences)",
      "status": "critical|action|communication|operational|monitoring|verification|recovery",
      "swimLane": "Role/Team name (if applicable)",
      "connections": ["node-2", "node-3"],
      "isDecisionPoint": false,
      "decisionCriteria": "Question being decided (if decision point)",
      "decisionOptions": {{"yes": "node-id-yes", "no": "node-id-no"}},
      "isLoop": false,
      "loopBackTo": "node-id (if loop)",
      "actors": ["Who does this"],
      "timing": "When/how long (if specified)",
      "systems": ["Systems used"]
    }}
  ],
  "swimLanes": [
    {{
      "id": "lane-1",
      "name": "Lane Name",
      "color": "#3B82F6"
    }}
  ],
  "contacts": [
    {{
      "name": "Contact Name",
      "phone": "Full phone number",
      "extension": "Extension (if any)",
      "email": "email@domain.com",
      "role": "Job title/role",
      "location": "onshore|offshore|central (if mentioned)",
      "timing": "Check-in frequency or availability"
    }}
  ],
  "templates": [
    {{
      "name": "Modica Script - Council",
      "type": "modica|email|sms|checklist|procedure",
      "content": {{
        "outageNotification": "FULL TEXT of outage message (word-for-word)",
        "restoration": "FULL TEXT of restoration message (word-for-word)"
      }},
      "items": ["item 1", "item 2"],
      "steps": ["step 1", "step 2"]
    }}
  ],
  "keyTimings": [
    "30 minutes for progress updates",
    "Check Wilson IT every 30 min"
  ]
}}

CRITICAL RULES:
- Create 15-25 nodes (good balance of detail and clarity)
- Every node must have at least 1 connection (except final node)
- Decision nodes must have exactly 2 connections and valid decisionOptions
- Extract FULL TEXT for scripts, not summaries
- Node IDs: "node-1", "node-2", etc.
- DO NOT include "YES" or "NO" in node titles - these are edge labels only
- Node titles should be clean action statements without branch labels
- Return ONLY valid JSON, no explanatory text"""

        try:
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            # Parse JSON response
            result = self._parse_json_response(response)
            
            # Validate and fix any issues
            result = self._validate_and_fix(result)
            
            logger.info(f"✅ Lightning processing complete: {len(result['nodes'])} nodes, {len(result.get('templates', []))} templates")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Lightning processing failed: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON."""
        try:
            # Try direct parse
            return json.loads(response)
        except:
            # Try to extract JSON from markdown or text
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise ValueError("Could not parse JSON from response")
    
    def _validate_and_fix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix common issues in extracted data."""
        
        # Ensure required fields exist
        if "nodes" not in data:
            data["nodes"] = []
        if "swimLanes" not in data:
            data["swimLanes"] = []
        if "contacts" not in data:
            data["contacts"] = []
        if "templates" not in data:
            data["templates"] = []
        if "keyTimings" not in data:
            data["keyTimings"] = []
        if "processName" not in data:
            data["processName"] = "Process Flowchart"
        
        # Validate nodes
        valid_node_ids = set()
        for i, node in enumerate(data["nodes"]):
            # Ensure ID exists
            if "id" not in node:
                node["id"] = f"node-{i+1}"
            valid_node_ids.add(node["id"])
            
            # Ensure connections is a list
            if "connections" not in node:
                node["connections"] = []
            
            # Fix decision points
            if node.get("isDecisionPoint"):
                options = node.get("decisionOptions", {})
                connections = node.get("connections", [])
                
                # Ensure decisionOptions matches connections
                if len(connections) == 2:
                    if not options or options.get("yes") not in connections:
                        node["decisionOptions"] = {
                            "yes": connections[0],
                            "no": connections[1]
                        }
                        logger.info(f"✅ Fixed decision options for {node.get('title')}")
                elif len(connections) != 2:
                    # Not a real decision point
                    node["isDecisionPoint"] = False
                    node["decisionOptions"] = {}
                    logger.warning(f"⚠️ Unmarked {node.get('title')} as decision (connections: {len(connections)})")
        
        # Validate connections - remove invalid ones
        for node in data["nodes"]:
            valid_connections = [
                conn for conn in node.get("connections", [])
                if conn in valid_node_ids
            ]
            node["connections"] = valid_connections
        
        logger.info(f"✅ Validation complete: {len(data['nodes'])} nodes validated")
        
        return data
