# src/notifiers/wechat.py
import logging
import httpx
from src.notifiers.base import BaseNotifier
from src.models import AlertMessage

logger = logging.getLogger(__name__)


class WechatNotifier(BaseNotifier):
    """WeChat push notification channel via Server酱/PushPlus."""

    def __init__(self, push_key: str = ""):
        self.push_key = push_key

    @property
    def name(self) -> str:
        return "wechat"

    def is_enabled(self) -> bool:
        return bool(self.push_key)

    async def send(self, msg: AlertMessage) -> bool:
        if not self.is_enabled():
            logger.warning("WechatNotifier is disabled (no push_key)")
            return False

        title = f"机票提醒 - {msg.route_name}"
        content = f"""
## 航班信息
- **航线**: {msg.origin} → {msg.destination}
- **日期**: {msg.departure_date}
- **价格**: {msg.price} {msg.currency}
- **航司**: {msg.airline}
- **来源**: {msg.source}

## 触发规则
- **类型**: {msg.rule_type}
- **详情**: {msg.rule_message}
"""
        url = f"https://sctapi.ftqq.com/{self.push_key}.send"
        payload = {"title": title, "desp": content}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, data=payload, timeout=10)
                resp.raise_for_status()
                logger.info(f"WeChat notification sent: {title}")
                return True
        except Exception as e:
            logger.error(f"WeChat notification failed: {e}")
            return False
