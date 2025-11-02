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

GROUPING RULES (STRATEGIC SIMPLIFICATION - NOT OVER-CONSOLIDATION):
1. **Combine ONLY closely related sequential steps** that serve the same immediate purpose
   Example: "Email councils", "Email MCs", "Send Modica" → "Stakeholder Communications"
   WRONG: Don't combine "Setup", "Execute", "Monitor", "Close" into one node

2. **Group PARALLEL setup activities** into single initialization nodes
   Example: "Onshore setup", "Offshore setup" → "Dual-Site BCP Setup"
   BUT: Keep them separate if they're sequential or have different actors

3. **Consolidate ONLY repetitive monitoring loops**
   Example: "Check every 30 minutes until resolved" → "Ongoing Status Monitoring"

4. **KEEP decision points as separate nodes** if they branch the flow

5. **Final activities can be grouped** if they're truly cleanup steps
   Example: "Create jobs", "Reallocate tasks", "Resume BAU" → "Return to Normal Operations"

CRITICAL RULES TO PREVENT OVER-GROUPING:
- If the original document has 9 distinct steps → Target 8-11 nodes (not 1!)
- NEVER combine more than 3 original steps into one node
- Each phase of the process should be a separate node (Setup, Execution, Monitoring, Recovery)
- When in doubt, KEEP IT SEPARATE

TARGET: Create between 8-13 nodes based on input complexity
- 5-10 original steps → 5-8 nodes
- 11-20 original steps → 9-13 nodes
- Always maintain the logical flow and phases

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
- All nodes in single vertical flow (X coordinate: 330 for center alignment)
- Y coordinates: Start at 0, increment by 150 for each step
- For parallel processes: Use slightly different X (300, 360) but keep Y spacing

TARGET NODE COUNT (BASED ON INPUT):
- 5-10 original steps → Generate 5-8 nodes
- 11-20 original steps → Generate 9-13 nodes
- 20+ original steps → Generate 12-15 nodes

CRITICAL: PREVENT OVER-GROUPING
- If you receive 9 distinct steps, you should return AT LEAST 7-9 nodes
- Each major phase/stage must be its own node
- Only combine steps that happen simultaneously or are sub-tasks of the same action

Return ONLY valid JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        enhanced = self._parse_json_response(response)
        
        # Validate
        if not enhanced.get('nodes'):
            raise ValueError("No nodes generated in enhancement")
        
        node_count = len(enhanced['nodes'])
        input_step_count = len(extracted_data.get('steps', []))
        
        # Strict validation against over-grouping
        if node_count < 5:
            logger.error(f"CRITICAL: Only {node_count} nodes from {input_step_count} input steps - SEVERE OVER-GROUPING!")
            raise ValueError(f"Over-grouped: Generated only {node_count} nodes from {input_step_count} steps. Minimum 5 nodes required.")
        elif node_count < input_step_count * 0.6:
            logger.warning(f"⚠️ Possible over-grouping: {node_count} nodes from {input_step_count} input steps")
        elif node_count > 20:
            logger.warning(f"⚠️ {node_count} nodes - may need more grouping")
        
        logger.info(f"✅ Enhanced {input_step_count} steps to {node_count} nodes with rich details")
        
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
