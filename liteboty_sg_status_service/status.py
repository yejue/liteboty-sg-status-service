from abc import ABC, abstractmethod

from liteboty.core.service import Service


class Status(ABC):
    """抽象状态基类
     - 生命周期：检查状态 -> 是否通知 -> 生成通知文本
    """

    def __init__(self, name: str, service: Service = None):
        self.name = name
        self.notified = False  # 传递到外部函数，认为此时应该播报
        self.service = service
        self.notification_text = None

    @abstractmethod
    async def check(self):
        """检查状态"""
        ...

    def set_notification(self, notified=True, text=None):
        self.notified = notified
        self.notification_text = text

    def reset_notification(self):
        self.notified = False
        self.notification_text = None


class BatteryStatus(Status):
    """电池状态检查"""

    def __init__(self, service: Service = None):
        super().__init__("BatteryStatus", service=service)
        self.notified_30 = False  # 用于跟踪30%通知状态
        self.notified_10 = False  # 用于跟踪10%通知状态

    async def check(self):
        battery = await self.service.get_redis_key("/batt/powerval")
        if not battery:
            return

        try:
            battery = int(eval(battery))
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return

        # 当电量≥30%时，重置所有通知状态
        if battery >= 30:
            self.notified_30 = False
            self.notified_10 = False
            self.reset_notification()
            return

        # 检查是否触发10%通知
        if battery <= 10 and not self.notified_10:
            self.set_notification(text="电量低于百分之十")
            self.notified_10 = True
            return  # 触发后直接返回，避免继续检查30%

        # 检查是否触发30%通知
        if 10 < battery < 30 and not self.notified_30:
            self.set_notification(text="电量低于百分之三十")
            self.notified_30 = True
            return
