"""HTTP 心跳推送插件配置定义。

用于向服务器定期发送心跳推送请求。
"""

from __future__ import annotations

from typing import ClassVar

from src.core.components.base.config import BaseConfig, Field, SectionBase, config_section


class HttpHeartbeatConfig(BaseConfig):
    """HTTP 心跳推送插件配置。"""

    config_name: ClassVar[str] = "config"
    config_description: ClassVar[str] = "HTTP 心跳推送插件配置"

    @config_section("plugin", title="插件设置", tag="plugin", order=0)
    class PluginSection(SectionBase):
        """插件基础配置。"""

        enabled: bool = Field(
            default=True,
            description="是否启用 HTTP 心跳推送插件",
            label="启用插件",
            tag="plugin",
            order=0
        )

    @config_section("push", title="推送配置", tag="network", order=10)
    class PushSection(SectionBase):
        """心跳推送配置。"""

        push_url: str = Field(
            default="http://localhost:8080/api/push/token?status=up&msg=OK&ping=",
            description="推送服务器 URL（本地私网地址）",
            label="推送 URL",
            placeholder="http://server:port/api/push/token?status=up&msg=OK&ping=",
            tag="network",
            hint="URL 末尾通常是时间戳，插件会自动附加当前时间",
            order=0
        )

        interval_seconds: int = Field(
            default=10,
            description="推送间隔（秒）",
            label="推送间隔",
            ge=1,
            le=3600,
            tag="network",
            hint="建议 10-300 秒之间",
            order=1
        )

        timeout_seconds: float = Field(
            default=5.0,
            description="单次请求超时时间（秒）",
            label="请求超时",
            ge=1.0,
            le=30.0,
            tag="network",
            order=2
        )

        enable_logging: bool = Field(
            default=True,
            description="是否记录推送日志",
            label="启用日志",
            tag="logging",
            order=3
        )

        headers: dict[str, str] = Field(
            default_factory=dict,
            description="推送时的额外 HTTP 请求头",
            label="自定义 Header",
            tag="network",
            hint='格式示例: {"User-Agent": "Mozilla/5.0"}',
            order=4
        )

    plugin: PluginSection = Field(default_factory=PluginSection)
    push: PushSection = Field(default_factory=PushSection)
