"""
要实现的功能：
 1. 电量低提示 30% 10%

服务生命周期：
 1. 服务启动
 2. 开启状态检测任务
"""

from liteboty.core.service import Service
from liteboty.core.message import MessageType
from . import status


class StatusService(Service):
    def __init__(self, **kwargs):
        super().__init__("StatusService", **kwargs)
        check_interval = self.config.get('check_interval', 5)
        self.status_list = [status.BatteryStatus(self), ]
        self.add_timer("check_timer", check_interval, self.check_status)

        self.tts_channel = self.config.get("outputs", {}).get("tts_channel", "/tts")

    async def check_status(self):
        for status_checker in self.status_list:
            checker = status_checker
            await checker.check()
            if checker.notified and checker.notification_text:
                tts_dict = {
                    "text": checker.notification_text,
                    "priority": 500,
                    "service_name": "StatusService"
                }
                self.logger.info(f"【StatusService】 {checker.notification_text}")
                checker.reset_notification()
                await self.publish(channel=self.tts_channel, data=tts_dict, msg_type=MessageType.JSON)

