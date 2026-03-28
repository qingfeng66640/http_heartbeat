"""HTTP 心跳推送插件入口。

用于定期向指定的本地私网服务器发送 HTTP 请求以推送心跳。
结合 Neo-MoFox 调度系统实现定期推送。
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from src.app.plugin_system.api.log_api import get_logger
from src.core.components.base import BasePlugin
from src.core.components.loader import register_plugin
from src.kernel.concurrency import get_task_manager

from .config import HttpHeartbeatConfig

logger = get_logger("http_heartbeat")


@register_plugin
class HttpHeartbeatPlugin(BasePlugin):
    """HTTP 心跳推送插件。

    定期向本地私网服务器发送 HTTP GET 请求以推送心跳。
    支持自定义推送间隔、超时、日志控制。
    """

    plugin_name = "http_heartbeat"
    plugin_version = "1.0.0"
    plugin_author = "MoFox Studio"
    plugin_description = "HTTP 心跳推送插件，定期向本地私网服务器推送心跳"
    configs = [HttpHeartbeatConfig]

    _push_task_id: str | None = None

    def __init__(self, config: HttpHeartbeatConfig | None = None) -> None:
        """初始化插件。

        Args:
            config: 插件配置实例
        """
        super().__init__(config)
        self.config: HttpHeartbeatConfig = config or HttpHeartbeatConfig()

    async def on_plugin_loaded(self) -> None:
        """插件加载时启动心跳推送任务。"""
        logger.info(
            f"HTTP 心跳推送插件已加载 | "
            f"推送 URL: {self.config.push.push_url} | "
            f"推送间隔: {self.config.push.interval_seconds}s"
        )

        if not self.config.plugin.enabled:
            logger.info("HTTP 心跳推送插件已禁用")
            return

        # 延迟注册推送任务：等待调度器启动
        async def _delayed_scheduler_register() -> None:
            """延迟注册推送任务，等待调度器启动。"""
            for attempt in range(30):
                await asyncio.sleep(1.0)
                try:
                    from src.kernel.scheduler import get_unified_scheduler

                    scheduler = get_unified_scheduler()
                    if scheduler._running:
                        await self._register_scheduler_tasks()
                        return
                except ImportError:
                    logger.warning("Scheduler 不可用，放弃注册推送任务")
                    return
                except Exception as e:
                    if attempt == 29:
                        logger.warning(f"等待调度器启动超时(30s)，放弃注册推送任务: {e}")
                    continue
            logger.warning("等待调度器启动超时(30s)，放弃注册推送任务")

        get_task_manager().create_task(
            _delayed_scheduler_register(),
            name="http_heartbeat_scheduler_init",
            daemon=True,
        )

    async def _register_scheduler_tasks(self) -> None:
        """注册定时推送任务到 scheduler。"""
        if not self.config.plugin.enabled:
            logger.info("插件已禁用，跳过推送任务注册")
            return

        try:
            from src.kernel.scheduler import TriggerType, get_unified_scheduler

            scheduler = get_unified_scheduler()
        except ImportError:
            logger.warning("Scheduler 不可用，跳过推送任务注册")
            return

        # 构建推送回调
        async def _push_callback() -> None:
            """scheduler 调度的推送回调。"""
            await self._do_push()

        # 注册周期性推送任务
        interval_seconds = self.config.push.interval_seconds
        self._push_task_id = await scheduler.create_schedule(
            callback=_push_callback,
            trigger_type=TriggerType.TIME,
            trigger_config={"delay_seconds": interval_seconds},
            is_recurring=True,
            task_name="http_heartbeat_push_task",
            force_overwrite=True,
            timeout=self.config.push.timeout_seconds + 5.0
        )

        logger.info(
            f"心跳推送任务已注册 (ID: {self._push_task_id}) | "
            f"间隔: {interval_seconds}s"
        )

        # 启动时立即执行一次首次推送
        logger.info("执行启动首次推送...")
        try:
            await _push_callback()
        except Exception as e:
            logger.warning(f"启动首次推送失败（不影响后续定时推送）: {e}")

    async def on_plugin_unloading(self) -> None:
        """插件卸载时停止心跳推送任务。"""
        await self._stop_push()
        logger.info("HTTP 心跳推送插件已卸载")

    def get_components(self) -> list[type]:
        """获取插件内所有组件类。

        Returns:
            list[type]: 插件内所有组件类的列表
        """
        # 本插件是一个后台服务，没有公开的组件
        return []

    async def _stop_push(self) -> None:
        """停止心跳推送。"""
        if not self._push_task_id:
            return

        try:
            from src.kernel.scheduler import get_unified_scheduler

            scheduler = get_unified_scheduler()
            await scheduler.remove_schedule(self._push_task_id)
            logger.info(f"心跳推送任务已停止 (ID: {self._push_task_id})")
        except Exception as e:
            logger.error(f"停止心跳推送任务失败: {e}")
        finally:
            self._push_task_id = None

    async def _do_push(self) -> None:
        """执行一次心跳推送。"""
        import urllib.request
        import urllib.error

        push_url = self.config.push.push_url
        timeout = self.config.push.timeout_seconds
        headers = self.config.push.headers.copy()

        # 设置默认 User-Agent，避免被服务器因爬虫特征拒绝 (403 Forbidden)
        if "User-Agent" not in headers:
            headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

        # 在 URL 末尾附加时间戳
        url_with_timestamp = push_url + str(int(time.time()))

        try:
            # 构造 Request 对象以携带 Headers
            req = urllib.request.Request(url_with_timestamp, headers=headers)

            # 在线程中执行阻塞的 HTTP 请求
            def _send_request():
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    return response.read()

            await asyncio.to_thread(_send_request)

            if self.config.push.enable_logging:
                logger.info(f"✓ 心跳推送成功 | URL: {push_url}")

        except urllib.error.HTTPError as e:
            logger.error(
                f"✗ 心跳推送失败 | URL: {push_url} | "
                f"状态码: {e.code} | 错误: {e.reason}"
            )
        except urllib.error.URLError as e:
            logger.error(
                f"✗ 心跳推送失败 | URL: {push_url} | "
                f"错误: {type(e).__name__}: {str(e)}"
            )
        except asyncio.TimeoutError:
            logger.error(
                f"✗ 心跳推送超时 | URL: {push_url} | "
                f"超时时间: {timeout}s"
            )
        except Exception as e:
            logger.error(
                f"✗ 心跳推送异常 | URL: {push_url} | "
                f"错误: {type(e).__name__}: {str(e)}"
            )
