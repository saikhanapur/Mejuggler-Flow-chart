"""
Parallel Lightning Processor - Revolutionary Architecture
Think like Elon: Instead of ONE big battery, use MANY small batteries in parallel!

Instead of ONE giant AI call → THREE parallel calls + merge
Total time: ~22 seconds (faster AND more reliable)
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class ParallelLightningProcessor:
    """
    Revolutionary parallel processing architecture.
    Three simultaneous AI calls for speed + reliability.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_document(
        self, 
        document_text: str, 
        document_name: str = "Document"
    ) -> Dict[str, Any]:
        """
        PARALLEL PROCESSING - Three simultaneous AI calls!
        """
        
        logger.info(f"⚡⚡⚡ PARALLEL Lightning processing: {document_name}")
        
        # Truncate if too long
        doc_text = document_text[:50000]
        
        # Launch THREE parallel calls
        logger.info("🚀 Launching 3 parallel AI calls...")
        
        structure_task = self._extract_structure(doc_text, document_name)
        content_task = self._extract_content(doc_text, document_name)
        references_task = self._extract_references(doc_text, document_name)
        
        # Wait for ALL three to complete (runs in parallel!)
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
        logger.info("🔗 Merging parallel results...")
        result = self._merge_results(structure, content, references)
        
        # Validate
        result = self._validate_and_fix(result)
        
        logger.info(f"✅ Parallel processing complete: {len(result['nodes'])} nodes")
        
        return result
    
    async def _extract_structure(self, doc_text: str, doc_name: str) -> Dict:
        """
        Call 1: Extract flowchart STRUCTURE (fast, focused)
        """
        logger.info("📊 [Call 1/3] Extracting structure...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="parallel_structure",
            system_message="Extract flowchart structure efficiently. Return valid JSON only."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=8000)
        
        prompt = f"""Extract the flowchart STRUCTURE from this document:

{doc_text[:100000]}

Return JSON:
{{
  "processName": "Process name",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process",
      "title": "Action Title (3-6 words)",
      "description": "Brief description (1 sentence)",
      "status": "critical|action|operational|communication",
      "swimLane": "Role/Team",
      "connections": ["node-2"],
      "isDecisionPoint": false,
      "decisionCriteria": "Question (if decision)",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Lane Name", "color": "#3B82F6"}}
  ]
}}

Create 15-25 nodes. Decision nodes must have 2 connections and valid decisionOptions.
Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return self._parse_json(response)
    
    async def _extract_content(self, doc_text: str, doc_name: str) -> Dict:
        """
        Call 2: Extract detailed CONTENT (sub-steps, timing)
        """
        logger.info("📝 [Call 2/3] Extracting content...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="parallel_content",
            system_message="Extract detailed content. Return valid JSON only."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=8000)
        
        prompt = f"""Extract DETAILED CONTENT from this document:

{doc_text[:100000]}

For each major step/action, extract:
- 3-5 specific sub-steps (for expandable dropdowns)
- Timing/duration estimates
- Systems used

Return JSON:
{{
  "contentByStep": {{
    "step-name-1": {{
      "subSteps": ["Sub-action 1", "Sub-action 2", "Sub-action 3"],
      "operationalDetails": {{
        "specificActions": ["Detail 1", "Detail 2"],
        "estimatedDuration": "X minutes",
        "gap": false
      }},
      "timing": "When/how long",
      "systems": ["System names"]
    }}
  }}
}}

Extract 3-5 sub-steps for EVERY major action. Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return self._parse_json(response)
    
    async def _extract_references(self, doc_text: str, doc_name: str) -> Dict:
        """
        Call 3: Extract CRITICAL REFERENCES ONLY (not full procedures)
        """
        logger.info("📚 [Call 3/3] Extracting references...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="parallel_references",
            system_message="Extract critical reference info only. Return valid JSON only."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=6000)
        
        prompt = f"""Extract CRITICAL REFERENCE INFORMATION ONLY from this document:

{doc_text[:30000]}

IMPORTANT: Extract ONLY quick reference info, NOT full procedures.

Extract:
1. Emergency contacts (name, phone, when to call)
2. Key communication scripts (SUMMARY only, 1-2 sentences)
3. Critical timings (e.g., "Wait 5 minutes", "Check every 30 min")

DO NOT EXTRACT:
- Full step-by-step procedures (these are in the flowchart)
- Detailed checklists (these are in node sub-steps)
- Long explanations

Return JSON:
{{
  "contacts": [
    {{
      "name": "Contact name",
      "phone": "Phone number",
      "role": "When to call them"
    }}
  ],
  "keyScripts": [
    {{
      "name": "Script name",
      "summary": "Brief 1-sentence summary of what to say"
    }}
  ],
  "criticalTimings": [
    "Wait 5 minutes before...",
    "Check every 30 minutes"
  ]
}}

Keep it CONCISE. These are QUICK references, not detailed instructions. Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return self._parse_json(response)
    
    def _merge_results(
        self, 
        structure: Dict, 
        content: Dict, 
        references: Dict
    ) -> Dict:
        """
        Merge the three parallel results into one complete flowchart.
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
                # Fallback: create basic sub-steps from description
                node["subSteps"] = [node.get("description", "Execute step")]
                node["operationalDetails"] = {
                    "specificActions": [node.get("description", "")],
                    "estimatedDuration": "",
                    "gap": False
                }
        
        logger.info(f"✅ Merged: {len(result['nodes'])} nodes with enhanced content")
        
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
        if "templates" not in data:
            data["templates"] = []
        
        # Validate nodes
        valid_node_ids = set()
        for i, node in enumerate(data["nodes"]):
            if "id" not in node:
                node["id"] = f"node-{i+1}"
            valid_node_ids.add(node["id"])
            
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
                    node["isDecisionPoint"] = False
                    node["decisionOptions"] = {}
            
            # Ensure sub-steps exist
            if "subSteps" not in node or not node["subSteps"]:
                node["subSteps"] = [node.get("description", "Execute step")]
        
        # Validate connections
        for node in data["nodes"]:
            node["connections"] = [c for c in node.get("connections", []) if c in valid_node_ids]
        
        return data
