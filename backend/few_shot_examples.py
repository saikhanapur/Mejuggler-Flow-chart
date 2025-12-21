"""
Few-Shot Learning Examples for Flowchart Generation

These examples teach the AI what "good" looks like:
- EXACT terminology from source documents
- NO hallucinated steps
- PROPER decision point identification
- CORRECT connection flow

Each example is a real input→output pair that demonstrates perfect extraction.
"""

# Example 1: Simple Linear Process (5 nodes)
EXAMPLE_1_INPUT = """
Employee Onboarding Process

Step 1: HR receives new hire paperwork
Step 2: HR creates employee account in system
Step 3: IT sets up computer and email
Step 4: Manager schedules orientation meeting
Step 5: Employee completes first day checklist
"""

EXAMPLE_1_OUTPUT = {
    "processName": "Employee Onboarding Process",
    "nodes": [
        {
            "id": "node-1",
            "type": "process",
            "title": "HR receives new hire paperwork",
            "description": "Initial paperwork receipt",
            "status": "action",
            "swimLane": "HR",
            "connections": ["node-2"],
            "isDecisionPoint": False,
            "actors": ["HR"],
            "sourceReference": "Step 1"
        },
        {
            "id": "node-2",
            "type": "process",
            "title": "HR creates employee account in system",
            "description": "System account creation",
            "status": "action",
            "swimLane": "HR",
            "connections": ["node-3"],
            "isDecisionPoint": False,
            "actors": ["HR"],
            "sourceReference": "Step 2"
        },
        {
            "id": "node-3",
            "type": "process",
            "title": "IT sets up computer and email",
            "description": "Technical setup",
            "status": "action",
            "swimLane": "IT",
            "connections": ["node-4"],
            "isDecisionPoint": False,
            "actors": ["IT"],
            "sourceReference": "Step 3"
        },
        {
            "id": "node-4",
            "type": "process",
            "title": "Manager schedules orientation meeting",
            "description": "Orientation scheduling",
            "status": "action",
            "swimLane": "Manager",
            "connections": ["node-5"],
            "isDecisionPoint": False,
            "actors": ["Manager"],
            "sourceReference": "Step 4"
        },
        {
            "id": "node-5",
            "type": "process",
            "title": "Employee completes first day checklist",
            "description": "First day completion",
            "status": "action",
            "swimLane": "Employee",
            "connections": [],
            "isDecisionPoint": False,
            "actors": ["Employee"],
            "sourceReference": "Step 5"
        }
    ],
    "swimLanes": [
        {"id": "lane-1", "name": "HR", "color": "#3B82F6"},
        {"id": "lane-2", "name": "IT", "color": "#10B981"},
        {"id": "lane-3", "name": "Manager", "color": "#F59E0B"},
        {"id": "lane-4", "name": "Employee", "color": "#8B5CF6"}
    ]
}


# Example 2: Process with Decision Points (7 nodes)
EXAMPLE_2_INPUT = """
Customer Support Ticket Process

1. Customer submits support ticket
2. Support agent reviews ticket
3. Check: Is this a technical issue?
   - If YES: Escalate to Technical Team
   - If NO: Continue to step 4
4. Support agent responds to customer
5. Check: Is customer satisfied?
   - If YES: Close ticket
   - If NO: Reopen and reassign
"""

EXAMPLE_2_OUTPUT = {
    "processName": "Customer Support Ticket Process",
    "nodes": [
        {
            "id": "node-1",
            "type": "process",
            "title": "Customer submits support ticket",
            "description": "Ticket submission",
            "status": "action",
            "swimLane": "Customer",
            "connections": ["node-2"],
            "isDecisionPoint": False,
            "actors": ["Customer"],
            "sourceReference": "Step 1"
        },
        {
            "id": "node-2",
            "type": "process",
            "title": "Support agent reviews ticket",
            "description": "Initial ticket review",
            "status": "action",
            "swimLane": "Support",
            "connections": ["node-3"],
            "isDecisionPoint": False,
            "actors": ["Support agent"],
            "sourceReference": "Step 2"
        },
        {
            "id": "node-3",
            "type": "decision",
            "title": "Is this a technical issue?",
            "description": "Determine ticket type",
            "status": "critical",
            "swimLane": "Support",
            "connections": ["node-4", "node-escalate"],
            "isDecisionPoint": True,
            "decisionCriteria": "Is this a technical issue?",
            "decisionOptions": {"yes": "node-escalate", "no": "node-4"},
            "actors": ["Support agent"],
            "sourceReference": "Step 3"
        },
        {
            "id": "node-escalate",
            "type": "process",
            "title": "Escalate to Technical Team",
            "description": "Technical escalation",
            "status": "action",
            "swimLane": "Technical Team",
            "connections": [],
            "isDecisionPoint": False,
            "actors": ["Technical Team"],
            "sourceReference": "Step 3 - YES branch"
        },
        {
            "id": "node-4",
            "type": "process",
            "title": "Support agent responds to customer",
            "description": "Customer response",
            "status": "action",
            "swimLane": "Support",
            "connections": ["node-5"],
            "isDecisionPoint": False,
            "actors": ["Support agent"],
            "sourceReference": "Step 4"
        },
        {
            "id": "node-5",
            "type": "decision",
            "title": "Is customer satisfied?",
            "description": "Satisfaction check",
            "status": "critical",
            "swimLane": "Support",
            "connections": ["node-close", "node-reopen"],
            "isDecisionPoint": True,
            "decisionCriteria": "Is customer satisfied?",
            "decisionOptions": {"yes": "node-close", "no": "node-reopen"},
            "actors": ["Support agent"],
            "sourceReference": "Step 5"
        },
        {
            "id": "node-close",
            "type": "process",
            "title": "Close ticket",
            "description": "Ticket closure",
            "status": "action",
            "swimLane": "Support",
            "connections": [],
            "isDecisionPoint": False,
            "actors": ["Support agent"],
            "sourceReference": "Step 5 - YES branch"
        },
        {
            "id": "node-reopen",
            "type": "process",
            "title": "Reopen and reassign",
            "description": "Ticket reopening",
            "status": "action",
            "swimLane": "Support",
            "connections": ["node-2"],
            "isDecisionPoint": False,
            "actors": ["Support agent"],
            "sourceReference": "Step 5 - NO branch"
        }
    ],
    "swimLanes": [
        {"id": "lane-1", "name": "Customer", "color": "#3B82F6"},
        {"id": "lane-2", "name": "Support", "color": "#10B981"},
        {"id": "lane-3", "name": "Technical Team", "color": "#F59E0B"}
    ]
}


# Example 3: Emergency Response Process (similar to user's Welfare First SOP)
EXAMPLE_3_INPUT = """
Missed Check-In Alert Process

1. System detects missed check-in from employee
2. System automatically sends alert to Monitoring Team
3. Monitoring Team attempts to contact employee via phone
4. Decision: Did employee respond?
   - YES: Log contact, close alert
   - NO: Continue to escalation
5. Monitoring Team contacts emergency contact
6. Decision: Emergency contact reached?
   - YES: Get employee status update
   - NO: Dispatch field team to last known location
7. Document all actions taken
8. Close case with outcome report
"""

EXAMPLE_3_OUTPUT = {
    "processName": "Missed Check-In Alert Process",
    "nodes": [
        {
            "id": "node-1",
            "type": "process",
            "title": "System detects missed check-in from employee",
            "description": "Automated detection of missed check-in",
            "status": "critical",
            "swimLane": "System",
            "connections": ["node-2"],
            "isDecisionPoint": False,
            "actors": ["System"],
            "sourceReference": "Step 1"
        },
        {
            "id": "node-2",
            "type": "process",
            "title": "System automatically sends alert to Monitoring Team",
            "description": "Alert notification",
            "status": "action",
            "swimLane": "System",
            "connections": ["node-3"],
            "isDecisionPoint": False,
            "actors": ["System"],
            "sourceReference": "Step 2"
        },
        {
            "id": "node-3",
            "type": "process",
            "title": "Monitoring Team attempts to contact employee via phone",
            "description": "Initial contact attempt",
            "status": "action",
            "swimLane": "Monitoring Team",
            "connections": ["node-4"],
            "isDecisionPoint": False,
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 3"
        },
        {
            "id": "node-4",
            "type": "decision",
            "title": "Did employee respond?",
            "description": "Check if contact was successful",
            "status": "critical",
            "swimLane": "Monitoring Team",
            "connections": ["node-log", "node-5"],
            "isDecisionPoint": True,
            "decisionCriteria": "Did employee respond?",
            "decisionOptions": {"yes": "node-log", "no": "node-5"},
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 4"
        },
        {
            "id": "node-log",
            "type": "process",
            "title": "Log contact, close alert",
            "description": "Document successful contact and close",
            "status": "action",
            "swimLane": "Monitoring Team",
            "connections": [],
            "isDecisionPoint": False,
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 4 - YES branch"
        },
        {
            "id": "node-5",
            "type": "process",
            "title": "Monitoring Team contacts emergency contact",
            "description": "Escalation to emergency contact",
            "status": "action",
            "swimLane": "Monitoring Team",
            "connections": ["node-6"],
            "isDecisionPoint": False,
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 5"
        },
        {
            "id": "node-6",
            "type": "decision",
            "title": "Emergency contact reached?",
            "description": "Check emergency contact success",
            "status": "critical",
            "swimLane": "Monitoring Team",
            "connections": ["node-status", "node-dispatch"],
            "isDecisionPoint": True,
            "decisionCriteria": "Emergency contact reached?",
            "decisionOptions": {"yes": "node-status", "no": "node-dispatch"},
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 6"
        },
        {
            "id": "node-status",
            "type": "process",
            "title": "Get employee status update",
            "description": "Obtain status from emergency contact",
            "status": "action",
            "swimLane": "Monitoring Team",
            "connections": ["node-7"],
            "isDecisionPoint": False,
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 6 - YES branch"
        },
        {
            "id": "node-dispatch",
            "type": "process",
            "title": "Dispatch field team to last known location",
            "description": "Physical response deployment",
            "status": "critical",
            "swimLane": "Field Team",
            "connections": ["node-7"],
            "isDecisionPoint": False,
            "actors": ["Field Team"],
            "sourceReference": "Step 6 - NO branch"
        },
        {
            "id": "node-7",
            "type": "process",
            "title": "Document all actions taken",
            "description": "Complete documentation",
            "status": "action",
            "swimLane": "Monitoring Team",
            "connections": ["node-8"],
            "isDecisionPoint": False,
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 7"
        },
        {
            "id": "node-8",
            "type": "process",
            "title": "Close case with outcome report",
            "description": "Final case closure",
            "status": "action",
            "swimLane": "Monitoring Team",
            "connections": [],
            "isDecisionPoint": False,
            "actors": ["Monitoring Team"],
            "sourceReference": "Step 8"
        }
    ],
    "swimLanes": [
        {"id": "lane-1", "name": "System", "color": "#6366F1"},
        {"id": "lane-2", "name": "Monitoring Team", "color": "#3B82F6"},
        {"id": "lane-3", "name": "Field Team", "color": "#EF4444"}
    ]
}


def get_few_shot_examples_text() -> str:
    """
    Returns formatted few-shot examples for the AI prompt.
    """
    import json
    
    return f"""
=== EXAMPLE 1: Simple Linear Process ===

INPUT DOCUMENT:
{EXAMPLE_1_INPUT}

CORRECT OUTPUT:
{json.dumps(EXAMPLE_1_OUTPUT, indent=2)}

KEY OBSERVATIONS:
- Each step maps to exactly ONE node
- Node titles use EXACT wording from document
- sourceReference field shows where each node came from
- No invented steps

---

=== EXAMPLE 2: Process with Decision Points ===

INPUT DOCUMENT:
{EXAMPLE_2_INPUT}

CORRECT OUTPUT:
{json.dumps(EXAMPLE_2_OUTPUT, indent=2)}

KEY OBSERVATIONS:
- "Check:" statements become decision nodes
- YES/NO branches create separate nodes
- decisionOptions maps to actual node IDs
- Both paths from decisions are captured

---

=== EXAMPLE 3: Emergency Response (Complex) ===

INPUT DOCUMENT:
{EXAMPLE_3_INPUT}

CORRECT OUTPUT:
{json.dumps(EXAMPLE_3_OUTPUT, indent=2)}

KEY OBSERVATIONS:
- Emergency processes have critical status
- Multiple decision points with clear branching
- All branches reconnect logically (documentation step)
- sourceReference traces every node to source text
"""


def get_anti_hallucination_rules() -> str:
    """
    Returns strict anti-hallucination rules for the AI.
    """
    return """
🚨 ANTI-HALLUCINATION RULES (CRITICAL - FAILURE = PRODUCT FAILS) 🚨

1. SOURCE GROUNDING
   - Every node MUST have a sourceReference pointing to specific text in the document
   - If you cannot point to source text, DO NOT create the node
   - Quote the exact phrase that justifies each node

2. TERMINOLOGY FIDELITY
   - Use EXACT words from the document
   - If document says "Contact employee via phone" → node title is "Contact employee via phone"
   - DO NOT rephrase to "Make phone call to worker" 
   - DO NOT add professional-sounding words not in the document

3. STEP COUNT ACCURACY
   - Count the numbered steps in the document
   - Your output should have approximately that many nodes (±20%)
   - If document has 8 steps, output should have 7-10 nodes, not 15 or 25

4. NO INVENTED STEPS
   ❌ "Review documentation" (unless document says this)
   ❌ "Quality check" (unless document says this)
   ❌ "Notify supervisor" (unless document says this)
   ❌ "Update records" (unless document says this)
   ❌ "Best practice" additions
   
5. DECISION POINT RULES
   - Only create decision nodes where document explicitly shows:
     * "If... then..." statements
     * "Check if..." questions
     * "Yes/No" branching
     * Explicit decision diamonds
   - DO NOT invent decision points to "improve" the flow

6. ROLE/ACTOR EXTRACTION
   - Only use roles explicitly mentioned in document
   - If document doesn't mention roles, use generic "Operations"
   - DO NOT invent department names

7. VERIFICATION CHECKLIST (Apply before returning)
   □ Can I quote document text for every node? If no → remove node
   □ Did I use exact wording? If no → fix wording
   □ Are there invented "improvement" steps? If yes → remove them
   □ Does node count match document structure? If no → adjust
   □ Are decision points only where document shows branching? If no → fix
"""
