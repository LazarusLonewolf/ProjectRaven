# project_ideation_engine.py
# Raven's narrative-driven ideation core for game projects

def gather_project_goals():
    print("[IDEATION] Let's shape your idea.")
    goal = input("What kind of game are you hoping to create? (e.g., platformer, story-based, puzzle, etc.)\n> ")
    audience = input("Who is this game intended for? (e.g., kids, teens, adults, educational use?)\n> ")
    style = input("Do you have a particular visual or narrative style in mind? (e.g., pixel art, noir, fantasy?)\n> ")
    platform = input("What platform do you want this game to run on? (e.g., PC, Android, iOS, Web?)\n> ")

    return {
        "goal": goal,
        "audience": audience,
        "style": style,
        "platform": platform
    }

def suggest_languages(project_info):
    suggestions = []

    platform = project_info.get("platform", "").lower()
    goal = project_info.get("goal", "").lower()

    if "web" in platform:
        suggestions.append("JavaScript with Phaser or HTML5")
    if "android" in platform or "ios" in platform:
        suggestions.append("Unity with C# or Godot with GDScript")
    if "pc" in platform:
        suggestions.append("Unity, Unreal Engine, or Pygame for lightweight builds")
    
    if "story" in goal or "narrative" in goal:
        suggestions.append("Ink or Twine for interactive fiction")

    if not suggestions:
        suggestions.append("Unity (C#) is a flexible default for many use cases.")

    return suggestions

def summarize_and_recommend(project_info, languages):
    print("\n[IDEATION SUMMARY]")
    print(f"Project Goal: {project_info['goal']}")
    print(f"Target Audience: {project_info['audience']}")
    print(f"Visual/Narrative Style: {project_info['style']}")
    print(f"Target Platform: {project_info['platform']}\n")

    print("[RECOMMENDED LANGUAGES/ENGINES]")
    for lang in languages:
        print(f"- {lang}")

    print("\nWould you like to scaffold a project structure based on these recommendations?")

if __name__ == "__main__":
    info = gather_project_goals()
    langs = suggest_languages(info)
    summarize_and_recommend(info, langs)
