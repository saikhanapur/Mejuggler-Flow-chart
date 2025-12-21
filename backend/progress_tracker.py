"""
Enterprise-Grade Progress Tracking System

Provides real-time progress updates for long-running operations.
Designed for scale: works the same for 10 or 100,000 concurrent users.

Architecture:
- In-memory progress store (can be replaced with Redis for multi-instance)
- SSE (Server-Sent Events) for real-time client updates
- Unique session IDs for tracking individual operations
- Automatic cleanup of stale sessions

Usage:
    tracker = ProgressTracker()
    session_id = tracker.create_session(user_id, total_steps=3)
    
    # In processing loop:
    tracker.update(session_id, step=1, message="Processing document 1/3")
    
    # Client connects via SSE to get updates
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ProgressSession:
    """Represents a single progress tracking session."""
    session_id: str
    user_id: Optional[str]
    operation_type: str
    total_steps: int
    current_step: int = 0
    current_phase: str = "initializing"
    current_message: str = ""
    sub_progress: float = 0.0  # 0-100 within current step
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_total_seconds: int = 60
    steps_completed: List[Dict[str, Any]] = field(default_factory=list)
    is_complete: bool = False
    is_error: bool = False
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def elapsed_seconds(self) -> float:
        """Calculate elapsed time since start."""
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    def estimated_remaining_seconds(self) -> int:
        """Estimate remaining time based on progress."""
        if self.current_step == 0:
            return self.estimated_total_seconds
        
        elapsed = self.elapsed_seconds()
        progress_fraction = (self.current_step + self.sub_progress / 100) / self.total_steps
        
        if progress_fraction > 0:
            estimated_total = elapsed / progress_fraction
            remaining = max(0, estimated_total - elapsed)
            return int(remaining)
        
        return self.estimated_total_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SSE transmission."""
        return {
            "sessionId": self.session_id,
            "operationType": self.operation_type,
            "totalSteps": self.total_steps,
            "currentStep": self.current_step,
            "currentPhase": self.current_phase,
            "currentMessage": self.current_message,
            "subProgress": self.sub_progress,
            "overallProgress": self._calculate_overall_progress(),
            "elapsedSeconds": int(self.elapsed_seconds()),
            "estimatedRemainingSeconds": self.estimated_remaining_seconds(),
            "stepsCompleted": self.steps_completed,
            "isComplete": self.is_complete,
            "isError": self.is_error,
            "errorMessage": self.error_message
        }
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress percentage (0-100)."""
        if self.total_steps == 0:
            return 0
        
        step_progress = (self.current_step / self.total_steps) * 100
        sub_step_contribution = (self.sub_progress / 100) * (100 / self.total_steps)
        
        return min(99.9 if not self.is_complete else 100, step_progress + sub_step_contribution)


class ProgressTracker:
    """
    Enterprise-grade progress tracking with SSE support.
    
    Thread-safe, scalable, and designed for concurrent operations.
    """
    
    # Singleton instance for global access
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._sessions: Dict[str, ProgressSession] = {}
        self._user_sessions: Dict[str, List[str]] = defaultdict(list)
        self._subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._cleanup_interval = 300  # 5 minutes
        self._session_ttl = 3600  # 1 hour
        self._initialized = True
        
        logger.info("🚀 ProgressTracker initialized")
    
    def create_session(
        self,
        user_id: Optional[str],
        operation_type: str,
        total_steps: int,
        estimated_seconds: int = 60
    ) -> str:
        """
        Create a new progress tracking session.
        
        Args:
            user_id: Optional user identifier
            operation_type: Type of operation (e.g., "multi_process_generation")
            total_steps: Total number of steps in the operation
            estimated_seconds: Estimated total time in seconds
            
        Returns:
            Unique session ID
        """
        session_id = str(uuid.uuid4())
        
        session = ProgressSession(
            session_id=session_id,
            user_id=user_id,
            operation_type=operation_type,
            total_steps=total_steps,
            estimated_total_seconds=estimated_seconds
        )
        
        self._sessions[session_id] = session
        
        if user_id:
            self._user_sessions[user_id].append(session_id)
        
        logger.info(f"📊 Created progress session {session_id} for {operation_type} ({total_steps} steps)")
        
        return session_id
    
    async def update(
        self,
        session_id: str,
        step: Optional[int] = None,
        phase: Optional[str] = None,
        message: Optional[str] = None,
        sub_progress: Optional[float] = None,
        step_completed: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update progress for a session and notify subscribers.
        
        Args:
            session_id: The session to update
            step: Current step number (1-indexed)
            phase: Current phase name
            message: Human-readable progress message
            sub_progress: Progress within current step (0-100)
            step_completed: Details of a completed step
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"⚠️ Attempted to update non-existent session: {session_id}")
            return
        
        if step is not None:
            session.current_step = step
        if phase is not None:
            session.current_phase = phase
        if message is not None:
            session.current_message = message
        if sub_progress is not None:
            session.sub_progress = sub_progress
        if step_completed is not None:
            session.steps_completed.append(step_completed)
        
        session.updated_at = datetime.now(timezone.utc)
        
        # Notify all subscribers
        await self._notify_subscribers(session_id, session.to_dict())
    
    async def complete(
        self,
        session_id: str,
        result: Optional[Dict[str, Any]] = None,
        message: str = "Operation completed successfully"
    ) -> None:
        """Mark a session as complete."""
        session = self._sessions.get(session_id)
        if not session:
            return
        
        session.is_complete = True
        session.current_step = session.total_steps
        session.sub_progress = 100
        session.current_message = message
        session.result = result
        session.updated_at = datetime.now(timezone.utc)
        
        # Notify subscribers of completion
        await self._notify_subscribers(session_id, {
            **session.to_dict(),
            "result": result
        }, event_type="complete")
        
        logger.info(f"✅ Session {session_id} completed in {session.elapsed_seconds():.1f}s")
    
    async def error(
        self,
        session_id: str,
        error_message: str
    ) -> None:
        """Mark a session as failed."""
        session = self._sessions.get(session_id)
        if not session:
            return
        
        session.is_error = True
        session.error_message = error_message
        session.updated_at = datetime.now(timezone.utc)
        
        await self._notify_subscribers(session_id, session.to_dict(), event_type="error")
        
        logger.error(f"❌ Session {session_id} failed: {error_message}")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a session."""
        session = self._sessions.get(session_id)
        return session.to_dict() if session else None
    
    async def subscribe(self, session_id: str) -> asyncio.Queue:
        """
        Subscribe to progress updates for a session.
        Returns a queue that will receive updates.
        """
        queue = asyncio.Queue()
        self._subscribers[session_id].append(queue)
        
        # Send current state immediately
        session = self._sessions.get(session_id)
        if session:
            await queue.put(("progress", session.to_dict()))
        
        return queue
    
    def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe from session updates."""
        if session_id in self._subscribers:
            try:
                self._subscribers[session_id].remove(queue)
            except ValueError:
                pass
    
    async def _notify_subscribers(
        self,
        session_id: str,
        data: Dict[str, Any],
        event_type: str = "progress"
    ) -> None:
        """Notify all subscribers of a session update."""
        subscribers = self._subscribers.get(session_id, [])
        
        for queue in subscribers:
            try:
                await queue.put((event_type, data))
            except Exception as e:
                logger.error(f"Failed to notify subscriber: {e}")
    
    def cleanup_stale_sessions(self) -> int:
        """Remove old sessions. Returns count of removed sessions."""
        now = datetime.now(timezone.utc)
        stale_sessions = []
        
        for session_id, session in self._sessions.items():
            age = (now - session.updated_at).total_seconds()
            if age > self._session_ttl:
                stale_sessions.append(session_id)
        
        for session_id in stale_sessions:
            session = self._sessions.pop(session_id, None)
            if session and session.user_id:
                try:
                    self._user_sessions[session.user_id].remove(session_id)
                except ValueError:
                    pass
            
            # Clean up subscribers
            self._subscribers.pop(session_id, None)
        
        if stale_sessions:
            logger.info(f"🧹 Cleaned up {len(stale_sessions)} stale progress sessions")
        
        return len(stale_sessions)


# Global singleton instance
progress_tracker = ProgressTracker()


# Convenience functions for common operations
def create_multi_process_session(
    user_id: Optional[str],
    process_count: int,
    process_titles: List[str]
) -> str:
    """Create a session for multi-process generation."""
    session_id = progress_tracker.create_session(
        user_id=user_id,
        operation_type="multi_process_generation",
        total_steps=process_count,
        estimated_seconds=process_count * 60  # ~60 seconds per process
    )
    
    # Store process titles in session for reference
    session = progress_tracker._sessions.get(session_id)
    if session:
        session.steps_completed = []
        # Add metadata
        setattr(session, 'process_titles', process_titles)
    
    return session_id


async def update_process_progress(
    session_id: str,
    process_index: int,
    process_title: str,
    phase: str,
    message: str,
    sub_progress: float = 0
) -> None:
    """Update progress for a specific process in multi-process generation."""
    await progress_tracker.update(
        session_id=session_id,
        step=process_index + 1,  # 1-indexed for display
        phase=phase,
        message=f"[{process_index + 1}] {process_title}: {message}",
        sub_progress=sub_progress
    )
