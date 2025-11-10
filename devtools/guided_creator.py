# guided_creator.py
# Raven's Guided Game Project Creator (CLI-first, Voice-ready)

import os
import shutil
from game_core_engine import GameProject, GameAsset, GameEntity, export_project
from game_framework import create_project_skeleton, SUPPORTED_LANGUAGES

DEFAULT_PROJECT_DIR = "aeris_projects"

def safe_input(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def start_guided_creation():
    print("\n=== Raven Game Creation Walkthrough ===\n")

    # Step 1: Game Title
    title = safe_input("What would you like to call your game? ")
    if not title:
        print("No title provided. Using 'Untitled_Game'.")
        title = "Untitled_Game"
    
    project_path = os.path.join(DEFAULT_PROJECT_DIR, title.replace(" ", "_"))
    os.makedirs(project_path, exist_ok=True)

    # Step 2: Platform
    print("Available platforms: desktop, android, ios, web")
    platform = safe_input("What platform is this for? [default: desktop] ").lower()
    if platform not in ["desktop", "android", "ios", "web"]:
        print("Defaulting to 'desktop'")
        platform = "desktop"

    # Step 3: Language
    print("Supported programming languages:")
    for lang in SUPPORTED_LANGUAGES:
        print(f" - {lang}")
    language = safe_input("Which language should I use for this project? ").capitalize()
    if language not in SUPPORTED_LANGUAGES:
        print(f"Unsupported or blank. Defaulting to Python.")
        language = "Python"

    # Step 4: Create project structure
    print(f"Creating project in '{project_path}'...")
    try:
        create_project_skeleton(project_path, language)
    except Exception as e:
        print(f"Error creating structure: {e}")
        return

    # Step 5: Start GameProject instance
    game = GameProject(title=title, platform=platform)

    # Step 6: Add Starter Asset
    asset_name = safe_input("Name a basic game asset to include (e.g. 'Hero Sprite'): ")
    if asset_name:
        asset = GameAsset(name=asset_name, asset_type="sprite", path=f"{project_path}/assets/{asset_name.replace(' ', '_')}.png")
        game.add_asset(asset)

    # Step 7: Add Game Entity
    entity_name = safe_input("Name a starting entity (e.g. 'Main Character'): ")
    if entity_name:
        entity = GameEntity(name=entity_name)
        game.add_entity(entity)

    # Step 8: Project Summary
    print("\nProject created with the following:")
    preview = game.compile_preview()
    for key, val in preview.items():
        print(f"{key}: {val}")

    # Step 9: Export
    confirm_export = safe_input("Export this project now? (yes/no) ").lower()
    if confirm_export == "yes":
        export_project(game, format="json")
        print(f"Project '{title}' exported successfully.")

    # Step 10: Copy to RavenDrop
    drop_path = "/aeris_drop"
    drop_target = os.path.join(drop_path, title.replace(" ", "_"))

    try:
        shutil.copytree(project_path, drop_target, dirs_exist_ok=True)
        
        # Create README.txt with summary
        readme_path = os.path.join(drop_target, "README.txt")
        with open(readme_path, "w") as f:
            f.write(f"Project: {preview['title']}\n")
            f.write(f"Platform: {preview['platform']}\n")
            f.write(f"Language: {language}\n")
            f.write(f"Assets: {len(game.assets)}\n")
            f.write(f"Entities: {len(game.entities)}\n")
            f.write("\nThis is a game project created with Raven.\nOpen the files in this folder to review or continue development.\n")

        print(f"\nProject copied to RavenDrop: {drop_target}")
        print("README.txt created to summarize project.")

    except Exception as e:
        print(f"Error sending to RavenDrop: {e}")

    print("\n=== Guided Creation Complete ===\n")

if __name__ == "__main__":
    start_guided_creation()