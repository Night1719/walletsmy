from typing import Optional
from ipaddress import ip_address, IPv4Address, IPv6Address


def extract_internal_ip(x_forwarded_for: Optional[str], real_ip: Optional[str]) -> Optional[str]:
    """
    Try to pick an internal/private IP from X-Forwarded-For chain; fallback to real_ip.
    """
    candidates = []
    if x_forwarded_for:
        parts = [p.strip() for p in x_forwarded_for.split(",") if p.strip()]
        candidates.extend(parts)
    if real_ip:
        candidates.append(real_ip)

    for candidate in candidates:
        try:
            ip_obj = ip_address(candidate)
            if (
                isinstance(ip_obj, (IPv4Address, IPv6Address))
                and (ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_loopback)
            ):
                return candidate
        except ValueError:
            continue

    return candidates[0] if candidates else None