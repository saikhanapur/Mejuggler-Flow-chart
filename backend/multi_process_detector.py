"""
Multi-Process Detector
Identifies if document contains multiple distinct processes.
"""

import logging
from typing import Dict, List, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

logger = logging.getLogger(__name__)


class MultiProcessDetector:
    """Detects if document has multiple distinct processes."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def detect_processes(self, document_text: str) -> Dict[str, Any]:
        """
        Detect if document has multiple processes.
        Returns: {"multipleProcesses": bool, "processes": [list of process names]}
        """
        
        logger.info("🔍 Detecting processes in document...")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="process_detection",
            system_message="Analyze documents for distinct processes. Return JSON only."
        ).with_model("openai", "gpt-4o").with_params(max_tokens=1000)
        
        prompt = f"""Analyze this document and determine if it contains MULTIPLE DISTINCT PROCESSES or ONE PROCESS.

DOCUMENT:
{document_text[:10000]}

IMPORTANT: A document has MULTIPLE PROCESSES only if it describes completely separate workflows with different triggers.

SINGLE PROCESS = One workflow with branches/decision points
Example: "1. Check status 2. If OK → proceed, If NOT OK → escalate 3. Complete"
This is ONE process with decision branches.

MULTIPLE PROCESSES = Completely separate workflows for different scenarios
Example: 
"## Process A: Equipment Failure - Steps: 1, 2, 3..."
"## Process B: Power Outage - Steps: 1, 2, 3..."
"## Process C: Data Loss - Steps: 1, 2, 3..."
These are THREE different processes.

KEY QUESTION: Are the sections describing:
- Different scenarios within ONE procedure? → SINGLE PROCESS
- Completely separate procedures? → MULTIPLE PROCESSES

Look for:
- ## section headers with different workflow names
- "Procedure A", "Procedure B" style labeling
- Completely different triggers/starting conditions

Return JSON:
{{
  "multipleProcesses": true/false,
  "processCount": number,
  "processes": [
    {{
      "name": "Process name from document",
      "description": "Brief description",
      "startSection": "Where it starts"
    }}
  ],
  "reasoning": "Why single or multiple"
}}

If unsure, default to SINGLE PROCESS with branches. Return ONLY JSON."""

        try:
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            # Debug logging
            logger.info(f"Raw AI response: {response[:200] if response else 'None'}")
            
            # Parse JSON
            result = self._parse_json(response)
            
            logger.info(f"✅ Detection complete: {result.get('processCount', 1)} process(es)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Process detection failed: {e}", exc_info=True)
            # Fallback: assume single process
            return {
                "multipleProcesses": False,
                "processCount": 1,
                "processes": [{"name": "Main Process", "description": ""}]
            }
    
    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from response."""
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
            return {"multipleProcesses": False, "processCount": 1, "processes": []}
