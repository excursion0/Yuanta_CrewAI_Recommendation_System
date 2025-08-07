"""
Core system components for the financial recommendation system.
"""

from .event_bus import EventBus, EventType

__all__ = [
    'EventBus',
    'EventType'
]
