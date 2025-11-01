# Enterprise-Grade AI Service - Clean Implementation
# This replaces the messy _parse_single_process and related methods

import json
import re
import logging
from typing import Dict, List, Any
from emergentintegrations.anthropic import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class EnterpriseAIService:
    """
    Enterprise-grade AI service for process extraction
    Implements multi-stage pipeline with proper separation of concerns
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def parse_process(self, input_text: str, input_type: str) -> Dict[str, Any]:
        """
        Main entry point for process parsing
        Returns: {"multipleProcesses": False, "processes": [process_dict]}
        """
        try:
            logger.info("🚀 Starting enterprise AI parsing pipeline")
            
            # STAGE 1: Extract strategic structure
            structure = await self.extract_structure(input_text, input_type)
            logger.info(f"✅ Stage 1 complete: {len(structure.get('nodes', []))} nodes extracted")
            
            # STAGE 2: Enrich with operational details
            enriched_nodes = await self.enrich_nodes(input_text, structure['nodes'])
            structure['nodes'] = enriched_nodes
            logger.info(f"✅ Stage 2 complete: Nodes enriched with operational details")
            
            # STAGE 3: Return formatted result
            return {"multipleProcesses": False, "processes": [structure]}
            
        except Exception as e:
            logger.error(f"❌ Enterprise AI parsing failed: {e}", exc_info=True)
            raise
    
    async def extract_structure(self, input_text: str, input_type: str) -> Dict[str, Any]:
        """
        STAGE 1: Extract high-level strategic structure
        Returns: Dict with processName, nodes, edges, swimLanes
        """
        logger.info("📊 Stage 1: Extracting strategic structure...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"structure_{hash(input_text[:100])}",
            system_message="You are an expert process architect. Extract HIGH-LEVEL strategic phases, not micro-steps."
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        prompt = f"""SMART PROCESS EXTRACTION

YOU ARE A BUSINESS CONSULTANT, NOT A TEXT SPLITTER.

Mission: Transform complex procedures into CLEAR, DIGESTIBLE workflows.

INTELLIGENT GROUPING:
- Group related actions into strategic PHASES
- Maximum 8-12 nodes (less is more)
- Each node = meaningful business phase

EXAMPLE BAD:
❌ "Open email", "Type message", "Add recipient", "Send email"

EXAMPLE GOOD:
✅ "Notify Stakeholders via Email"

INPUT DOCUMENT:
{input_text[:20000]}

IDENTIFY:
1. Strategic phases (8-12 max)
2. Parallel workflows (swim lanes)
3. Critical decisions only

Return JSON:
{{
  "processName": "string",
  "description": "brief",
  "actors": ["role1", "role2"],
  "swimLanes": [
    {{"id": "lane-1", "name": "Team Name", "role": "desc", "color": "#6366f1"}}
  ],
  "nodes": [
    {{
      "id": "node-1",
      "type": "trigger",
      "title": "Strategic Phase (4-6 words)",
      "description": "What this achieves",
      "actors": ["who"],
      "swimLane": "lane-1"
    }}
  ],
  "edges": [
    {{"id": "edge-1", "source": "node-1", "target": "node-2", "label": null}}
  ]
}}

RETURN VALID JSON ONLY"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse and validate
        structure = self._parse_and_validate_json(response)
        
        # Add default fields to nodes
        for node in structure.get('nodes', []):
            self._add_node_defaults(node)
        
        # Add default fields to structure
        structure.setdefault('swimLanes', [])
        structure.setdefault('edges', [])
        structure.setdefault('criticalGaps', [])
        structure.setdefault('improvementOpportunities', [])
        
        return structure
    
    async def enrich_nodes(self, input_text: str, nodes: List[Dict]) -> List[Dict]:
        """
        STAGE 2: Enrich nodes with VALUE-ADD operational details
        """
        logger.info(f"🔍 Stage 2: Enriching {len(nodes)} nodes...")
        
        if not nodes:
            logger.warning("No nodes to enrich")
            return nodes
        
        try:
            node_summary = [f"{i}. {n['id']}: {n['title']}" for i, n in enumerate(nodes[:12], 1)]
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"enrich_{hash(input_text[:100])}",
                system_message="Extract EXECUTABLE details that ADD VALUE."
            ).with_model("anthropic", "claude-4-sonnet-20250514")
            
            prompt = f"""EXTRACT VALUE-ADD OPERATIONAL DETAILS

Process nodes:
{chr(10).join(node_summary)}

For EACH node, extract:
1. specificActions: Concrete steps (not repeating node title)
2. requiredData: Input/data fields needed
3. contactInfo: Phone/email contacts
4. systems: Software/tools used
5. timeline: Time requirements
6. communicationTemplates: Email/message scripts
7. decisionCriteria: For decision nodes

DOCUMENT:
{input_text[:18000]}

Return JSON array:
[
  {{
    "id": "node-1",
    "specificActions": ["action 1", "action 2"],
    "requiredData": ["data1"],
    "contactInfo": {{"name": "phone"}},
    "systems": ["System1"],
    "timeline": "time",
    "communicationTemplates": ["template ref"],
    "decisionCriteria": "YES/NO criteria"
  }}
]

Keep items under 80 chars. Return valid JSON."""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            details_array = json.loads(response.strip())
            details_map = {d['id']: d for d in details_array if 'id' in d}
            
            # Map details to nodes
            for node in nodes:
                if node['id'] in details_map:
                    details = details_map[node['id']]
                    node['operationalDetails'] = {
                        "requiredData": details.get('requiredData', []),
                        "specificActions": details.get('specificActions', []),
                        "contactInfo": details.get('contactInfo', {}),
                        "timeline": details.get('timeline'),
                        "systems": details.get('systems', []),
                        "decisionCriteria": details.get('decisionCriteria'),
                        "emailTemplates": details.get('communicationTemplates', []),
                        "sourcePage": None
                    }
                else:
                    node['operationalDetails'] = self._get_empty_details()
            
            return nodes
            
        except Exception as e:
            logger.warning(f"Failed to enrich details: {e}. Proceeding with structure only.")
            # Graceful degradation - return nodes with empty details
            for node in nodes:
                if 'operationalDetails' not in node:
                    node['operationalDetails'] = self._get_empty_details()
            return nodes
    
    def _parse_and_validate_json(self, response: str) -> Dict[str, Any]:
        """Parse and validate JSON response from AI"""
        response_text = response.strip()
        
        # Remove markdown
        if response_text.startswith('```'):
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
        
        # Clean non-printable chars
        response_text = ''.join(c for c in response_text if c.isprintable() or c in ['\n', '\t'])
        
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Try repair
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
            if not response_text.rstrip().endswith('}'):
                response_text = response_text.rstrip() + '}'
            parsed = json.loads(response_text)
            logger.info("✅ JSON repaired successfully")
        
        # Validate required fields
        if 'nodes' not in parsed or not parsed['nodes']:
            logger.error(f"❌ No nodes in response: {response_text[:500]}")
            raise ValueError("AI did not extract any process steps")
        
        logger.info(f"✅ Parsed structure with {len(parsed['nodes'])} nodes")
        return parsed
    
    def _add_node_defaults(self, node: Dict):
        """Add default fields to a node"""
        node.setdefault('status', 'current' if node.get('type') != 'trigger' else 'trigger')
        node.setdefault('description', '')
        node.setdefault('subSteps', [])
        node.setdefault('dependencies', [])
        node.setdefault('parallelWith', [])
        node.setdefault('failures', [])
        node.setdefault('blocking', None)
        node.setdefault('currentState', None)
        node.setdefault('idealState', None)
        node.setdefault('gap', None)
        node.setdefault('impact', 'medium')
        node.setdefault('timeEstimate', None)
        node.setdefault('position', {"x": 0, "y": 0})
        node.setdefault('operationalDetails', None)
    
    def _get_empty_details(self) -> Dict:
        """Get empty operational details structure"""
        return {
            "requiredData": [],
            "specificActions": [],
            "contactInfo": {},
            "timeline": None,
            "systems": [],
            "decisionCriteria": None,
            "emailTemplates": [],
            "sourcePage": None
        }
