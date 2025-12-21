"""
AI Call Wrapper with Comprehensive Error Handling
Wraps all AI API calls with timeout, retry, and error handling
"""
import asyncio
import time
import logging
from typing import Optional, Dict, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage

from error_handling import ErrorCatalog, create_error_response

logger = logging.getLogger(__name__)


class AICallError(Exception):
    """Base exception for AI call failures"""
    def __init__(self, error_catalog_item, technical_detail: str = None):
        self.error_catalog_item = error_catalog_item
        self.technical_detail = technical_detail
        super().__init__(str(error_catalog_item.dict()))


class AICallWrapper:
    """
    Wrapper for AI API calls with error handling, timeouts, and retries
    """
    
    def __init__(self, api_key: str, timeout_seconds: int = 60, max_retries: int = 2):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
    
    async def call_with_timeout(
        self,
        chat: LlmChat,
        message: UserMessage,
        call_name: str = "AI Call"
    ) -> str:
        """
        Make AI call with timeout and error handling
        
        Args:
            chat: LlmChat instance
            message: UserMessage to send
            call_name: Name for logging (e.g., "Extract Structure")
        
        Returns:
            Response text from AI
        
        Raises:
            AICallError: If call fails after retries
        """
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"🤖 {call_name} - Attempt {attempt + 1}/{self.max_retries + 1}")
                start_time = time.time()
                
                # Create timeout
                response = await asyncio.wait_for(
                    chat.send_message(message),
                    timeout=self.timeout_seconds
                )
                
                duration = time.time() - start_time
                logger.info(f"✅ {call_name} completed in {duration:.1f}s")
                
                # Validate response
                if not response or len(response.strip()) == 0:
                    logger.warning(f"⚠️ {call_name} returned empty response")
                    if attempt < self.max_retries:
                        await asyncio.sleep(2)  # Brief delay before retry
                        continue
                    else:
                        raise AICallError(
                            ErrorCatalog.AI_INVALID_RESPONSE,
                            f"{call_name} returned empty response after {self.max_retries + 1} attempts"
                        )
                
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"⏱️ {call_name} timeout after {self.timeout_seconds}s")
                if attempt < self.max_retries:
                    logger.info(f"🔄 Retrying {call_name}...")
                    await asyncio.sleep(2)
                    continue
                else:
                    raise AICallError(
                        ErrorCatalog.AI_TIMEOUT,
                        f"{call_name} timed out after {self.timeout_seconds}s, {self.max_retries + 1} attempts"
                    )
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for specific error types
                if "rate limit" in error_msg or "429" in error_msg:
                    logger.error(f"🚫 Rate limit exceeded on {call_name}")
                    raise AICallError(
                        ErrorCatalog.RATE_LIMIT_EXCEEDED,
                        f"{call_name}: {str(e)}"
                    )
                
                elif "api key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                    logger.error(f"🔑 API key issue on {call_name}")
                    raise AICallError(
                        ErrorCatalog.API_KEY_MISSING,
                        f"{call_name}: {str(e)}"
                    )
                
                elif attempt < self.max_retries:
                    logger.warning(f"⚠️ {call_name} failed with error: {e}")
                    logger.info(f"🔄 Retrying {call_name}...")
                    await asyncio.sleep(2)
                    continue
                
                else:
                    logger.error(f"❌ {call_name} failed after {self.max_retries + 1} attempts: {e}")
                    raise AICallError(
                        ErrorCatalog.AI_INVALID_RESPONSE,
                        f"{call_name} error: {str(e)}"
                    )
        
        # Should never reach here, but just in case
        raise AICallError(
            ErrorCatalog.UNKNOWN_ERROR,
            f"{call_name} failed unexpectedly"
        )
    
    async def call_parallel(
        self,
        calls: list[tuple[LlmChat, UserMessage, str]]
    ) -> list[str]:
        """
        Make multiple AI calls in parallel with error handling
        
        Args:
            calls: List of (chat, message, call_name) tuples
        
        Returns:
            List of response texts
        
        Raises:
            AICallError: If any call fails
        """
        tasks = [
            self.call_with_timeout(chat, message, name)
            for chat, message, name in calls
        ]
        
        try:
            results = await asyncio.gather(*tasks)
            return results
        except AICallError:
            # Re-raise AI call errors
            raise
        except Exception as e:
            logger.error(f"❌ Parallel AI calls failed: {e}")
            raise AICallError(
                ErrorCatalog.UNKNOWN_ERROR,
                f"Parallel calls error: {str(e)}"
            )
    
    def validate_json_response(self, response: str, call_name: str) -> Dict[str, Any]:
        """
        Parse and validate JSON response from AI
        
        Args:
            response: Raw response text
            call_name: Name for logging
        
        Returns:
            Parsed JSON dict
        
        Raises:
            AICallError: If JSON is invalid
        """
        import json
        import re
        
        try:
            # Try direct parse first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to extract JSON from anywhere in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # All parsing attempts failed
            logger.error(f"❌ {call_name} returned invalid JSON")
            logger.debug(f"Response preview: {response[:200]}")
            raise AICallError(
                ErrorCatalog.AI_INVALID_RESPONSE,
                f"{call_name} returned invalid JSON. Response preview: {response[:100]}"
            )
