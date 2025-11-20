# HTML Flowchart Generator - The Simple Way
# Generate beautiful, interactive HTML flowcharts in one shot

import logging
from typing import Dict, Any
import re
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class HTMLFlowchartGenerator:
    """
    Generate complete HTML flowcharts like Claude did - simple, fast, beautiful.
    
    ONE PROMPT → COMPLETE HTML → DONE
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_html_flowchart(self, document_text: str, document_name: str = "Process Flow") -> str:
        """
        Generate complete interactive HTML flowchart
        
        Returns: Complete HTML string ready to display
        Time: 15-30 seconds
        """
        logger.info(f"🎨 Generating HTML flowchart for: {document_name}")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="html_flowchart",
            system_message="""You are an expert at creating beautiful, interactive HTML flowcharts.

You generate COMPLETE, SELF-CONTAINED HTML files that:
1. Work instantly (no external dependencies)
2. Are visually stunning (gradients, shadows, smooth interactions)
3. Have interactive elements (click nodes to see details)
4. Include rich side panels with PURPOSE, not duplication
5. Use modern CSS (Tailwind-style utilities inline)
6. Are mobile-responsive

Your HTML should be production-ready and beautiful."""
        ).with_model("openai", "gpt-5")
        
        # Reference the actual HTML structure from the example
        prompt = f"""GENERATE COMPLETE INTERACTIVE HTML FLOWCHART

DOCUMENT TO VISUALIZE:
{document_text}

DOCUMENT NAME: {document_name}

YOUR TASK:
Create a COMPLETE, SELF-CONTAINED HTML file that displays this process as a beautiful, interactive flowchart.

REQUIREMENTS:

1. **Visual Design:**
   - Modern gradient header (sticky)
   - Clean white background with subtle texture
   - Color-coded nodes by type:
     * Critical/Trigger: Red gradient (from-red-500 to-red-600)
     * Action/Operational: Blue border (border-blue-400)
     * Communication: Purple border (border-purple-400)
     * Monitoring: Amber border (border-amber-400)
     * Recovery: Green/Teal border
   - Smooth hover effects (scale-105, shadow-2xl)
   - Professional shadows and rounded corners

2. **Node Structure:**
   - Absolute positioned nodes with clear spacing
   - Icon + Title format (SVG icons inline)
   - Connecting lines (solid lines for main flow, dashed for feedback loops)
   - Arrows pointing to next steps
   - Annotation boxes for critical info

3. **Interactive Features:**
   - Click node → Show detailed side panel (right side slide-in)
   - Side panel includes:
     * Purpose (WHY this step)
     * Specific Actions (concrete steps)
     * Who's Responsible (actors)
     * Systems Used
     * Timeline/Frequency
     * Current State vs Ideal State
     * Dependencies
     * Contact Information
   - Smooth animations

4. **Bottom Section:**
   - Quick reference cards (3 columns):
     * Critical Actions
     * Key Timings
     * Emergency Contacts
   - Color-coded for quick scanning

5. **Technical:**
   - Self-contained (all CSS/JS inline)
   - Modern CSS (flexbox, grid, gradients)
   - Responsive design
   - Clean, readable code

REFERENCE STRUCTURE (adapt to your content):
- Header: Process name + description
- Legend: Show node types
- Main canvas: Flowchart with absolute-positioned nodes
- Connections: SVG or div-based lines/arrows
- Bottom: Quick reference sections
- Side panel: Detailed view (hidden by default, slides in on click)

RETURN:
Complete HTML from <!DOCTYPE html> to </html>

IMPORTANT: 
- Generate the COMPLETE HTML file
- Don't truncate or summarize
- Include ALL sections: header, canvas, nodes, connections, side panel, quick reference
- If the document is complex, simplify the visual representation but keep it complete
- Aim for 10-15 key nodes maximum to keep HTML manageable

Make it BEAUTIFUL and FUNCTIONAL. Users should immediately understand the process and find value."""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Clean up response
        html = response.strip()
        
        # Remove markdown code blocks if present
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]
        
        html = html.strip()
        
        # Validate it's HTML
        if not (html.startswith('<!DOCTYPE') or html.startswith('<html') or html.startswith('<HTML')):
            raise ValueError("Generated content is not valid HTML")
        
        # Check for basic completeness
        if '</html>' not in html.lower():
            logger.warning("HTML appears incomplete, missing closing tag")
            # Try to fix
            html += '\n</body>\n</html>'
        
        # Validate minimum length (should be substantial)
        if len(html) < 5000:
            logger.warning(f"HTML seems too short ({len(html)} chars) - may be incomplete")
        
        logger.info(f"✅ Generated {len(html)} characters of HTML")
        return html
