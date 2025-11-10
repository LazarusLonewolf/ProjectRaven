
# seed_activator.py – Central bridge to identify actionable seeds

from garden_core import RavenGarden

def get_actionable_seeds(tags=None):
    garden = RavenGarden()
    seeds = garden.scan_seeds()
    actionable = []

    for category, entries in seeds.items():
        for seed in entries:
            if tags:
                if any(tag in seed['content'] for tag in tags):
                    actionable.append({
                        "category": category,
                        "filename": seed['filename'],
                        "content": seed['content']
                    })
            else:
                actionable.append({
                    "category": category,
                    "filename": seed['filename'],
                    "content": seed['content']
                })
    return actionable
