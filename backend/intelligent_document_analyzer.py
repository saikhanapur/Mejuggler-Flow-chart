"""
Intelligent Document Analyzer

This module performs deep document understanding BEFORE processing.
Think like a human: First understand WHAT you're looking at, THEN process it.

Stages:
1. Document Classification: Is this already a flowchart or raw text?
2. Content Analysis: What elements exist? How many steps?
3. Complexity Assessment: Simple (5-10 nodes) vs Complex (20+ nodes)?
4. Fidelity Requirements: Must preserve exact structure vs can reorganize?
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """
    Analyzes documents to understand their structure and content
    BEFORE attempting to create flowcharts.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze(self, document_text: str, document_name: str = "Document") -> Dict[str, Any]:
        """
        Deep analysis of the document to understand its nature and structure.
        
        Returns:
        {
            "documentType": "visual_flowchart" | "text_sop" | "mixed",
            "existingStructure": {
                "hasFlowchart": bool,
                "estimatedNodes": int,
                "estimatedDecisions": int,
                "estimatedActions": int
            },
            "complexity": "simple" | "moderate" | "complex",
            "processingStrategy": "extract" | "generate" | "hybrid",
            "keyElements": {
                "decisionPoints": ["Question 1", "Question 2"],
                "actions": ["Action 1", "Action 2"],
                "actors": ["Role 1", "Role 2"]
            },
            "fidelityRequirement": "high" | "medium" | "low"
        }
        """
        
        logger.info(f"🔍 Analyzing document: {document_name}")
        
        # Truncate for analysis
        analysis_text = document_text[:30000]
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="doc_analyzer",
            system_message="You are a document analysis expert. Analyze documents deeply and accurately."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=4000)
        
        prompt = f"""Analyze this document thoroughly. This is CRITICAL for emergency services and must be PERFECT.

DOCUMENT:
{analysis_text}

TASK: Perform deep analysis and answer these questions:

1. DOCUMENT TYPE:
   - Is this already a visual flowchart that was converted to text? (Look for phrases like "diamond shape", "rectangle", "connects to", "branches to")
   - Is this a text-based SOP that needs to be converted into a flowchart?
   - Is it mixed (contains both narrative text and flowchart descriptions)?

2. EXISTING STRUCTURE (if it's already a flowchart):
   - Count: How many nodes/steps are explicitly mentioned?
   - Count: How many decision points (diamonds, yes/no branches)?
   - Count: How many action steps (rectangles, process boxes)?
   - Are the connections clearly defined?

3. CONTENT INVENTORY (for text SOPs):
   - List ALL decision points (questions that lead to different paths)
   - List ALL action steps (things that must be done)
   - List ALL actors/roles involved

4. COMPLEXITY ASSESSMENT:
   - Simple: 3-10 steps, linear or few branches
   - Moderate: 10-20 steps, multiple decision points
   - Complex: 20+ steps, many branches, multiple actors

5. PROCESSING STRATEGY:
   - "extract": Document already has clear flowchart structure, just extract it faithfully
   - "generate": Text-based SOP, need to create flowchart structure
   - "hybrid": Has some structure but needs organization

6. FIDELITY REQUIREMENT:
   - "high": Already structured, must preserve EXACTLY (emergency/safety critical)
   - "medium": Some structure, can improve organization
   - "low": Unstructured text, needs significant structuring

IMPORTANT: Be PRECISE. Count carefully. This affects emergency response procedures.

Return ONLY this JSON:
{{
  "documentType": "visual_flowchart" | "text_sop" | "mixed",
  "existingStructure": {{
    "hasFlowchart": true/false,
    "estimatedNodes": <exact count or best estimate>,
    "estimatedDecisions": <count>,
    "estimatedActions": <count>,
    "structureQuality": "clear" | "partial" | "none"
  }},
  "complexity": "simple" | "moderate" | "complex",
  "processingStrategy": "extract" | "generate" | "hybrid",
  "keyElements": {{
    "decisionPoints": ["list of questions"],
    "actions": ["list of action steps"],
    "actors": ["list of roles"]
  }},
  "fidelityRequirement": "high" | "medium" | "low",
  "analysisNotes": "Brief explanation of your assessment"
}}
"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        try:
            analysis = self._parse_json(response)
            logger.info(f"✅ Document Analysis Complete:")
            logger.info(f"   Type: {analysis.get('documentType')}")
            logger.info(f"   Strategy: {analysis.get('processingStrategy')}")
            logger.info(f"   Estimated Nodes: {analysis.get('existingStructure', {}).get('estimatedNodes')}")
            logger.info(f"   Complexity: {analysis.get('complexity')}")
            return analysis
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            # Fallback to safe defaults
            return {
                "documentType": "text_sop",
                "existingStructure": {
                    "hasFlowchart": False,
                    "estimatedNodes": 15,
                    "estimatedDecisions": 3,
                    "estimatedActions": 12,
                    "structureQuality": "none"
                },
                "complexity": "moderate",
                "processingStrategy": "generate",
                "keyElements": {
                    "decisionPoints": [],
                    "actions": [],
                    "actors": []
                },
                "fidelityRequirement": "medium",
                "analysisNotes": "Analysis failed, using defaults"
            }
    
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
            raise ValueError("Could not parse JSON from response")
