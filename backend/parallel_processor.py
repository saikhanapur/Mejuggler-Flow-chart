"""
Enterprise-Grade Parallel Processing System

Provides controlled parallelization for long-running AI operations.
Designed for scale with rate limiting and resource management.

Key Features:
- Semaphore-controlled concurrency (prevents API rate limiting)
- Per-operation timeouts
- Graceful degradation (partial results on timeout)
- Resource-aware scheduling

Usage:
    async with ParallelProcessor(max_concurrent=2) as processor:
        results = await processor.process_batch(
            items=process_titles,
            process_func=generate_flowchart,
            timeout_per_item=90
        )
"""

import asyncio
import logging
import time
from typing import List, Callable, Any, Dict, Optional, TypeVar
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ProcessingResult:
    """Result of a single item processing."""
    item_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    timed_out: bool = False


class ParallelProcessor:
    """
    Enterprise-grade parallel processor with controlled concurrency.
    
    Features:
    - Semaphore-based concurrency control
    - Per-item timeout
    - Progress callbacks
    - Graceful error handling
    """
    
    def __init__(
        self,
        max_concurrent: int = 2,
        default_timeout: float = 120.0,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        Initialize parallel processor.
        
        Args:
            max_concurrent: Maximum concurrent operations (default: 2 for API rate limits)
            default_timeout: Default timeout per item in seconds
            on_progress: Callback(current, total, item_name) for progress updates
        """
        self.max_concurrent = max_concurrent
        self.default_timeout = default_timeout
        self.on_progress = on_progress
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._completed = 0
        self._total = 0
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def process_batch(
        self,
        items: List[Dict[str, Any]],
        process_func: Callable[[Dict[str, Any]], Any],
        timeout_per_item: Optional[float] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[ProcessingResult]:
        """
        Process a batch of items in parallel with controlled concurrency.
        
        Args:
            items: List of items to process (each should have 'id' and 'name')
            process_func: Async function to process each item
            timeout_per_item: Timeout for each item (uses default if not specified)
            progress_callback: async callback(index, item, phase, sub_progress)
            
        Returns:
            List of ProcessingResult objects (in same order as input)
        """
        timeout = timeout_per_item or self.default_timeout
        self._total = len(items)
        self._completed = 0
        
        logger.info(f"🚀 Starting parallel processing of {len(items)} items (max {self.max_concurrent} concurrent)")
        
        # Create tasks for all items
        tasks = [
            self._process_item(
                index=i,
                item=item,
                process_func=process_func,
                timeout=timeout,
                progress_callback=progress_callback
            )
            for i, item in enumerate(items)
        ]
        
        # Run all tasks (semaphore controls actual concurrency)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to ProcessingResult
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ProcessingResult(
                    item_id=items[i].get('id', str(i)),
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        # Log summary
        successful = sum(1 for r in processed_results if r.success)
        failed = len(processed_results) - successful
        logger.info(f"✅ Batch complete: {successful} succeeded, {failed} failed")
        
        return processed_results
    
    async def _process_item(
        self,
        index: int,
        item: Dict[str, Any],
        process_func: Callable,
        timeout: float,
        progress_callback: Optional[Callable]
    ) -> ProcessingResult:
        """Process a single item with semaphore control and timeout."""
        item_id = item.get('id', str(index))
        item_name = item.get('name', f'Item {index + 1}')
        start_time = time.time()
        
        # Wait for semaphore (controls concurrency)
        async with self._semaphore:
            logger.info(f"⏳ Starting: {item_name}")
            
            # Notify progress - starting
            if progress_callback:
                try:
                    await progress_callback(index, item, 'starting', 0)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")
            
            try:
                # Run with timeout
                result = await asyncio.wait_for(
                    process_func(item),
                    timeout=timeout
                )
                
                duration = time.time() - start_time
                
                # Update completed count
                async with self._lock:
                    self._completed += 1
                
                # Notify progress - completed
                if progress_callback:
                    try:
                        await progress_callback(index, item, 'completed', 100)
                    except Exception as e:
                        logger.warning(f"Progress callback error: {e}")
                
                logger.info(f"✅ Completed: {item_name} in {duration:.1f}s")
                
                return ProcessingResult(
                    item_id=item_id,
                    success=True,
                    result=result,
                    duration_seconds=duration
                )
                
            except asyncio.TimeoutError:
                duration = time.time() - start_time
                logger.warning(f"⏰ Timeout: {item_name} after {timeout}s")
                
                return ProcessingResult(
                    item_id=item_id,
                    success=False,
                    error=f"Operation timed out after {timeout} seconds",
                    duration_seconds=duration,
                    timed_out=True
                )
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ Failed: {item_name} - {str(e)}")
                
                return ProcessingResult(
                    item_id=item_id,
                    success=False,
                    error=str(e),
                    duration_seconds=duration
                )
    
    @property
    def progress(self) -> tuple:
        """Get current progress (completed, total)."""
        return (self._completed, self._total)


class DocumentCache:
    """
    Simple document analysis cache to avoid re-analyzing same documents.
    
    Uses content hash for cache key.
    Thread-safe with TTL-based expiration.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()
    
    def _hash_content(self, content: str) -> str:
        """Create hash of content for cache key."""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def get(self, content: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis for content."""
        cache_key = self._hash_content(content)
        
        async with self._lock:
            if cache_key not in self._cache:
                return None
            
            # Check TTL
            timestamp = self._timestamps.get(cache_key)
            if timestamp:
                age = (datetime.now(timezone.utc) - timestamp).total_seconds()
                if age > self._ttl:
                    # Expired
                    del self._cache[cache_key]
                    del self._timestamps[cache_key]
                    return None
            
            logger.info(f"📦 Cache hit for document analysis")
            return self._cache[cache_key]
    
    async def set(self, content: str, analysis: Dict[str, Any]) -> None:
        """Cache analysis result."""
        cache_key = self._hash_content(content)
        
        async with self._lock:
            self._cache[cache_key] = analysis
            self._timestamps[cache_key] = datetime.now(timezone.utc)
            logger.info(f"💾 Cached document analysis (key: {cache_key})")
    
    def clear(self) -> int:
        """Clear all cached entries. Returns count of cleared entries."""
        count = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        return count


# Global instances
document_cache = DocumentCache()
