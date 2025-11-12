# EROAD-Style Enhancement Layer
# Phase 2: Transform extracted data into 10-15 intelligent nodes with rich details

import asyncio
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

DECISION POINT DETECTION (BE VERY SELECTIVE):
- ONLY mark as decision point if the process BRANCHES into TWO OR MORE different paths based on a condition
- Look for: "IF condition THEN path A ELSE path B", branching logic, conditional routing
- NOT decision points: "Confirm X", "Verify Y", "Check status" (these are just verification steps, not branches)
- Real examples:
  * "Is connectivity lost? YES → Full BCP activation, NO → Partial workaround" ✓ DECISION
  * "Confirm outage occurred" ✗ NOT A DECISION (just verification)
  * "Check if resolved. If YES → Close incident, If NO → Continue monitoring" ✓ DECISION
- Mark ONLY real decisions as: "isDecisionPoint": true, "decisionCriteria": "Clear question?", "decisionOptions": {{"yes": "node_id_yes_path", "no": "node_id_no_path"}}

LOOP DETECTION (MANDATORY fields):
- Look for: "repeat until", "check every X minutes", "continue monitoring", "loop back"
- Example: "Check every 30 minutes" loops back to "Monitor Status"
- Mark as: "isLoop": true, "loopBackTo": "node_id_or_self"
- **CRITICAL**: If isLoop=true, you MUST provide loopBackTo field (can be same node ID for self-loop)

SWIM LANE ASSIGNMENT (MANDATORY if swim lanes detected):
- If extracted data contains swimLanes array, YOU MUST assign nodes to lanes
- Match node content to lane steps/purpose from extracted data
- Add "swimLane": "lane_name" field to EVERY node
- Example: If node is about "Raise ticket", assign to "Onshore Tasks" lane

SWIM LANE POSITIONING:
- Lane 1: X=200 (leftmost)
- Lane 2: X=450 (center)
- Lane 3: X=700 (rightmost)
- Lane 4+: X=200 + (lane_number * 250)
- Nodes in same lane at same stage should have same Y coordinate
- Y spacing: 200px between sequential nodes in same lane

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
        
        # Retry logic for API failures (502, 503, timeout)
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                response = await chat.send_message(message)
                break  # Success, exit retry loop
            except Exception as retry_error:
                error_msg = str(retry_error)
                if "502" in error_msg or "503" in error_msg or "timeout" in error_msg.lower():
                    if attempt < max_retries - 1:
                        logger.warning(f"API error (attempt {attempt + 1}/{max_retries}): {error_msg}. Retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                raise  # Re-raise if not retryable or max retries reached
        
        # Parse response
        enhanced = self._parse_json_response(response)
        
        # ============ POST-PROCESSING: CONSERVATIVE DECISION & LOOP DETECTION ============
        # Only mark as decision point if the AI explicitly set decisionCriteria OR decisionOptions
        # DO NOT use keyword matching - it causes false positives (e.g., "Confirm" is not a decision point)
        try:
            nodes = enhanced.get('nodes', [])
            for node in nodes:
                # Only mark as decision if the AI explicitly provided decision metadata
                criteria = node.get('decisionCriteria', '')
                options = node.get('decisionOptions', {})
                
                # STRICT: Only set isDecisionPoint if AI provided explicit decision metadata
                if criteria and options and len(options) >= 2:
                    node['isDecisionPoint'] = True
                    logger.info(f"✅ Confirmed decision point: {node.get('title')} → {options}")
                else:
                    # Ensure it's explicitly False if no decision metadata
                    node['isDecisionPoint'] = False
                
                # CONSERVATIVE LOOP DETECTION: Only if AI provided loopBackTo
                if node.get('loopBackTo'):
                    node['isLoop'] = True
                    logger.info(f"✅ Confirmed loop: {node.get('title')} → loops back to {node.get('loopBackTo')}")
                else:
                    node['isLoop'] = False
        except Exception as e:
            logger.warning(f"⚠️ Post-processing failed: {e}")
        
        # ============ NEW: USE EXTRACTED DECISIONS/LOOPS/PARALLEL DATA ============
        # Map extracted decisions, loops, and parallel processes to specific nodes
        try:
            extracted_decisions = extracted_data.get('decisions', [])
            extracted_loops = extracted_data.get('loops', [])
            extracted_parallel = extracted_data.get('parallelProcesses', [])
            
            logger.info(f"📍 Mapping extracted structure: {len(extracted_decisions)} decisions, {len(extracted_loops)} loops, {len(extracted_parallel)} parallel groups")
            
            # Map decisions to nodes
            for decision in extracted_decisions:
                decision_question = decision.get('question', '').lower()
                decision_location = decision.get('location', '').lower()
                
                # Find matching node
                for node in nodes:
                    title_lower = node.get('title', '').lower()
                    details_lower = node.get('details', '').lower()
                    
                    # Check if this node matches the decision
                    if decision_question and (decision_question in title_lower or decision_question in details_lower):
                        node['isDecisionPoint'] = True
                        node['decisionCriteria'] = decision.get('question', '')
                        node['decisionOptions'] = {
                            'yes': decision.get('yesPath', 'Continue'),
                            'no': decision.get('noPath', 'Alternative')
                        }
                        logger.info(f"✅ Mapped decision: {node.get('title')} → YES: {decision.get('yesPath')}, NO: {decision.get('noPath')}")
                        break
            
            # Map loops to nodes
            for loop in extracted_loops:
                loop_action = loop.get('action', '').lower()
                loop_trigger = loop.get('trigger', '').lower()
                
                for node in nodes:
                    title_lower = node.get('title', '').lower()
                    details_lower = node.get('details', '').lower()
                    
                    if (loop_action and loop_action in title_lower) or (loop_trigger and loop_trigger in details_lower):
                        node['isLoop'] = True
                        node['loopType'] = loop.get('type', 'monitoring')
                        node['loopTrigger'] = loop.get('trigger', '')
                        node['loopExitCondition'] = loop.get('exitCondition', '')
                        logger.info(f"✅ Mapped loop: {node.get('title')} → Type: {loop.get('type')}, Exit: {loop.get('exitCondition')}")
                        break
            
            # Map parallel processes
            for parallel_group in extracted_parallel:
                if isinstance(parallel_group, list) and len(parallel_group) >= 2:
                    # Find nodes matching parallel group steps
                    matched_nodes = []
                    for step in parallel_group:
                        step_lower = step.lower() if isinstance(step, str) else ''
                        for node in nodes:
                            title_lower = node.get('title', '').lower()
                            if step_lower and step_lower in title_lower and node['id'] not in [n['id'] for n in matched_nodes]:
                                matched_nodes.append(node)
                                break
                    
                    # Mark them as parallel
                    if len(matched_nodes) >= 2:
                        for node in matched_nodes:
                            other_ids = [n['id'] for n in matched_nodes if n['id'] != node['id']]
                            node['parallelWith'] = other_ids
                        logger.info(f"✅ Mapped parallel group: {[n.get('title') for n in matched_nodes]}")
            
        except Exception as e:
            logger.warning(f"⚠️ Extracted structure mapping failed: {e}")
        
        # ============ NEW: SWIM LANE CREATION FROM EXTRACTED DATA ============
        try:
            extracted_swim_lanes = extracted_data.get('swimLanes', [])
            if extracted_swim_lanes:
                logger.info(f"🏊 Creating {len(extracted_swim_lanes)} swim lanes from extracted data")
                
                # Create swim lane objects for frontend
                swim_lane_objects = []
                lane_colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
                
                for idx, lane_data in enumerate(extracted_swim_lanes):
                    lane_id = f"lane_{idx + 1}"
                    lane_obj = {
                        'id': lane_id,
                        'name': lane_data.get('name', f'Lane {idx + 1}'),
                        'role': lane_data.get('purpose', ''),
                        'color': lane_colors[idx % len(lane_colors)]
                    }
                    swim_lane_objects.append(lane_obj)
                    logger.info(f"  Created swim lane: {lane_obj['name']}")
                
                # Add swim lanes to enhanced output
                enhanced['swimLanes'] = swim_lane_objects
                
                # Now assign nodes to swim lanes based on content matching
                nodes = enhanced.get('nodes', [])
                for node in nodes:
                    node_title = node.get('title', '').lower()
                    node_details = node.get('details', '').lower()
                    
                    # Try to match node to a swim lane
                    best_match_lane = None
                    best_match_score = 0
                    
                    for idx, lane_data in enumerate(extracted_swim_lanes):
                        lane_name = lane_data.get('name', '').lower()
                        lane_purpose = lane_data.get('purpose', '').lower()
                        
                        # Check if lane name appears in node content
                        score = 0
                        if 'onshore' in lane_name and 'onshore' in (node_title + node_details):
                            score += 10
                        if 'offshore' in lane_name and 'offshore' in (node_title + node_details):
                            score += 10
                        if 'supervisor' in lane_name and 'supervisor' in (node_title + node_details):
                            score += 5
                        if 'manager' in lane_name and 'manager' in (node_title + node_details):
                            score += 5
                        
                        # Check purpose keywords
                        purpose_keywords = lane_purpose.split()
                        for keyword in purpose_keywords:
                            if len(keyword) > 3 and keyword in (node_title + node_details):
                                score += 1
                        
                        if score > best_match_score:
                            best_match_score = score
                            best_match_lane = f"lane_{idx + 1}"
                    
                    # Assign lane if good match found
                    if best_match_lane and best_match_score >= 3:
                        node['swimLane'] = best_match_lane
                        logger.info(f"  Assigned '{node.get('title')}' to swim lane {best_match_lane}")
            else:
                logger.info("ℹ️ No swim lanes detected in extracted data")
        except Exception as e:
            logger.warning(f"⚠️ Swim lane creation failed: {e}")
        
        # ============ FIX #1: SMART POSITIONING WITH MERGE POINT DETECTION ============
        # Enhanced positioning with:
        # - Sequential: X=330, Y increments by 150
        # - Parallel: X=200/460 (2 nodes) or X=150/330/510 (3 nodes), same Y
        # - Merge points: Detected when multiple nodes connect to same target
        # - Swim lanes: X position based on lane assignment
        
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
        
        # Step 2: Position nodes with awareness of structure AND swim lanes
        swim_lane_positions = {
            'lane_1': 200,
            'lane_2': 450,
            'lane_3': 700,
            'lane_4': 950
        }
        
        for i, node in enumerate(nodes):
            if node['id'] in processed_ids:
                continue
            
            # Check if this node is a merge point
            is_merge = node['id'] in merge_points
            
            # Check if node has swim lane assignment
            swim_lane = node.get('swimLane')
            
            # Check if this node has parallel companions
            parallel_with = node.get('parallelWith', [])
            
            if parallel_with:
                # This is part of a parallel group
                parallel_nodes = [node] + [n for n in nodes if n['id'] in parallel_with]
                
                # If nodes have swim lanes, position them in their lanes
                if swim_lane:
                    for j, pnode in enumerate(parallel_nodes):
                        pnode_lane = pnode.get('swimLane')
                        if pnode_lane and pnode_lane in swim_lane_positions:
                            pnode['x'] = swim_lane_positions[pnode_lane]
                        else:
                            # Fallback: spread across default positions
                            pnode['x'] = 40 if j % 2 == 0 else 620
                        pnode['y'] = y_position
                else:
                    # No swim lanes: use standard parallel positioning
                    if len(parallel_nodes) == 2:
                        parallel_nodes[0]['x'] = 40
                        parallel_nodes[0]['y'] = y_position
                        parallel_nodes[1]['x'] = 620
                        parallel_nodes[1]['y'] = y_position
                    elif len(parallel_nodes) == 3:
                        parallel_nodes[0]['x'] = 30
                        parallel_nodes[0]['y'] = y_position
                        parallel_nodes[1]['x'] = 330
                        parallel_nodes[1]['y'] = y_position
                        parallel_nodes[2]['x'] = 630
                        parallel_nodes[2]['y'] = y_position
                    else:
                        for j, pnode in enumerate(parallel_nodes):
                            pnode['x'] = 40 if j % 2 == 0 else 620
                            pnode['y'] = y_position
                
                # Mark as processed
                for pnode in parallel_nodes:
                    processed_ids.add(pnode['id'])
                
                y_position += 150
            elif is_merge:
                # Merge points: use swim lane if assigned, otherwise center
                if swim_lane and swim_lane in swim_lane_positions:
                    node['x'] = swim_lane_positions[swim_lane]
                else:
                    node['x'] = 330  # Center merge points
                node['y'] = y_position
                node['isMergePoint'] = True
                processed_ids.add(node['id'])
                y_position += 150
            else:
                # Sequential node: position based on swim lane or center
                if swim_lane and swim_lane in swim_lane_positions:
                    node['x'] = swim_lane_positions[swim_lane]
                else:
                    node['x'] = 330  # Default center position
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
                # Try to complete truncated JSON by finding last complete object
                # If response is truncated at line 332, try to close it
                logger.warning("⚠️ Attempting to close truncated JSON...")
                
                # Count braces to determine what's missing
                open_braces = response_text.count('{') - response_text.count('}')
                open_brackets = response_text.count('[') - response_text.count(']')
                
                # Try to close the structure
                completed = response_text.rstrip()
                # Remove trailing comma if exists
                if completed.endswith(','):
                    completed = completed[:-1]
                
                # Close arrays and objects
                for _ in range(open_brackets):
                    completed += ']'
                for _ in range(open_braces):
                    completed += '}'
                
                return json.loads(completed)
            except json.JSONDecodeError:
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
            
            try:
                # Handle truncated JSON - common with long responses
                # Find last complete key-value pair and close properly
                start = response_text.find('{')
                if start != -1:
                    # Find last valid closing point
                    last_complete = response_text.rfind('}')
                    if last_complete == -1:
                        # No closing brace at all - add one
                        fixed = response_text + '}'
                    else:
                        fixed = response_text[:last_complete+1]
                    
                    # Try parsing
                    try:
                        return json.loads(fixed)
                    except:
                        # Still broken, try adding closing braces for nested structures
                        open_braces = fixed.count('{') - fixed.count('}')
                        open_brackets = fixed.count('[') - fixed.count(']')
                        
                        # Close all open structures
                        for _ in range(open_brackets):
                            fixed += ']'
                        for _ in range(open_braces):
                            fixed += '}'
                        
                        return json.loads(fixed)
            except (json.JSONDecodeError, ValueError):
                pass
            
            # If all repairs fail, raise original error
            logger.error(f"❌ Could not repair JSON. First 500 chars: {response_text[:500]}")
            logger.error(f"❌ Last 500 chars: {response_text[-500:]}")
            raise ValueError(f"Failed to parse JSON response: {e}")
