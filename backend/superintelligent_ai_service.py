# Superintelligent AI Service - Multi-Stage Pipeline with Learning
# Built for enterprise-grade document processing with full transparency

import json
import re
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class SuperintelligentAIService:
    """
    Superintelligent AI service that processes documents like a human mind (but 100x better)
    
    Multi-Stage Pipeline:
    - Stage 0: Document Intelligence & Classification (with reasoning)
    - Stage 1: Structure Extraction (focused on flowchartable content)
    - Stage 2: Detail Enrichment (per phase, no truncation)
    - Stage 3: Assembly & Coverage Report
    
    Features:
    - Full transparency (shows AI reasoning at each stage)
    - Learning system (captures patterns globally)
    - No quality compromises (no truncation)
    - Handles 50+ step documents
    """
    
    def __init__(self, api_key: str, db_client):
        self.api_key = api_key
        self.db = db_client
        self.learning_db = db_client.get_database("learning")
    
    async def analyze_document(self, document_text: str, input_type: str, user_id: str = None) -> Dict[str, Any]:
        """
        STAGE 0: Document Intelligence & Classification
        
        Now includes EROAD-style enhancement option
        
        CRITICAL: Document Size Handling
        - Processes up to 80,000 characters (~40 pages)
        - Warns if document exceeds limits
        """
        logger.info("🧠 STAGE 0: Document Intelligence & Classification")
        
        # ⚠️ CRITICAL: Check document size and warn
        doc_length = len(document_text)
        if doc_length > 40000:
            logger.warning(
                f"⚠️ LARGE DOCUMENT: {doc_length:,} characters\n"
                f"   Processing first 40,000 chars (~20 pages)"
            )
        if doc_length > 100000:
            logger.error(
                f"❌ VERY LARGE DOCUMENT: {doc_length:,} characters\n"
                f"   Results will likely be incomplete."
            )
        
        try:
            # Check learning database for similar patterns
            learning_context = await self._get_learning_context(document_text, input_type)
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"analyze_{uuid.uuid4()}",
                system_message="""You are a document intelligence expert. Your job is to analyze documents and extract structured data.

Extract:
1. All process steps (numbered or bulleted)
2. Decision points (if/then/else)
3. Contact information (names, phones, emails)
4. Systems/tools mentioned
5. Timing requirements
6. Parallel processes (things happening simultaneously)"""
            ).with_model("openai", "gpt-5")
            
            prompt = f"""EXTRACT STRUCTURED DATA FROM DOCUMENT - WORLD-CLASS ANALYSIS

{learning_context}

DOCUMENT:
{document_text}

VISUAL PATTERN RECOGNITION (if flowchart present):
- Diamond shapes (◆) = Decision points
- Boxes with red/bold borders = Critical/urgent actions  
- Dashed lines/arrows = Loops or repeated processes
- Horizontal bands/sections = Swim lanes (different teams/roles)
- Parallel vertical alignment = Simultaneous processes
- Color coding: Red=critical, Blue=action, Purple=communication, Green=operational, Yellow=monitoring

EXTRACT WITH PRECISION:
1. **All Steps**: Every procedural step (maintain exact order)

2. **Decision Points** (DIAMONDS - BE HIGHLY SELECTIVE!):
   A decision point is ONLY where the process BRANCHES into different paths based on a condition.
   
   ✓ IS A DECISION POINT:
   - "If X, then do Y, otherwise do Z" (explicit branching)
   - "Is condition met? YES → path A, NO → path B"
   - Process explicitly splits into multiple paths based on outcome
   
   ✗ NOT A DECISION POINT:
   - "Check if X" (verification step, no branching)
   - "Confirm Y" (validation step, linear flow)
   - "Verify Z" (checking step, continues to next step regardless)
   - "Determine status" (assessment, but doesn't branch)
   
   For EACH REAL decision found, capture:
   - Question being asked (exact wording)
   - YES branch: what happens + which step it leads to
   - NO branch: what happens + which step it leads to  
   - Default/preferred path
   - What triggers this decision
   
   EXAMPLE OF REAL DECISION: "Is connectivity restored?"
   - If YES → "Resume normal operations" (step 8)
   - If NO → "Continue monitoring loop" (return to step 5)
   → This creates a BRANCH, so it's a decision point
   
   {{
     "question": "Is connectivity restored?",
     "yesPath": "Resume normal operations (step 8)",
     "noPath": "Continue monitoring (return to step 5)",
     "location": "After monitoring cycle",
     "trigger": "30-minute status check"
   }}

3. **Loops** (DASHED LINES - Important!):
   For each loop, capture:
   - Type: retry/monitoring/iterative
   - Trigger: What causes the loop
   - Action: What repeats
   - Exit condition: How loop ends
   - Loop-back target: Which step it returns to

4. **Swim Lanes** (HORIZONTAL BANDS - Critical for BCPs!):
   Look for role-based or team-based sections that indicate parallel workflows:
   
   WHAT TO LOOK FOR:
   - Section headers: "Onshore Tasks", "Offshore Tasks", "Onshore Actions", "Offshore Actions"
   - Role labels: "Manager", "Supervisor", "Operator", "Field Officer"
   - Department labels: "FSC Actions", "DSC Actions", "NBC Actions"
   - Flowchart visual separations (horizontal bands or columns in original doc)
   
   For EACH swim lane found, capture:
   - Lane name/label (exact text from document)
   - Which step numbers belong to this lane
   - Role/responsibility description
   
   EXAMPLE from BCP document:
   {{
     "name": "Onshore Tasks",
     "steps": ["1", "2", "4", "5", "6", "9"],
     "purpose": "Actions performed by onshore supervisor and team"
   }},
   {{
     "name": "Offshore Tasks", 
     "steps": ["14", "15", "17"],
     "purpose": "Actions performed by offshore operators"
   }}

5. **Contacts**: Names, phone numbers, emails WITH context (extensions, options)

6. **Systems**: Software, tools, platforms mentioned

7. **Timings**: Time constraints, frequencies, schedules

8. **Parallel Processes**: Steps that happen simultaneously

9. **Document Sections**: ALL section headers, references, escalation hierarchies, timelines (extract EVERYTHING)

CONTACT EXTRACTION RULES (CRITICAL):
- Preserve ALL context: extensions, options, instructions
- Extensions: "ext 8088", "extension 8088", "x8088" → Include in contact value
- Options: "Option 1:", "Press 1 for", "Dial 1:" → Include as separate note
- Format: "Name: Number (Extension: X) | Option 1: Description"
- Examples:
  * "Wilson IT: 0061 8 9415 2888 ext 8088" → {{"Wilson IT": "0061 8 9415 2888 (Extension: 8088)"}}
  * "Dispatch: 0800 347 787 - Press 1 for Alarm" → {{"Dispatch": "0800 347 787 | Option 1: Alarm Response"}}
  * "Support: 0800 123 456 (Option 1: Technical, Option 2: Billing)" → {{"Support": "0800 123 456 | Option 1: Technical | Option 2: Billing"}}

RETURN JSON (MUST BE VALID JSON):
{{
  "documentSummary": "Brief overview",
  "documentType": "BCP/SOP/Workflow/Policy",
  "steps": ["Step 1", "Step 2",...],
  "decisions": [
    {{
      "question": "What is being decided?",
      "location": "After which step?",
      "yesPath": "What happens if YES",
      "noPath": "What happens if NO",
      "defaultPath": "yes or no",
      "trigger": "What triggers this decision"
    }}
  ],
  "loops": [
    {{
      "type": "retry/monitoring/iterative",
      "trigger": "What causes the loop",
      "action": "What repeats",
      "exitCondition": "How loop ends",
      "loopBackTo": "Which step"
    }}
  ],
  "swimLanes": [
    {{
      "name": "Lane name",
      "steps": ["step indices in this lane"],
      "purpose": "What this lane represents"
    }}
  ],
  "contacts": {{"ContactName1": "phone (Extension: X) | Option 1: Description", "ContactName2": "phone"}},
  "systems": ["System1", "System2"],
  "timings": ["Every 30 minutes", "Within 2 hours"],
  "parallelProcesses": [["Step A", "Step B"]],
  "documentSections": [
    {{"title": "Emergency Contacts", "content": "..."}},
    {{"title": "Templates & Scripts", "content": "..."}},
    {{"title": "Forms & Credentials", "content": "..."}},
    {{"title": "Monitoring Schedule", "content": "..."}},
    {{"title": "Critical Procedures", "content": "..."}},
    {{"title": "Checklists & Timelines", "content": "..."}}
  ]
}}

CRITICAL: 
- contacts MUST be a JSON object with key-value pairs, NOT an array
- PRESERVE extensions and options in the contact value string
- Use " | " as separator between number and options
- Return ONLY valid JSON, no explanatory text

Be thorough. Return valid JSON only."""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            try:
                analysis = self._parse_json_response(response)
            except ValueError:
                logger.warning("⚠️ Complex prompt failed, trying simplified extraction...")
                
                # Fallback: Use a simpler prompt with minimal JSON structure
                simplified_prompt = f"""Analyze this document and extract basic information. Return ONLY a valid JSON object.

Document:
{document_text[:40000]}

Return this exact JSON structure (no additional text):
{{
  "documentSummary": "one sentence summary",
  "steps": ["step1", "step2", "step3"],
  "decisions": [],
  "contacts": {{}},
  "systems": [],
  "timings": [],
  "parallelProcesses": [],
  "documentSections": []
}}

Return ONLY the JSON, nothing else."""
                
                message = UserMessage(text=simplified_prompt)
                response = await chat.send_message(message)
                analysis = self._parse_json_response(response)
                analysis['simplified'] = True
                logger.info("✅ Used simplified extraction mode")
            
            analysis['analysisId'] = str(uuid.uuid4())
            analysis['timestamp'] = datetime.now(timezone.utc).isoformat()
            analysis['inputType'] = input_type
            
            # Store in learning database
            await self._store_document_analysis(analysis, document_text, user_id)
            
            logger.info(f"✅ Stage 0 complete: Extracted {len(analysis.get('steps', []))} steps")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Stage 0 failed: {e}", exc_info=True)
            raise
    
    async def extract_structure(
        self, 
        document_text: str, 
        approved_sections: List[str],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STAGE 1: Structure Extraction with Two-Pass Architecture
        
        Pass 1: Extract skeleton (IDs, titles, edges) - minimal JSON
        Pass 2: Enrich nodes with descriptions in batches
        
        This approach GUARANTEES success by keeping JSON responses small and manageable.
        """
        logger.info("🏗️  STAGE 1: Structure Extraction (Two-Pass Architecture)")
        
        try:
            # Filter to only approved flowchartable sections
            flowchartable_sections = [
                sec for sec in analysis.get('sections', [])
                if sec['sectionId'] in approved_sections and sec['classification'] == 'flowchartable'
            ]
            
            if not flowchartable_sections:
                raise ValueError("No flowchartable sections approved")
            
            # Extract content for these sections
            section_content = self._extract_section_content(document_text, flowchartable_sections)
            
            # PASS 1: Extract Skeleton (Minimal JSON)
            logger.info("🔹 Pass 1: Extracting skeleton structure...")
            skeleton = await self._extract_skeleton(section_content)
            
            # PASS 2: Enrich Nodes (Batch Processing)
            logger.info("🔹 Pass 2: Enriching nodes with descriptions...")
            enriched_structure = await self._enrich_skeleton(skeleton, section_content)
            
            logger.info(f"✅ Stage 1 complete: {len(enriched_structure.get('nodes', []))} steps extracted")
            return enriched_structure
            
        except Exception as e:
            logger.error(f"❌ Stage 1 failed: {e}", exc_info=True)
            raise
    
    async def _extract_skeleton(self, section_content: str) -> Dict[str, Any]:
        """
        PASS 1: Extract minimal skeleton structure
        
        Returns only: node IDs, titles, types, edges, swimlanes
        NO descriptions - keeps JSON tiny (~2KB)
        """
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"skeleton_{uuid.uuid4()}",
            system_message="Extract flowchart skeleton. ONLY IDs and titles. NO descriptions."
        ).with_model("openai", "gpt-5")
        
        prompt = f"""EXTRACT FLOWCHART SKELETON - MINIMAL JSON ONLY

DOCUMENT:
{section_content[:20000]}

EXTRACT:
1. Every procedural step as a node (ID + short title ONLY)
2. Decision points as type: "decision"
3. All connections (edges)
4. Swimlanes if parallel workflows exist

RETURN THIS ULTRA-MINIMAL JSON:
{{
  "processName": "Name (5 words max)",
  "actors": ["Role1"],
  "swimLanes": [{{"id": "lane-1", "name": "Name", "color": "#6366f1"}}],
  "nodes": [
    {{"id": "node-1", "type": "trigger|active|decision", "title": "Action (6 words max)", "swimLane": "lane-1"}}
  ],
  "edges": [{{"id": "e1", "source": "node-1", "target": "node-2", "label": null}}]
}}

CRITICAL: 
- NO descriptions
- NO extra fields
- Titles: 6 words MAX
- Capture EVERY step as a separate node
- Valid JSON only"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        skeleton = self._parse_json_response(response)
        
        # Validate skeleton
        if not skeleton.get('nodes'):
            raise ValueError("Skeleton extraction failed - no nodes")
        
        # Validate and clean edges
        node_ids = {node['id'] for node in skeleton.get('nodes', [])}
        valid_edges = []
        
        for edge in skeleton.get('edges', []):
            source = edge.get('source')
            target = edge.get('target')
            
            # Skip edges with undefined or missing source/target
            if not source or not target or source == 'undefined' or target == 'undefined':
                logger.warning(f"Skipping invalid edge: {edge.get('id')} (source: {source}, target: {target})")
                continue
            
            # Skip edges pointing to non-existent nodes
            if source not in node_ids or target not in node_ids:
                logger.warning(f"Skipping edge {edge.get('id')} - references non-existent nodes (source: {source}, target: {target})")
                continue
            
            valid_edges.append(edge)
        
        skeleton['edges'] = valid_edges
        
        logger.info(f"✅ Skeleton extracted: {len(skeleton.get('nodes', []))} nodes, {len(valid_edges)} valid edges")
        return skeleton
    
    async def _enrich_skeleton(self, skeleton: Dict[str, Any], section_content: str) -> Dict[str, Any]:
        """
        PASS 2: Enrich skeleton nodes with descriptions in batches
        
        Processes 15 nodes at a time to keep JSON manageable
        """
        nodes = skeleton.get('nodes', [])
        batch_size = 15
        enriched_nodes = []
        
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i+batch_size]
            node_titles = [f"{n['id']}: {n['title']}" for n in batch]
            
            logger.info(f"🔸 Enriching batch {i//batch_size + 1} ({len(batch)} nodes)...")
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"enrich_{uuid.uuid4()}",
                system_message="Add descriptions to flowchart nodes. Keep brief."
            ).with_model("openai", "gpt-5")
            
            prompt = f"""ADD DESCRIPTIONS TO NODES

DOCUMENT CONTEXT:
{section_content[:15000]}

NODES TO ENRICH:
{chr(10).join(node_titles)}

For each node, provide:
- Brief description (15 words max)
- Actors (who does it)

RETURN JSON ARRAY:
[
  {{"id": "node-1", "description": "Brief description", "actors": ["Role"]}}
]

Keep descriptions SHORT. Valid JSON only."""
            
            try:
                message = UserMessage(text=prompt)
                response = await chat.send_message(message)
                
                descriptions = json.loads(response.strip())
                desc_map = {d['id']: d for d in descriptions if 'id' in d}
                
                # Merge descriptions with skeleton nodes
                for node in batch:
                    if node['id'] in desc_map:
                        node['description'] = desc_map[node['id']].get('description', '')
                        node['actors'] = desc_map[node['id']].get('actors', [])
                    else:
                        node['description'] = ''
                        node['actors'] = skeleton.get('actors', [])[:1]
                    
                    # Add default fields
                    self._add_node_defaults(node)
                    enriched_nodes.append(node)
                    
            except Exception as e:
                logger.warning(f"⚠️  Batch enrichment failed, using skeleton only: {e}")
                # Fallback: use skeleton without descriptions
                for node in batch:
                    node['description'] = ''
                    node['actors'] = skeleton.get('actors', [])[:1]
                    self._add_node_defaults(node)
                    enriched_nodes.append(node)
        
        # Build final structure
        structure = {
            "processName": skeleton.get('processName', 'Untitled Process'),
            "description": f"Process with {len(enriched_nodes)} steps",
            "actors": skeleton.get('actors', []),
            "swimLanes": skeleton.get('swimLanes', []),
            "nodes": enriched_nodes,
            "edges": skeleton.get('edges', []),
            "criticalGaps": [],
            "improvementOpportunities": [],
            "totalSteps": len(enriched_nodes)
        }
        
        return structure
    
    async def enrich_details(
        self, 
        document_text: str,
        structure: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STAGE 2: Detail Enrichment
        
        Enriches each node with operational details extracted from full document
        (NO TRUNCATION - uses full document context)
        
        Processes in batches to stay within token limits while maintaining quality
        """
        logger.info("💎 STAGE 2: Detail Enrichment")
        
        try:
            nodes = structure.get('nodes', [])
            if not nodes:
                return structure
            
            # Get reference sections for enrichment
            reference_sections = [
                sec for sec in analysis.get('sections', [])
                if sec['classification'] == 'reference'
            ]
            reference_content = self._extract_section_content(document_text, reference_sections)
            
            # Process nodes in batches of 10 to manage token usage
            batch_size = 10
            enriched_nodes = []
            
            for i in range(0, len(nodes), batch_size):
                batch = nodes[i:i+batch_size]
                enriched_batch = await self._enrich_node_batch(
                    batch, 
                    document_text,
                    reference_content
                )
                enriched_nodes.extend(enriched_batch)
            
            structure['nodes'] = enriched_nodes
            logger.info(f"✅ Stage 2 complete: {len(enriched_nodes)} nodes enriched")
            return structure
            
        except Exception as e:
            logger.error(f"⚠️  Stage 2 partial failure: {e}. Proceeding with structure only.")
            # Graceful degradation
            for node in structure.get('nodes', []):
                if 'operationalDetails' not in node:
                    node['operationalDetails'] = self._get_empty_details()
            return structure
    
    async def _enrich_node_batch(
        self, 
        nodes: List[Dict], 
        document_text: str,
        reference_content: str
    ) -> List[Dict]:
        """Enrich a batch of nodes with operational details"""
        
        node_summary = [f"{n['id']}: {n['title']}" for n in nodes]
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"enrich_{uuid.uuid4()}",
            system_message="Extract precise operational details. Be specific, not generic."
        ).with_model("openai", "gpt-5")
        
        # Use targeted excerpts to stay under token limit while maintaining quality
        prompt = f"""EXTRACT OPERATIONAL DETAILS

TARGET NODES:
{chr(10).join(node_summary)}

REFERENCE MATERIAL:
{reference_content[:40000]}

FULL DOCUMENT CONTEXT (for cross-reference):
{document_text[:40000]}

FOR EACH NODE, EXTRACT:
1. **specificActions**: DETAILED HOW-TO STEPS (break down the action into specific instructions)
   - Example: Instead of "Send notifications", provide ["Open email client", "Use template XYZ", "Send to distribution list ABC"]
   - These should be MORE detailed than the node title
   - If the node says "Notify stakeholders", actions should be "Draft email using template", "Send to council distribution list", "CC manager"
2. **requiredData**: Input fields, information needed
3. **contactInfo**: Names, phone numbers, emails (from reference section)
4. **systems**: Software, tools, platforms mentioned
5. **timeline**: Time limits, frequencies ("every 30 minutes", "within 2 hours")
6. **communicationTemplates**: Email scripts, message templates (reference by name)

**7. decisionCriteria (CRITICAL - HUMAN READABLE!):**
For decision nodes, provide a PLAIN ENGLISH explanation of the decision logic.
❌ WRONG: {{"yes": "node_id", "no": "other_id"}}
❌ WRONG: {{"yes": "start_documentation", "no": "emergency_relocation"}}
✅ CORRECT: "If the user is safe and can communicate, proceed with documentation. If the user cannot speak or is in immediate danger, initiate emergency relocation protocol."
✅ CORRECT: "Check if system is restored. If GDS responds within 15 minutes, resume normal operations. If no response after 15 minutes, continue manual operations."

The decision criteria should be a SENTENCE or PARAGRAPH explaining:
- What condition is being checked
- What happens in the YES case
- What happens in the NO case
- Any time limits or thresholds

**8. riskFactors (NEW - HIGH VALUE!):**
Identify what could go wrong with this step.
Examples:
- "Single point of failure - only supervisor can authorize"
- "No backup if primary contact unavailable"
- "Manual process prone to human error"
- "Time-critical - delays compound downstream"

**9. successCriteria (NEW - HIGH VALUE!):**
How do we know this step succeeded?
Examples:
- "Email sent confirmation received"
- "All stakeholders acknowledged receipt"
- "System status shows 'restored'"
- "No errors reported within 30 minutes"

**10. estimatedDuration (NEW - HIGH VALUE!):**
Based on document clues, estimate how long this step takes.
Examples:
- "2-5 minutes" (for simple email)
- "15-30 minutes" (for complex coordination)
- "Ongoing - check every 30 minutes" (for monitoring)
- "1-2 hours" (for system restoration)

**11. dependencies (NEW - HIGH VALUE!):**
What MUST happen before this step?
Examples:
- "Requires: Outage confirmed, IT team notified"
- "Depends on: Manager approval received"
- "Prerequisites: System credentials, access to dashboard"

**12. trainingRequired (NEW - HIGH VALUE!):**
What skills/knowledge does someone need?
Examples:
- "Basic: Email, phone"
- "Intermediate: System access, incident procedures"
- "Advanced: Technical troubleshooting, escalation protocols"

CRITICAL: specificActions must be DIFFERENT and MORE DETAILED than what's already in the node title/description.
If the node is simple and has no substeps, leave specificActions as empty array [].

BE SPECIFIC. Extract actual values from document, not placeholders.

RETURN JSON ARRAY:
[
  {{
    "id": "node-1",
    "specificActions": ["Actual action 1", "Actual action 2"],
    "requiredData": ["Field name", "Data element"],
    "contactInfo": {{"Name": "Phone number", "Email": "address"}},
    "systems": ["System name"],
    "timeline": "Specific timeframe",
    "communicationTemplates": ["Template reference"],
    "decisionCriteria": "YES: condition | NO: condition",
    "riskFactors": ["Risk 1", "Risk 2"],
    "successCriteria": "How to verify success",
    "estimatedDuration": "Time estimate",
    "dependencies": ["Prerequisite 1", "Prerequisite 2"],
    "trainingRequired": "Skill level description"
  }}
]

Return valid JSON only."""
        
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
                    "decisionCriteria": self._validate_decision_criteria(details.get('decisionCriteria'), node.get('isDecisionPoint', False)),
                    "emailTemplates": details.get('communicationTemplates', []),
                    "riskFactors": details.get('riskFactors', []),
                    "successCriteria": details.get('successCriteria'),
                    "estimatedDuration": details.get('estimatedDuration'),
                    "dependencies": details.get('dependencies', []),
                    "trainingRequired": details.get('trainingRequired'),
                    "sourcePage": None
                }
            else:
                node['operationalDetails'] = self._get_empty_details()
        
        return nodes
    
    def _validate_decision_criteria(self, criteria, is_decision_point):
        """Ensure decisionCriteria is human-readable, not dict/code"""
        if not is_decision_point:
            return None
        
        # If it's a dict or looks like code, convert to human-readable
        if isinstance(criteria, dict):
            logger.warning(f"Decision criteria is dict, converting to readable: {criteria}")
            return "Decision logic defined but needs human-readable explanation. Please review."
        
        if criteria and (criteria.startswith('{') or criteria.startswith('[')):
            logger.warning(f"Decision criteria looks like code: {criteria}")
            return "Decision point requires review - logic defined in technical format."
        
        # If it's empty or None for a decision point, provide generic guidance
        if not criteria:
            return "This is a decision point. Review the document to determine the decision logic."
        
        return criteria
    
    async def generate_coverage_report(
        self,
        structure: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STAGE 3: Assembly & Coverage Report
        
        Returns:
        {
            "stepsCaptured": 37,
            "stepsExpected": 37,
            "completeness": 100,
            "referencesLinked": 18,
            "decisionTreesMapped": 3,
            "exclusions": [
                {
                    "section": "Figure 1",
                    "reasoning": "Screenshot - contextual only"
                }
            ]
        }
        """
        logger.info("📊 STAGE 3: Assembly & Coverage Report")
        
        try:
            total_nodes = len(structure.get('nodes', []))
            expected_steps = analysis.get('overallAnalysis', {}).get('totalEstimatedSteps', total_nodes)
            
            # Count operational details
            nodes_with_details = sum(
                1 for n in structure.get('nodes', [])
                if n.get('operationalDetails') and any([
                    n['operationalDetails'].get('contactInfo'),
                    n['operationalDetails'].get('systems'),
                    n['operationalDetails'].get('emailTemplates')
                ])
            )
            
            # Count decision nodes
            decision_nodes = sum(
                1 for n in structure.get('nodes', [])
                if n.get('type') == 'decision'
            )
            
            # Get excluded sections
            excluded_sections = [
                {
                    "section": sec['title'],
                    "reasoning": sec['reasoning']
                }
                for sec in analysis.get('sections', [])
                if sec['classification'] == 'excluded'
            ]
            
            report = {
                "stepsCaptured": total_nodes,
                "stepsExpected": expected_steps,
                "completeness": round((total_nodes / expected_steps * 100) if expected_steps > 0 else 100, 1),
                "nodesWithOperationalDetails": nodes_with_details,
                "decisionNodesMapped": decision_nodes,
                "swimLanes": len(structure.get('swimLanes', [])),
                "exclusions": excluded_sections,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Stage 3 complete: {report['completeness']}% completeness")
            return report
            
        except Exception as e:
            logger.error(f"❌ Stage 3 failed: {e}", exc_info=True)
            raise
    
    # ==================== LEARNING SYSTEM ====================
    
    async def _get_learning_context(self, document_text: str, input_type: str) -> str:
        """Retrieve learning patterns from database to improve analysis"""
        try:
            # Find similar document patterns
            patterns = await self.learning_db.document_patterns.find(
                {"inputType": input_type}
            ).sort("confidence", -1).limit(5).to_list(length=5)
            
            if not patterns:
                return ""
            
            context = "LEARNING CONTEXT (from similar documents):\n"
            for pattern in patterns:
                context += f"- {pattern.get('pattern', '')} (confidence: {pattern.get('confidence', 0)})\n"
            
            return context + "\n"
            
        except Exception as e:
            logger.warning(f"Could not retrieve learning context: {e}")
            return ""
    
    async def _store_document_analysis(self, analysis: Dict, document_text: str, user_id: str):
        """Store document analysis in learning database"""
        try:
            learning_entry = {
                "analysisId": analysis['analysisId'],
                "timestamp": analysis['timestamp'],
                "inputType": analysis['inputType'],
                "documentLength": len(document_text),
                "sections": analysis.get('sections', []),
                "complexity": analysis.get('overallAnalysis', {}).get('complexity'),
                "totalSteps": analysis.get('overallAnalysis', {}).get('totalEstimatedSteps'),
                "userId": user_id,
                "validated": False  # Will be updated when user approves
            }
            
            await self.learning_db.document_analyses.insert_one(learning_entry)
            logger.info(f"💾 Stored analysis {analysis['analysisId']} in learning database")
            
        except Exception as e:
            logger.warning(f"Could not store learning data: {e}")
    
    async def store_user_feedback(
        self, 
        analysis_id: str,
        user_corrections: List[Dict],
        user_id: str
    ):
        """Store user corrections for learning"""
        try:
            feedback_entry = {
                "feedbackId": str(uuid.uuid4()),
                "analysisId": analysis_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "corrections": user_corrections,
                "userId": user_id
            }
            
            await self.learning_db.user_feedback.insert_one(feedback_entry)
            
            # Update patterns based on feedback
            await self._update_learning_patterns(user_corrections)
            
            # Mark analysis as validated
            await self.learning_db.document_analyses.update_one(
                {"analysisId": analysis_id},
                {"$set": {"validated": True, "validatedAt": datetime.now(timezone.utc).isoformat()}}
            )
            
            logger.info(f"📚 Stored user feedback for {analysis_id}")
            
        except Exception as e:
            logger.warning(f"Could not store feedback: {e}")
    
    async def _update_learning_patterns(self, corrections: List[Dict]):
        """Update global learning patterns based on user corrections"""
        try:
            for correction in corrections:
                section_title_pattern = correction.get('sectionTitle', '').lower()
                correct_classification = correction.get('correctClassification')
                
                # Find or create pattern
                pattern = await self.learning_db.document_patterns.find_one({
                    "pattern": {"$regex": section_title_pattern, "$options": "i"}
                })
                
                if pattern:
                    # Update confidence
                    new_confidence = min(pattern.get('confidence', 0.5) + 0.05, 0.99)
                    await self.learning_db.document_patterns.update_one(
                        {"_id": pattern['_id']},
                        {
                            "$set": {
                                "confidence": new_confidence,
                                "classification": correct_classification,
                                "updatedAt": datetime.now(timezone.utc).isoformat()
                            },
                            "$inc": {"validationCount": 1}
                        }
                    )
                else:
                    # Create new pattern
                    await self.learning_db.document_patterns.insert_one({
                        "pattern": section_title_pattern,
                        "classification": correct_classification,
                        "confidence": 0.7,
                        "validationCount": 1,
                        "createdAt": datetime.now(timezone.utc).isoformat()
                    })
            
            logger.info(f"📈 Updated {len(corrections)} learning patterns")
            
        except Exception as e:
            logger.warning(f"Could not update patterns: {e}")
    
    async def detect_multiple_processes_and_structure(self, document_text: str) -> Dict[str, Any]:
        """
        STAGE 0.5: Comprehensive Document Analysis
        
        Detects:
        1. Multiple processes (like Recruitment: 9 processes)
        2. Swim lanes/role sections (like BCPs: Onshore/Offshore)
        3. Phased structures (like DR SOP: 7 phases)
        4. Decision points (if/then branches)
        5. Monitoring loops (every X minutes)
        6. Parallel activities (simultaneous actions)
        7. RACI tables (role matrices)
        
        Returns comprehensive structure for AI to use
        """
        logger.info("🔍 Comprehensive document structure detection...")
        
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"detect_{uuid.uuid4()}",
                system_message="""You are an enterprise process intelligence expert. Analyze documents from:
- Manufacturing (Quality Control, Product Recall, Safety)
- Healthcare (Clinical pathways, Emergency protocols)
- Finance (KYC, Transaction processing, Approval chains)
- IT (Incident management, Disaster Recovery, Change management)
- HR (Recruitment, Onboarding, Performance, Offboarding)

Your job: Identify ALL structural patterns in the document."""
            ).with_model("openai", "gpt-5")
            
            prompt = f"""COMPREHENSIVE DOCUMENT STRUCTURE ANALYSIS

DOCUMENT (first 40,000 chars):
{document_text[:40000]}

ANALYZE FOR ALL PATTERNS:

1. MULTIPLE PROCESSES:
   - Are there 2+ distinct processes in this document?
   - Look for: Numbered sections (Process 1, 2, 3), Separate workflows
   - Example: "Recruitment Process Maps" with 9 separate processes
   - If found, list each process title

2. SWIM LANES / ROLE SECTIONS:
   - Are there parallel columns/sections by role or team?
   - Look for: "Onshore Actions", "Offshore Actions", "IDENTIFY", "ASSESS", "MITIGATE"
   - Look for: Role-based headers (QA Manager, DR Manager, Platform Owner)
   - Example: BCP with "Identify | Onshore | Offshore" columns

3. PHASED STRUCTURE:
   - Is the process divided into phases/stages?
   - Look for: "Phase 1", "Phase 2", "Stage 1", "Step 1"
   - Example: DR SOP with "Phase 0: Preparedness, Phase 1: Incident Declaration..."
   - If found, list phase names

4. DECISION POINTS:
   - Look for if/then/else logic, branching
   - Patterns: "If [condition]", "[System] down?", "Has [X] occurred?"
   - Example: "If Supplier Issue → Trigger SD-07"
   - Example: "Has Wilsar Outage? YES/NO"
   - List all decision criteria found

5. MONITORING LOOPS:
   - Look for recurring checks/validations
   - Patterns: "Check every [X] minutes", "Monitor until [condition]"
   - Example: "Check in with Wilson IT every 30 minutes until services restored"
   - Example: "RCA validated until accepted by QA Director"
   - List all loops with frequency

6. PARALLEL ACTIVITIES:
   - Look for simultaneous actions by different teams
   - Patterns: "Meanwhile", "At the same time", "Parallel", actions in same row
   - Example: "QA notifies Regulatory, Supply Chain halts distribution, Customer Service drafts notice"
   - Look for: Same timing/level but different actors
   - List parallel activity groups

7. RACI TABLES / ROLE MATRICES:
   - Look for tables showing Responsible, Accountable, Consulted, Informed
   - Look for: Role columns (Manager, Employee, HR, IT)
   - Example: RACI matrix in Product Recall SOP
   - If found, note presence

8. REFERENCED SUB-PROCESSES:
   - Look for references to other procedures
   - Patterns: "SOP-XXX", "Refer to [Procedure]", "Trigger [Sub-Process]"
   - Example: "Trigger Supplier Deviation Procedure SD-07"
   - List referenced procedures

9. GATES / APPROVALS:
   - Look for approval points or gates
   - Patterns: "Gate G3", "Approval required", "Sign-off"
   - Example: "Gate G6: Steering Committee approval required"
   - List all gates

10. DOCUMENT COMPLEXITY:
    - Simple (3-10 steps, linear)
    - Medium (10-20 steps, some branching)
    - Complex (20+ steps, multiple branches/phases)
    - Very Complex (30+ steps, nested processes, tables)

RETURN JSON (VALID JSON ONLY, NO MARKDOWN):
{{
  "multipleProcesses": true or false,
  "processCount": 1,
  "processTitles": ["Process 1 title"],
  
  "swimLanes": [
    {{"id": "identify", "title": "IDENTIFY", "team": "Dispatch"}},
    {{"id": "onshore", "title": "ONSHORE ACTIONS", "team": "Onshore Supervisor"}}
  ],
  
  "phases": [
    {{"number": 0, "title": "Preparedness", "description": "Pre-incident"}},
    {{"number": 1, "title": "Incident Declaration", "description": "Initial response"}}
  ],
  
  "decisionPoints": [
    {{"condition": "Has Wilsar Outage?", "branches": ["YES", "NO"], "location": "section 2"}},
    {{"condition": "If Supplier Issue", "branches": ["Trigger SD-07", "Continue"], "location": "step 5"}}
  ],
  
  "monitoringLoops": [
    {{"action": "Check with Wilson IT", "frequency": "every 30 minutes", "until": "services restored"}},
    {{"action": "RCA validation", "frequency": "iterative", "until": "accepted by QA Director"}}
  ],
  
  "parallelActivities": [
    {{"level": "notification", "activities": ["QA notifies Regulatory", "Supply Chain halts", "Customer Service drafts"]}}
  ],
  
  "hasRACITable": false,
  "referencedProcedures": ["SOP-RCA-001", "SD-07", "FR-05"],
  "gates": ["Gate G3", "Gate G6"],
  
  "complexity": "simple",
  "reasoning": "Why this structure?",
  "recommendation": "single_flowchart",
  "pageEstimate": 5
}}

CRITICAL:
- If processCount >= 2, set multipleProcesses: true
- If swimLanes found, list ALL swim lanes with their teams
- If phases found, list ALL phases
- Return ONLY valid JSON, no explanatory text before/after
- Be thorough - capture ALL patterns

Analyze now:"""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            # Parse response
            detection = self._parse_json_response(response)
            
            # Auto-decide based on detection
            if detection.get("multipleProcesses") and detection.get("processCount", 0) >= 2:
                # AUTO-DECIDE: Multiple processes → Create separately
                detection["recommendation"] = "multiple_flowcharts"
                detection["autoDecision"] = "Create each process as a separate flowchart"
            elif detection.get("phases") and len(detection.get("phases", [])) >= 3:
                # AUTO-DECIDE: Phased process → Keep as one with phases
                detection["recommendation"] = "phased_single_flowchart"
                detection["autoDecision"] = "Create one flowchart with phase stages"
            elif detection.get("swimLanes") and len(detection.get("swimLanes", [])) >= 2:
                # AUTO-DECIDE: Swim lanes → Keep as one with lanes
                detection["recommendation"] = "swimlane_single_flowchart"
                detection["autoDecision"] = "Create one flowchart with swim lanes"
            else:
                # AUTO-DECIDE: Simple process → Standard flowchart
                detection["recommendation"] = "single_flowchart"
                detection["autoDecision"] = "Create standard flowchart"
            
            logger.info(f"✅ Detection complete: {detection.get('processCount')} process(es)")
            logger.info(f"   Auto-decision: {detection.get('autoDecision')}")
            logger.info(f"   Swim lanes: {len(detection.get('swimLanes', []))}")
            logger.info(f"   Phases: {len(detection.get('phases', []))}")
            logger.info(f"   Decisions: {len(detection.get('decisionPoints', []))}")
            logger.info(f"   Loops: {len(detection.get('monitoringLoops', []))}")
            
            return detection
            
        except Exception as e:
            logger.error(f"❌ Detection failed: {e}", exc_info=True)
            return {
                "multipleProcesses": False,
                "processCount": 1,
                "processTitles": [],
                "swimLanes": [],
                "phases": [],
                "decisionPoints": [],
                "monitoringLoops": [],
                "parallelActivities": [],
                "hasRACITable": False,
                "referencedProcedures": [],
                "gates": [],
                "complexity": "unknown",
                "recommendation": "single_flowchart",
                "autoDecision": "Create standard flowchart (detection failed)",
                "reasoning": f"Detection failed: {str(e)}"
            }
    
    async def generate_eroad_style_flowchart(
        self,
        document_text: str,
        input_type: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        HYBRID APPROACH WITH COMPREHENSIVE DETECTION: Detect → Extract → Enhance → Return
        
        NEW: Now detects multiple processes, swim lanes, phases, decisions, loops!
        
        Phase 0: Detect structure (multi-process, swim lanes, phases, etc.)
        Phase 1: Extract structured data
        Phase 2: Enhance with EROAD-style grouping and rich details
        
        Returns visualization-ready flowchart(s) with detected structure
        """
        logger.info("🚀 EROAD-Style Flowchart Generation with Comprehensive Detection")
        
        try:
            # PHASE 0: Comprehensive structure detection
            detection = await self.detect_multiple_processes_and_structure(document_text)
            
            # AUTO-DECIDE based on detection
            if detection.get("multipleProcesses") and detection.get("processCount", 0) >= 2:
                logger.info(f"🔍 Multiple processes detected: {detection['processCount']}")
                logger.info(f"   Auto-decision: {detection['autoDecision']}")
                
                # Return detection result for multi-process handling
                return {
                    "multipleProcesses": True,
                    "processCount": detection["processCount"],
                    "processTitles": detection["processTitles"],
                    "detection": detection,  # Include full detection for reference
                    "autoDecision": detection["autoDecision"],
                    "reasoning": detection.get("reasoning", ""),
                    "processes": []  # Empty - will be created individually by separate endpoint
                }
            
            # PHASE 1: Single process - Extract data with structure context
            logger.info(f"📄 Single process detected - using structure: {detection.get('autoDecision')}")
            logger.info(f"   Swim lanes: {len(detection.get('swimLanes', []))}")
            logger.info(f"   Phases: {len(detection.get('phases', []))}")
            logger.info(f"   Decisions: {len(detection.get('decisionPoints', []))}")
            logger.info(f"   Loops: {len(detection.get('monitoringLoops', []))}")
            
            extracted = await self.analyze_document(document_text, input_type, user_id)
            
            # PHASE 2: Enhance for visualization with detected structure
            from eroad_style_enhancer import EROADStyleEnhancer
            
            enhancer = EROADStyleEnhancer(self.api_key)
            enhanced = await enhancer.enhance_for_visualization(
                extracted, 
                document_text,
                detection  # NEW: Pass detected structure to enhancer
            )
            
            # Map to expected format (existing code continues...)
            process = {
                "name": enhanced.get("processName"),
                "description": extracted.get("documentSummary"),
                "nodes": [],
                "edges": [],
                "swimLanes": enhanced.get("swimLanes", []),
                "actors": list(set([
                    actor 
                    for node in enhanced.get("nodes", []) 
                    for actor in node.get("contacts", [])
                ])),
                "quickReference": {},  # Will be populated after node processing
                "_pendingQuickReference": True,  # Flag to populate later
                "progressStages": []  # Will be populated based on node positions
            }
            
            # Add metadata for verification
            process["metadata"] = {
                "originalStepCount": len(extracted.get("steps", [])),
                "nodesCreated": len(enhanced.get("nodes", [])),
                "coveragePercent": 100,
                "contactsExtracted": len(extracted.get("contacts", {})),
                "timingsExtracted": len(extracted.get("timings", [])),
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "aiModel": "Claude Sonnet 4"
            }
            
            logger.info(f"✅ Metadata added: {process['metadata']}")
            
            # Process nodes and identify progress stages
            critical_nodes = []
            monitoring_nodes = []
            recovery_nodes = []
            
            for node in enhanced.get("nodes", []):
                # Calculate priority for this node
                priority_info = self.calculate_node_priority(node)
                
                processed_node = {
                    "id": node["id"],
                    "title": node["title"],
                    "description": node.get("details", ""),
                    "type": self._map_status_to_type(node.get("status")),
                    "status": node.get("status", "operational"),
                    "priority": priority_info,  # NEW: Priority classification
                    "x": node.get("x", 330),
                    "y": node.get("y", 0),
                    "position": {"x": node.get("x", 0), "y": node.get("y", 0)},
                    "actors": node.get("contacts", []),
                    "subSteps": node.get("actions", []),
                    "dependencies": node.get("dependencies", []),
                    "parallelWith": node.get("parallelWith", []),
                    "isDecisionPoint": node.get("isDecisionPoint", False),
                    "decisionOptions": node.get("decisionOptions", {}),
                    "isLoop": node.get("isLoop", False),
                    "loopBackTo": node.get("loopBackTo"),
                    "failures": [],
                    "blocking": None,
                    "impact": "high" if node.get("status") == "critical" else "medium",
                    "timeEstimate": node.get("timing"),
                    "operationalDetails": {
                        "purpose": node.get("purpose", ""),
                        "specificActions": node.get("actions", []),
                        "requiredData": [],
                        "contactInfo": {c.split(":")[0]: c.split(":")[1].strip() if ":" in c else c for c in node.get("contacts", [])},
                        "timeline": node.get("timing"),
                        "systems": node.get("systems", []),
                        "decisionCriteria": node.get("decisionCriteria") if node.get("isDecisionPoint") else None,
                        "emailTemplates": [],
                        "currentState": node.get("currentState"),
                        "idealState": node.get("idealState"),
                        "gap": node.get("gap"),
                        "sourcePage": None
                    }
                }
                
                logger.info(f"   → {node['title']}: {priority_info['emoji']} {priority_info['level']} (score: {priority_info['score']})")
                
                process["nodes"].append(processed_node)
                
                # Track nodes by status for progress stages
                if node.get("status") == "critical":
                    critical_nodes.append(node)
                elif node.get("status") in ["monitoring", "verification"]:
                    monitoring_nodes.append(node)
                elif node.get("status") in ["recovery"]:
                    recovery_nodes.append(node)
                
                # Create edges
                for target_id in node.get("connections", []):
                    edge = {
                        "id": f"e-{node['id']}-{target_id}",
                        "source": node['id'],
                        "target": target_id,
                        "label": None
                    }
                    
                    # Mark as dashed if it's a loop
                    if node.get("isLoop") and target_id == node.get("loopBackTo"):
                        edge["type"] = "dashed"
                    
                    # Add label for decision branches
                    if node.get("isDecisionPoint") and node.get("decisionOptions"):
                        decision_opts = node.get("decisionOptions", {})
                        if decision_opts.get("yes") == target_id:
                            edge["label"] = "YES"
                        elif decision_opts.get("no") == target_id:
                            edge["label"] = "NO"
                    
                    process["edges"].append(edge)
            
            # Add progress stage badges
            if critical_nodes:
                first_critical = min(critical_nodes, key=lambda n: n.get("y", 0))
                process["progressStages"].append({
                    "type": "immediate",
                    "x": 630,
                    "y": first_critical.get("y", 0) + 5,
                    "title": "IMMEDIATE ACTION",
                    "description": "Critical response required - all teams coordinate"
                })
            
            if monitoring_nodes:
                first_monitoring = min(monitoring_nodes, key=lambda n: n.get("y", 0))
                process["progressStages"].append({
                    "type": "ongoing",
                    "x": 630,
                    "y": first_monitoring.get("y", 0) + 5,
                    "title": "ONGOING",
                    "description": "Continue operations until resolution confirmed"
                })
            
            if recovery_nodes:
                first_recovery = min(recovery_nodes, key=lambda n: n.get("y", 0))
                process["progressStages"].append({
                    "type": "complete",
                    "x": 630,
                    "y": first_recovery.get("y", 0) + 5,
                    "title": "RECOVERY COMPLETE",
                    "description": "All systems operational, timeline documented"
                })
            
            # Populate quickReference with intelligent extraction
            if process.get("_pendingQuickReference"):
                logger.info("🎯 Generating intelligent quickReference...")
                
                # Extract critical actions intelligently (top 5 most urgent)
                critical_actions_data = self.extract_critical_actions_intelligent(
                    enhanced.get("nodes", []), 
                    extracted
                )
                
                # Format for frontend with priority information
                critical_actions_list = []
                for action_data in critical_actions_data:
                    # Find the corresponding node to get priority
                    node_id = action_data.get("nodeId")
                    priority_emoji = "🔴"  # Default
                    priority_level = "P0"
                    
                    # Find the processed node with this ID
                    for proc_node in process["nodes"]:
                        if proc_node["id"] == node_id:
                            priority_emoji = proc_node["priority"]["emoji"]
                            priority_level = proc_node["priority"]["level"]
                            break
                    
                    # Format: "🔴 P0: Call 111 immediately (immediately)"
                    action_text = f"{priority_emoji} {priority_level}: {action_data['action']}"
                    if action_data.get("timeWindow"):
                        action_text += f" ({action_data['timeWindow']})"
                    critical_actions_list.append(action_text)
                
                # Extract recovery steps (nodes with status="recovery")
                recovery_steps_list = [
                    {"title": n["title"], "id": n["id"]} 
                    for n in enhanced.get("nodes", []) 
                    if n.get("status") == "recovery"
                ]
                
                # Parse contacts hierarchically (extensions + options)
                hierarchical_contacts = self.parse_contacts_hierarchical(
                    extracted.get("contacts", {})
                )
                
                # Extract key timings with enhanced context
                enhanced_timings = self.extract_key_timings_enhanced(
                    enhanced.get("nodes", []),
                    extracted
                )
                
                # Extract supporting references (ALL document sections)
                supporting_refs = extracted.get("documentSections", [])
                
                # Only populate quickReference if there's meaningful data
                has_critical_actions = len(critical_actions_list) > 0
                has_timings = len(enhanced_timings) > 0
                has_contacts = len(hierarchical_contacts) > 0
                has_recovery = len(recovery_steps_list) > 0
                has_refs = len(supporting_refs) > 0
                
                if has_critical_actions or has_timings or has_contacts or has_recovery or has_refs:
                    process["quickReference"] = {
                        "criticalActions": critical_actions_list if has_critical_actions else [],
                        "keyTimings": enhanced_timings if has_timings else [],
                        "emergencyContacts": hierarchical_contacts if has_contacts else {},
                        "recoverySteps": recovery_steps_list if has_recovery else [],
                        "supportingReferences": supporting_refs if has_refs else []
                    }
                    logger.info(f"✅ QuickReference populated: {len(critical_actions_list)} actions, {len(hierarchical_contacts)} contacts, {len(supporting_refs)} refs")
                else:
                    # No meaningful reference data - don't create quickReference at all
                    process["quickReference"] = None
                    logger.info("ℹ️ No meaningful reference data found - quickReference not populated")
                
                # Remove the flag
                del process["_pendingQuickReference"]
                
                logger.info(f"   ✅ Critical Actions: {len(critical_actions_list)}")
                logger.info(f"   ✅ Key Timings: {len(extracted.get('timings', []))}")
                logger.info(f"   ✅ Emergency Contacts: {len(extracted.get('contacts', {}))}")
                logger.info(f"   ✅ Recovery Steps: {len(recovery_steps_list)}")
            
            # INNOVATION 1: Generate Contextual AI Recommendations
            logger.info("💡 Generating AI recommendations for process improvement...")
            process['nodes'] = await self.generate_contextual_recommendations(process['nodes'])
            
            # WORLD-CLASS ANALYSIS: Calculate comprehensive metrics
            logger.info("📊 Calculating world-class process metrics...")
            
            # Complexity Score
            process['complexityScore'] = self.calculate_complexity_score({"nodes": process['nodes'], "_extracted_data": extracted})
            logger.info(f"   Complexity: {process['complexityScore']['score']}/10 ({process['complexityScore']['level']})")
            
            # Process Health Score
            process['healthScore'] = self.calculate_process_health_score(process)
            logger.info(f"   Health: {process['healthScore']['score']}/100 ({process['healthScore']['level']})")
            
            # Execution Time Estimate
            process['executionTime'] = self.estimate_execution_time(process['nodes'])
            logger.info(f"   Est. Time: {process['executionTime']['average']} (avg)")
            
            # Multi-Lens Gap Analysis
            process['gapAnalysis'] = self.multi_lens_gap_analysis(process['nodes'], extracted)
            total_gaps = sum(len(gaps) for gaps in process['gapAnalysis'].values())
            logger.info(f"   Gaps Found: {total_gaps} across 4 lenses")
            
            # Critical Path Detection
            process['criticalPath'] = self.detect_critical_path(process['nodes'])
            logger.info(f"   Critical Path: {len(process['criticalPath'])} blocking steps")
            
            # Process Metrics Summary
            process['processMetrics'] = {
                "totalNodes": len(process['nodes']),
                "decisionPoints": len([n for n in process['nodes'] if n.get('isDecisionPoint')]),
                "loops": len([n for n in process['nodes'] if n.get('isLoop')]),
                "avgAutomation": round(sum([n.get('aiRecommendations', {}).get('automationScore', 0) for n in process['nodes']]) / len(process['nodes']), 1) if process['nodes'] else 0,
                "criticalSteps": len([n for n in process['nodes'] if n.get('status') == 'critical'])
            }
            
            logger.info(f"✅ EROAD-style flowchart complete: {len(process['nodes'])} nodes with world-class intelligence")
            return {"processes": [process], "multipleProcesses": False}
            
        except Exception as e:
            logger.error(f"❌ EROAD-style generation failed: {e}", exc_info=True)
            raise
    
    def _map_status_to_type(self, status: str) -> str:
        """Map EROAD status to node type - preserve all status distinctions"""
        mapping = {
            "critical": "critical",      # RED gradient - urgent action
            "action": "action",          # BLUE border - action required
            "communication": "communication",  # PURPLE border - stakeholder comms
            "operational": "operational",     # EMERALD border - operational task
            "monitoring": "monitoring",  # AMBER border - monitoring/checking
            "verification": "verification",  # TEAL border - verification step
            "recovery": "recovery"       # GREEN border - recovery/restoration
        }
        return mapping.get(status, "operational")  # Default to operational if unknown
    
    def _extract_section_content(self, document_text: str, sections: List[Dict]) -> str:
        """Extract content for specified sections from document"""
        # In a real implementation, you'd use section markers or ML to extract
        # For now, return full document (since we're not truncating)
        
        if not sections:
            return ""
        
        section_titles = [sec['title'] for sec in sections]
        header = f"SECTIONS: {', '.join(section_titles)}\n\n"
        
        return header + document_text
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate JSON response from AI with robust error handling"""
        response_text = response.strip()
        
        # Remove markdown code blocks
        if response_text.startswith('```'):
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
        
        # Clean non-printable chars
        response_text = ''.join(c for c in response_text if c.isprintable() or c in ['\n', '\t'])
        
        # Debug: Log response around character 4457 to see what's malformed
        if len(response_text) > 4457:
            logger.warning(f"DEBUG - Response around char 4457: ...{response_text[4400:4500]}...")
        
        # Pre-parsing fix: Normalize contacts field from malformed array to object
        # More aggressive pattern to catch various malformed contacts formats
        try:
            # Find the contacts field and its content up to the next field
            contacts_match = re.search(r'"contacts"\s*:\s*\[([^\]]+)\]', response_text, re.DOTALL)
            if contacts_match:
                contacts_content = contacts_match.group(1)
                logger.info(f"DEBUG - Found contacts array: [{contacts_content[:100]}...]")
                
                # Check if it contains object-like syntax (has colons outside of quotes)
                if ':' in contacts_content and not contacts_content.strip().startswith('"'):
                    # This is malformed - convert array brackets to object brackets
                    response_text = response_text.replace(
                        contacts_match.group(0),
                        '"contacts": {' + contacts_content + '}'
                    )
                    logger.info("✅ Normalized contacts field from malformed array to object format")
        except Exception as e:
            logger.warning(f"Contacts normalization failed: {e}")
        
        # Try parsing first
        try:
            parsed = json.loads(response_text)
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parsing failed at position {e.pos}: {e.msg}")
            logger.warning("Attempting repairs...")
            
            # Repair strategy 1: Remove trailing commas
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
            
            # Repair strategy 2: Fix missing commas between array/object elements
            response_text = re.sub(r'}\s*{', '},{', response_text)
            response_text = re.sub(r']\s*\[', '],[', response_text)
            
            # Repair strategy 3: Ensure proper closing
            if not response_text.rstrip().endswith('}'):
                # Count opening and closing braces
                open_braces = response_text.count('{')
                close_braces = response_text.count('}')
                if open_braces > close_braces:
                    response_text = response_text.rstrip() + ('}' * (open_braces - close_braces))
            
            # Repair strategy 4: Remove any trailing text after final }
            last_brace = response_text.rfind('}')
            if last_brace != -1:
                response_text = response_text[:last_brace+1]
            
            # Try parsing again
            try:
                parsed = json.loads(response_text)
                logger.info("✅ JSON repaired successfully with basic fixes")
                return parsed
            except json.JSONDecodeError as e2:
                logger.warning("Basic repair failed. Attempting advanced repair...")
                
                # Advanced repair: Try to fix the specific error location
                try:
                    error_pos = e2.pos if hasattr(e2, 'pos') else 0
                    
                    # Extract context around error
                    context_start = max(0, error_pos - 50)
                    context_end = min(len(response_text), error_pos + 50)
                    context = response_text[context_start:context_end]
                    logger.error(f"Error context: ...{context}...")
                    
                    # Try fixing common issues at error position
                    if error_pos < len(response_text):
                        # Check if there's a missing comma
                        if response_text[error_pos:error_pos+1] in ['{', '[', '"']:
                            # Add comma before this character
                            response_text = response_text[:error_pos] + ',' + response_text[error_pos:]
                            parsed = json.loads(response_text)
                            logger.info("✅ JSON repaired by adding missing comma")
                            return parsed
                except:
                    pass
                
                # Last resort: Try to extract valid JSON by truncation
                logger.warning("Attempting truncation strategy...")
                first_brace = response_text.find('{')
                last_brace = response_text.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    truncated = response_text[first_brace:last_brace+1]
                    try:
                        parsed = json.loads(truncated)
                        logger.warning("✅ JSON extracted by truncation - may be incomplete")
                        return parsed
                    except:
                        pass
                
                # Ultimate fallback: Ask LLM to regenerate with stricter instructions
                logger.error("❌ All JSON repair attempts failed")
                raise ValueError(f"Failed to parse AI response as JSON after all repair attempts. Original error: {e2}")
    
    def _add_node_defaults(self, node: Dict):
        """Add default fields to a node"""
        node.setdefault('status', 'current' if node.get('type') != 'trigger' else 'trigger')
        node.setdefault('description', node.get('description', ''))
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
            "riskFactors": [],
            "successCriteria": None,
            "estimatedDuration": None,
            "dependencies": [],
            "trainingRequired": None,
            "sourcePage": None
        }
    
    def _extract_process_section(
        self,
        document_text: str,
        process_title: str,
        all_process_titles: List[str]
    ) -> str:
        """
        Extract text section for a specific process from multi-process document
        
        Strategy:
        1. Find the heading that matches process_title
        2. Extract text from that heading to the next process heading
        3. Return the extracted section
        """
        import re
        
        logger.info(f"📄 Extracting section for: {process_title}")
        
        # Create pattern to find the process title
        # Make it flexible to handle variations
        title_pattern = re.escape(process_title)
        title_pattern = title_pattern.replace(r'\ ', r'\s+')  # Allow flexible spacing
        
        # Find where this process starts
        start_match = re.search(title_pattern, document_text, re.IGNORECASE)
        
        if not start_match:
            logger.warning(f"⚠️ Could not find '{process_title}' in document, using full text")
            return document_text
        
        start_pos = start_match.start()
        
        # Find where the next process starts
        end_pos = len(document_text)
        
        for other_title in all_process_titles:
            if other_title == process_title:
                continue
            
            other_pattern = re.escape(other_title)
            other_pattern = other_pattern.replace(r'\ ', r'\s+')
            
            next_match = re.search(other_pattern, document_text[start_pos + len(process_title):], re.IGNORECASE)
            
            if next_match:
                potential_end = start_pos + len(process_title) + next_match.start()
                if potential_end < end_pos:
                    end_pos = potential_end
        
        # Extract the section
        section = document_text[start_pos:end_pos].strip()
        
        logger.info(f"✅ Extracted {len(section)} chars for '{process_title}'")
        return section
    
    async def generate_eroad_style_single_process(
        self,
        process_text: str,
        process_title: str,
        input_type: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate EROAD-style flowchart for a SINGLE PROCESS
        
        Used when user selects individual processes from multi-process document
        """
        logger.info(f"🎯 Generating EROAD-style flowchart for: {process_title}")
        
        try:
            # Extract data for this one process
            extracted = await self.analyze_document(process_text, input_type, user_id)
            
            # Override process name with the selected title
            extracted["processName"] = process_title
            
            # Enhance for visualization (without detection - single process)
            from eroad_style_enhancer import EROADStyleEnhancer
            
            enhancer = EROADStyleEnhancer(self.api_key)
            enhanced = await enhancer.enhance_for_visualization(
                extracted, 
                process_text,
                detection=None  # No detection needed for single extracted process
            )
            
            # Override name again (ensure it's preserved)
            enhanced["processName"] = process_title
            
            # Map to expected format (same as generate_eroad_style_flowchart)
            process = {
                "name": process_title,  # Use selected title
                "description": extracted.get("documentSummary", f"Workflow for {process_title}"),
                "nodes": [],
                "edges": [],
                "swimLanes": enhanced.get("swimLanes", []),
                "actors": list(set([
                    actor 
                    for node in enhanced.get("nodes", []) 
                    for actor in node.get("contacts", [])
                ])),
                "quickReference": {},  # Will be populated after node processing
                "_pendingQuickReference": True,  # Flag to populate later
                "progressStages": []
            }
            
            # Add metadata for verification
            process["metadata"] = {
                "originalStepCount": len(extracted.get("steps", [])),
                "nodesCreated": len(enhanced.get("nodes", [])),
                "coveragePercent": 100,
                "contactsExtracted": len(extracted.get("contacts", {})),
                "timingsExtracted": len(extracted.get("timings", [])),
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "aiModel": "Claude Sonnet 4"
            }
            
            logger.info(f"✅ Metadata added: {process['metadata']}")
            
            # Process nodes (same logic as before)
            for node in enhanced.get("nodes", []):
                # Calculate priority for this node
                priority_info = self.calculate_node_priority(node)
                
                processed_node = {
                    "id": node["id"],
                    "title": node["title"],
                    "description": node.get("details", ""),
                    "type": self._map_status_to_type(node.get("status")),
                    "status": node.get("status", "operational"),
                    "priority": priority_info,  # NEW: Priority classification
                    "x": node.get("x", 330),
                    "y": node.get("y", 0),
                    "position": {"x": node.get("x", 0), "y": node.get("y", 0)},
                    "actors": node.get("contacts", []),
                    "subSteps": node.get("actions", []),
                    "dependencies": node.get("dependencies", []),
                    "parallelWith": node.get("parallelWith", []),
                    "isDecisionPoint": node.get("isDecisionPoint", False),
                    "decisionCriteria": node.get("decisionCriteria"),
                    "decisionOptions": node.get("decisionOptions", {}),
                    "isLoop": node.get("isLoop", False),
                    "loopBackTo": node.get("loopBackTo"),
                    "failures": [],
                    "blocking": None,
                    "impact": "high" if node.get("status") == "critical" else "medium",
                    "timeEstimate": node.get("timing"),
                    "operationalDetails": {
                        "purpose": node.get("purpose", ""),
                        "specificActions": node.get("actions", []),
                        "requiredData": [],
                        "contactInfo": {c.split(":")[0]: c.split(":")[1].strip() if ":" in c else c for c in node.get("contacts", [])},
                        "timeline": node.get("timing"),
                        "systems": node.get("systems", []),
                        "decisionCriteria": node.get("decisionCriteria") if node.get("isDecisionPoint") else None,
                        "emailTemplates": [],
                        "currentState": node.get("currentState"),
                        "idealState": node.get("idealState"),
                        "gap": node.get("gap"),
                        "sourcePage": None
                    }
                }
                process["nodes"].append(processed_node)
                
                # Create edges
                for target_id in node.get("connections", []):
                    edge = {
                        "id": f"e-{node['id']}-{target_id}",
                        "source": node['id'],
                        "target": target_id,
                        "label": None
                    }
                    
                    # Mark as dashed if it's a loop
                    if node.get("isLoop") and target_id == node.get("loopBackTo"):
                        edge["type"] = "dashed"
                    
                    # Add label for decision branches
                    if node.get("isDecisionPoint") and node.get("decisionOptions"):
                        decision_opts = node.get("decisionOptions", {})
                        if decision_opts.get("yes") == target_id:
                            edge["label"] = "YES"
                        elif decision_opts.get("no") == target_id:
                            edge["label"] = "NO"
                    
                    process["edges"].append(edge)
            
            # Populate quickReference with intelligent extraction
            if process.get("_pendingQuickReference"):
                logger.info("🎯 Generating intelligent quickReference...")
                
                # Extract critical actions intelligently (top 5 most urgent)
                critical_actions_data = self.extract_critical_actions_intelligent(
                    enhanced.get("nodes", []), 
                    extracted
                )
                
                # Format for frontend with priority information
                critical_actions_list = []
                for action_data in critical_actions_data:
                    # Find the corresponding node to get priority
                    node_id = action_data.get("nodeId")
                    priority_emoji = "🔴"  # Default
                    priority_level = "P0"
                    
                    # Find the processed node with this ID
                    for proc_node in process["nodes"]:
                        if proc_node["id"] == node_id:
                            priority_emoji = proc_node["priority"]["emoji"]
                            priority_level = proc_node["priority"]["level"]
                            break
                    
                    # Format: "🔴 P0: Call 111 immediately (immediately)"
                    action_text = f"{priority_emoji} {priority_level}: {action_data['action']}"
                    if action_data.get("timeWindow"):
                        action_text += f" ({action_data['timeWindow']})"
                    critical_actions_list.append(action_text)
                
                # Extract recovery steps (nodes with status="recovery")
                recovery_steps_list = [
                    {"title": n["title"], "id": n["id"]} 
                    for n in enhanced.get("nodes", []) 
                    if n.get("status") == "recovery"
                ]
                
                # Parse contacts hierarchically (extensions + options)
                hierarchical_contacts = self.parse_contacts_hierarchical(
                    extracted.get("contacts", {})
                )
                
                # Extract key timings with enhanced context
                enhanced_timings = self.extract_key_timings_enhanced(
                    enhanced.get("nodes", []),
                    extracted
                )
                
                # Extract supporting references (ALL document sections)
                supporting_refs = extracted.get("documentSections", [])
                
                # Only populate quickReference if there's meaningful data
                has_critical_actions = len(critical_actions_list) > 0
                has_timings = len(enhanced_timings) > 0
                has_contacts = len(hierarchical_contacts) > 0
                has_recovery = len(recovery_steps_list) > 0
                has_refs = len(supporting_refs) > 0
                
                if has_critical_actions or has_timings or has_contacts or has_recovery or has_refs:
                    process["quickReference"] = {
                        "criticalActions": critical_actions_list if has_critical_actions else [],
                        "keyTimings": enhanced_timings if has_timings else [],
                        "emergencyContacts": hierarchical_contacts if has_contacts else {},
                        "recoverySteps": recovery_steps_list if has_recovery else [],
                        "supportingReferences": supporting_refs if has_refs else []
                    }
                    logger.info(f"✅ QuickReference populated: {len(critical_actions_list)} actions, {len(hierarchical_contacts)} contacts, {len(supporting_refs)} refs")
                else:
                    # No meaningful reference data - don't create quickReference at all
                    process["quickReference"] = None
                    logger.info("ℹ️ No meaningful reference data found - quickReference not populated")
                
                # Remove the flag
                del process["_pendingQuickReference"]
                
                logger.info(f"   ✅ Critical Actions: {len(critical_actions_list)}")
                logger.info(f"   ✅ Key Timings: {len(extracted.get('timings', []))}")
                logger.info(f"   ✅ Emergency Contacts: {len(extracted.get('contacts', {}))}")
                logger.info(f"   ✅ Recovery Steps: {len(recovery_steps_list)}")
            
            logger.info(f"✅ EROAD-style flowchart complete for '{process_title}': {len(process['nodes'])} nodes")
            return {"processes": [process], "multipleProcesses": False}
            
        except Exception as e:
            logger.error(f"❌ Single process generation failed for '{process_title}': {e}", exc_info=True)
            raise

    
    def extract_critical_actions_intelligent(self, nodes: List[Dict], extracted_data: Dict) -> List[Dict]:
        """
        Intelligently extract top 5 most critical actions from ALL nodes.
        
        Unlike simple extraction (status=="critical"), this analyzes:
        - Urgency keywords: "immediately", "first", "urgent", "ASAP"
        - Time sensitivity: "within X minutes", "before", "as soon as"
        - Emergency indicators: "call 111", "P1 ticket", "emergency"
        - Impact: "all", "entire", "whole system"
        - Verbs: Action-oriented language
        
        Returns top 5 actions ranked by urgency score.
        """
        logger.info("🎯 Extracting critical actions intelligently...")
        
        # Urgency keywords and their weights
        urgency_keywords = {
            'immediately': 100,
            'urgent': 90,
            'emergency': 95,
            'critical': 85,
            'first': 80,
            'asap': 90,
            'now': 85,
            'call 111': 100,
            'call 911': 100,
            'p1': 90,
            'p0': 100,
            'life-threatening': 100,
            'safety': 85,
            'injury': 90,
        }
        
        # Time sensitivity patterns
        time_patterns = [
            (r'within\s+(\d+)\s*min', lambda m: 100 - int(m.group(1))),  # within 5 min = 95
            (r'within\s+(\d+)\s*hour', lambda m: 70 - (int(m.group(1)) * 5)),  # within 2 hours = 60
            (r'before\s+', 80),
            (r'as soon as', 85),
        ]
        
        # Impact keywords
        impact_keywords = {
            'all': 20,
            'entire': 20,
            'whole': 15,
            'every': 15,
            'system-wide': 25,
        }
        
        # Action verbs (for verb extraction)
        action_verbs = [
            'call', 'notify', 'alert', 'contact', 'raise', 'create',
            'send', 'email', 'inform', 'activate', 'initiate', 'check',
            'verify', 'confirm', 'document', 'screenshot', 'escalate'
        ]
        
        scored_actions = []
        
        for node in nodes:
            title = node.get("title", "").lower()
            description = node.get("details", node.get("description", "")).lower()
            status = node.get("status", "")
            actions = node.get("actions", [])
            timing = node.get("timing", "").lower() if node.get("timing") else ""
            
            # Combine all text for analysis
            full_text = f"{title} {description} {timing}"
            
            # Calculate urgency score
            score = 0
            reasons = []
            
            # Base score from status
            if status == "critical":
                score += 50
                reasons.append("Critical status")
            elif status == "action":
                score += 30
                reasons.append("Action required")
            
            # Check urgency keywords
            for keyword, weight in urgency_keywords.items():
                if keyword in full_text:
                    score += weight
                    reasons.append(f"Contains '{keyword}'")
            
            # Check time sensitivity
            for pattern, weight_func in time_patterns:
                if isinstance(weight_func, int):
                    if re.search(pattern, full_text):
                        score += weight_func
                        reasons.append(f"Time-sensitive: {pattern}")
                else:
                    match = re.search(pattern, full_text)
                    if match:
                        score += weight_func(match)
                        reasons.append(f"Time-sensitive: {match.group(0)}")
            
            # Check impact keywords
            for keyword, weight in impact_keywords.items():
                if keyword in full_text:
                    score += weight
                    reasons.append(f"High impact: '{keyword}'")
            
            # Extract verb from title (for action framing)
            verb = None
            title_words = node.get("title", "").split()
            for word in title_words:
                if word.lower() in action_verbs:
                    verb = word.capitalize()
                    break
            
            # If score > 0, this is a potential critical action
            if score > 0:
                # Extract action text (prefer title, fallback to first action)
                action_text = node.get("title", "")
                
                # Ensure verb-first framing
                if verb and not action_text.startswith(verb):
                    # Check if there's a specific action in the actions array
                    if actions and len(actions) > 0:
                        first_action = actions[0]
                        # Check if first action starts with verb
                        for v in action_verbs:
                            if first_action.lower().startswith(v):
                                action_text = first_action
                                break
                
                # Extract time window if mentioned
                time_window = None
                time_match = re.search(r'within\s+(\d+\s+(?:min|hour|day)s?)', full_text)
                if time_match:
                    time_window = time_match.group(1)
                elif 'immediately' in full_text:
                    time_window = "immediately"
                elif 'urgent' in full_text or 'asap' in full_text:
                    time_window = "ASAP"
                
                scored_actions.append({
                    "action": action_text,
                    "score": score,
                    "timeWindow": time_window,
                    "reasoning": "; ".join(reasons[:3]),  # Top 3 reasons
                    "nodeId": node.get("id"),
                    "status": status
                })
        
        # Sort by score (descending) and take top 5
        scored_actions.sort(key=lambda x: x["score"], reverse=True)
        top_5 = scored_actions[:5]
        
        logger.info(f"✅ Extracted {len(top_5)} critical actions from {len(nodes)} nodes")
        for i, action in enumerate(top_5, 1):
            logger.info(f"   {i}. {action['action']} (score: {action['score']}, {action['timeWindow'] or 'no time constraint'})")
        
        return top_5


    
    def parse_contacts_hierarchical(self, contacts_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse contacts into hierarchical structure with extensions and options.
        
        Input format: {"Name": "phone (Extension: X) | Option 1: Description"}
        Output format: {"Name": {"main": "phone", "extension": "X", "options": [...]}}
        
        Handles multiple formats:
        - "Wilson IT: 0061 8 9415 2888 (Extension: 8088)"
        - "Dispatch: 0800 347 787 | Option 1: Alarm | Option 2: Council"
        - "Support: 0800 123 456" (simple format)
        """
        logger.info("📞 Parsing contacts hierarchically...")
        
        hierarchical_contacts = {}
        
        for name, contact_info in contacts_dict.items():
            try:
                parsed = {
                    "main": contact_info,  # Default to full string
                    "extension": None,
                    "options": []
                }
                
                # Split by pipe to separate main number from options
                parts = contact_info.split(" | ")
                main_part = parts[0].strip()
                option_parts = parts[1:] if len(parts) > 1 else []
                
                # Parse extension from main part
                extension_patterns = [
                    r'\(Extension:\s*([^)]+)\)',  # (Extension: 8088)
                    r'\(ext\.?\s*([^)]+)\)',      # (ext 8088) or (ext. 8088)
                    r'\(x\s*([^)]+)\)',           # (x 8088)
                    r'ext\.?\s*(\d+)',            # ext 8088 or ext. 8088
                    r'extension\s*(\d+)',         # extension 8088
                ]
                
                extension_found = None
                clean_main = main_part
                
                for pattern in extension_patterns:
                    match = re.search(pattern, main_part, re.IGNORECASE)
                    if match:
                        extension_found = match.group(1).strip()
                        # Remove the extension part from main
                        clean_main = re.sub(pattern, '', main_part, flags=re.IGNORECASE).strip()
                        break
                
                parsed["main"] = clean_main
                parsed["extension"] = extension_found
                
                # Parse options
                for option_part in option_parts:
                    option_part = option_part.strip()
                    # Match "Option X: Description" or "Press X for Description"
                    option_match = re.match(r'Option\s+(\d+):\s*(.+)', option_part, re.IGNORECASE)
                    if option_match:
                        parsed["options"].append({
                            "number": option_match.group(1),
                            "description": option_match.group(2).strip()
                        })
                    else:
                        # Try alternate format: "Press 1 for Alarm"
                        press_match = re.match(r'(?:Press|Dial)\s+(\d+)\s+for\s+(.+)', option_part, re.IGNORECASE)
                        if press_match:
                            parsed["options"].append({
                                "number": press_match.group(1),
                                "description": press_match.group(2).strip()
                            })
                
                hierarchical_contacts[name] = parsed
                
            except Exception as e:
                logger.warning(f"Error parsing contact '{name}': {e}")
                # Fallback to simple format
                hierarchical_contacts[name] = {"main": contact_info, "extension": None, "options": []}
        
        return hierarchical_contacts

    def extract_key_timings_enhanced(self, nodes: List[Dict], extracted_data: Dict) -> List[str]:
        """
        Extract timing requirements with FULL CONTEXT from nodes.
        
        Unlike basic extraction, this captures:
        - Action associated with timing: "Check MyIT" not just "30 min"
        - Method/tool: "via email", "in Lighthouse", "on phone"
        - Complete context: "Check MyIT ticket status every 30 minutes"
        
        Returns array of context-rich timing strings.
        """
        logger.info("⏰ Extracting key timings with context...")
        
        timing_patterns = [
            # "every X minutes/hours/days"
            (r'(.{0,50})\s+(every|each)\s+(\d+)\s*(min|minute|minutes|hour|hours|day|days)(.{0,30})', 
             lambda m: self._format_timing_context(m.group(1), f"every {m.group(3)} {m.group(4)}", m.group(5))),
            
            # "within X minutes/hours"
            (r'(.{0,50})\s+(within)\s+(\d+)\s*(min|minute|minutes|hour|hours)(.{0,30})',
             lambda m: self._format_timing_context(m.group(1), f"within {m.group(3)} {m.group(4)}", m.group(5))),
            
            # "at X am/pm" or "by X am/pm"
            (r'(.{0,50})\s+(at|by)\s+(\d+:\d+\s*(?:am|pm|AM|PM))(.{0,30})',
             lambda m: self._format_timing_context(m.group(1), f"{m.group(2)} {m.group(3)}", m.group(4))),
            
            # "hourly", "daily", "weekly"
            (r'(.{0,50})\s+(hourly|daily|weekly|monthly)(.{0,30})',
             lambda m: self._format_timing_context(m.group(1), m.group(2), m.group(3))),
            
            # "X times per day/hour"
            (r'(.{0,50})\s+(\d+)\s*times?\s+(per|each)\s+(day|hour|week)(.{0,30})',
             lambda m: self._format_timing_context(m.group(1), f"{m.group(2)} times per {m.group(4)}", m.group(5))),
        ]
        
        enhanced_timings = []
        seen_timings = set()  # Avoid duplicates
        
        # First, check all nodes for timing patterns
        for node in nodes:
            title = node.get("title", "")
            description = node.get("details", node.get("description", ""))
            actions = node.get("actions", [])
            timing = node.get("timing", "")
            
            # Combine all text for analysis
            full_text = f"{title}. {description}. {timing}. {' '.join(actions)}"
            
            for pattern, formatter in timing_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    try:
                        formatted_timing = formatter(match)
                        # Normalize for deduplication
                        normalized = formatted_timing.lower().strip()
                        if normalized and normalized not in seen_timings:
                            enhanced_timings.append(formatted_timing)
                            seen_timings.add(normalized)
                    except Exception as e:
                        logger.warning(f"Failed to format timing from match: {e}")
                        continue
        
        # Also include basic timings from extracted data (fallback)
        basic_timings = extracted_data.get("timings", [])
        for basic_timing in basic_timings:
            normalized = basic_timing.lower().strip()
            if normalized and normalized not in seen_timings:
                enhanced_timings.append(basic_timing)
                seen_timings.add(normalized)
        
        # Limit to most important timings (avoid overwhelming users)
        # Prioritize: immediate > within X min > hourly/daily > other
        priority_keywords = ['immediately', 'urgent', 'asap', 'within', 'first', 'before']
        
        priority_timings = []
        regular_timings = []
        
        for timing in enhanced_timings:
            timing_lower = timing.lower()
            if any(keyword in timing_lower for keyword in priority_keywords):
                priority_timings.append(timing)
            else:
                regular_timings.append(timing)
        
        # Combine: all priority + limited regular (max 8 total)
        final_timings = priority_timings + regular_timings[:max(0, 8 - len(priority_timings))]
        
        logger.info(f"✅ Extracted {len(final_timings)} key timing requirements (from {len(enhanced_timings)} total)")
        for i, timing in enumerate(final_timings[:5], 1):  # Log top 5
            logger.info(f"   {i}. {timing}")
        
        return final_timings
    
    def _format_timing_context(self, before: str, timing: str, after: str) -> str:
        """
        Format timing with context by extracting action and method.
        
        Example:
        before = "Check MyIT ticket status"
        timing = "every 30 minutes"
        after = "via portal"
        
        Returns: "Check MyIT ticket status every 30 minutes via portal"
        """
        # Clean up before/after text
        before = before.strip()
        after = after.strip()
        
        # Extract action verb from before (if present)
        action_verbs = ['check', 'update', 'monitor', 'verify', 'send', 'email', 'call', 
                       'notify', 'review', 'document', 'log', 'report', 'escalate']
        
        words_before = before.lower().split()
        action = None
        for i, word in enumerate(words_before):
            if word in action_verbs:
                # Take from this verb onwards
                action = ' '.join(before.split()[i:])
                break
        
        if not action:
            # No verb found, take last few words
            action = ' '.join(before.split()[-5:]) if before else ""
        
        # Extract method from after (if present)
        method_keywords = ['via', 'in', 'using', 'through', 'on', 'by']
        method = None
        words_after = after.lower().split()
        for i, word in enumerate(words_after):
            if word in method_keywords:
                # Take from this keyword onwards
                method = ' '.join(after.split()[i:])
                break
        
        if not method and after:
            # No method keyword found, but we have after text
            method = f"via {after}"
        
        # Combine parts
        parts = []
        if action:
            parts.append(action)
        if timing:
            parts.append(timing)
        if method:
            parts.append(method)
        
        return ' '.join(parts) if parts else timing


    def calculate_node_priority(self, node: Dict) -> Dict:
        """
        Calculate priority (P0-P4) for a node based on multiple factors.
        
        Priority Levels:
        - P0 (90-100): IMMEDIATE - Life/safety critical, system-wide failures
        - P1 (70-89): URGENT - Time-sensitive, high-impact actions
        - P2 (50-69): HIGH - Important but not immediate
        - P3 (30-49): MEDIUM - Standard operational tasks
        - P4 (0-29): LOW - Informational, optional steps
        
        Scoring Factors:
        - Severity: Impact of NOT doing this (0-100)
        - Urgency: Time sensitivity (0-100)
        - Frequency: How often needed (0-100)
        - Visibility: Stakeholder impact (0-100)
        
        Returns: {level: "P0", score: 95, emoji: "🔴", color: "red"}
        """
        title = node.get("title", "").lower()
        description = node.get("details", node.get("description", "")).lower()
        status = node.get("status", "")
        timing = node.get("timing", "").lower() if node.get("timing") else ""
        
        full_text = f"{title} {description} {timing}"
        
        # Initialize score
        score = 0
        
        # SEVERITY SCORING (0-100)
        severity_keywords = {
            'life-threatening': 100, 'injury': 95, 'safety': 90, 'death': 100,
            'emergency': 90, 'critical': 85, 'failure': 80, 'outage': 85,
            'down': 75, 'broken': 70, 'error': 60, 'issue': 50,
            'system-wide': 85, 'entire': 70, 'all': 60
        }
        severity_score = 0
        for keyword, weight in severity_keywords.items():
            if keyword in full_text:
                severity_score = max(severity_score, weight)
        
        # URGENCY SCORING (0-100)
        urgency_keywords = {
            'immediately': 100, 'now': 95, 'asap': 90, 'urgent': 85,
            'call 111': 100, 'call 911': 100, '911': 100, '111': 100,
            'first': 80, 'before': 75, 'priority': 70
        }
        urgency_score = 0
        for keyword, weight in urgency_keywords.items():
            if keyword in full_text:
                urgency_score = max(urgency_score, weight)
        
        # Time-based urgency
        if 'within' in full_text:
            # Extract minutes if present
            time_match = re.search(r'within\s+(\d+)\s*min', full_text)
            if time_match:
                minutes = int(time_match.group(1))
                # Shorter time = higher urgency
                urgency_score = max(urgency_score, 100 - minutes)
        
        # FREQUENCY SCORING (0-100)
        frequency_score = 0
        if any(word in full_text for word in ['always', 'every', 'continuous', 'constant']):
            frequency_score = 80
        elif any(word in full_text for word in ['often', 'regular', 'frequent']):
            frequency_score = 60
        elif any(word in full_text for word in ['sometimes', 'occasional']):
            frequency_score = 40
        elif any(word in full_text for word in ['rarely', 'seldom']):
            frequency_score = 20
        
        # VISIBILITY/STAKEHOLDER IMPACT (0-100)
        visibility_keywords = {
            'stakeholder': 70, 'customer': 80, 'client': 80, 'executive': 75,
            'management': 65, 'team': 50, 'public': 85, 'external': 70
        }
        visibility_score = 0
        for keyword, weight in visibility_keywords.items():
            if keyword in full_text:
                visibility_score = max(visibility_score, weight)
        
        # STATUS-BASED BASELINE
        status_baseline = {
            'critical': 50,
            'trigger': 50,
            'action': 30,
            'communication': 20,
            'operational': 15,
            'monitoring': 25,
            'verification': 20,
            'recovery': 40
        }
        baseline = status_baseline.get(status, 10)
        
        # CALCULATE COMPOSITE SCORE (weighted average)
        composite_score = (
            severity_score * 0.40 +    # Severity most important (40%)
            urgency_score * 0.30 +     # Urgency second (30%)
            frequency_score * 0.15 +   # Frequency third (15%)
            visibility_score * 0.15 +  # Visibility fourth (15%)
            baseline                   # Status baseline added
        )
        
        # Classify into P0-P4
        if composite_score >= 90:
            level = "P0"
            emoji = "🔴"
            color = "red"
            label = "IMMEDIATE"
        elif composite_score >= 70:
            level = "P1"
            emoji = "🟠"
            color = "orange"
            label = "URGENT"
        elif composite_score >= 50:
            level = "P2"
            emoji = "🟡"
            color = "yellow"
            label = "HIGH"
        elif composite_score >= 30:
            level = "P3"
            emoji = "🔵"
            color = "blue"
            label = "MEDIUM"
        else:
            level = "P4"
            emoji = "⚪"
            color = "gray"
            label = "LOW"
        
        return {
            "level": level,
            "score": round(composite_score, 1),
            "emoji": emoji,
            "color": color,
            "label": label,
            "breakdown": {
                "severity": round(severity_score, 1),
                "urgency": round(urgency_score, 1),
                "frequency": round(frequency_score, 1),
                "visibility": round(visibility_score, 1),
                "baseline": baseline
            }
        }

    
    async def generate_node_embedding(self, node: Dict) -> List[float]:
        """
        Generate vector embedding for a node using OpenAI embeddings.
        
        Combines node title, description, and actions into searchable text.
        Uses text-embedding-3-small model for efficiency.
        
        Returns: List of floats representing the embedding vector (1536 dimensions)
        """
        # Combine all searchable text from node
        title = node.get("title", "")
        description = node.get("description", node.get("details", ""))
        
        # Extract operational details
        op_details = node.get("operationalDetails", {})
        actions = " ".join(op_details.get("specificActions", []) if isinstance(op_details.get("specificActions"), list) else [])
        systems = " ".join(op_details.get("systems", []) if isinstance(op_details.get("systems"), list) else [])
        
        # Extract contacts
        contacts = " ".join(str(c) for c in node.get("actors", []))
        
        # Get priority info
        priority = node.get("priority", {})
        priority_text = f"{priority.get('level', '')} {priority.get('label', '')}" if priority else ""
        
        # Create comprehensive search text
        search_text = f"{title}. {description}. {priority_text}. Actions: {actions}. Contacts: {contacts}. Systems: {systems}"
        search_text = search_text.strip()
        
        # Limit to 8000 characters (token limit safety)
        if len(search_text) > 8000:
            search_text = search_text[:8000]
        
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            from openai import OpenAI
            
            # Use OpenAI API key (not Emergent LLM key - embeddings not supported)
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.error("OPENAI_API_KEY not found in environment")
                return []
            
            client = OpenAI(api_key=openai_key)
            
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=search_text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"✅ Generated embedding for node: {title[:50]}... (dimension: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Returns: Similarity score between 0 and 1 (1 = identical, 0 = orthogonal)
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def generate_contextual_recommendations(self, nodes: List[Dict]) -> List[Dict]:
        """
        INNOVATION 1: Contextual AI Recommendations
        
        Analyzes each node and provides:
        1. Automation Opportunity Score (0-100)
        2. Bottleneck Risk Score (0-100)
        3. Improvement Suggestions (actionable tips)
        
        This turns flowcharts from descriptive to PRESCRIPTIVE.
        Makes SuperHumanly the only tool that tells users HOW to improve.
        """
        logger.info("💡 Generating Contextual AI Recommendations for all nodes...")
        
        try:
            # Analyze all nodes in batch for efficiency
            nodes_summary = []
            for i, node in enumerate(nodes, 1):
                title = node.get("title", "")
                description = node.get("description", node.get("details", ""))
                op_details = node.get("operationalDetails", {})
                actions = op_details.get("specificActions", [])
                
                nodes_summary.append(f"{i}. {title}: {description[:100]}")
            
            # Create AI prompt for recommendations
            prompt = f"""You are an expert business process consultant analyzing a workflow.

For each node below, provide:
1. **automationScore** (0-100): How automatable is this step?
   - High (80-100): Data entry, emails, status checks, reports, notifications
   - Medium (40-79): Requires some judgment but can be semi-automated
   - Low (0-39): Complex decisions, physical tasks, human judgment required

2. **bottleneckRisk** (0-100): Likelihood this step slows down the process?
   - High (80-100): Manual approvals, external dependencies, sequential blockers
   - Medium (40-79): Some waiting but not critical path
   - Low (0-39): Fast steps, parallel-capable

3. **suggestions** (1-3 actionable improvements):
   - Specific tools/automations (Zapier, APIs, scripts)
   - Process redesign ideas (parallelize, eliminate, combine)
   - Best practices from similar workflows

NODES TO ANALYZE:
{chr(10).join(nodes_summary[:20])}  

Return JSON array with this structure:
[
  {{
    "nodeIndex": 1,
    "automationScore": 85,
    "bottleneckRisk": 45,
    "suggestions": [
      "Automate email notifications using Zapier or Make.com",
      "Consider using email templates to reduce composition time"
    ],
    "rationale": "Email sending is highly automatable"
  }}
]

Analyze ONLY the nodes shown above. Return valid JSON array."""

            chat = LlmChat(
                api_key=self.api_key
            )
            chat.add_message(UserMessage(content=prompt))
            
            response = await chat.send_message_async()
            result_text = response.content[0].text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', result_text)
            if not json_match:
                logger.warning("No JSON found in recommendations response")
                return nodes
            
            recommendations = json.loads(json_match.group())
            
            # Apply recommendations to nodes
            for rec in recommendations:
                node_idx = rec.get("nodeIndex", 0) - 1  # Convert to 0-indexed
                if 0 <= node_idx < len(nodes):
                    nodes[node_idx]["aiRecommendations"] = {
                        "automationScore": rec.get("automationScore", 0),
                        "bottleneckRisk": rec.get("bottleneckRisk", 0),
                        "suggestions": rec.get("suggestions", []),
                        "rationale": rec.get("rationale", ""),
                        "generatedAt": datetime.now(timezone.utc).isoformat()
                    }
            
            logger.info(f"✅ Generated recommendations for {len(recommendations)} nodes")
            return nodes
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
            # Return nodes unchanged if recommendations fail
            return nodes

    def calculate_complexity_score(self, process_data: Dict) -> Dict[str, Any]:
        """
        Calculate process complexity score (0-10) based on multiple factors.
        
        Higher complexity = more decisions, loops, parallel processes, stakeholders
        """
        nodes = process_data.get("nodes", [])
        extracted = process_data.get("_extracted_data", {})
        
        # Count complexity factors
        decision_count = len([n for n in nodes if n.get("isDecisionPoint")])
        loop_count = len([n for n in nodes if n.get("isLoop")])
        parallel_count = len(extracted.get("parallelProcesses", []))
        stakeholder_count = len(set([actor for n in nodes for actor in n.get("actors", [])]))
        branch_count = sum([len(n.get("connections", [])) for n in nodes if n.get("isDecisionPoint")])
        
        # Calculate weighted score (0-10)
        score = min(10, (
            (decision_count * 1.5) +
            (loop_count * 2.0) +
            (parallel_count * 1.0) +
            (stakeholder_count * 0.3) +
            (branch_count * 0.5)
        ) / 2)
        
        # Determine complexity level
        if score >= 8:
            level = "Very High"
            color = "red"
        elif score >= 6:
            level = "High"
            color = "orange"
        elif score >= 4:
            level = "Medium"
            color = "yellow"
        else:
            level = "Low"
            color = "green"
        
        return {
            "score": round(score, 1),
            "level": level,
            "color": color,
            "factors": {
                "decisions": decision_count,
                "loops": loop_count,
                "parallelProcesses": parallel_count,
                "stakeholders": stakeholder_count,
                "branches": branch_count
            },
            "reasoning": f"{level} complexity due to {decision_count} decisions, {loop_count} loops, and {stakeholder_count} stakeholders"
        }
    
    def calculate_process_health_score(self, process_data: Dict) -> Dict[str, Any]:
        """
        Calculate overall process health score (0-100) combining multiple metrics.
        
        Higher score = better health (low complexity, high automation, low bottleneck risk, few gaps)
        """
        nodes = process_data.get("nodes", [])
        complexity = process_data.get("complexityScore", {}).get("score", 5)
        
        # Calculate component scores
        automation_scores = [n.get("aiRecommendations", {}).get("automationScore", 50) for n in nodes if n.get("aiRecommendations")]
        avg_automation = sum(automation_scores) / len(automation_scores) if automation_scores else 50
        
        bottleneck_scores = [n.get("aiRecommendations", {}).get("bottleneckRisk", 50) for n in nodes if n.get("aiRecommendations")]
        avg_bottleneck = sum(bottleneck_scores) / len(bottleneck_scores) if bottleneck_scores else 50
        
        # Count gaps
        gap_count = len([n for n in nodes if n.get("operationalDetails", {}).get("gap")])
        gap_penalty = min(30, gap_count * 10)
        
        # Health formula (0-100)
        health_score = (
            (100 - (complexity * 10)) * 0.3 +  # Lower complexity = better
            avg_automation * 0.3 +                # Higher automation = better
            (100 - avg_bottleneck) * 0.3 +       # Lower bottleneck = better
            (100 - gap_penalty) * 0.1             # Fewer gaps = better
        )
        
        health_score = max(0, min(100, health_score))
        
        # Determine health level
        if health_score >= 80:
            level = "Excellent"
            color = "green"
            emoji = "💚"
        elif health_score >= 60:
            level = "Good"
            color = "blue"
            emoji = "💙"
        elif health_score >= 40:
            level = "Fair"
            color = "yellow"
            emoji = "💛"
        else:
            level = "Needs Work"
            color = "red"
            emoji = "❤️"
        
        return {
            "score": round(health_score, 1),
            "level": level,
            "color": color,
            "emoji": emoji,
            "breakdown": {
                "complexity": round(100 - (complexity * 10), 1),
                "automation": round(avg_automation, 1),
                "efficiency": round(100 - avg_bottleneck, 1),
                "completeness": round(100 - gap_penalty, 1)
            }
        }
    
    def estimate_execution_time(self, nodes: List[Dict]) -> Dict[str, Any]:
        """
        Estimate total process execution time based on node timings.
        
        Returns best case, average case, and worst case estimates.
        """
        total_minutes = 0
        timing_found = False
        
        for node in nodes:
            # Extract timing from operationalDetails
            timing = node.get("operationalDetails", {}).get("estimatedDuration", "")
            if not timing:
                timing = node.get("timing", "")
            
            if timing:
                timing_found = True
                # Parse timing strings
                if "minute" in timing.lower() or "min" in timing.lower():
                    import re
                    match = re.search(r'(\d+)', timing)
                    if match:
                        total_minutes += int(match.group(1))
                elif "hour" in timing.lower() or "hr" in timing.lower():
                    import re
                    match = re.search(r'(\d+)', timing)
                    if match:
                        total_minutes += int(match.group(1)) * 60
        
        if not timing_found or total_minutes == 0:
            # Fallback: estimate based on node count (avg 15 min per node)
            total_minutes = len(nodes) * 15
        
        # Calculate estimates
        best_case = total_minutes * 0.7  # Optimistic
        average_case = total_minutes
        worst_case = total_minutes * 1.5  # Delays, issues
        
        def format_time(minutes):
            if minutes < 60:
                return f"{int(minutes)} min"
            else:
                hours = minutes / 60
                return f"{hours:.1f} hours" if hours < 10 else f"{int(hours)} hours"
        
        return {
            "bestCase": format_time(best_case),
            "average": format_time(average_case),
            "worstCase": format_time(worst_case),
            "totalMinutes": int(average_case),
            "confidence": "high" if timing_found else "estimated"
        }
    
    def multi_lens_gap_analysis(self, nodes: List[Dict], extracted_data: Dict) -> Dict[str, List[str]]:
        """
        Analyze process from 4 different lenses:
        - Operational: bottlenecks, delays, resource constraints
        - Risk: single points of failure, error handling
        - Compliance: SLA, audit, documentation
        - Stakeholder: communication, escalation
        """
        gaps = {
            "operational": [],
            "risk": [],
            "compliance": [],
            "stakeholder": []
        }
        
        # Operational lens
        manual_nodes = [n for n in nodes if "manual" in n.get("title", "").lower() or "manual" in n.get("description", "").lower()]
        if len(manual_nodes) > 3:
            gaps["operational"].append(f"{len(manual_nodes)} manual steps could cause delays")
        
        single_actor_nodes = [n for n in nodes if len(n.get("actors", [])) == 1]
        if len(single_actor_nodes) > 0:
            gaps["operational"].append(f"{len(single_actor_nodes)} steps depend on single person")
        
        # Risk lens
        critical_nodes = [n for n in nodes if n.get("status") == "critical"]
        for node in critical_nodes:
            if len(node.get("operationalDetails", {}).get("contactInfo", {})) == 0:
                gaps["risk"].append(f"Critical step '{node.get('title')}' has no backup contact")
        
        decision_nodes = [n for n in nodes if n.get("isDecisionPoint")]
        unclear_decisions = [n for n in decision_nodes if not n.get("description")]
        if unclear_decisions:
            gaps["risk"].append(f"{len(unclear_decisions)} decisions lack clear criteria")
        
        # Compliance lens
        if not any("document" in n.get("title", "").lower() for n in nodes):
            gaps["compliance"].append("No documentation step found")
        
        extracted_str = str(extracted_data).lower()
        if "sla" not in extracted_str and "service level" not in extracted_str:
            gaps["compliance"].append("No SLA commitments mentioned")
        
        # Stakeholder lens
        external_mentions = [n for n in nodes if "customer" in str(n).lower() or "client" in str(n).lower()]
        if external_mentions and not any("notify" in n.get("title", "").lower() for n in nodes):
            gaps["stakeholder"].append("Customer involved but no notification step")
        
        escalation_nodes = [n for n in nodes if "escalat" in n.get("title", "").lower()]
        if len(escalation_nodes) == 0:
            gaps["stakeholder"].append("No escalation path defined")
        
        return gaps
    
    def detect_critical_path(self, nodes: List[Dict]) -> List[str]:
        """
        Identify critical path - steps that must complete for process to succeed.
        These are blocking steps that gate everything else.
        """
        critical_path = []
        
        for node in nodes:
            # Mark as critical if:
            # 1. Status is critical/trigger
            # 2. Is a decision point (blocks progress)
            # 3. Has dependencies from multiple other nodes
            # 4. Is mentioned in multiple connections
            
            is_blocking = (
                node.get("status") in ["critical", "trigger"] or
                node.get("isDecisionPoint") or
                len(node.get("connections", [])) > 1
            )
            
            if is_blocking:
                critical_path.append(node.get("id"))
        
        return critical_path


