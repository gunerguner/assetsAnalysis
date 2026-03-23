import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


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
    
    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _load_prompts(self) -> dict[str, Any]:
        prompts_path = self.project_root / "prompts.yaml"
        if prompts_path.exists():
            with open(prompts_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}
    
    @property
    def assets(self) -> dict[str, list[dict[str, str]]]:
        return self._config.get("assets", {})
    
    @property
    def all_assets(self) -> list[dict[str, str]]:
        result = []
        for category, assets in self.assets.items():
            for asset in assets:
                asset_with_category = asset.copy()
                asset_with_category["category"] = category
                result.append(asset_with_category)
        return result
    
    @property
    def analysis(self) -> dict[str, Any]:
        return self._config.get("analysis", {})
    
    @property
    def use_ai(self) -> bool:
        return self.analysis.get("use_ai", False)
    
    @property
    def output_format(self) -> str:
        return self.analysis.get("output_format", "markdown")
    
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
