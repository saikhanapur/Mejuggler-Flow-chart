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
        
        prompt = f"""Analyze this document and identify if it contains MULTIPLE DISTINCT PROCESSES or ONE UNIFIED PROCESS.

{document_text[:10000]}

A document has MULTIPLE PROCESSES if:
- Different scenarios/procedures with distinct names (e.g., "Day Shift Protocol", "Night Shift Protocol")
- Separate flowcharts or procedures for different situations
- Clear section headings indicating different processes (e.g., "Process A", "Process B")

Examples of MULTIPLE processes:
- "Panic Alert Emergency Procedure" + "False Panic Alert Procedure" + "Silent Alert Procedure"
- "Customer Onboarding" + "Customer Offboarding"
- "Day Operations" + "Night Operations"

Examples of SINGLE process:
- One continuous workflow with steps
- Decision branches within same process
- Different swim lanes in same process

Return JSON:
{{
  "multipleProcesses": true/false,
  "processCount": number,
  "processes": [
    {{
      "name": "Process name",
      "description": "Brief description",
      "startSection": "Where it starts in document"
    }}
  ]
}}

Be ACCURATE. Return ONLY JSON."""

        try:
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            # Parse JSON
            result = self._parse_json(response)
            
            logger.info(f"✅ Detection complete: {result.get('processCount', 1)} process(es)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Process detection failed: {e}")
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
