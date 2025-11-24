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
        Generate optimal node positions with DECISION-AWARE spacing.
        
        KEY RULES:
        1. Decision nodes (diamonds) get WIDE horizontal separation for YES/NO branches
        2. YES branches go LEFT, NO branches go RIGHT
        3. Minimum 500px horizontal spacing between decision branches
        4. Vertical alignment for sequential nodes
        """
        logger.info("📐 Generating DECISION-AWARE layout...")
        
        # Build node map and identify decision nodes
        node_map = {n["id"]: n for n in nodes}
        
        # DEBUG: Log node structure to understand the format
        if nodes:
            logger.info(f"📋 Sample node structure: {list(nodes[0].keys())}")
            logger.info(f"📋 Sample node: {nodes[0]}")
        
        # Try multiple ways to detect decision nodes (different data structures)
        decision_nodes = set()
        for n in nodes:
            # Method 1: Check data.isDecisionPoint
            if n.get("data", {}).get("isDecisionPoint", False):
                decision_nodes.add(n["id"])
            # Method 2: Check type field
            elif n.get("type") == "decision":
                decision_nodes.add(n["id"])
            # Method 3: Check isDecisionPoint at root level
            elif n.get("isDecisionPoint", False):
                decision_nodes.add(n["id"])
        
        logger.info(f"🔶 Found {len(decision_nodes)} decision nodes: {decision_nodes}")
        
        # Build adjacency and edge label map
        adjacency = {}
        edge_labels = {}  # Maps (source, target) -> label (YES/NO)
        in_degree = {}
        
        for node in nodes:
            node_id = node["id"]
            adjacency[node_id] = []
            in_degree[node_id] = 0
        
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            label = edge.get("label", "").upper()
            
            if source in adjacency:
                adjacency[source].append(target)
                edge_labels[(source, target)] = label
            if target in in_degree:
                in_degree[target] += 1
        
        # Topological layering with decision awareness
        layers = []
        current_layer = [nid for nid, deg in in_degree.items() if deg == 0]
        visited = set(current_layer)
        
        while current_layer:
            layers.append(current_layer[:])
            next_layer = []
            for node_id in current_layer:
                for neighbor in adjacency.get(node_id, []):
                    if neighbor not in visited:
                        all_pred_visited = True
                        for edge in edges:
                            if edge["target"] == neighbor and edge["source"] not in visited:
                                all_pred_visited = False
                                break
                        if all_pred_visited:
                            next_layer.append(neighbor)
                            visited.add(neighbor)
            current_layer = next_layer
        
        # DECISION-AWARE POSITIONING
        optimized_nodes = []
        layer_spacing = 200  # Vertical space between layers
        base_node_spacing = 400  # Base horizontal spacing
        decision_branch_spacing = 600  # WIDE spacing for decision branches
        
        positions = {}  # Track all positions
        
        for layer_idx, layer in enumerate(layers):
            y_pos = layer_idx * layer_spacing
            
            # Check if this layer has decision branches (children of decision nodes)
            is_decision_branch_layer = any(
                any(parent in decision_nodes for parent in self._get_parents(node_id, edges))
                for node_id in layer
            )
            
            if is_decision_branch_layer:
                # SPECIAL HANDLING: Decision branches need WIDE separation
                logger.info(f"🔶 Layer {layer_idx} has decision branches - applying WIDE spacing")
                
                # Group nodes by their parent decision
                decision_groups = {}
                for node_id in layer:
                    parents = self._get_parents(node_id, edges)
                    for parent in parents:
                        if parent in decision_nodes:
                            edge_label = edge_labels.get((parent, node_id), "")
                            if parent not in decision_groups:
                                decision_groups[parent] = {"YES": [], "NO": []}
                            
                            if "YES" in edge_label or "✓" in edge_label:
                                decision_groups[parent]["YES"].append(node_id)
                            elif "NO" in edge_label or "×" in edge_label:
                                decision_groups[parent]["NO"].append(node_id)
                
                # Position decision branches with WIDE separation
                x_offset = 0
                for decision_id, branches in decision_groups.items():
                    # Get decision node position (from previous layer)
                    decision_pos = positions.get(decision_id, {"x": 0, "y": 0})
                    
                    # Position YES branch (LEFT of decision)
                    for yes_node in branches["YES"]:
                        x_pos = decision_pos["x"] - decision_branch_spacing
                        positions[yes_node] = {"x": x_pos, "y": y_pos}
                        original_node = node_map[yes_node]
                        optimized_nodes.append({
                            **original_node,  # Preserve ALL original fields
                            "position": {"x": x_pos, "y": y_pos}
                        })
                    
                    # Position NO branch (RIGHT of decision)
                    for no_node in branches["NO"]:
                        x_pos = decision_pos["x"] + decision_branch_spacing
                        positions[no_node] = {"x": x_pos, "y": y_pos}
                        original_node = node_map[no_node]
                        optimized_nodes.append({
                            **original_node,  # Preserve ALL original fields
                            "position": {"x": x_pos, "y": y_pos}
                        })
            else:
                # NORMAL LAYER: Center nodes
                layer_width = len(layer) * base_node_spacing
                start_x = -layer_width / 2 + base_node_spacing / 2
                
                for node_idx, node_id in enumerate(layer):
                    x_pos = start_x + (node_idx * base_node_spacing)
                    positions[node_id] = {"x": x_pos, "y": y_pos}
                    original_node = node_map[node_id]
                    optimized_nodes.append({
                        **original_node,  # Preserve ALL original fields including type, data, etc.
                        "position": {"x": x_pos, "y": y_pos}
                    })
        
        # Handle unvisited nodes
        for node in nodes:
            if node["id"] not in visited:
                optimized_nodes.append(node)
        
        logger.info(f"✅ Generated {len(optimized_nodes)} positions with decision-aware spacing")
        return optimized_nodes
    
    def _get_parents(self, node_id: str, edges: List[Dict]) -> List[str]:
        """Get all parent nodes for a given node."""
        return [e["source"] for e in edges if e["target"] == node_id]
    
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
