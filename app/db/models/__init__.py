"""
models SQLAlchemy.

import all models for alembic migration
"""

from app.db.models.alert import Alert
from app.db.models.audit_log import AuditLog
from app.db.models.device import Device
from app.db.models.device_command import DeviceCommand
from app.db.models.door_event import DoorEvent, DoorEventType
from app.db.models.game import Game
from app.db.models.hardware_event import HardwareEvent
from app.db.models.location import Location
from app.db.models.movement_event import MovementEvent, MovementLevel
from app.db.models.payment import Payment
from app.db.models.permission import Permission
from app.db.models.refresh_token import RefreshToken
from app.db.models.role import Role, role_permissions, user_roles
from app.db.models.user import User

__all__ = [
    # auth
    "User",
    "Role",
    "Permission",
    "RefreshToken",
    "AuditLog",
    "role_permissions",
    "user_roles",
    # devices
    "Device",
    "Location",
    # hardware events
    "HardwareEvent",
    "Payment",
    "Game",
    "DoorEvent",
    "DoorEventType",
    "MovementEvent",
    "MovementLevel",
    "DeviceCommand",
    # alerts
    "Alert",
]
