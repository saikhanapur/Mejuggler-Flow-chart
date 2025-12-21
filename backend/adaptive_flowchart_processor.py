"""
Adaptive Flowchart Processor

Uses document analysis to apply the RIGHT processing strategy:
- EXTRACT mode: For documents already containing flowcharts
- GENERATE mode: For text-based SOPs that need structuring
- HYBRID mode: For mixed documents

The key insight: AI must ADAPT to the document, not force the document into a template.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from error_handling import ErrorCatalog

logger = logging.getLogger(__name__)


class AdaptiveFlowchartProcessor:
    """
    Processes documents intelligently based on their analyzed structure.
    NO MORE "create 15-25 nodes" - we create EXACTLY what's in the document.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_document(
        self, 
        document_text: str,
        analysis: Dict[str, Any],
        document_name: str = "Document"
    ) -> Dict[str, Any]:
        """
        Process document using the strategy determined by analysis.
        WITH COMPREHENSIVE ERROR HANDLING
        """
        from ai_call_wrapper import AICallError
        from fastapi import HTTPException
        from error_handling import create_error_response
        
        strategy = analysis.get("processingStrategy", "generate")
        estimated_nodes = analysis.get("existingStructure", {}).get("estimatedNodes", 15)
        
        logger.info(f"⚡ Processing with strategy: {strategy}")
        logger.info(f"📊 Expected nodes: ~{estimated_nodes}")
        
        # Truncate if too long
        doc_text = document_text[:50000]
        
        try:
            # Launch THREE parallel calls with ADAPTIVE prompts
            structure_task = self._extract_structure(
                doc_text, document_name, analysis
            )
            content_task = self._extract_content(
                doc_text, document_name, analysis
            )
            references_task = self._extract_references(
                doc_text, document_name
            )
            
            # Wait for all three to complete
            structure, content, references = await asyncio.gather(
                structure_task,
                content_task,
                references_task,
                return_exceptions=True
            )
            
            # Check for AI call failures
            if isinstance(structure, AICallError):
                logger.error(f"❌ Structure extraction failed: {structure}")
                raise HTTPException(
                    status_code=422,
                    detail=create_error_response(
                        structure.error_catalog_item,
                        structure.technical_detail
                    )
                )
            if isinstance(content, AICallError):
                logger.error(f"❌ Content extraction failed: {content}")
                # Content failure is less critical, use fallback
                content = {}
            if isinstance(references, AICallError):
                logger.error(f"❌ References extraction failed: {references}")
                # References failure is less critical, use fallback
                references = {"contacts": [], "templates": []}
            
            # Check for other exceptions
            if isinstance(structure, Exception):
                logger.error(f"❌ Structure extraction error: {structure}", exc_info=True)
                structure = {"nodes": [], "swimLanes": []}
            if isinstance(content, Exception):
                logger.error(f"❌ Content extraction error: {content}", exc_info=True)
                content = {}
            if isinstance(references, Exception):
                logger.error(f"❌ References extraction error: {references}", exc_info=True)
                references = {"contacts": [], "templates": []}
            
            # MERGE the results
            result = self._merge_results(structure, content, references, analysis)
            
            # Validate structure
            result = self._validate_and_fix(result)
            
            # Validate against source document to catch hallucinations
            result = self._validate_against_source(result, doc_text)
            
            # Apply intelligent grouping post-processing
            result = self._apply_intelligent_grouping(result)
            
            logger.info(f"✅ Processing complete: {len(result['nodes'])} nodes (expected ~{estimated_nodes})")
            
            return result
            
        except AICallError as e:
            # AI call errors are already user-friendly
            logger.error(f"❌ AI processing failed: {e}")
            raise HTTPException(
                status_code=422,
                detail=create_error_response(
                    e.error_catalog_item,
                    e.technical_detail
                )
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Unexpected errors
            logger.error(f"❌ Unexpected processing error: {e}", exc_info=True)
            from error_handling import ErrorCatalog
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    ErrorCatalog.UNKNOWN_ERROR,
                    str(e)
                )
            )
    
    async def _extract_structure(
        self, 
        doc_text: str, 
        doc_name: str,
        analysis: Dict[str, Any]
    ) -> Dict:
        """
        Extract flowchart structure with ADAPTIVE prompts based on analysis.
        WITH FEW-SHOT LEARNING and COMPREHENSIVE ERROR HANDLING
        """
        from ai_call_wrapper import AICallWrapper, AICallError
        from few_shot_examples import get_few_shot_examples_text, get_anti_hallucination_rules
        
        strategy = analysis.get("processingStrategy", "generate")
        estimated_nodes = analysis.get("existingStructure", {}).get("estimatedNodes", 15)
        doc_type = analysis.get("documentType", "text_sop")
        fidelity = analysis.get("fidelityRequirement", "medium")
        
        logger.info(f"📊 [Call 1/3] Extracting structure (strategy: {strategy}) with FEW-SHOT LEARNING...")
        
        try:
            # Enhanced system message with anti-hallucination emphasis
            system_message = """You are a precise document-to-flowchart converter. Your ONLY job is to extract EXACTLY what's in the document.

CRITICAL RULES:
- NEVER invent steps not explicitly in the document
- ALWAYS use exact wording from the source
- EVERY node must have a sourceReference to document text
- If unsure, include LESS nodes, not more
- NO "best practice" additions

You will be given examples of perfect extractions. Follow them exactly."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id="adaptive_structure",
                system_message=system_message
            ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=8000)
            
            # Build adaptive prompt based on strategy WITH few-shot examples
            if strategy == "extract":
                instruction = self._build_extract_prompt_with_examples(doc_text, estimated_nodes, doc_type)
            elif strategy == "generate":
                instruction = self._build_generate_prompt_with_examples(doc_text, estimated_nodes)
            else:
                instruction = self._build_hybrid_prompt_with_examples(doc_text, estimated_nodes)
            
            message = UserMessage(text=instruction)
            
            # Use wrapper for error handling
            ai_wrapper = AICallWrapper(self.api_key, timeout_seconds=60)
            response = await ai_wrapper.call_with_timeout(
                chat, message, "Extract Structure (1/3)"
            )
            
            # Parse and validate JSON
            return ai_wrapper.validate_json_response(response, "Extract Structure")
            
        except AICallError:
            # Re-raise AI errors (already user-friendly)
            raise
        except Exception as e:
            logger.error(f"❌ Structure extraction failed: {e}", exc_info=True)
            raise AICallError(
                ErrorCatalog.AI_INVALID_RESPONSE,
                f"Structure extraction error: {str(e)}"
            )
    
    def _build_extract_prompt(self, doc_text: str, estimated_nodes: int, doc_type: str) -> str:
        """
        Build prompt for EXTRACTION mode (document already has flowchart).
        """
        return f"""CRITICAL TASK: This document describes an EXISTING flowchart. Your job is to EXTRACT it EXACTLY as described.

DOCUMENT:
{doc_text[:100000]}

TASK: Extract the EXACT flowchart structure described in this document.

RULES (CRITICAL - THIS IS EMERGENCY SERVICES):
1. This document describes approximately {estimated_nodes} nodes. Extract EXACTLY what's described.
2. DO NOT add steps that aren't explicitly mentioned.
3. DO NOT skip any steps that ARE mentioned.
4. DO NOT "improve" or "reorganize" - preserve EXACTLY.
5. Look for explicit node descriptions like "Step 1:", "Decision Node:", "Action Node:", diamond shapes, rectangle shapes, etc.

DECISION NODE IDENTIFICATION:
- Any node with "?" in the title is a DECISION (e.g., "User Contacted?")
- Any node labeled "Decision Node" or "Diamond shape" is a DECISION
- Any node with YES/NO branches is a DECISION
- Set isDecisionPoint: true and provide decisionOptions

ACTION NODE IDENTIFICATION:
- Nodes labeled "Action Node", "Process Node", or "Rectangle shape" are ACTIONS
- Nodes with imperative verbs ("Call", "Dispatch", "Contact") are ACTIONS
- Start and End nodes (Ovals) are ACTIONS
- Set isDecisionPoint: false

NODE CONSOLIDATION:
- If "Start" and first action are essentially the same (e.g., "Panic Triggered" → "Call User"), keep them separate only if both are explicitly described as distinct nodes
- Do NOT create intermediate nodes between clearly connected steps

For EACH node mentioned, extract:
- The EXACT title/name given in the document
- Correct type based on shape or context (decision vs action)
- Exact connections as described
- Roles if mentioned

Return JSON:
{{
  "processName": "Exact process name from document",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "EXACT title from document",
      "description": "Brief description if provided",
      "status": "critical|action|operational|communication",
      "swimLane": "Role if mentioned, otherwise 'Operations'",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question for decision nodes",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Operations", "color": "#3B82F6"}}
  ]
}}

Target: EXACTLY {estimated_nodes} nodes (±1 acceptable).
PERFECT FIDELITY to source. NO hallucinations.
Return ONLY JSON."""
    
    def _build_generate_prompt(self, doc_text: str, estimated_nodes: int) -> str:
        """
        Build prompt for GENERATION mode.
        Simple, clear instructions for accurate extraction.
        """
        
        return f"""Extract a flowchart from this SOP document. Be accurate and use exact terminology from the document.

DOCUMENT:
{doc_text[:100000]}

INSTRUCTIONS:

1. READ the document carefully to understand the process
2. EXTRACT steps in the exact order they appear
3. IDENTIFY decision points (questions, if-then statements, YES/NO branches)
4. USE exact wording from the document for node titles
5. CREATE connections that match the document's flow

DECISION POINTS:
- Look for: "Check if...", "Ask if...", "Is X?", "If X then Y else Z"
- Mark as: isDecisionPoint: true
- Define: decisionOptions with "yes" and "no" paths

NODE STRUCTURE:
- Each numbered step (1., 2., 3.) = one node
- Each clear action = one node  
- Each decision/question = one decision node
- Group only if document explicitly groups steps together

CRITICAL RULES:
✅ Use exact terminology from document
✅ Follow document's sequence
✅ Mark all decisions with isDecisionPoint: true
✅ Define both YES and NO paths for decisions
❌ Don't invent steps not in document
❌ Don't add "best practices" not mentioned
❌ Don't rename actions - use document's wording

Return JSON:
{{
  "processName": "Process name from document",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "Exact action/question from document",
      "description": "What happens in this step",
      "status": "critical|action|operational|communication",
      "swimLane": "Actor/Role",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question if decision",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"],
      "subSteps": ["Detail 1", "Detail 2"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Role Name", "color": "#3B82F6"}}
  ]
}}

Expected nodes: {max(5, estimated_nodes-2)} to {estimated_nodes+2}
Return ONLY valid JSON."""
    
    def _build_hybrid_prompt(self, doc_text: str, estimated_nodes: int) -> str:
        """
        Build prompt for HYBRID mode (mixed structure).
        """
        return f"""TASK: Process this document which has SOME flowchart structure but needs organization.

DOCUMENT:
{doc_text[:100000]}

TASK: Extract existing structure and intelligently organize any unstructured parts.

RULES:
1. Where flowchart structure is clearly described, EXTRACT it exactly
2. Where text is unstructured, intelligently organize it
3. Estimated complexity: ~{estimated_nodes} nodes
4. Maintain fidelity to source material
5. Do not over-complicate or under-simplify

Return JSON:
{{
  "processName": "Process name",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "Node title",
      "description": "Description",
      "status": "critical|action|operational|communication",
      "swimLane": "Role",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"]
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Lane Name", "color": "#3B82F6"}}
  ]
}}

Expected range: {max(3, estimated_nodes-3)} to {estimated_nodes+3} nodes.
Return ONLY JSON."""
    
    def _build_generate_prompt_with_examples(self, doc_text: str, estimated_nodes: int) -> str:
        """
        Build prompt for GENERATION mode with few-shot learning.
        This is the CORE method for accurate flowchart extraction.
        """
        from few_shot_examples import get_few_shot_examples_text, get_anti_hallucination_rules
        
        return f"""{get_anti_hallucination_rules()}

=== LEARN FROM THESE EXAMPLES ===
{get_few_shot_examples_text()}

=== NOW PROCESS THIS DOCUMENT ===

DOCUMENT TO PROCESS:
\"\"\"
{doc_text[:100000]}
\"\"\"

YOUR TASK:
Extract a flowchart from the document above. Follow the EXACT same pattern as the examples.

CRITICAL REQUIREMENTS:
1. Each node MUST have a "sourceReference" field showing which part of the document it came from
2. Use EXACT wording from the document for node titles
3. Only create decision nodes where document explicitly shows YES/NO or IF/THEN
4. Expected node count: approximately {estimated_nodes} nodes (based on document structure)

VALIDATION BEFORE RETURNING:
- Count your nodes. Do you have roughly {estimated_nodes}? If wildly different, re-check.
- For EACH node, can you quote the source text? If not, delete that node.
- Did you invent any "improvement" steps? Delete them.

Return ONLY valid JSON in this exact format:
{{
  "processName": "Process name from document",
  "nodes": [
    {{
      "id": "node-1",
      "type": "process" | "decision",
      "title": "EXACT text from document",
      "description": "Brief description",
      "status": "critical|action|operational|communication",
      "swimLane": "Role mentioned in document",
      "connections": ["node-2"],
      "isDecisionPoint": true/false,
      "decisionCriteria": "Question if decision node",
      "decisionOptions": {{"yes": "node-id", "no": "node-id"}},
      "actors": ["Role"],
      "sourceReference": "Step X / Line Y / Quote from document"
    }}
  ],
  "swimLanes": [
    {{"id": "lane-1", "name": "Role Name", "color": "#3B82F6"}}
  ]
}}

Return ONLY JSON, no explanations."""
    
    def _build_extract_prompt_with_examples(self, doc_text: str, estimated_nodes: int, doc_type: str) -> str:
        """
        Build prompt for EXTRACTION mode with few-shot learning.
        For documents that already describe a flowchart structure.
        """
        from few_shot_examples import get_few_shot_examples_text, get_anti_hallucination_rules
        
        return f"""{get_anti_hallucination_rules()}

=== LEARN FROM THESE EXAMPLES ===
{get_few_shot_examples_text()}

=== NOW EXTRACT FROM THIS DOCUMENT ===

This document already describes a flowchart structure. Your job is to EXTRACT it EXACTLY as described.

DOCUMENT:
\"\"\"
{doc_text[:100000]}
\"\"\"

EXTRACTION RULES:
1. This document describes approximately {estimated_nodes} nodes. Extract EXACTLY what's described.
2. Look for explicit node descriptions: "Step 1:", "Node:", "Action:", etc.
3. Preserve EXACT titles as written in the document
4. Map connections exactly as the document describes them
5. Every node MUST have sourceReference showing where it came from

DECISION NODE IDENTIFICATION:
- Nodes with "?" in title → DECISION
- Nodes with YES/NO branches → DECISION
- "Check if..." statements → DECISION

Return ONLY valid JSON in the standard format with sourceReference for each node."""
    
    def _build_hybrid_prompt_with_examples(self, doc_text: str, estimated_nodes: int) -> str:
        """
        Build prompt for HYBRID mode with few-shot learning.
        For documents with mixed structured and unstructured content.
        """
        from few_shot_examples import get_few_shot_examples_text, get_anti_hallucination_rules
        
        return f"""{get_anti_hallucination_rules()}

=== LEARN FROM THESE EXAMPLES ===
{get_few_shot_examples_text()}

=== NOW PROCESS THIS MIXED DOCUMENT ===

This document has SOME flowchart structure but also unstructured text. Extract what's clear, organize what's unclear.

DOCUMENT:
\"\"\"
{doc_text[:100000]}
\"\"\"

RULES:
1. Where structure is clear (numbered steps, explicit nodes), EXTRACT exactly
2. Where text is narrative, identify the key actions and sequence them
3. Estimated complexity: ~{estimated_nodes} nodes
4. Every node MUST have sourceReference to justify its existence
5. If you can't point to source text for a node, don't create it

Return ONLY valid JSON with sourceReference for each node."""

    async def _extract_content(
        self, 
        doc_text: str, 
        doc_name: str,
        analysis: Dict[str, Any]
    ) -> Dict:
        """
        Extract detailed content for each node.
        """
        logger.info("📝 [Call 2/3] Extracting content...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="adaptive_content",
            system_message="Extract detailed content accurately. No hallucination."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=8000)
        
        prompt = f"""Extract ACTIONABLE, DIFFERENTIATED CONTENT from this document for interactive flowchart nodes:

{doc_text[:100000]}

CRITICAL: For each major step, provide DIFFERENT types of information:
1. subSteps: Concrete action items someone would DO (not just restating the step name)
2. operationalDetails: Specific how-to information, checklists, timing, tools

EXAMPLES OF GOOD vs BAD:

❌ BAD (Duplication):
  Step: "Call First Contact"
  subSteps: ["Call the first contact person"]  <-- Just repeating the title!

✅ GOOD (Actionable):
  Step: "Call First Contact" 
  subSteps: [
    "Locate contact phone number in escalation list",
    "Prepare incident summary before calling",
    "Make call and document response time"
  ]

For each major step/action, extract:
- 2-5 SPECIFIC sub-actions (what to actually DO, not just restate the step)
- Timing/duration if mentioned
- Systems/tools/documents to use
- Any checklists or verification steps

Return JSON:
{{
  "contentByStep": {{
    "step-name-1": {{
      "subSteps": ["Specific action 1", "Specific action 2", "Specific action 3"],
      "operationalDetails": {{
        "specificActions": ["How-to detail 1", "Checklist item 2"],
        "estimatedDuration": "X minutes if mentioned",
        "gap": false,
        "toolsRequired": ["System names", "Documents needed"]
      }},
      "timing": "When/how long if mentioned",
      "systems": ["System names if mentioned"]
    }}
  }}
}}

Extract ONLY what's in the document. If document lacks detail, generate logical sub-steps based on context.
Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        
        # Use wrapper for error handling
        from ai_call_wrapper import AICallWrapper, AICallError
        try:
            ai_wrapper = AICallWrapper(self.api_key, timeout_seconds=60)
            response = await ai_wrapper.call_with_timeout(
                chat, message, "Extract Content (2/3)"
            )
            return ai_wrapper.validate_json_response(response, "Extract Content")
        except AICallError:
            raise
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {e}", exc_info=True)
            raise AICallError(
                ErrorCatalog.AI_INVALID_RESPONSE,
                f"Content extraction error: {str(e)}"
            )
    
    async def _extract_references(self, doc_text: str, doc_name: str) -> Dict:
        """
        Extract critical reference information.
        """
        logger.info("📚 [Call 3/3] Extracting references...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="adaptive_references",
            system_message="Extract critical reference info only."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=6000)
        
        prompt = f"""Extract CRITICAL REFERENCE INFORMATION ONLY:

{doc_text[:30000]}

Extract ONLY:
1. Emergency contacts (name, phone, when to call)
2. Key scripts/templates (SUMMARY only, 1-2 sentences)
3. Critical timings (e.g., "Wait 5 minutes", "Check every 30 min")

Return JSON:
{{
  "contacts": [
    {{
      "name": "Contact name",
      "phone": "Phone",
      "role": "When to call"
    }}
  ],
  "keyScripts": [
    {{
      "name": "Script name",
      "summary": "1-sentence summary"
    }}
  ],
  "criticalTimings": [
    "Timing guideline"
  ]
}}

Keep CONCISE. Return ONLY JSON."""
        
        message = UserMessage(text=prompt)
        
        # Use wrapper for error handling
        from ai_call_wrapper import AICallWrapper, AICallError
        try:
            ai_wrapper = AICallWrapper(self.api_key, timeout_seconds=60)
            response = await ai_wrapper.call_with_timeout(
                chat, message, "Extract References (3/3)"
            )
            return ai_wrapper.validate_json_response(response, "Extract References")
        except AICallError:
            raise
        except Exception as e:
            logger.error(f"❌ References extraction failed: {e}", exc_info=True)
            raise AICallError(
                ErrorCatalog.AI_INVALID_RESPONSE,
                f"References extraction error: {str(e)}"
            )
    
    def _merge_results(
        self, 
        structure: Dict, 
        content: Dict, 
        references: Dict,
        analysis: Dict[str, Any]
    ) -> Dict:
        """
        Merge the three parallel results.
        """
        logger.info("🔗 Merging structure + content + references...")
        
        # Start with structure
        result = {
            "processName": structure.get("processName", "Process Flowchart"),
            "nodes": structure.get("nodes", []),
            "swimLanes": structure.get("swimLanes", []),
            "contacts": references.get("contacts", []),
            "keyScripts": references.get("keyScripts", []),
            "criticalTimings": references.get("criticalTimings", [])
        }
        
        # Enhance nodes with detailed content
        content_map = content.get("contentByStep", {})
        
        for node in result["nodes"]:
            title = node.get("title", "")
            
            # Try to find matching content
            matching_content = None
            for step_name, step_content in content_map.items():
                if step_name.lower() in title.lower() or title.lower() in step_name.lower():
                    matching_content = step_content
                    break
            
            if matching_content:
                node["subSteps"] = matching_content.get("subSteps", [])
                node["operationalDetails"] = matching_content.get("operationalDetails", {})
                if "timing" in matching_content:
                    node["timing"] = matching_content["timing"]
                if "systems" in matching_content:
                    node["systems"] = matching_content["systems"]
            else:
                # Fallback: Generate meaningful sub-steps from title
                title_lower = title.lower()
                desc = node.get("description", "")
                
                # Create actionable sub-steps based on common patterns
                if "call" in title_lower or "contact" in title_lower:
                    node["subSteps"] = [
                        f"Locate contact information",
                        f"Make the call and document the attempt",
                        f"Record response or no-answer status"
                    ]
                elif "review" in title_lower or "check" in title_lower:
                    node["subSteps"] = [
                        f"Access the relevant system or document",
                        f"Verify key details and indicators",
                        f"Document findings"
                    ]
                elif "escalate" in title_lower or "notify" in title_lower:
                    node["subSteps"] = [
                        f"Prepare incident summary",
                        f"Contact appropriate party",
                        f"Confirm handover"
                    ]
                elif desc and len(desc) > 10:
                    # Use description as single substep if it's meaningful
                    node["subSteps"] = [desc]
                else:
                    # Generic fallback
                    node["subSteps"] = [f"Complete {title.lower()} as documented"]
                
                node["operationalDetails"] = {
                    "specificActions": node["subSteps"][:],
                    "estimatedDuration": "",
                    "gap": False
                }
        
        # POST-PROCESSING: Deduplicate content
        for node in result["nodes"]:
            title = node.get("title", "").lower()
            desc = node.get("description", "").lower()
            substeps = node.get("subSteps", [])
            
            # If substeps just repeat the description, make them more actionable
            if substeps and len(substeps) == 1:
                substep_lower = substeps[0].lower()
                # Check if substep is essentially the same as description
                if desc and (substep_lower == desc or (len(desc) > 20 and substep_lower in desc)):
                    # Replace with more actionable steps
                    logger.info(f"⚠️ Deduplicating substeps for: {node.get('title')}")
                    if "call" in title or "contact" in title:
                        node["subSteps"] = [
                            "Retrieve contact information from escalation list",
                            "Place call and document attempt time",
                            "Record outcome (answered/no answer)"
                        ]
                    elif "review" in title or "evaluate" in title or "check" in title:
                        node["subSteps"] = [
                            "Access relevant information or system",
                            "Examine key indicators or details",
                            "Document findings and next steps"
                        ]
                    elif "record" in title or "log" in title or "document" in title:
                        node["subSteps"] = [
                            "Gather all relevant information",
                            "Enter data into system",
                            "Verify entry accuracy"
                        ]
                    else:
                        # Keep the original but add context
                        node["subSteps"] = [
                            substeps[0],
                            "Document completion",
                            "Proceed to next step"
                        ]
        
        logger.info(f"✅ Merged and deduplicated: {len(result['nodes'])} nodes")
        return result
    

    def _apply_intelligent_grouping(self, result: Dict) -> Dict:
        """
        Post-process nodes to detect and group repetitive patterns.
        
        Patterns to detect:
        1. Sequential "Call Contact" nodes → Group into "Contact Escalation"
        2. Sequential similar actions → Group into single node
        3. Preserve decision nodes (never group these)
        """
        nodes = result.get("nodes", [])
        if len(nodes) <= 5:
            logger.info("⏭️ Skipping grouping - already concise")
            return result
        
        logger.info(f"🔍 Analyzing {len(nodes)} nodes for grouping opportunities...")
        
        # Detect repetitive "Call X Contact" pattern
        grouped_nodes = []
        i = 0
        while i < len(nodes):
            node = nodes[i]
            title_lower = node.get("title", "").lower()
            
            # Pattern 1: Detect "Call First/Second/Third Contact" sequence
            if "call" in title_lower and "contact" in title_lower:
                # Look ahead for similar patterns
                contact_sequence = [node]
                j = i + 1
                while j < len(nodes) and j < i + 5:  # Look up to 5 nodes ahead
                    next_node = nodes[j]
                    next_title_lower = next_node.get("title", "").lower()
                    if "call" in next_title_lower and "contact" in next_title_lower:
                        contact_sequence.append(next_node)
                        j += 1
                    elif next_node.get("isDecisionPoint"):
                        # Stop at decision nodes, but include them
                        j += 1
                        break
                    else:
                        break
                
                # If we found 2+ contact calls, group them
                if len(contact_sequence) >= 2:
                    logger.info(f"📦 Grouping {len(contact_sequence)} contact escalation nodes")
                    
                    # Create grouped node
                    grouped_node = {
                        "id": contact_sequence[0]["id"],
                        "type": "process",
                        "title": "Escalate Through Contacts",
                        "description": f"Attempt to reach escalation contacts (up to {len(contact_sequence)} attempts)",
                        "status": "critical",
                        "swimLane": contact_sequence[0].get("swimLane", "Operations"),
                        "connections": [],
                        "isDecisionPoint": False,
                        "actors": contact_sequence[0].get("actors", []),
                        "subSteps": []
                    }
                    
                    # Collect all sub-steps from grouped nodes
                    for seq_node in contact_sequence:
                        if not seq_node.get("isDecisionPoint"):
                            grouped_node["subSteps"].extend([
                                f"{seq_node.get('title')}: {step}"
                                for step in seq_node.get("subSteps", [seq_node.get("description", "")])[:2]
                            ])
                    
                    # Find the final connection (skip intermediary decision nodes)
                    for seq_node in reversed(contact_sequence):
                        if seq_node.get("connections"):
                            grouped_node["connections"] = seq_node["connections"][:1]
                            break
                    
                    grouped_nodes.append(grouped_node)
                    i = j  # Skip past all grouped nodes
                    continue
            
            # No grouping applied, keep node as-is
            grouped_nodes.append(node)
            i += 1
        
        if len(grouped_nodes) < len(nodes):
            logger.info(f"✅ Reduced nodes from {len(nodes)} → {len(grouped_nodes)}")
            result["nodes"] = grouped_nodes
        else:
            logger.info("ℹ️ No grouping opportunities found")
        
        return result

    def _parse_json(self, response: str) -> Dict:
        """Parse AI response to JSON."""
        try:
            return json.loads(response)
        except:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            logger.warning("⚠️ Could not parse JSON, returning empty dict")
            return {}
    
    def _validate_and_fix(self, data: Dict) -> Dict:
        """Validate and fix the merged data."""
        
        # Ensure required fields
        if "nodes" not in data:
            data["nodes"] = []
        if "swimLanes" not in data:
            data["swimLanes"] = []
        if "contacts" not in data:
            data["contacts"] = []
        
        # Validate nodes
        valid_node_ids = set()
        for i, node in enumerate(data["nodes"]):
            if "id" not in node:
                node["id"] = f"node-{i+1}"
            valid_node_ids.add(node["id"])
            
            # Smart decision point detection
            title = node.get("title", "")
            conns = node.get("connections", [])
            
            # Auto-detect decision nodes by title pattern or connection count
            if not node.get("isDecisionPoint"):
                # Questions ending with "?" are decisions
                if "?" in title:
                    logger.info(f"🔍 Auto-detected decision node: {title}")
                    node["isDecisionPoint"] = True
                    node["type"] = "decision"
                # Nodes with exactly 2 connections are likely decisions
                elif len(conns) == 2 and "decision" in title.lower():
                    logger.info(f"🔍 Auto-detected decision node: {title}")
                    node["isDecisionPoint"] = True
                    node["type"] = "decision"
            
            if "type" not in node:
                node["type"] = "decision" if node.get("isDecisionPoint") else "process"
            
            if "connections" not in node:
                node["connections"] = []
            
            # Fix decision points
            if node.get("isDecisionPoint"):
                opts = node.get("decisionOptions", {})
                conns = node.get("connections", [])
                
                if len(conns) == 2:
                    if not opts or opts.get("yes") not in conns:
                        node["decisionOptions"] = {"yes": conns[0], "no": conns[1]}
                elif len(conns) != 2:
                    # Not a valid decision if it doesn't have exactly 2 connections
                    node["isDecisionPoint"] = False
                    node["decisionOptions"] = {}
                    node["type"] = "process"
            
            # Ensure sub-steps exist
            if "subSteps" not in node or not node["subSteps"]:
                node["subSteps"] = [node.get("description", "Execute step")]
        
        # Validate connections
        for node in data["nodes"]:
            node["connections"] = [c for c in node.get("connections", []) if c in valid_node_ids]
        
        return data
    
    def _validate_against_source(self, data: Dict, source_text: str) -> Dict:
        """
        Validate generated flowchart against source document to catch hallucinations.
        Adds confidence scores to each node.
        """
        import re
        from difflib import SequenceMatcher
        
        def text_similarity(a: str, b: str) -> float:
            """Calculate similarity between two strings (0-1)."""
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()
        
        def find_in_source(text: str, source: str, threshold: float = 0.5) -> bool:
            """Check if text or similar phrase exists in source."""
            text_lower = text.lower().strip()
            source_lower = source.lower()
            
            # Direct substring match
            if text_lower in source_lower:
                return True
            
            # Split into sentences and check similarity
            sentences = re.split(r'[.!?]\s+', source)
            for sentence in sentences:
                if text_similarity(text_lower, sentence) > threshold:
                    return True
            
            # Split text into words and check if majority are in source
            words = text_lower.split()
            if len(words) > 0:
                matches = sum(1 for word in words if len(word) > 3 and word in source_lower)
                if matches / len(words) > 0.6:  # 60% of words match
                    return True
            
            return False
        
        nodes = data.get("nodes", [])
        hallucination_detected = False
        
        logger.info(f"🔍 Validating {len(nodes)} nodes against source document...")
        
        for node in nodes:
            title = node.get("title", "")
            description = node.get("description", "")
            
            # Check if title exists in source
            title_found = find_in_source(title, source_text)
            
            # Check if description concepts exist in source
            desc_found = find_in_source(description, source_text) if description else True
            
            # Confidence score
            if title_found and desc_found:
                node["_validationScore"] = 1.0  # High confidence
            elif title_found:
                node["_validationScore"] = 0.7  # Medium confidence
            else:
                node["_validationScore"] = 0.3  # Low confidence - possible hallucination
                hallucination_detected = True
                logger.warning(f"⚠️ Potential hallucination detected: '{title}' not found in source document")
        
        if hallucination_detected:
            data["_hasHallucinations"] = True
            data["_validationMessage"] = "Some nodes may not accurately reflect the source document. Please review carefully."
        else:
            data["_hasHallucinations"] = False
            data["_validationMessage"] = "All nodes validated against source document."
        
        logger.info(f"✅ Validation complete. Hallucinations detected: {hallucination_detected}")
        
        return data
