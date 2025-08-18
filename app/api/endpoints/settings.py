from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.system_settings import SystemSettings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class SettingsUpdate(BaseModel):
    # Subset of fields for simplicity; UI will post these
    min_tvl_usd: Optional[float] = None
    max_fee_percent: Optional[float] = None
    max_slippage_percent: Optional[float] = None
    enable_honeypot_check: Optional[bool] = None
    enable_rugpull_check: Optional[bool] = None
    use_dynamic_position_sizing: Optional[bool] = None
    position_size_usd: Optional[float] = None
    kelly_fraction: Optional[float] = None
    tp1_percent: Optional[float] = None
    tp1_size_percent: Optional[float] = None
    trailing_stop_enabled: Optional[bool] = None
    trailing_stop_pct: Optional[float] = None
    hard_stop_loss_pct: Optional[float] = None
    use_jito_bundles: Optional[bool] = None
    priority_fee_micro_lamports: Optional[int] = None
    compute_unit_limit: Optional[int] = None
    rpc_primary_url: Optional[str] = None
    rpc_fallback_urls: Optional[str] = None
    sniper_enabled: Optional[bool] = None
    sniper_auto_trading: Optional[bool] = None
    sniper_min_liquidity_usd: Optional[float] = None
    sniper_max_slippage_percent: Optional[float] = None
    sniper_quick_exit_tp_pct: Optional[float] = None
    sniper_quick_exit_sl_pct: Optional[float] = None
    sniper_min_token_age_minutes: Optional[int] = None
    sniper_min_volume_usd: Optional[float] = None
    token_denylist: Optional[str] = None
    token_allowlist: Optional[str] = None
    wallet_watchlist: Optional[str] = None
    kill_switch_enabled: Optional[bool] = None
    kill_on_error_rate_pct: Optional[float] = None
    kill_on_block_rate_pct: Optional[float] = None


async def _get_or_create_settings(db: AsyncSession) -> SystemSettings:
    result = await db.execute(select(SystemSettings).order_by(SystemSettings.id.asc()).limit(1))
    settings_row = result.scalar_one_or_none()
    if not settings_row:
        settings_row = SystemSettings()
        db.add(settings_row)
        await db.commit()
        await db.refresh(settings_row)
    return settings_row


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: AsyncSession = Depends(get_db)):
    row = await _get_or_create_settings(db)
    return templates.TemplateResponse("settings.html", {"request": request, "settings": row})


@router.get("/settings/json")
async def get_settings(db: AsyncSession = Depends(get_db)):
    row = await _get_or_create_settings(db)
    return {k: getattr(row, k) for k in row.__table__.columns.keys()}


@router.post("/settings")
async def update_settings(request: Request, db: AsyncSession = Depends(get_db)):
    row = await _get_or_create_settings(db)
    content_type = request.headers.get("content-type", "")
    data = {}
    if "application/json" in content_type:
        payload = await request.json()
        data = payload or {}
    else:
        # Parse form data from HTMX
        form = await request.form()
        for k, v in form.items():
            if v in ("on", "true", "True"):  # checkboxes
                data[k] = True
            elif v in ("off", "false", "False", ""):
                # If checkbox unchecked it won't be posted; leave as-is
                # For text inputs empty means None
                pass
            else:
                data[k] = v

        # Handle unchecked checkboxes explicitly by looking at known boolean fields
        bool_fields = [
            "enable_honeypot_check", "enable_rugpull_check", "use_dynamic_position_sizing",
            "trailing_stop_enabled", "use_jito_bundles", "sniper_enabled", "sniper_auto_trading",
            "kill_switch_enabled"
        ]
        for bf in bool_fields:
            if bf not in data and bf in row.__table__.columns.keys():
                # If not present in form, set to False
                data[bf] = False

    # Coerce numeric fields
    def to_float(x):
        try:
            return float(x)
        except Exception:
            return None
    def to_int(x):
        try:
            return int(float(x))
        except Exception:
            return None

    float_fields = [
        "min_tvl_usd","max_fee_percent","max_slippage_percent","position_size_usd","kelly_fraction",
        "tp1_percent","tp1_size_percent","trailing_stop_pct","hard_stop_loss_pct","sniper_min_liquidity_usd",
        "sniper_max_slippage_percent","sniper_quick_exit_tp_pct","sniper_quick_exit_sl_pct","sniper_min_volume_usd",
        "kill_on_error_rate_pct","kill_on_block_rate_pct"
    ]
    int_fields = ["priority_fee_micro_lamports","compute_unit_limit","sniper_min_token_age_minutes"]

    for k in list(data.keys()):
        if k in float_fields:
            val = to_float(data[k])
            if val is not None:
                data[k] = val
            else:
                data.pop(k)
        elif k in int_fields:
            val = to_int(data[k])
            if val is not None:
                data[k] = val
            else:
                data.pop(k)

    for field, value in data.items():
        if field in row.__table__.columns.keys():
            setattr(row, field, value)
    await db.commit()
    return {"status": "ok"}

