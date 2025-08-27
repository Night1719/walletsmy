from typing import Optional
from prometheus_client import Counter, Summary, Gauge, start_http_server
from config import METRICS_PORT

_notifications = Counter(
    "tgbot_notifications_total",
    "Notifications sent by type",
    labelnames=["type"],
)

_api_errors = Counter(
    "tgbot_api_errors_total",
    "API errors encountered",
    labelnames=["where"],
)

_cycles = Summary(
    "tgbot_background_cycle_seconds",
    "Background cycle duration in seconds",
)

_sessions_gauge = Gauge(
    "tgbot_sessions",
    "Number of active sessions",
)


def inc_notification(kind: str) -> None:
    _notifications.labels(kind).inc()


def inc_api_error(where: str) -> None:
    _api_errors.labels(where).inc()


def observe_cycle(seconds: float) -> None:
    _cycles.observe(seconds)


def set_sessions(count: int) -> None:
    _sessions_gauge.set(count)


def start_metrics_server(port: Optional[int] = None) -> None:
    start_http_server(port or METRICS_PORT)