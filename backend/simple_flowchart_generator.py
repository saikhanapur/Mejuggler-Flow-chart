# Simple One-Shot Flowchart Generator
# What Claude did in 5 minutes vs our complex multi-stage pipeline

import json
import logging
from typing import Dict, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class SimpleFlowchartGenerator:
    """
    Simple, fast flowchart generation - inspired by what Claude can do in 5 minutes
    
    ONE PROMPT. ONE RESPONSE. DONE.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_flowchart(self, document_text: str) -> Dict[str, Any]:
        """
        Generate complete flowchart in ONE SHOT
        
        Returns beautiful, structured flowchart with:
        - Nodes with proper classification (critical, action, communication, etc.)
        - Edges with proper flow
        - Side panel details (purpose, steps, dependencies, current/ideal state)
        - Visual metadata (colors, positions, styling hints)
        
        Time: 10-15 seconds
        """
        logger.info("🚀 Simple One-Shot Flowchart Generation")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="simple_flowchart",
            system_message="""You are an expert at creating clean, actionable process flowcharts.

Your goal: Transform complex procedures into clear, visual flowcharts that people can UNDERSTAND and USE immediately.

Key principles:
1. SIMPLIFY - Group related steps, show what matters
2. CATEGORIZE - Use visual types (Critical, Action, Communication, Monitoring, Decision)
3. ENRICH - Each node has rich side panel details (not just duplication)
4. MAKE IT BEAUTIFUL - Clean visual hierarchy, proper colors, clear flow"""
        ).with_model("openai", "gpt-5")
        
        prompt = f"""GENERATE COMPLETE FLOWCHART

DOCUMENT:
{document_text}

YOUR TASK:
Create a clean, actionable flowchart that someone can understand in 30 seconds.

OUTPUT THIS JSON STRUCTURE:
{{
  "processName": "Clear name",
  "description": "One-line description",
  "nodes": [
    {{
      "id": "node-1",
      "title": "Clear action title (short)",
      "type": "critical|action|communication|monitoring|decision|operational",
      "category": "Detection|Response|Recovery|etc",
      "position": {{"x": 100, "y": 50}},
      "color": "red|blue|purple|amber|emerald|green",
      "details": {{
        "purpose": "WHY this step exists",
        "specificActions": ["Concrete action 1", "Concrete action 2"],
        "actors": ["Who does this"],
        "systems": ["Systems involved"],
        "timeline": "Time constraint",
        "dependencies": ["What must happen first"],
        "currentState": "What happens now",
        "idealState": "What should happen",
        "contacts": {{"Name": "Phone/Email"}},
        "templates": ["Email script reference"]
      }}
    }}
  ],
  "edges": [
    {{
      "id": "e1",
      "source": "node-1",
      "target": "node-2",
      "label": "YES|NO|null",
      "style": "solid|dashed"
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Team/Phase", "nodeIds": ["node-1"]}}
  ],
  "quickReference": {{
    "criticalActions": ["Action 1", "Action 2"],
    "keyTimings": ["Every 30 mins", "Immediate"],
    "emergencyContacts": {{"IT Support": "555-1234"}}
  }}
}}

CRITICAL RULES:
1. Nodes: 10-20 nodes (not 43!). Group intelligently.
2. Types: Use visual types for instant recognition
3. Details: Rich side panel content - PURPOSE, not duplication
4. Flow: Clear paths, decision points obvious
5. Positions: Logical top-to-bottom or left-to-right layout

EXAMPLE NODE DETAILS (GOOD):
{{
  "purpose": "Ensure all stakeholders are aware of service disruption to manage expectations",
  "specificActions": [
    "Email councils using template A",
    "Send Modica group message to patrol officers",
    "Update monitoring companies via email"
  ],
  "currentState": "Manual notification process, 15-20 minutes to complete all communications",
  "idealState": "Automated notification system triggered by monitoring, instant delivery",
  "gap": "No automated alerting, relies on manual process during high-stress situation"
}}

RETURN VALID JSON ONLY."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        flowchart = self._parse_json_response(response)
        
        # Validate
        if not flowchart.get('nodes'):
            raise ValueError("No nodes generated")
        
        logger.info(f"✅ Generated {len(flowchart['nodes'])} nodes in one shot")
        return flowchart
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from response"""
        response_text = response.strip()
        
        # Remove markdown
        if response_text.startswith('```'):
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
        
        return json.loads(response_text)
