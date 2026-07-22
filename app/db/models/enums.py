"""
Enum های سیستم — استفاده می‌شوند در ستون‌های PostgreSQL.
"""

from enum import Enum


class UserStatus(str, Enum):
    """وضعیت حساب کاربری."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class DeviceStatus(str, Enum):
    """وضعیت اتصال دستگاه."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class AlertSeverity(str, Enum):
    """سطح اهمیت هشدار."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """وضعیت هشدار."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class PaymentStatus(str, Enum):
    """وضعیت پرداخت."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    REFUNDED = "refunded"


class GameResult(str, Enum):
    """نتیجه بازی."""

    WIN = "win"
    LOSE = "lose"
    ABORTED = "aborted"


class CommandStatus(str, Enum):
    """وضعیت اعمال فرمان روی دستگاه."""

    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    APPLIED = "applied"
    FAILED = "failed"
    EXPIRED = "expired"


class NotificationChannel(str, Enum):
    """کانال ارسال اعلان."""

    SMS = "sms"
    BALE = "bale"
    EMAIL = "email"


class NotificationStatus(str, Enum):
    """وضعیت ارسال اعلان."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class HardwareEventType(str, Enum):
    """انواع رویدادهای دریافتی از دستگاه (ESP8266)."""

    HEARTBEAT = "heartbeat"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    GAME_STARTED = "game_started"
    GAME_FINISHED = "game_finished"
    PRIZE_DROPPED = "prize_dropped"
    PRIZE_PASSED = "prize_passed"
    INVENTORY_SNAPSHOT = "inventory_snapshot"
    INVENTORY_LOW = "inventory_low"
    IMPACT_DETECTED = "impact_detected"
    DOOR_OPENED = "door_opened"
    DOOR_CLOSED = "door_closed"
    ERROR_DETECTED = "error_detected"
    SETTINGS_APPLIED = "settings_applied"
    SETTINGS_APPLY_FAILED = "settings_apply_failed"
    DEVICE_STATUS_CHANGED = "device_status_changed"
    MOVEMENT_DETECTED = "movement_detected"
    LOCATION_UPDATED = "location_updated"
    GEOFENCE_VIOLATION = "geofence_violation"
