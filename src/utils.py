from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

def load_yaml(
    path: Path, *, allow_missing: bool = False, root_name: str = "文件"
) -> dict[str, Any]:
    if not path.exists():
        if allow_missing:
            return {}
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        parsed = yaml.safe_load(f) or {}

    if not isinstance(parsed, dict):
        raise ValueError(f"{root_name}格式错误：根节点必须是对象")

    return parsed

def format_timestamp(dt: datetime | None = None) -> str:
    return (dt or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


def log_step(message: str) -> None:
    print(f"[{format_timestamp()}] {message}")
