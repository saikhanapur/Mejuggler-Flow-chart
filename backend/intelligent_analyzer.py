"""
Intelligent Document Analyzer & Node Balancer

This module provides SMART analysis to determine the RIGHT level of detail
for flowchart generation - not too aggressive, not too conservative.

Design Principles:
1. TRUST: Output should match document structure exactly
2. RELIABILITY: Consistent results for similar documents  
3. ZERO HALLUCINATION: Every node must trace to source text
4. DELIGHT: Clean, readable flowcharts that "just work"

The key insight: Analyze document complexity FIRST, then set appropriate
node targets. A 5-step SOP should yield ~5-7 nodes, not 15.
"""

import re
import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentComplexity:
    """Analysis result describing document complexity."""
    level: str  # "simple", "moderate", "complex"
    explicit_steps: int  # Numbered steps found in document
    decision_points: int  # IF/THEN patterns found
    parallel_paths: int  # Multiple concurrent workflows
    actors_count: int  # Different roles/people mentioned
    recommended_nodes: int  # Target node count
    grouping_strategy: str  # "aggressive", "moderate", "minimal"
    reasoning: str  # Why this classification


class IntelligentDocumentAnalyzer:
    """
    Analyzes document to determine optimal flowchart complexity.
    
    This runs BEFORE AI extraction to set appropriate expectations.
    """
    
    def __init__(self):
        # Patterns for detecting explicit structure
        self.step_patterns = [
            r'(?:^|\n)\s*(?:step\s+)?(\d+)[.:)\s]',  # "Step 1:" or "1." or "1)"
            r'(?:^|\n)\s*([a-z])[.:)\s]',  # "a." or "a)"
            r'(?:^|\n)\s*[-•*]\s+',  # Bullet points
            r'(?:^|\n)\s*(?:first|second|third|fourth|fifth|then|next|finally)[,:\s]',
        ]
        
        self.decision_patterns = [
            r'\bif\b.*\bthen\b',
            r'\bif\s+(?:yes|no)\b',
            r'\b(?:yes|no)\s*[-:→]',
            r'\bdecision\b',
            r'\bcheck\s+(?:if|whether)\b',
            r'\?.*(?:yes|no)',
        ]
        
        self.parallel_patterns = [
            r'\b(?:simultaneously|at the same time|in parallel|concurrently)\b',
            r'\bwhile\s+\w+\s+is\b',
            r'\bmeanwhile\b',
        ]
        
        self.actor_patterns = [
            r'\b(?:operator|manager|supervisor|team|agent|officer|staff|user|customer|client|employee)\b',
            r'\b(?:IT|HR|QA|support|admin|security)\b',
        ]
        
        # Patterns that suggest grouping is appropriate
        self.groupable_patterns = [
            (r'(?:call|contact|notify|alert)\s+(?:first|second|third|1st|2nd|3rd|\d+)', 'contact_sequence'),
            (r'(?:update|log|record|document)\s+(?:the|in|to)', 'documentation_sequence'),
            (r'(?:send|email|message)\s+(?:to|notification)', 'notification_sequence'),
            (r'(?:verify|check|confirm|validate)\s+', 'verification_sequence'),
        ]
    
    def analyze(self, document_text: str) -> DocumentComplexity:
        """
        Analyze document and return complexity assessment.
        """
        text_lower = document_text.lower()
        
        # Count explicit steps
        explicit_steps = self._count_explicit_steps(document_text)
        
        # Count decision points
        decision_points = self._count_patterns(text_lower, self.decision_patterns)
        
        # Check for parallel paths
        parallel_paths = self._count_patterns(text_lower, self.parallel_patterns)
        
        # Count distinct actors
        actors = self._extract_actors(text_lower)
        actors_count = len(actors)
        
        # Determine complexity level and recommendations
        complexity = self._determine_complexity(
            explicit_steps, decision_points, parallel_paths, actors_count, len(document_text)
        )
        
        logger.info(f"📊 Document Analysis: {complexity.level} complexity")
        logger.info(f"   Explicit steps: {explicit_steps}")
        logger.info(f"   Decision points: {decision_points}")
        logger.info(f"   Parallel paths: {parallel_paths}")
        logger.info(f"   Actors: {actors_count}")
        logger.info(f"   → Recommended nodes: {complexity.recommended_nodes}")
        logger.info(f"   → Grouping strategy: {complexity.grouping_strategy}")
        
        return complexity
    
    def _count_explicit_steps(self, text: str) -> int:
        """Count explicitly numbered/bulleted steps in document."""
        count = 0
        
        # Count numbered steps (1, 2, 3... or Step 1, Step 2...)
        numbered = re.findall(r'(?:^|\n)\s*(?:step\s+)?(\d+)[.:)\s]', text, re.IGNORECASE)
        if numbered:
            # Get the highest number found (handles non-sequential)
            count = max(int(n) for n in numbered)
        
        # Count lettered steps (a, b, c...)
        lettered = re.findall(r'(?:^|\n)\s*([a-z])[.:)\s]', text)
        if lettered:
            count = max(count, len(set(lettered)))
        
        # Count bullet points if no numbered/lettered
        if count == 0:
            bullets = re.findall(r'(?:^|\n)\s*[-•*]\s+\S', text)
            count = len(bullets)
        
        return count
    
    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        """Count occurrences of patterns in text."""
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count
    
    def _extract_actors(self, text: str) -> set:
        """Extract unique actors/roles from document."""
        actors = set()
        for pattern in self.actor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actors.update(m.lower() for m in matches)
        return actors
    
    def _determine_complexity(
        self, 
        explicit_steps: int,
        decision_points: int,
        parallel_paths: int,
        actors_count: int,
        doc_length: int
    ) -> DocumentComplexity:
        """
        Determine document complexity and recommendations.
        
        Philosophy:
        - Trust the document structure
        - If document has 5 numbered steps → aim for ~5-7 nodes
        - If document has decisions → add ~1-2 nodes per decision
        - If document has parallel paths → allow more nodes
        """
        
        # Base node count on explicit structure
        if explicit_steps > 0:
            # Document has clear structure - respect it
            base_nodes = explicit_steps
        else:
            # No clear structure - estimate from length
            # Rough: 1 node per 200-300 chars of meaningful content
            base_nodes = max(3, min(15, doc_length // 500))
        
        # Add nodes for decision points (each decision creates ~2 branches)
        decision_nodes = min(decision_points * 2, 6)  # Cap at 6 extra nodes
        
        # Add nodes for parallel paths
        parallel_nodes = parallel_paths * 2
        
        # Calculate recommended total
        recommended = base_nodes + decision_nodes + parallel_nodes
        
        # Determine complexity level
        if recommended <= 7:
            level = "simple"
            grouping_strategy = "aggressive"  # Group similar steps together
        elif recommended <= 12:
            level = "moderate"
            grouping_strategy = "moderate"  # Group only clear sequences
        else:
            level = "complex"
            grouping_strategy = "minimal"  # Keep most steps separate
        
        # Cap recommendations for sanity
        recommended = max(3, min(20, recommended))
        
        reasoning = (
            f"Document has {explicit_steps} explicit steps, "
            f"{decision_points} decision points, "
            f"{parallel_paths} parallel paths. "
            f"Targeting {recommended} nodes with {grouping_strategy} grouping."
        )
        
        return DocumentComplexity(
            level=level,
            explicit_steps=explicit_steps,
            decision_points=decision_points,
            parallel_paths=parallel_paths,
            actors_count=actors_count,
            recommended_nodes=recommended,
            grouping_strategy=grouping_strategy,
            reasoning=reasoning
        )


class IntelligentNodeGrouper:
    """
    Groups nodes intelligently based on document complexity analysis.
    
    Grouping Rules:
    1. NEVER group decision nodes
    2. NEVER group critical/emergency actions
    3. Group sequential similar actions (contact escalation, notifications)
    4. Group documentation/logging steps
    5. Respect the recommended node count from analysis
    """
    
    def __init__(self, complexity: DocumentComplexity):
        self.complexity = complexity
        self.target_nodes = complexity.recommended_nodes
        self.strategy = complexity.grouping_strategy
    
    def group_nodes(self, nodes: List[Dict], edges: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Apply intelligent grouping to nodes.
        
        Returns: (grouped_nodes, updated_edges)
        """
        if len(nodes) <= self.target_nodes:
            logger.info(f"✅ Node count ({len(nodes)}) at or below target ({self.target_nodes}), no grouping needed")
            return nodes, edges
        
        logger.info(f"🔄 Grouping needed: {len(nodes)} nodes → target {self.target_nodes}")
        
        # Build node lookup and connection map
        node_map = {n['id']: n for n in nodes}
        
        # Identify groupable sequences
        grouped_nodes = []
        processed_ids = set()
        
        i = 0
        while i < len(nodes):
            node = nodes[i]
            
            if node['id'] in processed_ids:
                i += 1
                continue
            
            # RULE 1: Never group decision nodes
            if node.get('isDecisionPoint') or node.get('type') == 'decision':
                grouped_nodes.append(node)
                processed_ids.add(node['id'])
                i += 1
                continue
            
            # RULE 2: Never group critical/emergency nodes
            if self._is_critical_node(node):
                grouped_nodes.append(node)
                processed_ids.add(node['id'])
                i += 1
                continue
            
            # Try to find groupable sequence starting from this node
            sequence = self._find_groupable_sequence(nodes, i, processed_ids)
            
            if len(sequence) >= 2 and self.strategy in ['aggressive', 'moderate']:
                # Create grouped node
                grouped_node = self._create_grouped_node(sequence)
                grouped_nodes.append(grouped_node)
                
                for seq_node in sequence:
                    processed_ids.add(seq_node['id'])
                
                logger.info(f"📦 Grouped {len(sequence)} nodes → '{grouped_node['title']}'")
                i += len(sequence)
            else:
                # Keep as individual node
                grouped_nodes.append(node)
                processed_ids.add(node['id'])
                i += 1
        
        # Update edges to point to grouped nodes
        updated_edges = self._update_edges(edges, nodes, grouped_nodes)
        
        logger.info(f"✅ Grouping complete: {len(nodes)} → {len(grouped_nodes)} nodes")
        
        return grouped_nodes, updated_edges
    
    def _is_critical_node(self, node: Dict) -> bool:
        """Check if node is critical and should never be grouped."""
        title_lower = node.get('title', '').lower()
        status = node.get('status', '').lower()
        
        critical_keywords = [
            'emergency', 'critical', '111', '911', 'urgent',
            'immediate', 'escalate', 'priority', 'p1', 'alert'
        ]
        
        return (
            status == 'critical' or
            any(kw in title_lower for kw in critical_keywords)
        )
    
    def _find_groupable_sequence(
        self, 
        nodes: List[Dict], 
        start_idx: int,
        processed_ids: set
    ) -> List[Dict]:
        """Find a sequence of similar nodes that can be grouped."""
        sequence = [nodes[start_idx]]
        start_node = nodes[start_idx]
        start_title = start_node.get('title', '').lower()
        
        # Determine what kind of sequence this might be
        sequence_type = self._detect_sequence_type(start_title)
        
        if not sequence_type:
            return sequence
        
        # Look ahead for similar nodes
        for j in range(start_idx + 1, min(start_idx + 6, len(nodes))):
            next_node = nodes[j]
            
            if next_node['id'] in processed_ids:
                continue
            
            # Stop at decision nodes
            if next_node.get('isDecisionPoint') or next_node.get('type') == 'decision':
                break
            
            # Stop at critical nodes
            if self._is_critical_node(next_node):
                break
            
            # Check if this node matches the sequence type
            next_title = next_node.get('title', '').lower()
            if self._matches_sequence_type(next_title, sequence_type):
                sequence.append(next_node)
            else:
                break
        
        return sequence
    
    def _detect_sequence_type(self, title: str) -> str:
        """Detect what type of sequence this node might start."""
        patterns = {
            'contact': ['call', 'contact', 'phone', 'reach'],
            'notify': ['notify', 'alert', 'inform', 'advise', 'send'],
            'document': ['document', 'log', 'record', 'update', 'note'],
            'verify': ['verify', 'check', 'confirm', 'validate', 'review'],
        }
        
        for seq_type, keywords in patterns.items():
            if any(kw in title for kw in keywords):
                return seq_type
        
        return None
    
    def _matches_sequence_type(self, title: str, seq_type: str) -> bool:
        """Check if title matches the given sequence type."""
        patterns = {
            'contact': ['call', 'contact', 'phone', 'reach', 'escalat'],
            'notify': ['notify', 'alert', 'inform', 'advise', 'send', 'email'],
            'document': ['document', 'log', 'record', 'update', 'note', 'save'],
            'verify': ['verify', 'check', 'confirm', 'validate', 'review'],
        }
        
        keywords = patterns.get(seq_type, [])
        return any(kw in title for kw in keywords)
    
    def _create_grouped_node(self, sequence: List[Dict]) -> Dict:
        """Create a single node from a sequence of similar nodes."""
        first = sequence[0]
        
        # Determine group title based on sequence type
        title = self._get_group_title(sequence)
        
        # Collect all sub-steps
        sub_steps = []
        for node in sequence:
            node_title = node.get('title', '')
            node_desc = node.get('description', '')
            sub_steps.append(f"• {node_title}")
            if node_desc and node_desc != node_title:
                sub_steps.append(f"  {node_desc[:100]}")
        
        # Get final connections (from last node in sequence)
        final_connections = sequence[-1].get('connections', [])
        
        return {
            'id': first['id'],  # Keep first node's ID
            'type': 'process',
            'title': title,
            'description': f"Includes {len(sequence)} steps",
            'status': first.get('status', 'action'),
            'swimLane': first.get('swimLane', 'Operations'),
            'connections': final_connections,
            'isDecisionPoint': False,
            'isGrouped': True,
            'groupedCount': len(sequence),
            'subSteps': sub_steps[:8],  # Limit to 8 sub-steps
            'actors': first.get('actors', []),
            'details': {
                'specificActions': sub_steps[:6],
                'groupedFrom': [n['id'] for n in sequence]
            }
        }
    
    def _get_group_title(self, sequence: List[Dict]) -> str:
        """Generate appropriate title for grouped nodes."""
        first_title = sequence[0].get('title', '').lower()
        count = len(sequence)
        
        if 'contact' in first_title or 'call' in first_title:
            return f"Contact Escalation ({count} attempts)"
        elif 'notify' in first_title or 'alert' in first_title:
            return f"Send Notifications ({count} recipients)"
        elif 'document' in first_title or 'log' in first_title:
            return f"Document Actions ({count} records)"
        elif 'verify' in first_title or 'check' in first_title:
            return f"Verification Steps ({count} checks)"
        else:
            return f"Process Steps ({count} actions)"
    
    def _update_edges(
        self, 
        edges: List[Dict], 
        original_nodes: List[Dict],
        grouped_nodes: List[Dict]
    ) -> List[Dict]:
        """Update edges to reflect grouped nodes."""
        # Map old IDs to new IDs
        grouped_node_ids = {n['id'] for n in grouped_nodes}
        
        # For grouped nodes, map all original IDs to the group ID
        id_mapping = {}
        for node in grouped_nodes:
            if node.get('isGrouped'):
                group_id = node['id']
                for orig_id in node.get('details', {}).get('groupedFrom', []):
                    id_mapping[orig_id] = group_id
        
        updated_edges = []
        seen_edges = set()
        
        for edge in edges:
            source = id_mapping.get(edge['source'], edge['source'])
            target = id_mapping.get(edge['target'], edge['target'])
            
            # Skip self-loops created by grouping
            if source == target:
                continue
            
            # Skip if neither source nor target exists in grouped nodes
            if source not in grouped_node_ids and target not in grouped_node_ids:
                # Check if these were grouped away
                if edge['source'] in id_mapping or edge['target'] in id_mapping:
                    source = id_mapping.get(edge['source'], edge['source'])
                    target = id_mapping.get(edge['target'], edge['target'])
                else:
                    continue
            
            # Avoid duplicate edges
            edge_key = f"{source}-{target}"
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            
            updated_edges.append({
                **edge,
                'source': source,
                'target': target
            })
        
        return updated_edges


# Convenience function for direct use
def analyze_and_recommend(document_text: str) -> Dict[str, Any]:
    """
    Analyze document and return recommendations for flowchart generation.
    
    Returns dict with:
    - recommended_nodes: Target node count
    - grouping_strategy: "aggressive", "moderate", or "minimal"
    - complexity: "simple", "moderate", or "complex"
    - reasoning: Explanation of the analysis
    """
    analyzer = IntelligentDocumentAnalyzer()
    complexity = analyzer.analyze(document_text)
    
    return {
        "recommended_nodes": complexity.recommended_nodes,
        "grouping_strategy": complexity.grouping_strategy,
        "complexity": complexity.level,
        "explicit_steps": complexity.explicit_steps,
        "decision_points": complexity.decision_points,
        "reasoning": complexity.reasoning
    }
