"""
Intelligent Layout Optimizer

Uses AI to analyze flowchart layout and automatically reorganize nodes
for optimal readability and visual clarity.

Key Features:
- Analyzes current node positions and connections
- Identifies layout issues (overlaps, poor spacing, confusing branches)
- Suggests optimal positions using layout algorithms
- Preserves logical flow while improving visual organization
"""

import logging
from typing import Dict, List, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

logger = logging.getLogger(__name__)


class IntelligentLayoutOptimizer:
    """
    AI-powered layout optimizer for flowcharts.
    Analyzes and reorganizes node positions for maximum clarity.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def optimize_layout(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze current layout and suggest optimal node positions.
        
        Args:
            nodes: List of nodes with current positions
            edges: List of edges showing connections
            
        Returns:
            {
                "optimized_nodes": [...],  # Nodes with new positions
                "changes_made": ["list of improvements"],
                "layout_score": 85  # 0-100 quality score
            }
        """
        logger.info(f"🎨 Optimizing layout for {len(nodes)} nodes, {len(edges)} edges")
        
        # Step 1: Analyze current layout
        analysis = await self._analyze_layout(nodes, edges)
        logger.info(f"📊 Layout analysis: {analysis.get('summary', 'N/A')}")
        
        # Step 2: Generate optimal positions
        optimized_nodes = await self._generate_optimal_layout(nodes, edges, analysis)
        
        logger.info(f"✅ Layout optimization complete")
        
        return {
            "optimized_nodes": optimized_nodes,
            "changes_made": analysis.get("issues", []),
            "layout_score": analysis.get("score", 50),
            "original_score": analysis.get("original_score", 30)
        }
    
    async def _analyze_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """
        Use AI to analyze current layout and identify issues.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="layout_analyzer",
            system_message="You are a flowchart layout expert. Analyze layouts and identify visual issues."
        ).with_model("anthropic", "claude-4-sonnet-20250514").with_params(max_tokens=2000)
        
        # Create a simplified representation
        node_summary = []
        for node in nodes:
            node_summary.append({
                "id": node["id"],
                "type": node.get("type", "process"),
                "title": node.get("data", {}).get("label", "Unknown")[:50],
                "position": node.get("position", {"x": 0, "y": 0}),
                "isDecision": node.get("data", {}).get("isDecisionPoint", False)
            })
        
        edge_summary = []
        for edge in edges:
            edge_summary.append({
                "from": edge["source"],
                "to": edge["target"],
                "label": edge.get("label", "")
            })
        
        prompt = f"""Analyze this flowchart layout and identify visual issues:

NODES: {json.dumps(node_summary[:30], indent=2)}  
EDGES: {json.dumps(edge_summary[:50], indent=2)}

ANALYSIS REQUIRED:
1. Are nodes too close together or overlapping?
2. Are decision branches clear and well-separated?
3. Is the vertical flow logical and easy to follow?
4. Are there crossing edges that create confusion?
5. Is horizontal spacing consistent for parallel paths?

Return JSON:
{{
  "issues": ["Issue 1", "Issue 2", "Issue 3"],
  "summary": "Brief overall assessment",
  "original_score": 0-100,
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}

Focus on VISUAL CLARITY and READABILITY."""

        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        try:
            return self._parse_json(response)
        except:
            return {
                "issues": ["Unable to analyze layout"],
                "summary": "Analysis failed",
                "original_score": 50,
                "recommendations": []
            }
    
    async def _generate_optimal_layout(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        analysis: Dict
    ) -> List[Dict]:
        """
        Generate optimal node positions using layout algorithm.
        Uses a simple but effective vertical layering approach.
        """
        logger.info("📐 Generating optimal layout...")
        
        # Build adjacency map
        adjacency = {}
        in_degree = {}
        for node in nodes:
            node_id = node["id"]
            adjacency[node_id] = []
            in_degree[node_id] = 0
        
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            if source in adjacency:
                adjacency[source].append(target)
            if target in in_degree:
                in_degree[target] += 1
        
        # Topological layering
        layers = []
        current_layer = [nid for nid, deg in in_degree.items() if deg == 0]
        visited = set(current_layer)
        
        while current_layer:
            layers.append(current_layer[:])
            next_layer = []
            for node_id in current_layer:
                for neighbor in adjacency.get(node_id, []):
                    if neighbor not in visited:
                        # Check if all predecessors have been visited
                        all_pred_visited = True
                        for edge in edges:
                            if edge["target"] == neighbor and edge["source"] not in visited:
                                all_pred_visited = False
                                break
                        if all_pred_visited:
                            next_layer.append(neighbor)
                            visited.add(neighbor)
            current_layer = next_layer
        
        # Assign positions based on layers
        optimized_nodes = []
        layer_spacing = 180  # Vertical space between layers
        node_spacing = 300   # Horizontal space between nodes in same layer
        
        for layer_idx, layer in enumerate(layers):
            layer_width = len(layer) * node_spacing
            start_x = -layer_width / 2 + node_spacing / 2  # Center the layer
            
            for node_idx, node_id in enumerate(layer):
                # Find original node
                original_node = next((n for n in nodes if n["id"] == node_id), None)
                if not original_node:
                    continue
                
                # Calculate new position
                new_x = start_x + (node_idx * node_spacing)
                new_y = layer_idx * layer_spacing
                
                # Create optimized node
                optimized_node = {
                    **original_node,
                    "position": {
                        "x": new_x,
                        "y": new_y
                    }
                }
                optimized_nodes.append(optimized_node)
        
        # Handle any nodes not in layers (shouldn't happen, but safety)
        for node in nodes:
            if node["id"] not in visited:
                optimized_nodes.append(node)
        
        logger.info(f"✅ Generated {len(optimized_nodes)} optimized positions across {len(layers)} layers")
        return optimized_nodes
    
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
