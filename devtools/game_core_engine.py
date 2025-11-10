# Raven's Core Game Development Framework
# Provides base tools for interactive builds and export scaffolding

import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

class GameAsset:
    def __init__(self, name, asset_type, path=None):
        self.name = name
        self.asset_type = asset_type  # sprite, sound, script, etc.
        self.path = path
        self.meta = {}

    def describe(self):
        return f"{self.asset_type.upper()} - {self.name} @ {self.path or 'in-memory'}"

class GameEntity:
    def __init__(self, name, components=None):
        self.name = name
        self.components = components if components else []

    def add_component(self, component):
        self.components.append(component)

    def summary(self):
        return {
            "name": self.name,
            "component_count": len(self.components),
            "components": [type(c).__name__ for c in self.components]
        }

class GameProject:
    def __init__(self, title, platform="desktop"):
        self.title = title
        self.platform = platform  # desktop, android, ios, web
        self.assets = []
        self.entities = []
        self.settings = {}

    def add_asset(self, asset):
        self.assets.append(asset)

    def add_entity(self, entity):
        self.entities.append(entity)

    def compile_preview(self):
        return {
            "title": self.title,
            "platform": self.platform,
            "assets": [a.describe() for a in self.assets],
            "entities": [e.summary() for e in self.entities]
        }

def get_supported_platforms():
    return ["desktop", "android", "ios", "web"]

def export_project(project, format="json"):
    """Exports game project preview to local file."""
    print(f"[EXPORT] Preparing to export '{project.title}' for {project.platform} in {format.upper()} format...")
    if format == "json":
        output_path = EXPORT_DIR / f"{project.title.replace(' ', '_')}_preview.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(project.compile_preview(), f, indent=4)
        print(f"[EXPORT] Saved to {output_path}")
        return output_path
    return True

if __name__ == "__main__":
    # Minimal functional test
    p = GameProject("Prototype Quest")
    p.add_asset(GameAsset("Hero Sprite", "sprite", "/assets/hero.png"))
    p.add_entity(GameEntity("Main Character"))
    print(p.compile_preview())
    export_project(p)
