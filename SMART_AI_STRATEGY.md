# SMART AI EXTRACTION STRATEGY

## PRINCIPLE: SMART GROUPING + VALUE-ADD DETAILS

### What Goes in NODES (Flowchart):
1. **High-level strategic steps** (5-10 max for clarity)
   - Example: "Identify & Confirm Outage" (not 5 separate nodes)
   - Example: "Notify Stakeholders" (groups all notifications)
   - Example: "Execute Emergency Procedures"

2. **Decision Points** (critical branching only)
   - Example: "Outage Confirmed?" YES/NO
   - Example: "Services Restored?" YES/NO

3. **Swim Lanes** (parallel teams/roles)
   - Onshore Team
   - Offshore Team
   - IT Support

### What Goes in SIDE PANEL (Operational Details):
1. **Specific Actions** (the HOW)
   - "Screenshot error messages"
   - "Call Wilson IT: 0061 8 9415 2888 ext. 8088"
   - "Send Modica group message to patrol officers"

2. **Contact Information** (the WHO)
   - All phone numbers, emails
   - Escalation contacts
   - Team members

3. **Communication Templates** (the WHAT TO SAY)
   - Email scripts
   - Message templates
   - Notification text

4. **Systems & Tools** (the WHERE)
   - Lighthouse
   - Wilsar
   - Service Hub

5. **Timelines & SLAs** (the WHEN)
   - "Check every 30 minutes"
   - "Respond within 2 hours"

6. **Required Data** (the INPUTS)
   - "Officer name"
   - "Ticket number"
   - "Error message text"

## INTELLIGENT GROUPING RULES:

### Rule 1: HIERARCHICAL ORGANIZATION
```
Parent Node: "Identify & Confirm Outage"
  ├─ Sub-action: Determine if Wilsar is down
  ├─ Sub-action: Check other systems (browsers, email)
  ├─ Sub-action: Test with patrol officer
  └─ Decision: Confirmed outage?
```

### Rule 2: ROLE-BASED SWIM LANES
```
Onshore Supervisor Lane:
  → Node: "Activate BCP"
  → Node: "Notify Teams"
  → Node: "Monitor Resolution"

Offshore Team Lane:
  → Node: "Switch to Manual Mode"
  → Node: "Track Incidents"
  → Node: "Confirm Restoration"
```

### Rule 3: COMMUNICATION CONSOLIDATION
Instead of 5 nodes for different notifications:
```
❌ BAD:
  - "Notify councils via email"
  - "Send Modica message to officers"
  - "Email monitoring companies"
  - "Update regional managers"
  - "Alert escalation contacts"

✅ GOOD:
  Node: "Notify All Stakeholders"
  Side Panel Details:
    - Councils: Email (script provided)
    - Patrol Officers: Modica message (script provided)
    - Monitoring Companies: Email (script provided)
    - Regional Managers: Modica message (script provided)
    - Escalation Contacts: Listed below
```

### Rule 4: ACTION CONSOLIDATION
Instead of separate nodes for each action:
```
❌ BAD:
  - "Begin Lighthouse timeline"
  - "Distribute BCP phones"
  - "Reallocate tasks"
  - "Update ticketing system"

✅ GOOD:
  Node: "Execute Emergency Procedures"
  Side Panel Details:
    Specific Actions:
      1. Begin Lighthouse timeline under Buddy location
      2. Distribute 2x BCP mobile phones to patrol officers
      3. Reallocate AR tasks based on staffing
      4. Update P1 ticket in MyIT system
    
    Required Data:
      - Staffing numbers
      - Available patrol officers
      - Current task queue
```

## VALUE PROPOSITION:

### Current (Dumb Splitter):
- 30+ nodes (overwhelming)
- Each node = 1 sentence
- Side panel repeats node text
- **NO VALUE ADDED**

### Smart (AI Intelligence):
- 8-12 nodes (digestible)
- Each node = strategic phase
- Side panel = executable details
- **MASSIVE VALUE: Turn chaos into clarity**

## EXAMPLE TRANSFORMATION:

### INPUT (From BCP SOP):
```
1. Determine if there is a Wilsar Outage
2. Shut down the session and open a new session
3. Screenshot any errors and save
4. Supervisor to dispatch a test job
5. Contact Patrol Officer to check if job received
6. Advise patrol officer to restart phone
7. Onshore Supervisor to instruct teams
8. Advise local team about manual dispatch
9. Begin Lighthouse timeline
10. Notify councils via email
... (20 more steps)
```

### OUTPUT (Smart AI):
```
NODES (Swim Lane: Onshore Supervisor):
1. Identify & Confirm Outage
2. Activate Business Continuity Plan
3. Switch to Manual Operations
4. Monitor & Support Resolution
5. Restore Normal Operations

SIDE PANEL for "Identify & Confirm Outage":
  Decision Criteria:
    - Wilsar session unresponsive
    - Users cannot access Wilsar
    - Error messages on loading
    - Patrol officers can't see jobs on Rapid
  
  Specific Actions:
    1. Shut down and restart Wilsar session
    2. Screenshot any error messages
    3. Dispatch test job to patrol officer
    4. Contact patrol officer to verify job receipt
    5. Check if other systems working (browsers, Outlook, RingCentral)
  
  Contact Info:
    - Wilson IT: 0061 8 9415 2888 ext. 8088
    - Patrol Officer: [dynamic]
  
  Systems:
    - Wilsar (primary)
    - Rapid (patrol app)
    - Lighthouse (tracking)
  
  Timeline:
    - Initial check: immediate
    - Retest: within 5 minutes
    - Escalation: if unresolved after 10 minutes
```

## AI PROMPT STRATEGY:

### Stage 1: SEMANTIC ANALYSIS
- Identify themes/phases (not just actions)
- Detect parallel workflows (swim lanes)
- Find decision points (branching)
- Recognize communication vs execution

### Stage 2: INTELLIGENT GROUPING
- Group by PHASE (identify → activate → execute → monitor → restore)
- Group by ROLE (onshore vs offshore)
- Group by TYPE (notifications vs actions vs monitoring)

### Stage 3: DETAIL EXTRACTION
- For each grouped node, extract:
  - Executable actions (specific steps)
  - Contact information (who to call)
  - Communication templates (what to say)
  - Systems (where to do it)
  - Timelines (when to do it)

## SUCCESS CRITERIA:

✅ User looks at flowchart and immediately understands the process  
✅ User clicks a node and gets ALL details needed to execute  
✅ Side panel ADDS value (not repeats)  
✅ Complex 30-step SOP becomes clear 8-step flowchart  
✅ Details are preserved (nothing lost)  
✅ USP delivered: "Turn process chaos into clarity"  
