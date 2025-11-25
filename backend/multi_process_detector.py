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
        
        prompt = f"""Analyze this document to detect if it contains MULTIPLE DISTINCT PROCESSES.

DOCUMENT:
{document_text[:10000]}

═══════════════════════════════════════════════════════════════════════════

🔍 DETECTION CRITERIA:

A document has MULTIPLE PROCESSES if it contains:

1. **Multiple Section Headers with Different Process Names**
   - Example: "## Panic Alert" followed by "## Silent Alert" followed by "## Missed Check-In"
   - Each section describes a DIFFERENT procedure/scenario
   - Keywords: "Procedure", "Alert", "Process", "Protocol", "SOP", "Scenario"

2. **Separate Procedures for Different Situations**
   - Example: "Emergency Response" vs "False Alarm Response"
   - Each has its own steps, not branches of the same process

3. **Different Actors/Triggers**
   - Example: "When X happens, do A-B-C" and "When Y happens, do D-E-F"
   - X and Y are fundamentally different triggers

A document has a SINGLE PROCESS if:
- One main workflow with decision branches (YES/NO paths)
- Steps that flow sequentially as part of one procedure
- Subsections are just parts of the same overall process

═══════════════════════════════════════════════════════════════════════════

📋 EXAMPLES:

**MULTIPLE PROCESSES (Return multipleProcesses: true):**

Document: 
"## Panic Alert - This is when duress button is pressed...
 Steps: 1. Check if user can speak 2. Contact emergency services...
 
 ## Silent Alert - This is when silent duress is activated...
 Steps: 1. Check if user can speak 2. Contact emergency services...
 
 ## Missed Check-In - When user doesn't check in...
 Steps: 1. Wait 5 mins 2. Call customer..."

→ Result: 3 processes (Panic Alert, Silent Alert, Missed Check-In)

**SINGLE PROCESS (Return multipleProcesses: false):**

Document:
"## Customer Support Escalation
 1. Receive ticket
 2. Check severity: If high → escalate, If low → handle
 3. Resolve issue
 4. Close ticket"

→ Result: 1 process (Customer Support Escalation with branches)

═══════════════════════════════════════════════════════════════════════════

🎯 YOUR TASK:

1. Scan the document for section headers (##, bold text, numbered sections)
2. Identify if each section describes a DIFFERENT process or is part of the SAME process
3. Count the distinct processes
4. For EACH process, extract:
   - Name (from section header)
   - Brief description
   - Where it starts in the document

Return JSON:
{{
  "multipleProcesses": true/false,
  "processCount": number,
  "processes": [
    {{
      "name": "Exact process name from document",
      "description": "What this process handles",
      "startSection": "Section header or line where it starts"
    }}
  ],
  "reasoning": "Brief explanation of why you detected single or multiple processes"
}}

Be PRECISE. Look for explicit section boundaries. Return ONLY JSON."""

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
