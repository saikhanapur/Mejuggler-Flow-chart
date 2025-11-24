"""
AI Learning System - Feedback & Training Database

Enables the AI to learn from user corrections and examples.
Stores training data and uses it for few-shot learning.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class LearningSystem:
    """
    Manages AI training data and feedback collection.
    Enables continuous improvement through user examples.
    """
    
    def __init__(self, db_client):
        self.db = db_client
        self.learning_db = db_client.flowforge_db.learning_examples
        self.feedback_db = db_client.flowforge_db.user_feedback
    
    async def store_training_example(
        self,
        document_text: str,
        document_name: str,
        user_classification: Dict[str, Any],
        preferred_structure: Dict[str, Any],
        industry: str,
        user_id: str = None
    ) -> str:
        """
        Store a training example for future AI learning.
        
        Args:
            document_text: The full document text
            document_name: Name/title of the document
            user_classification: How the user classified this document
            preferred_structure: User's preferred flowchart structure
            industry: Industry category (e.g., "Emergency Services", "Physical Security")
            user_id: ID of the user who created this example
            
        Returns:
            example_id: ID of the stored example
        """
        example_id = str(uuid.uuid4())
        
        example = {
            "id": example_id,
            "document_name": document_name,
            "document_text": document_text[:10000],  # Store first 10k chars for reference
            "document_length": len(document_text),
            "document_hash": hash(document_text),  # For deduplication
            "industry": industry,
            "user_classification": user_classification,
            "preferred_structure": preferred_structure,
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "usage_count": 0,  # Track how often this example is used
            "effectiveness_score": 0.0  # Track if using this example improves results
        }
        
        try:
            await self.learning_db.insert_one(example)
            logger.info(f"✅ Stored training example: {example_id} - {document_name}")
            return example_id
        except Exception as e:
            logger.error(f"❌ Failed to store training example: {e}")
            raise
    
    async def get_relevant_examples(
        self,
        industry: str = None,
        document_type: str = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant training examples for few-shot learning.
        
        Args:
            industry: Filter by industry
            document_type: Filter by document type
            limit: Maximum number of examples to return
            
        Returns:
            List of training examples
        """
        query = {}
        
        if industry:
            query["industry"] = industry
        if document_type:
            query["user_classification.document_type"] = document_type
        
        try:
            # Get most used examples first (they're probably good)
            examples = await self.learning_db.find(
                query,
                {"_id": 0}
            ).sort("usage_count", -1).limit(limit).to_list(limit)
            
            # Increment usage counter
            for example in examples:
                await self.learning_db.update_one(
                    {"id": example["id"]},
                    {"$inc": {"usage_count": 1}}
                )
            
            logger.info(f"📚 Retrieved {len(examples)} training examples for industry: {industry}")
            return examples
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve examples: {e}")
            return []
    
    async def store_user_feedback(
        self,
        process_id: str,
        document_name: str,
        rating: int,
        issues: List[str],
        corrections: Optional[Dict[str, Any]] = None,
        user_id: str = None
    ) -> str:
        """
        Store user feedback on generated flowchart.
        
        Args:
            process_id: ID of the generated process
            document_name: Name of the document
            rating: User rating (1-5 stars)
            issues: List of issues (e.g., ["node_grouping", "multi_process_detection"])
            corrections: User's corrections/preferences
            user_id: ID of the user providing feedback
            
        Returns:
            feedback_id: ID of the stored feedback
        """
        feedback_id = str(uuid.uuid4())
        
        feedback = {
            "id": feedback_id,
            "process_id": process_id,
            "document_name": document_name,
            "rating": rating,
            "issues": issues,
            "corrections": corrections or {},
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "resolved": False
        }
        
        try:
            await self.feedback_db.insert_one(feedback)
            logger.info(f"✅ Stored user feedback: {feedback_id} - Rating: {rating}/5")
            
            # If rating is low, log for review
            if rating <= 2:
                logger.warning(f"⚠️ Low rating ({rating}/5) for {document_name}: Issues: {issues}")
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store feedback: {e}")
            raise
    
    async def get_feedback_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics on user feedback for continuous improvement.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            all_feedback = await self.feedback_db.find(
                {"created_at": {"$gte": cutoff_date.isoformat()}},
                {"_id": 0}
            ).to_list(1000)
            
            if not all_feedback:
                return {"total": 0, "average_rating": 0, "common_issues": []}
            
            # Calculate stats
            total = len(all_feedback)
            avg_rating = sum(f["rating"] for f in all_feedback) / total
            
            # Count common issues
            issue_counts = {}
            for f in all_feedback:
                for issue in f.get("issues", []):
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_feedback": total,
                "average_rating": round(avg_rating, 2),
                "common_issues": [{"issue": issue, "count": count} for issue, count in common_issues],
                "low_ratings": sum(1 for f in all_feedback if f["rating"] <= 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get feedback stats: {e}")
            return {"total": 0, "average_rating": 0, "common_issues": [], "error": str(e)}
    
    def format_training_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """
        Format training examples for inclusion in AI prompts (few-shot learning).
        
        Args:
            examples: List of training examples
            
        Returns:
            Formatted string for prompt
        """
        if not examples:
            return ""
        
        prompt_text = "\n📚 TRAINING EXAMPLES (Learn from these):\n\n"
        
        for idx, example in enumerate(examples, 1):
            classification = example.get("user_classification", {})
            structure = example.get("preferred_structure", {})
            
            prompt_text += f"EXAMPLE {idx}:\n"
            prompt_text += f"Document: {example.get('document_name', 'Unknown')}\n"
            prompt_text += f"Industry: {example.get('industry', 'Unknown')}\n"
            
            # Multi-process classification
            if classification.get("multipleProcesses"):
                prompt_text += f"Classification: MULTIPLE PROCESSES ({classification.get('processCount')})\n"
                prompt_text += f"Process Titles: {classification.get('processTitles', [])}\n"
                prompt_text += f"Reasoning: {classification.get('reasoning', 'N/A')}\n"
            else:
                prompt_text += f"Classification: SINGLE PROCESS\n"
                prompt_text += f"Reasoning: {classification.get('reasoning', 'N/A')}\n"
            
            # Preferred structure
            if structure:
                prompt_text += f"Preferred Structure:\n"
                if "node_count" in structure:
                    prompt_text += f"  - Node Count: {structure['node_count']}\n"
                if "grouping_strategy" in structure:
                    prompt_text += f"  - Grouping: {structure['grouping_strategy']}\n"
                if "decision_points" in structure:
                    prompt_text += f"  - Decisions: {structure['decision_points']}\n"
            
            prompt_text += "\n"
        
        prompt_text += "NOW APPLY THE SAME LOGIC TO THE CURRENT DOCUMENT.\n"
        prompt_text += "=" * 60 + "\n\n"
        
        return prompt_text
