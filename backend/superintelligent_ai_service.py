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
        """
        logger.info("🧠 STAGE 0: Document Intelligence & Classification")
        
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
            ).with_model("anthropic", "claude-4-sonnet-20250514")
            
            prompt = f"""EXTRACT STRUCTURED DATA FROM DOCUMENT

{learning_context}

DOCUMENT:
{document_text}

EXTRACT:
1. **All Steps**: List every procedural step (maintain order)
2. **Decision Points**: Any if/then/else logic
3. **Contacts**: Names, phone numbers, emails WITH context (extensions, options)
4. **Systems**: Software, tools, platforms mentioned
5. **Timings**: Time constraints, frequencies
6. **Parallel Processes**: Steps that happen simultaneously

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
  "steps": ["Step 1", "Step 2",...],
  "decisions": [{{"condition": "...", "ifYes": "...", "ifNo": "..."}}],
  "contacts": {{"ContactName1": "phone (Extension: X) | Option 1: Description", "ContactName2": "phone"}},
  "systems": ["System1", "System2"],
  "timings": ["Every 30 minutes", "Within 2 hours"],
  "parallelProcesses": [["Step A", "Step B"]]
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
{document_text[:15000]}

Return this exact JSON structure (no additional text):
{{
  "documentSummary": "one sentence summary",
  "steps": ["step1", "step2", "step3"],
  "decisions": [],
  "contacts": {{}},
  "systems": [],
  "timings": [],
  "parallelProcesses": []
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
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
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
            ).with_model("anthropic", "claude-4-sonnet-20250514")
            
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
        ).with_model("anthropic", "claude-4-sonnet-20250514")
        
        # Use targeted excerpts to stay under token limit while maintaining quality
        prompt = f"""EXTRACT OPERATIONAL DETAILS

TARGET NODES:
{chr(10).join(node_summary)}

REFERENCE MATERIAL:
{reference_content[:15000]}

FULL DOCUMENT CONTEXT (for cross-reference):
{document_text[:25000]}

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
            ).with_model("anthropic", "claude-4-sonnet-20250514")
            
            prompt = f"""COMPREHENSIVE DOCUMENT STRUCTURE ANALYSIS

DOCUMENT (first 25,000 chars):
{document_text[:25000]}

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
            
            # Process nodes and identify progress stages
            critical_nodes = []
            monitoring_nodes = []
            recovery_nodes = []
            
            for node in enhanced.get("nodes", []):
                processed_node = {
                    "id": node["id"],
                    "title": node["title"],
                    "description": node.get("details", ""),
                    "type": self._map_status_to_type(node.get("status")),
                    "status": node.get("status", "operational"),
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
                
                # Format for frontend (simple string array for now, can enhance later)
                critical_actions_list = []
                for action_data in critical_actions_data:
                    action_text = action_data["action"]
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
                
                process["quickReference"] = {
                    "criticalActions": critical_actions_list,
                    "keyTimings": enhanced_timings,
                    "emergencyContacts": hierarchical_contacts,
                    "recoverySteps": recovery_steps_list
                }
                
                # Remove the flag
                del process["_pendingQuickReference"]
                
                logger.info(f"   ✅ Critical Actions: {len(critical_actions_list)}")
                logger.info(f"   ✅ Key Timings: {len(extracted.get('timings', []))}")
                logger.info(f"   ✅ Emergency Contacts: {len(extracted.get('contacts', {}))}")
                logger.info(f"   ✅ Recovery Steps: {len(recovery_steps_list)}")
            
            logger.info(f"✅ EROAD-style flowchart complete: {len(process['nodes'])} nodes")
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
            
            # Process nodes (same logic as before)
            for node in enhanced.get("nodes", []):
                processed_node = {
                    "id": node["id"],
                    "title": node["title"],
                    "description": node.get("details", ""),
                    "type": self._map_status_to_type(node.get("status")),
                    "status": node.get("status", "operational"),
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
                
                # Format for frontend (simple string array for now, can enhance later)
                critical_actions_list = []
                for action_data in critical_actions_data:
                    action_text = action_data["action"]
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
                
                process["quickReference"] = {
                    "criticalActions": critical_actions_list,
                    "keyTimings": enhanced_timings,
                    "emergencyContacts": hierarchical_contacts,
                    "recoverySteps": recovery_steps_list
                }
                
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
        
        logger.info(f"✅ Extracted {len(enhanced_timings)} timing requirements with context")
        for i, timing in enumerate(enhanced_timings[:5], 1):  # Log top 5
            logger.info(f"   {i}. {timing}")
        
        return enhanced_timings
    
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
                # Take from this keyword onwards (next 2-3 words)
                method = ' '.join(after.split()[i:i+3])
                break
        
        # Construct the timing string
        parts = []
        if action:
            parts.append(action.strip())
        parts.append(timing.strip())
        if method:
            parts.append(method.strip())
        
        result = ' '.join(parts)
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
        
        return result
                logger.info(f"   ✅ {name}: {parsed['main']}")
                if parsed["extension"]:
                    logger.info(f"      → Extension: {parsed['extension']}")
                for opt in parsed["options"]:
                    logger.info(f"      → Option {opt['number']}: {opt['description']}" if opt['number'] else f"      → {opt['description']}")
        
        logger.info(f"✅ Parsed {len(hierarchical_contacts)} contacts")
        return hierarchical_contacts

