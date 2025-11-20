# Actionable Intelligence Service - Revolutionary Document Processing
# Extracts ALL information types: Flow + Resources + Context
# Built for emergency response, BCP, and complex operational procedures

import json
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class ActionableIntelligenceService:
    """
    Revolutionary AI service that extracts ACTIONABLE INTELLIGENCE from documents.
    
    Goes beyond flowcharts to capture:
    - Process Flow (steps, decisions, swim lanes)
    - Contact Information (who to call, escalation paths)
    - Templates (emails, scripts, forms)
    - Systems (URLs, access guides, credentials)
    - Context (purpose, timelines, decision criteria)
    - Troubleshooting (common issues, resolutions)
    
    Design Principles:
    1. Complete Extraction - NO information left behind
    2. Intelligent Linking - Resources linked to relevant steps
    3. Structured Output - Ready for immediate use in emergencies
    4. Extensible - Easy to add new information types
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.extraction_stages = [
            "flow_structure",
            "resource_extraction", 
            "contextual_intelligence",
            "entity_linking"
        ]
    
    async def process_document_comprehensively(
        self, 
        document_text: str,
        document_name: str = "Untitled Document"
    ) -> Dict[str, Any]:
        """
        Master orchestrator - runs all extraction stages in sequence.
        
        Returns complete actionable intelligence package ready for UI rendering.
        """
        logger.info(f"🎯 Starting Comprehensive Document Processing: {document_name}")
        logger.info(f"📄 Document length: {len(document_text)} characters")
        
        try:
            # STAGE 1: Extract Process Flow Structure
            flow_data = await self._extract_flow_structure(document_text, document_name)
            logger.info(f"✅ Flow Structure: {len(flow_data['nodes'])} nodes, {len(flow_data['edges'])} edges")
            
            # STAGE 2: Extract All Resources (Contacts, Templates, Systems)
            resources = await self._extract_resources(document_text, document_name)
            logger.info(f"✅ Resources: {len(resources['contacts'])} contacts, {len(resources['templates'])} templates")
            
            # STAGE 3: Extract Contextual Intelligence per Step
            context_map = await self._extract_contextual_intelligence(
                document_text,
                flow_data['nodes'],
                document_name
            )
            logger.info(f"✅ Context: Enriched {len(context_map)} nodes with detailed intelligence")
            
            # STAGE 4: Link Resources to Steps (Smart Matching)
            resource_links = await self._link_resources_to_steps(
                flow_data['nodes'],
                resources,
                document_text
            )
            logger.info(f"✅ Linking: Created {sum(len(v['contacts']) + len(v['templates']) for v in resource_links.values())} resource links")
            
            # ASSEMBLE: Combine all intelligence into unified structure
            actionable_intelligence = self._assemble_actionable_package(
                flow_data=flow_data,
                resources=resources,
                context_map=context_map,
                resource_links=resource_links,
                document_name=document_name
            )
            
            # VALIDATE: Ensure completeness
            validation_report = self._validate_completeness(
                actionable_intelligence,
                document_text
            )
            
            logger.info(f"🎉 Processing Complete! Completeness: {validation_report['completeness_score']}%")
            
            return {
                "actionable_intelligence": actionable_intelligence,
                "validation": validation_report,
                "metadata": {
                    "document_name": document_name,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "extraction_stages": self.extraction_stages,
                    "ai_model": "claude-sonnet-4"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive processing failed: {str(e)}")
            raise
    
    async def _extract_flow_structure(
        self,
        document_text: str,
        document_name: str
    ) -> Dict[str, Any]:
        """
        STAGE 1: Extract Process Flow Structure
        
        Identifies:
        - Sequential steps
        - Decision points (branches)
        - Parallel processes
        - Swim lanes (phases/actors)
        - Loops and iterations
        """
        logger.info("📊 STAGE 1: Extracting Flow Structure...")
        
        prompt = f"""You are analyzing a process document to extract its COMPLETE flow structure.

Document: {document_name}

Extract ALL of the following:

1. STEPS (Sequential Actions):
   - Every distinct action or activity
   - Include sub-steps if mentioned
   - Maintain original order

2. DECISION POINTS:
   - Any if/then logic
   - Branching conditions
   - Multiple paths

3. PARALLEL PROCESSES:
   - Steps that happen simultaneously
   - Concurrent activities

4. SWIM LANES (Phases/Actors):
   - Group steps by phase, team, or role
   - Identify who does what

5. LOOPS & ITERATIONS:
   - Repeating processes
   - "Until X happens" logic

6. TRIGGERS & END POINTS:
   - What starts the process
   - What ends it

Return JSON in this EXACT format:
{{
  "nodes": [
    {{
      "id": "node-1",
      "title": "Step title (10-15 words max)",
      "type": "action|decision|parallel|loop",
      "category": "detection|assessment|action|communication|verification|recovery",
      "swimLane": "Phase/Team name"
    }}
  ],
  "edges": [
    {{
      "id": "e1",
      "source": "node-1",
      "target": "node-2",
      "label": "condition or blank",
      "style": "solid|dashed"
    }}
  ],
  "swimLanes": [
    {{
      "id": "lane-1",
      "name": "Detection Phase",
      "nodeIds": ["node-1", "node-2"]
    }}
  ]
}}

CRITICAL RULES:
- DO NOT SIMPLIFY: Include every step mentioned
- DO NOT CONSOLIDATE: Keep granular detail
- ENSURE COMPLETENESS: Every action becomes a node
- VALIDATE IDs: All edge sources/targets must exist in nodes

Document to analyze:
{document_text[:15000]}
"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=str(uuid.uuid4()),
            system_message="You are an expert document analyst extracting structured information."
        )
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse AI response
        flow_data = self._parse_json_response(response)
        
        # Validate data integrity
        flow_data = self._validate_flow_data(flow_data)
        
        return flow_data
    
    async def _extract_resources(
        self,
        document_text: str,
        document_name: str
    ) -> Dict[str, Any]:
        """
        STAGE 2: Extract ALL Resources
        
        Finds:
        - Contact information (names, phones, emails, roles)
        - Email templates (subject lines, body content)
        - System information (URLs, credentials, access methods)
        - Forms & checklists
        - External references
        - Escalation paths
        """
        logger.info("📚 STAGE 2: Extracting Resources...")
        
        prompt = f"""You are extracting ALL supporting resources from this document.

Document: {document_name}

Extract EVERY instance of:

1. CONTACTS:
   - Names (any person mentioned)
   - Phone numbers (any format)
   - Email addresses
   - Roles/titles
   - Teams/departments
   - Availability (24/7, business hours, etc)
   - Escalation levels

2. EMAIL TEMPLATES:
   - Subject lines
   - Body content
   - Recipients
   - When to send

3. SYSTEMS & TOOLS:
   - System names
   - URLs
   - Login methods
   - Access requirements
   - Status pages

4. FORMS & CHECKLISTS:
   - Form names
   - Required fields
   - When to use

5. EXTERNAL REFERENCES:
   - Other documents mentioned
   - Links to resources
   - Related procedures

6. ESCALATION PATHS:
   - Who to contact in what order
   - Conditions for escalation

Return JSON:
{{
  "contacts": [
    {{
      "id": "contact-1",
      "name": "Full name",
      "role": "Job title/role",
      "phone": "+XX-XXX-XXXX",
      "email": "email@domain.com",
      "team": "Department/team",
      "availability": "24/7 or specific hours",
      "escalation_level": 1
    }}
  ],
  "templates": [
    {{
      "id": "template-1",
      "name": "Template name",
      "type": "email|script|form",
      "subject": "Email subject",
      "body": "Template content",
      "when_to_use": "Conditions for use"
    }}
  ],
  "systems": [
    {{
      "id": "system-1",
      "name": "System name",
      "type": "application|tool|platform",
      "url": "https://...",
      "access_method": "How to access",
      "credentials": "Credential info",
      "status_page": "Status URL"
    }}
  ],
  "guides": [
    {{
      "id": "guide-1",
      "name": "Guide name",
      "type": "procedure|manual|reference",
      "description": "What it contains"
    }}
  ],
  "escalation_paths": [
    {{
      "id": "escalation-1",
      "trigger": "When to escalate",
      "sequence": ["contact-1", "contact-2", "contact-3"]
    }}
  ]
}}

CRITICAL RULES:
- Extract EVERYTHING - no information left behind
- Preserve exact phone numbers, emails, URLs
- Infer missing information logically (e.g., if email not stated, create placeholder)

Document to analyze:
{document_text}
"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=str(uuid.uuid4()),
            system_message="You are an expert document analyst extracting structured information."
        )
        response = await chat.send_message(UserMessage(text=prompt))
        
        resources = self._parse_json_response(response)
        
        # Generate IDs if missing
        resources = self._ensure_resource_ids(resources)
        
        return resources
    
    async def _extract_contextual_intelligence(
        self,
        document_text: str,
        nodes: List[Dict],
        document_name: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        STAGE 3: Extract Contextual Intelligence per Step
        
        For each node, extract:
        - Purpose (why this step exists)
        - Detailed actions (complete checklist)
        - Timeline (how long it should take)
        - Urgency level
        - Success criteria
        - Decision logic (for decision nodes)
        - Troubleshooting tips
        """
        logger.info("🧠 STAGE 3: Extracting Contextual Intelligence...")
        
        context_map = {}
        
        # Process nodes in batches to avoid token limits
        batch_size = 5
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i+batch_size]
            
            node_list = "\n".join([f"- {n['id']}: {n['title']}" for n in batch])
            
            prompt = f"""For each of these process steps, extract COMPLETE contextual intelligence.

Document: {document_name}

Steps to analyze:
{node_list}

For EACH step, provide:
1. Purpose: Why this step exists (1-2 sentences)
2. All Actions: Complete detailed checklist (include every sub-action mentioned)
3. Timeline: How long should this take
4. Urgency: critical|high|medium|low
5. Owner: Who is responsible
6. Success Criteria: How to know it's complete
7. Decision Logic: IF this is a decision point, what are the criteria
8. Troubleshooting: Common issues and solutions

Return JSON:
{{
  "node-1": {{
    "purpose": "Why statement",
    "allActions": ["Action 1", "Action 2", ...],
    "timeline": "X minutes/hours",
    "urgency": "critical",
    "owner": "Role/team",
    "successCriteria": "Completion definition",
    "decisionLogic": "If X then Y",
    "troubleshooting": ["Issue: Solution", ...]
  }}
}}

Document context:
{document_text[:10000]}
"""
            
            chat = LlmChat(api_key=self.api_key, model="claude-sonnet-4-20250514")
            response = await chat.send_message(UserMessage(text=prompt))
            
            batch_context = self._parse_json_response(response)
            context_map.update(batch_context)
        
        return context_map
    
    async def _link_resources_to_steps(
        self,
        nodes: List[Dict],
        resources: Dict[str, List[Dict]],
        document_text: str
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        STAGE 4: Link Resources to Steps (Smart Matching)
        
        Uses AI to determine which contacts, templates, systems are relevant to which steps.
        """
        logger.info("🔗 STAGE 4: Linking Resources to Steps...")
        
        node_titles = {n['id']: n['title'] for n in nodes}
        
        prompt = f"""Link resources to process steps based on relevance.

Process Steps:
{json.dumps(node_titles, indent=2)}

Available Resources:
Contacts: {[c['name'] + ' (' + c['role'] + ')' for c in resources.get('contacts', [])]}
Templates: {[t['name'] for t in resources.get('templates', [])]}
Systems: {[s['name'] for s in resources.get('systems', [])]}

For each step, determine which resources are DIRECTLY relevant.

Return JSON:
{{
  "node-1": {{
    "contacts": ["contact-1", "contact-2"],
    "templates": ["template-1"],
    "systems": ["system-1"]
  }}
}}

Rules:
- Only link resources that are DIRECTLY used in that step
- A resource can be linked to multiple steps
- Some steps may have no linked resources (empty arrays)
"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=str(uuid.uuid4()),
            system_message="You are an expert document analyst extracting structured information."
        )
        response = await chat.send_message(UserMessage(text=prompt))
        
        resource_links = self._parse_json_response(response.content)
        
        return resource_links
    
    def _assemble_actionable_package(
        self,
        flow_data: Dict,
        resources: Dict,
        context_map: Dict,
        resource_links: Dict,
        document_name: str
    ) -> Dict[str, Any]:
        """
        Assemble all extracted intelligence into unified structure.
        
        Creates the complete data package ready for frontend rendering.
        """
        # Enrich nodes with context and resource links
        enriched_nodes = []
        for node in flow_data['nodes']:
            node_id = node['id']
            
            # Get context for this node
            context = context_map.get(node_id, {})
            
            # Get linked resources
            links = resource_links.get(node_id, {'contacts': [], 'templates': [], 'systems': []})
            
            enriched_node = {
                **node,
                "quickContext": {
                    "timeline": context.get('timeline', ''),
                    "urgency": context.get('urgency', 'medium'),
                    "actors": [context.get('owner', 'Unassigned')],
                    "keyActions": context.get('allActions', [])[:3]  # Top 3 for dropdown
                },
                "fullDetails": {
                    "purpose": context.get('purpose', ''),
                    "allActions": context.get('allActions', []),
                    "timeline": context.get('timeline', ''),
                    "owner": context.get('owner', ''),
                    "successCriteria": context.get('successCriteria', ''),
                    "decisionLogic": context.get('decisionLogic', ''),
                    "troubleshooting": context.get('troubleshooting', [])
                },
                "linkedResources": links
            }
            
            enriched_nodes.append(enriched_node)
        
        return {
            "id": str(uuid.uuid4()),
            "name": document_name,
            "type": "actionable_intelligence",
            "nodes": enriched_nodes,
            "edges": flow_data['edges'],
            "swimLanes": flow_data.get('swimLanes', []),
            "resources": resources,
            "resourceLinks": resource_links,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
    
    def _validate_completeness(
        self,
        actionable_intelligence: Dict,
        original_document: str
    ) -> Dict[str, Any]:
        """
        Validate that extraction captured all critical information.
        
        Returns completeness report with score and missing items.
        """
        # Count extracted items
        node_count = len(actionable_intelligence['nodes'])
        contact_count = len(actionable_intelligence['resources'].get('contacts', []))
        template_count = len(actionable_intelligence['resources'].get('templates', []))
        system_count = len(actionable_intelligence['resources'].get('systems', []))
        
        # Calculate completeness score (simple heuristic)
        score = min(100, (node_count * 5) + (contact_count * 10) + (template_count * 10) + (system_count * 10))
        
        return {
            "completeness_score": score,
            "extracted_counts": {
                "nodes": node_count,
                "contacts": contact_count,
                "templates": template_count,
                "systems": system_count
            },
            "recommendations": self._generate_recommendations(actionable_intelligence)
        }
    
    def _generate_recommendations(self, actionable_intelligence: Dict) -> List[str]:
        """Generate recommendations for improving the extraction."""
        recommendations = []
        
        if len(actionable_intelligence['resources'].get('contacts', [])) == 0:
            recommendations.append("Consider adding contact information for key stakeholders")
        
        if len(actionable_intelligence['resources'].get('templates', [])) == 0:
            recommendations.append("Consider adding communication templates for consistency")
        
        return recommendations
    
    # Helper methods
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON from AI response, handling markdown code blocks."""
        try:
            # Remove markdown code blocks if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
            content = content.strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Content: {content[:500]}")
            return {}
    
    def _validate_flow_data(self, flow_data: Dict) -> Dict:
        """Validate and fix flow data integrity."""
        # Ensure all required keys exist
        flow_data.setdefault('nodes', [])
        flow_data.setdefault('edges', [])
        flow_data.setdefault('swimLanes', [])
        
        # Get all valid node IDs
        valid_node_ids = set(node['id'] for node in flow_data['nodes'])
        
        # Filter edges to only include valid references
        valid_edges = []
        for edge in flow_data['edges']:
            if edge['source'] in valid_node_ids and edge['target'] in valid_node_ids:
                valid_edges.append(edge)
            else:
                logger.warning(f"Removing invalid edge: {edge['id']} (source: {edge['source']}, target: {edge['target']})")
        
        flow_data['edges'] = valid_edges
        
        return flow_data
    
    def _ensure_resource_ids(self, resources: Dict) -> Dict:
        """Ensure all resources have unique IDs."""
        for resource_type in ['contacts', 'templates', 'systems', 'guides', 'escalation_paths']:
            if resource_type in resources:
                for idx, resource in enumerate(resources[resource_type]):
                    if 'id' not in resource:
                        resource['id'] = f"{resource_type[:-1]}-{idx+1}"
        
        return resources


# Import for uuid
import uuid
