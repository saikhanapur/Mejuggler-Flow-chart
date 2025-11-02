# EROAD-Style Enhancement Layer
# Phase 2: Transform extracted data into 10-15 intelligent nodes with rich details

import json
import logging
from typing import Dict, List, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class EROADStyleEnhancer:
    """
    Phase 2: Takes extracted process data and transforms it into
    EROAD-style flowchart with 10-15 intelligent nodes
    
    Key Features:
    - Intelligent grouping (parallel, sequential, decision points)
    - Rich PURPOSE field (WHY, not WHAT)
    - Current vs Ideal state comparison
    - Status-based classification
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def enhance_for_visualization(
        self, 
        extracted_data: Dict[str, Any],
        document_text: str = None
    ) -> Dict[str, Any]:
        """
        Transform extracted data into visualization-ready format
        
        Input: Raw extracted data (steps, contacts, systems, etc.)
        Output: 10-15 enriched nodes with PURPOSE, current/ideal state
        """
        logger.info("🎨 EROAD-Style Enhancement Layer")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="eroad_enhance",
            system_message="""You are a process visualization expert specializing in creating clear, actionable flowcharts.

Your goal: Transform complex process data into 10-15 intelligent workflow nodes that people can UNDERSTAND and USE immediately.

Key principles:
1. SIMPLIFY - Group intelligently, show what matters
2. EXPLAIN WHY - Purpose field explains the goal, not the mechanics
3. ADD VALUE - Current vs Ideal shows improvement opportunities
4. CLASSIFY - Use visual status types for instant recognition"""
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        # Prepare extracted data summary
        steps = extracted_data.get('steps', [])
        contacts = extracted_data.get('contacts', {})
        systems = extracted_data.get('systems', [])
        timings = extracted_data.get('timings', [])
        decisions = extracted_data.get('decisions', [])
        
        prompt = f"""TRANSFORM EXTRACTED DATA INTO VISUALIZATION-READY FLOWCHART

EXTRACTED DATA:
Steps: {json.dumps(steps, indent=2)}
Contacts: {json.dumps(contacts, indent=2)}
Systems: {systems}
Timings: {timings}
Decision Points: {decisions}

YOUR TASK:
Transform this into 10-15 workflow nodes for an interactive flowchart.

GROUPING RULES:
1. **Combine sequential steps** that serve the same purpose
   Example: "Email councils", "Email MCs", "Send Modica" → "Stakeholder Communications"

2. **Parallel processes** (happening simultaneously) → Separate nodes with same Y coordinate
   Example: "Onshore response" and "Offshore response" happen at same time

3. **Decision points** → Keep as distinct nodes
   Example: "Has Wilsar outaged?" YES/NO branches

4. **Repetitive actions** (loops) → Single node with loop indicator
   Example: "Check every 30 minutes" → "30-Minute Update Cycle"

OUTPUT STRUCTURE:
{{
  "processName": "Clear name from document",
  "nodes": [
    {{
      "id": "unique_id",
      "title": "Short title (max 50 chars)",
      "purpose": "WHY this step exists - the GOAL, not the HOW (1 sentence)",
      "details": "Full description of what happens",
      "status": "critical|action|communication|operational|monitoring|verification|recovery",
      "actions": ["Specific action 1", "Specific action 2"],
      "currentState": "How this is done now (from document)",
      "idealState": "How this could be improved (if applicable, otherwise null)",
      "gap": "What's problematic/missing (if applicable, otherwise null)",
      "contacts": ["Name: Phone/Email"],
      "systems": ["Tool/platform names"],
      "timing": "When/how long (if specified)",
      "dependencies": ["What must happen first"],
      "x": 330,
      "y": 0,
      "connections": ["next_node_id"]
    }}
  ]
}}

STATUS CLASSIFICATION GUIDE:
- **critical**: Emergencies, outages, system down, immediate action required
- **action**: Tasks, setup, configuration, operational work
- **communication**: Emails, calls, notifications, stakeholder updates
- **operational**: Day-to-day operations, routine tasks
- **monitoring**: Checking, tracking, status updates, verification loops
- **verification**: Testing, confirming, validation
- **recovery**: Restoration, cleanup, return to normal

PURPOSE FIELD RULES (MOST IMPORTANT):
The PURPOSE field explains WHY (the goal), not HOW (the process).

Examples:
❌ BAD: "Send emails to stakeholders"
✅ GOOD: "Ensure all parties are aware of the outage and can adjust operations"

❌ BAD: "Raise P1 ticket"
✅ GOOD: "Initiate formal incident tracking and trigger escalation procedures"

❌ BAD: "Check status every 30 minutes"
✅ GOOD: "Maintain situational awareness and anticipate resolution timeline"

CURRENT vs IDEAL STATE RULES:
- **Current State**: What's in the document (always present)
- **Ideal State**: Only populate if there's a clear improvement opportunity
- **Gap**: Only populate if there's a problem/risk mentioned

Don't force it. Some steps are fine as-is (no ideal state needed).

POSITIONING GUIDE:
- X coordinates: Center=330, Left=0, Right=660
- Y coordinates: Start at 0, increment by 150 for each sequential step
- Parallel processes: Same Y, different X

TARGET: Create between 10-15 nodes. 
- If fewer than 10: You've over-grouped
- If more than 15: Combine related steps

Return ONLY valid JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        enhanced = self._parse_json_response(response)
        
        # Validate
        if not enhanced.get('nodes'):
            raise ValueError("No nodes generated in enhancement")
        
        node_count = len(enhanced['nodes'])
        if node_count < 8:
            logger.warning(f"Only {node_count} nodes - may be over-grouped")
        elif node_count > 20:
            logger.warning(f"{node_count} nodes - may need more grouping")
        
        logger.info(f"✅ Enhanced to {node_count} nodes with rich details")
        
        return enhanced
    
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
