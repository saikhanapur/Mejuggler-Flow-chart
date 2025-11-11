"""
Budget Monitoring Service
Prevents LLM API failures due to budget exhaustion
"""
import os
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class BudgetMonitor:
    """Monitor and enforce LLM budget limits"""
    
    # Thresholds
    CRITICAL_THRESHOLD = 0.95  # Block at 95% usage
    WARNING_THRESHOLD = 0.80   # Warn at 80% usage
    
    @staticmethod
    def check_budget() -> Tuple[bool, str, Dict]:
        """
        Check if we have sufficient LLM budget.
        
        Returns:
            (can_proceed, message, details)
            - can_proceed: bool - Whether generation can proceed
            - message: str - User-friendly message
            - details: dict - Budget details for logging
        """
        try:
            # Get Emergent LLM key from environment
            api_key = os.environ.get("EMERGENT_LLM_KEY")
            
            if not api_key:
                logger.warning("⚠️ EMERGENT_LLM_KEY not found in environment")
                return True, "OK", {}  # Allow if no key (fallback mode)
            
            # TODO: Query actual budget from Emergent API
            # For now, we'll use a conservative estimate based on recent usage patterns
            # In production, this should call: GET /api/v1/keys/{key_id}/usage
            
            # Placeholder: Assume budget is OK
            # Real implementation would query Emergent API endpoint
            details = {
                "status": "budget_check_placeholder",
                "message": "Budget monitoring active (placeholder implementation)"
            }
            
            logger.info(f"💰 Budget check: {details['message']}")
            
            # For now, always return True (allow generation)
            # Once we have Emergent API integration, we'll calculate actual usage
            return True, "Budget OK", details
            
        except Exception as e:
            logger.error(f"❌ Budget check failed: {e}")
            # On error, allow generation (fail open)
            return True, "Budget check unavailable, proceeding", {"error": str(e)}
    
    @staticmethod
    def get_budget_status() -> Dict:
        """
        Get detailed budget status for display.
        
        Returns:
            {
                "current_usage": 34.00,
                "max_budget": 50.00,
                "percent_used": 68.0,
                "remaining": 16.00,
                "status": "ok" | "warning" | "critical",
                "message": "Budget healthy"
            }
        """
        try:
            # TODO: Implement actual budget query
            # Placeholder response
            return {
                "current_usage": 0.0,
                "max_budget": 50.0,
                "percent_used": 0.0,
                "remaining": 50.0,
                "status": "ok",
                "message": "Budget monitoring placeholder - Real API integration needed"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get budget status: {e}")
            return {
                "status": "error",
                "message": f"Budget check failed: {str(e)}"
            }
    
    @staticmethod
    def format_budget_error(usage_percent: float) -> str:
        """
        Format user-friendly error message when budget is exhausted.
        
        Args:
            usage_percent: Percentage of budget used (0-100)
            
        Returns:
            User-friendly error message with actionable steps
        """
        if usage_percent >= 100:
            return (
                "⚠️ LLM API budget exhausted! "
                "Please add balance to continue: "
                "Profile → Universal Key → Add Balance"
            )
        elif usage_percent >= BudgetMonitor.CRITICAL_THRESHOLD * 100:
            return (
                f"⚠️ LLM API budget critically low ({usage_percent:.0f}% used). "
                "Please add balance soon: Profile → Universal Key"
            )
        elif usage_percent >= BudgetMonitor.WARNING_THRESHOLD * 100:
            return (
                f"⚡ LLM API budget at {usage_percent:.0f}%. "
                "Consider adding balance to avoid interruptions."
            )
        else:
            return "Budget OK"
    
    @staticmethod
    def should_block_generation(usage_percent: float) -> bool:
        """
        Determine if generation should be blocked due to budget.
        
        Args:
            usage_percent: Percentage of budget used (0-100)
            
        Returns:
            True if generation should be blocked
        """
        return usage_percent >= (BudgetMonitor.CRITICAL_THRESHOLD * 100)
    
    @staticmethod
    def get_budget_warning(usage_percent: float) -> str:
        """
        Get warning message if budget is low (but not critical).
        
        Args:
            usage_percent: Percentage of budget used (0-100)
            
        Returns:
            Warning message or empty string if OK
        """
        if usage_percent >= BudgetMonitor.WARNING_THRESHOLD * 100:
            return BudgetMonitor.format_budget_error(usage_percent)
        return ""
