import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .model import AnalysisConfig, AssetSpec, CategorySpec
from .utils import load_yaml


class Config:
    def __init__(self, config_path: str | None = None):
        self.project_root = Path(__file__).parent.parent
        load_dotenv(self.project_root / ".env")

        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.project_root / "config.yaml"

        self._config = self._load_config()
        self._prompts = self._load_prompts()
        self._categories = self._parse_assets()
        self._analysis = self._parse_analysis()

    def _load_config(self) -> dict[str, Any]:
        return load_yaml(self.config_path, root_name="配置文件")

    def _load_prompts(self) -> dict[str, Any]:
        prompts_path = self.project_root / "prompts.yaml"
        return load_yaml(prompts_path, allow_missing=True, root_name="prompts 文件")

    def _parse_assets(self) -> list[CategorySpec]:
        assets_config = self._config.get("assets", [])
        if not isinstance(assets_config, list):
            raise ValueError("assets 配置必须是数组")

        result: list[CategorySpec] = []
        for cat_idx, category in enumerate(assets_config):
            if not isinstance(category, dict):
                raise ValueError(f"assets[{cat_idx}] 必须是对象")

            key = category.get("key")
            display_name = category.get("display_name")
            items = category.get("items", [])

            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"assets[{cat_idx}].key 必须是非空字符串")
            if not isinstance(display_name, str) or not display_name.strip():
                raise ValueError(f"assets[{cat_idx}].display_name 必须是非空字符串")
            if not isinstance(items, list):
                raise ValueError(f"assets[{cat_idx}].items 必须是数组")

            asset_specs: list[AssetSpec] = []
            for item_idx, item in enumerate(items):
                if not isinstance(item, dict):
                    raise ValueError(f"assets[{cat_idx}].items[{item_idx}] 必须是对象")

                symbol = item.get("symbol")
                name = item.get("name")
                if not isinstance(symbol, str) or not symbol.strip():
                    raise ValueError(
                        f"assets[{cat_idx}].items[{item_idx}].symbol 必须是非空字符串"
                    )
                if not isinstance(name, str) or not name.strip():
                    raise ValueError(
                        f"assets[{cat_idx}].items[{item_idx}].name 必须是非空字符串"
                    )

                asset_specs.append(
                    AssetSpec(
                        symbol=symbol.strip(),
                        name=name.strip(),
                        category_key=key.strip(),
                    )
                )

            result.append(
                CategorySpec(
                    key=key.strip(),
                    display_name=display_name.strip(),
                    items=asset_specs,
                )
            )

        return result

    def _parse_analysis(self) -> AnalysisConfig:
        analysis_config = self._config.get("analysis", {})
        if not isinstance(analysis_config, dict):
            raise ValueError("analysis 配置必须是对象")

        use_ai = bool(analysis_config.get("use_ai", False))
        output_format = analysis_config.get("output_format", "markdown")
        if not isinstance(output_format, str) or not output_format.strip():
            output_format = "markdown"

        return AnalysisConfig(use_ai=use_ai, output_format=output_format.strip())

    @property
    def categories(self) -> list[CategorySpec]:
        return self._categories

    @property
    def all_assets(self) -> list[AssetSpec]:
        return [asset for cat in self._categories for asset in cat.items]

    @property
    def category_names(self) -> dict[str, str]:
        return {cat.key: cat.display_name for cat in self._categories}

    @property
    def analysis(self) -> AnalysisConfig:
        return self._analysis

    @property
    def use_ai(self) -> bool:
        return self._analysis.use_ai

    @property
    def output_format(self) -> str:
        return self._analysis.output_format

    @property
    def zai_api_key(self) -> str | None:
        return os.getenv("ZAI_API_KEY")

    @property
    def ai_model(self) -> str:
        return os.getenv("AI_MODEL", "glm-4.5-air")

    @property
    def output_dir(self) -> Path:
        return self.project_root / "output"

    @property
    def analysis_prompt(self) -> str:
        return self._prompts.get("analysis_prompt", "")
