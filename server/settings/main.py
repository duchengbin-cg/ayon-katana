from ayon_server.settings import BaseSettingsModel, SettingsField


class KatanaSettings(BaseSettingsModel):
    """Katana addon settings.

    目前保持最小实现，后续可在此处加入：
    - 显式加载 Katana 插件
    - 发布/提交相关开关
    - 站点(site)级别路径等
    """

    enabled: bool = SettingsField(True, title="Enabled")


DEFAULT_VALUES = {
    "enabled": True,
}

