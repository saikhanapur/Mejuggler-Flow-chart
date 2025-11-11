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
        document_text: str = None,
        detection: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Transform extracted data into visualization-ready format
        
        NEW: Now uses detected structure (swim lanes, phases, decisions, loops)
        
        Input: Raw extracted data + detected structure
        Output: 8-13 enriched nodes with PURPOSE, current/ideal state, and structure
        """
        logger.info("🎨 EROAD-Style Enhancement with Structure Awareness")
        
        input_step_count = len(extracted_data.get('steps', []))
        logger.info(f"📊 Input: {input_step_count} steps to enhance")
        
        # Build structure context from detection
        structure_context = self._build_structure_context(detection) if detection else "No structure detected"
        logger.info(f"🏗️ Structure context: {structure_context}")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="eroad_enhance",
            system_message="""You are a process visualization expert specializing in creating clear, actionable flowcharts.

Your goal: Transform complex process data into 10-15 intelligent workflow nodes that people can UNDERSTAND and USE immediately.

Key principles:
1. SIMPLIFY - Group intelligently, show what matters
2. EXPLAIN WHY - Purpose field explains the goal, not the mechanics
3. ADD VALUE - Current vs Ideal shows improvement opportunities
4. CLASSIFY - Use visual status types for instant recognition
5. USE DETECTED STRUCTURE - Swim lanes, phases, decisions, loops from analysis"""
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        # Prepare extracted data summary
        steps = extracted_data.get('steps', [])
        contacts = extracted_data.get('contacts', {})
        systems = extracted_data.get('systems', [])
        timings = extracted_data.get('timings', [])
        decisions = extracted_data.get('decisions', [])
        
        prompt = f"""TRANSFORM EXTRACTED DATA INTO VISUALIZATION-READY FLOWCHART

DETECTED STRUCTURE:
{structure_context}

EXTRACTED DATA:
Steps: {json.dumps(steps, indent=2)[:8000]}
Contacts: {json.dumps(contacts, indent=2)[:2000]}
Systems: {systems}
Timings: {timings}
Decision Points: {decisions}

YOUR TASK:
Transform this into 10-15 workflow nodes for an interactive flowchart.
USE THE DETECTED STRUCTURE (swim lanes, phases, decisions, loops) in your transformation.

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
  "progressStages": [
    {{
      "title": "IMMEDIATE ACTION",
      "description": "0-15 minutes",
      "y": 50
    }},
    {{
      "title": "ONGOING",
      "description": "30 min intervals",
      "y": 400
    }},
    {{
      "title": "RECOVERY",
      "description": "Final steps",
      "y": 800
    }}
  ],
  "quickReference": {{
    "criticalActions": ["Action 1", "Action 2"],
    "keyTimings": ["Every 30 minutes: Status check", "Within 2 hours: Notify stakeholders"],
    "emergencyContacts": {{
      "Primary Contact": "Name: 0800-xxx-xxx",
      "Backup Contact": "Name: 0800-xxx-xxx"
    }}
  }},
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
      "parallelWith": ["node_id_if_parallel"],
      "isDecisionPoint": false,
      "decisionCriteria": "Human readable: If X is true, go to Y. If X is false, go to Z.",
      "decisionOptions": {{"yes": "next_node_id", "no": "alt_node_id"}},
      "isLoop": false,
      "loopBackTo": "node_id_if_loop",
      "x": 330,
      "y": 0,
      "connections": ["next_node_id"]
    }}
  ]
}}

PARALLEL PROCESS DETECTION:
- Look for phrases: "meanwhile", "at the same time", "simultaneously", "in parallel", "both teams"
- Example: "Onshore team sets up tracking" + "Offshore team sets up tracking" = PARALLEL
- Mark both nodes with: "parallelWith": ["other_node_id"]

DECISION POINT DETECTION:
- Look for: "if", "check if", "verify whether", "has X happened?", "is Y true?"
- Example: "Check if Wilsar restored" → YES path / NO path
- Mark as: "isDecisionPoint": true, "decisionOptions": {{"yes": "node_restored", "no": "node_keep_monitoring"}}

LOOP DETECTION:
- Look for: "repeat until", "check every X minutes", "continue monitoring", "loop back"
- Example: "Check every 30 minutes" loops back to "Monitor Status"
- Mark as: "isLoop": true, "loopBackTo": "monitor_node_id"

SWIM LANE POSITIONING (if swim lanes detected):
- If swim lanes detected in structure, position nodes by their role/team
- Lane 1 (Left): X=150
- Lane 2 (Center): X=380  
- Lane 3 (Right): X=610
- Example: "Onshore Actions" nodes at X=150, "Offshore Actions" nodes at X=610
- Parallel nodes in different lanes should have same Y position
- Add "swimLane": "lane_id" field to each node

PHASE GROUPING (if phases detected):
- If phases detected, include "phase": number field
- Example: Phase 0 nodes, Phase 1 nodes, Phase 2 nodes
- Keep nodes grouped by phase for visual clarity

STATUS CLASSIFICATION GUIDE (CRITICAL - Choose Carefully):
- **critical**: Urgent, time-sensitive, high-impact failures (e.g., "Emergency Response", "System Down", "Call 111")
- **action**: Steps requiring immediate action/decision (e.g., "Notify Manager", "Initiate BCP", "Contact Stakeholders")
- **communication**: Sending information to stakeholders (e.g., "Email Teams", "Broadcast Alert", "Update Status")
- **operational**: Standard operational tasks (e.g., "Manual Dispatch", "Create Jobs", "Update Records")
- **monitoring**: Checking, tracking, or monitoring status (e.g., "Check Every 30 Min", "Track Progress", "Monitor Systems")
- **verification**: Testing, confirming, or verifying (e.g., "Test Systems", "Verify Resolution", "Confirm Restoration")
- **recovery**: Final restoration or return to normal (e.g., "Resume Operations", "Close Incident", "Return to BAU")
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
- Initial X/Y coordinates will be calculated automatically based on your flow structure
- For sequential flow: Suggest parallelWith=[] (will be centered automatically)
- For parallel processes: Specify parallelWith=["node_id"] (will be positioned side-by-side)
- For decision branches: Mark isDecisionPoint=true (branching will be handled)
- You can suggest initial x, y values but they may be adjusted for optimal layout

TARGET NODE COUNT (BASED ON INPUT):
- 5-10 original steps → Generate 5-8 nodes
- 11-20 original steps → Generate 9-13 nodes
- 20+ original steps → Generate 12-15 nodes

CRITICAL: PREVENT OVER-GROUPING
- If you receive 9 distinct steps, you should return AT LEAST 7-9 nodes
- Each major phase/stage must be its own node
- Only combine steps that happen simultaneously or are sub-tasks of the same action

PROGRESS STAGES (REQUIRED):
Analyze the timeline and create 2-4 progress stages that divide the process chronologically:
- **IMMEDIATE ACTION**: Steps in first 0-15 minutes (position y near first critical nodes)
- **ONGOING**: Steps that loop/repeat (position y in middle of process)  
- **RECOVERY COMPLETE**: Final restoration steps (position y near last nodes)
- Use timing indicators from document (e.g., "Every 30 minutes", "Within 2 hours")

QUICK REFERENCE (REQUIRED):
Extract from the document:
- **criticalActions**: 3-5 most important immediate actions
- **keyTimings**: Time-sensitive checkpoints (e.g., "Every 30 min: Update teams")
- **emergencyContacts**: Key contacts with phone/email (from document appendix/contact section)

Return ONLY valid JSON."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        enhanced = self._parse_json_response(response)
        
        # ============ POST-PROCESSING: FORCE DECISION & LOOP DETECTION ============
        # AI sometimes misses isDecisionPoint even when decisionCriteria exists
        # This ensures visual intelligence is always applied
        nodes = enhanced.get('nodes', [])
        for node in nodes:
            # FORCE isDecisionPoint if any decision indicators present
            decision_keywords = ['if', 'check if', 'verify', 'has ', ' or ', '?', 'yes/no', 'true/false', 'depends on']
            title_lower = node.get('title', '').lower()
            details_lower = node.get('details', '').lower()
            criteria = node.get('decisionCriteria', '')
            
            # If ANY decision indicator, force it to true
            if criteria or any(kw in title_lower for kw in decision_keywords) or any(kw in details_lower for kw in ['if ', 'check if', 'verify whether']):
                node['isDecisionPoint'] = True
                if not criteria:
                    # Generate basic criteria if missing
                    node['decisionCriteria'] = f"Based on {node.get('title', 'condition')}"
                logger.info(f"✅ FORCED decision point: {node.get('title')}")
            
            # FORCE isLoop if loop indicators present
            loop_keywords = ['loop', 'repeat', 'until', 'every', 'check again', 'monitor', 'continue', 'recurring']
            if any(kw in title_lower for kw in loop_keywords) or any(kw in details_lower for kw in ['repeat', 'until', 'every ', 'loop back']):
                if not node.get('isLoop'):
                    node['isLoop'] = True
                    logger.info(f"✅ FORCED loop detection: {node.get('title')}")
        
        # ============ FIX #1: SMART POSITIONING WITH MERGE POINT DETECTION ============
        # Enhanced positioning with:
        # - Sequential: X=330, Y increments by 150
        # - Parallel: X=200/460 (2 nodes) or X=150/330/510 (3 nodes), same Y
        # - Merge points: Detected when multiple nodes connect to same target
        
        nodes = enhanced.get('nodes', [])
        y_position = 40  # Start with top padding so first node isn't at edge
        processed_ids = set()
        
        # Step 1: Detect merge points (nodes with multiple incoming connections)
        incoming_connections = {}
        for node in nodes:
            for target_id in node.get('connections', []):
                if target_id not in incoming_connections:
                    incoming_connections[target_id] = []
                incoming_connections[target_id].append(node['id'])
        
        merge_points = {node_id: sources for node_id, sources in incoming_connections.items() if len(sources) > 1}
        
        # Step 2: Position nodes with awareness of structure
        for i, node in enumerate(nodes):
            if node['id'] in processed_ids:
                continue
            
            # Check if this node is a merge point
            is_merge = node['id'] in merge_points
            
            # Check if this node has parallel companions
            parallel_with = node.get('parallelWith', [])
            
            if parallel_with:
                # This is part of a parallel group
                parallel_nodes = [node] + [n for n in nodes if n['id'] in parallel_with]
                
                # FIX #1: INCREASE PARALLEL NODE SPACING - Move MUCH further from center
                # Center line is at X=330, nodes are 240px wide
                # Previous: X=80 (extends to 320) and X=580 (extends to 820) - TOO CLOSE!
                # New: X=40 (extends to 280) and X=620 (extends to 860) - BETTER CLEARANCE
                if len(parallel_nodes) == 2:
                    parallel_nodes[0]['x'] = 40   # Far left (node extends 40-280, good clearance from center 330)
                    parallel_nodes[0]['y'] = y_position
                    parallel_nodes[1]['x'] = 620  # Far right (node extends 620-860, good clearance from center 330)
                    parallel_nodes[1]['y'] = y_position
                elif len(parallel_nodes) == 3:
                    parallel_nodes[0]['x'] = 30   # Far left
                    parallel_nodes[0]['y'] = y_position
                    parallel_nodes[1]['x'] = 330  # Center (acceptable for 3 nodes)
                    parallel_nodes[1]['y'] = y_position
                    parallel_nodes[2]['x'] = 630  # Far right
                    parallel_nodes[2]['y'] = y_position
                else:
                    # More than 3 parallel - use far spacing
                    for j, pnode in enumerate(parallel_nodes):
                        pnode['x'] = 40 if j % 2 == 0 else 620
                        pnode['y'] = y_position
                
                # Mark as processed
                for pnode in parallel_nodes:
                    processed_ids.add(pnode['id'])
                
                # FIX #2: UNIFORM SPACING - Always use 150px (was 160px)
                y_position += 150
            elif is_merge:
                # FIX #2: UNIFORM SPACING - Remove extra spacing before merge for consistency
                # (Previous: y_position += 30 - caused non-uniform distances)
                node['x'] = 330  # Center merge points
                node['y'] = y_position
                node['isMergePoint'] = True  # Mark for frontend
                processed_ids.add(node['id'])
                y_position += 150
            else:
                # Sequential node - center it
                node['x'] = 330
                node['y'] = y_position
                processed_ids.add(node['id'])
                y_position += 150
        # ============ END FIX #1 ============
        
        # Position progress badges relative to nodes
        progress_stages = enhanced.get('progressStages', [])
        if progress_stages:
            for stage in progress_stages:
                # Position badges on the right side at specified Y
                stage['x'] = 630  # Right side of main flow
        
        # ============ FIX #2: CONNECTION VALIDATION ============
        # Ensure all non-terminal nodes have outgoing connections
        # Terminal nodes: recovery, complete, final, end
        terminal_keywords = ['recovery', 'complete', 'resume', 'close', 'end', 'final', 'return to normal']
        
        for i, node in enumerate(nodes):
            # Check if this is a terminal node
            is_terminal = any(keyword in node.get('title', '').lower() for keyword in terminal_keywords)
            
            # Skip if it's the last node or a terminal node
            if is_terminal or i == len(nodes) - 1:
                continue
            
            # Check if node has connections
            connections = node.get('connections', [])
            if not connections or len(connections) == 0:
                logger.warning(f"⚠️ Node '{node.get('title')}' ({node.get('id')}) has no outgoing connections!")
                
                # Auto-fix strategy:
                # 1. If node is part of parallel group, connect to merge point
                if node.get('parallelWith'):
                    # Find the merge point (next non-parallel node)
                    for j in range(i + 1, len(nodes)):
                        future_node = nodes[j]
                        if not future_node.get('parallelWith'):
                            node['connections'] = [future_node['id']]
                            logger.info(f"✅ Auto-connected parallel node '{node.get('title')}' → '{future_node.get('title')}'")
                            break
                else:
                    # 2. Otherwise, connect to immediate next node
                    if i + 1 < len(nodes):
                        next_node = nodes[i + 1]
                        node['connections'] = [next_node['id']]
                        logger.info(f"✅ Auto-connected sequential node '{node.get('title')}' → '{next_node.get('title')}'")
        # ============ END FIX #2 ============
        
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
    
    def _build_structure_context(self, detection: Dict[str, Any]) -> str:
        """Build human-readable context from detection"""
        if not detection:
            return "No structure detected - using standard flowchart layout"
        
        context_parts = []
        
        if detection.get("swimLanes") and len(detection.get("swimLanes", [])) > 0:
            lanes = [f"{lane.get('title', 'Unknown')} ({lane.get('team', 'Team')})" for lane in detection['swimLanes']]
            context_parts.append(f"SWIM LANES DETECTED: {', '.join(lanes)}")
            context_parts.append("  → Position nodes in correct lanes (X coordinates vary by lane)")
        
        if detection.get("phases") and len(detection.get("phases", [])) > 0:
            phases = [f"Phase {p.get('number', '?')}: {p.get('title', 'Unknown')}" for p in detection['phases']]
            context_parts.append(f"PHASES DETECTED: {', '.join(phases)}")
            context_parts.append("  → Group nodes by phase")
        
        if detection.get("decisionPoints") and len(detection.get("decisionPoints", [])) > 0:
            context_parts.append(f"DECISION POINTS DETECTED: {len(detection['decisionPoints'])} decision branches")
            for dp in detection['decisionPoints'][:3]:  # Show first 3
                condition = dp.get('condition', 'Unknown')
                context_parts.append(f"  → {condition}")
        
        if detection.get("monitoringLoops") and len(detection.get("monitoringLoops", [])) > 0:
            context_parts.append(f"MONITORING LOOPS DETECTED: {len(detection['monitoringLoops'])} loops")
            for loop in detection['monitoringLoops'][:3]:  # Show first 3
                action = loop.get('action', 'Unknown')
                freq = loop.get('frequency', 'periodic')
                context_parts.append(f"  → {action} ({freq})")
        
        if detection.get("parallelActivities") and len(detection.get("parallelActivities", [])) > 0:
            context_parts.append(f"PARALLEL ACTIVITIES DETECTED: {len(detection['parallelActivities'])} groups")
            context_parts.append("  → Position at same Y level, different X positions")
        
        if detection.get("hasRACITable"):
            context_parts.append("RACI TABLE DETECTED: Role-based responsibilities present")
        
        if detection.get("referencedProcedures") and len(detection.get("referencedProcedures", [])) > 0:
            refs = ', '.join(detection['referencedProcedures'][:5])
            context_parts.append(f"REFERENCED SUB-PROCESSES: {refs}")
        
        if detection.get("gates") and len(detection.get("gates", [])) > 0:
            gates = ', '.join(detection['gates'])
            context_parts.append(f"APPROVAL GATES DETECTED: {gates}")
        
        complexity = detection.get('complexity', 'unknown')
        context_parts.append(f"\nCOMPLEXITY: {complexity}")
        context_parts.append(f"RECOMMENDATION: {detection.get('autoDecision', 'Standard flowchart')}")
        
        return "\n".join(context_parts)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response with robust error handling"""
        response_text = response.strip()
        
        # Remove markdown code blocks
        if response_text.startswith('```'):
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON parse error: {e}")
            logger.warning(f"   Response snippet: {response_text[max(0, e.pos-100):e.pos+100]}")
            
            # Try to repair common issues
            try:
                # Replace single quotes with double quotes
                fixed = response_text.replace("'", '"')
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass
            
            try:
                # Remove trailing commas
                import re
                fixed = re.sub(r',\s*}', '}', response_text)
                fixed = re.sub(r',\s*]', ']', fixed)
                return json.loads(fixed)
            except (json.JSONDecodeError, re.error):
                pass
            
            try:
                # Try to extract just the JSON object
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    fixed = response_text[start:end+1]
                    return json.loads(fixed)
            except json.JSONDecodeError:
                pass
            
            # If all repairs fail, raise original error
            logger.error(f"❌ Could not repair JSON. First 500 chars: {response_text[:500]}")
            raise ValueError(f"Failed to parse JSON response: {e}")
