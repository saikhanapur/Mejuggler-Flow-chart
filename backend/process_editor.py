"""
Process Editor Service
Allows manual editing of AI-generated flowcharts
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ProcessEditor:
    """Handle manual edits to process flowcharts"""
    
    @staticmethod
    def update_node_priority(node: Dict, new_priority_level: str) -> Dict:
        """
        Update node priority manually.
        
        Args:
            node: Node dict with existing priority
            new_priority_level: New priority (P0, P1, P2, P3, P4)
            
        Returns:
            Updated node dict with new priority
        """
        priority_config = {
            "P0": {"emoji": "🔴", "color": "red", "label": "IMMEDIATE", "score": 95},
            "P1": {"emoji": "🟠", "color": "orange", "label": "URGENT", "score": 80},
            "P2": {"emoji": "🟡", "color": "yellow", "label": "HIGH", "score": 60},
            "P3": {"emoji": "🔵", "color": "blue", "label": "MEDIUM", "score": 40},
            "P4": {"emoji": "⚪", "color": "gray", "label": "LOW", "score": 20},
        }
        
        if new_priority_level not in priority_config:
            logger.warning(f"Invalid priority level: {new_priority_level}, defaulting to P3")
            new_priority_level = "P3"
        
        config = priority_config[new_priority_level]
        
        # Update priority with manual override flag
        node["priority"] = {
            "level": new_priority_level,
            "emoji": config["emoji"],
            "color": config["color"],
            "label": config["label"],
            "score": config["score"],
            "manualOverride": True,  # Flag that this was manually set
            "overrideAt": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"✏️ Node '{node.get('title', 'Unknown')}' priority changed to {new_priority_level}")
        
        return node
    
    @staticmethod
    def update_node_title(node: Dict, new_title: str) -> Dict:
        """
        Update node title manually.
        
        Args:
            node: Node dict
            new_title: New title text
            
        Returns:
            Updated node dict
        """
        if not new_title or not new_title.strip():
            logger.warning("Empty title provided, skipping update")
            return node
        
        old_title = node.get("title", "")
        node["title"] = new_title.strip()
        
        # Track edit history
        if "editHistory" not in node:
            node["editHistory"] = []
        
        node["editHistory"].append({
            "field": "title",
            "oldValue": old_title,
            "newValue": new_title.strip(),
            "editedAt": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"✏️ Node title changed: '{old_title}' → '{new_title}'")
        
        return node
    
    @staticmethod
    def update_node_description(node: Dict, new_description: str) -> Dict:
        """
        Update node description manually.
        
        Args:
            node: Node dict
            new_description: New description text
            
        Returns:
            Updated node dict
        """
        old_description = node.get("description", "")
        node["description"] = new_description.strip()
        
        # Track edit history
        if "editHistory" not in node:
            node["editHistory"] = []
        
        node["editHistory"].append({
            "field": "description",
            "oldValue": old_description,
            "newValue": new_description.strip(),
            "editedAt": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"✏️ Node description updated")
        
        return node
    
    @staticmethod
    def add_node(process: Dict, node_data: Dict, position: Optional[Dict] = None) -> Dict:
        """
        Add a new node manually to the process.
        
        Args:
            process: Process dict
            node_data: New node data (title, description, status)
            position: Optional position {x, y}
            
        Returns:
            Updated process dict
        """
        import uuid
        
        # Generate node ID
        node_id = f"node-{str(uuid.uuid4())[:8]}"
        
        # Default position (bottom of canvas)
        if not position:
            existing_nodes = process.get("nodes", [])
            max_y = max([n.get("y", 0) for n in existing_nodes] or [0])
            position = {"x": 330, "y": max_y + 150}
        
        # Create node
        new_node = {
            "id": node_id,
            "title": node_data.get("title", "New Step"),
            "description": node_data.get("description", ""),
            "status": node_data.get("status", "operational"),
            "x": position["x"],
            "y": position["y"],
            "position": position,
            "priority": {
                "level": "P3",
                "emoji": "🔵",
                "color": "blue",
                "label": "MEDIUM",
                "score": 40,
                "manualOverride": True
            },
            "subSteps": [],
            "operationalDetails": {},
            "manuallyAdded": True,
            "addedAt": datetime.now(timezone.utc).isoformat()
        }
        
        # Add to process
        if "nodes" not in process:
            process["nodes"] = []
        
        process["nodes"].append(new_node)
        
        logger.info(f"➕ Added new node: '{new_node['title']}' at ({position['x']}, {position['y']})")
        
        return process
    
    @staticmethod
    def delete_node(process: Dict, node_id: str) -> Dict:
        """
        Delete a node from the process.
        
        Args:
            process: Process dict
            node_id: ID of node to delete
            
        Returns:
            Updated process dict
        """
        nodes = process.get("nodes", [])
        original_count = len(nodes)
        
        # Filter out the node
        process["nodes"] = [n for n in nodes if n.get("id") != node_id]
        
        # Also remove edges connected to this node
        edges = process.get("edges", [])
        process["edges"] = [
            e for e in edges 
            if e.get("source") != node_id and e.get("target") != node_id
        ]
        
        deleted_count = original_count - len(process["nodes"])
        
        if deleted_count > 0:
            logger.info(f"🗑️ Deleted node: {node_id}")
        else:
            logger.warning(f"Node {node_id} not found for deletion")
        
        return process
