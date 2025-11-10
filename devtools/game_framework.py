# game_framework.py – Raven's Unified Game Creation Core
# Merged on 2025-08-07 from:
#   - game_framework.py (2025-07-02)
#   - game_framework_hybrid.py (2025-06-17)
#
# Goals:
# - One framework to manage templates AND language-first scaffolds
# - Backward-compatible function signatures
# - Simple, portable filesystem behavior (no hardcoded absolute paths)

import os
from datetime import datetime
from pathlib import Path

# -------------------------------------------------------------------
# Supported targets
# -------------------------------------------------------------------
SUPPORTED_LANGUAGES = ["python", "javascript", "csharp", "lua", "java"]
SUPPORTED_PLATFORMS  = ["desktop", "android", "ios", "web"]

# -------------------------------------------------------------------
# Template-driven API (from original game_framework.py)
# -------------------------------------------------------------------
class GameTemplate:
    def __init__(self, name, description, components):
        self.name = name
        self.description = description
        self.components = components  # list[str]

class TemplateLibrary:
    def __init__(self):
        # Fixed a couple minor punctuation issues and typos
        self.templates = {
            "Platformer": GameTemplate(
                "Platformer",
                "Jump, run, and navigate obstacles.",
                [
                    "player",
                    "platforms",
                    "enemies",
                    "collectibles",
                    "tile_map",
                    "gravity_physics",
                    "collision_detection",
                ],
            ),
            "VisualNovel": GameTemplate(
                "VisualNovel",
                "Text-driven story with character images and branching paths.",
                ["scenes", "dialogue", "choices"],
            ),
            "PuzzleGrid": GameTemplate(
                "PuzzleGrid",
                "Solve grid-based puzzles, patterns, or logic games.",
                ["grid", "tiles", "logic_rules", "state_tracker", "scoring_system"],
            ),
            "RPG": GameTemplate(
                "RPG",
                "Role-playing elements with quests and character growth.",
                ["character_stats", "inventory", "quests", "combat"],
            ),
            "Sandbox": GameTemplate(
                "Sandbox",
                "Open-ended interaction with systems and creativity tools.",
                ["terrain", "building_system", "physics_engine", "world_state_memory", "modular_engine"],
            ),
            "TextAdventure": GameTemplate(
                "TextAdventure",
                "Narrative-driven command input game.",
                ["parser", "story_nodes", "dialogue_engine", "inventory_system"],
            ),
            "TopDownShooter": GameTemplate(
                "TopDownShooter",
                "Top-down perspective with player, projectiles, and enemy waves.",
                ["player_controls", "enemy_spawns", "projectiles", "sprite_system", "physics_engine"],
            ),
        }
        self.pending_approvals = {}

    # Safe template submission/approval (unchanged behavior)
    def safe_add_template(self, name, description, components, submitted_by="system"):
        if not isinstance(name, str) or not name.isidentifier():
            return "Invalid template name."
        if not isinstance(description, str) or len(description) < 10:
            return "Description too short or malformed."
        if not isinstance(components, list) or not all(isinstance(c, str) for c in components):
            return "Components must be a list of strings."
        if name in self.templates or name in self.pending_approvals:
            return f"Template '{name}' already exists or is pending approval."

        self.pending_approvals[name] = {
            "template": GameTemplate(name, description, components),
            "submitted_by": submitted_by,
            "timestamp": datetime.now().isoformat(),
        }
        return f"Template '{name}' submitted for approval."

    def approve_template(self, name):
        if name in self.pending_approvals:
            self.templates[name] = self.pending_approvals.pop(name)["template"]
            return f"Template '{name}' approved and added."
        return f"No pending template named '{name}'."

    def get_available_templates(self):
        return list(self.templates.keys())

    def get_pending_templates(self):
        return list(self.pending_approvals.keys())

# -------------------------------------------------------------------
# Language-first scaffold API (from hybrid)
# -------------------------------------------------------------------
class ProjectSkeleton:
    def __init__(self, title, language):
        self.title = title
        self.language = language.lower()
        self.structure = {
            "main": f"main.{self._ext()}",
            "assets": [],
            "scenes": [],
        }

    def _ext(self):
        return {
            "python": "py",
            "javascript": "js",
            "csharp": "cs",
            "lua": "lua",
            "java": "java",
        }.get(self.language, "txt")

    def build_summary(self):
        return {
            "title": self.title,
            "language": self.language,
            "files": list(self.structure.keys()),
        }

# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------
def detect_game_language(file_path):
    ext = Path(file_path).suffix.lower()
    return {
        ".py": "python",
        ".js": "javascript",
        ".cs": "csharp",
        ".lua": "lua",
        ".java": "java",
    }.get(ext, "unknown")

# -------------------------------------------------------------------
# Skeleton builders (both styles)
# -------------------------------------------------------------------
def create_template_skeleton(template_name, library: TemplateLibrary, destination):
    """
    Build a component-file skeleton from a named template into 'destination/<TemplateName>/'.
    Returns the created path, or a string error.
    """
    if not isinstance(library, TemplateLibrary) or template_name not in library.templates:
        return f"Template '{template_name}' not found."
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    template = library.templates[template_name]
    structure_path = destination / template_name
    structure_path.mkdir(parents=True, exist_ok=True)

    for comp in template.components:
        comp_file = structure_path / f"{comp}.txt"
        comp_file.write_text(f"# Placeholder for {comp}", encoding="utf-8")

    return str(structure_path)

def create_language_skeleton(destination, language, title=None):
    """
    Build a minimal language-first scaffold in 'destination'.
    Creates main.<ext>, assets/, scenes/ and a README.
    Returns the destination path.
    """
    language = (language or "").lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("Unsupported language. Choose from: " + ", ".join(SUPPORTED_LANGUAGES))

    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    # Create core folders
    (destination / "assets").mkdir(exist_ok=True)
    (destination / "scenes").mkdir(exist_ok=True)

    # Create main file
    ext = {
        "python": "py",
        "javascript": "js",
        "csharp": "cs",
        "lua": "lua",
        "java": "java",
    }[language]
    main_path = destination / f"main.{ext}"
    if not main_path.exists():
        main_path.write_text("// Entry point\n" if ext != "py" else "# Entry point\n", encoding="utf-8")

    # Optional README
    readme = destination / "README.txt"
    title_text = f"{title}" if title else destination.name
    readme.write_text(
        f"Project: {title_text}\nLanguage: {language}\n\nScaffold created by Raven.\n",
        encoding="utf-8"
    )

    return str(destination)

# -------------------------------------------------------------------
# Backward-compatible facade
# -------------------------------------------------------------------
def create_project_skeleton(*args, **kwargs):
    """
    Backward-compatible entry point used by existing tools.

    Supported call patterns:

    1) Template-style (original):
       create_project_skeleton(template_name, library: TemplateLibrary, destination)

    2) Language-style (hybrid / guided_creator expectation):
       create_project_skeleton(destination, language, title=None)

    This function inspects argument types/count and dispatches accordingly.
    """
    # Pattern 1: (template_name:str, library:TemplateLibrary, destination:str/Path)
    if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], TemplateLibrary):
        template_name, library, destination = args
        return create_template_skeleton(template_name, library, destination)

    # Pattern 2: (destination:str/Path, language:str[, title:str])
    if 2 <= len(args) <= 3 and isinstance(args[0], (str, Path)) and isinstance(args[1], str):
        destination = args[0]
        language    = args[1]
        title       = args[2] if len(args) == 3 else kwargs.get("title")
        return create_language_skeleton(destination, language, title=title)

    # If we get here, the signature is unexpected
    raise TypeError(
        "create_project_skeleton expected either:\n"
        "  (template_name:str, library:TemplateLibrary, destination) OR\n"
        "  (destination, language[, title])"
    )

# -------------------------------------------------------------------
# Optional helper (kept for convenience)
# -------------------------------------------------------------------
def sample_templates():
    return [
        {"name": "TextAdventure", "language": "python", "description": "Simple story-driven engine."},
        {"name": "TopDownShooter", "language": "javascript", "description": "Arcade-style shooter for web."},
        {"name": "PuzzleGrid", "language": "lua", "description": "2D puzzle layout for logic games."},
        {"name": "Platformer", "language": "csharp", "description": "Unity-based classic side-scroller."},
    ]
