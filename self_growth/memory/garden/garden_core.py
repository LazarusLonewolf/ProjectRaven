# garden_core.py
# Core garden model that organizes symbolic memory anchors

import os
from raven_path_initializer import set_project_root, get_full_path

set_project_root()

SEED_DIR = get_full_path("self_growth/memory/garden/seeds")

class GardenAnchor:
    def __init__(self, name, type_tag, memory_refs=None):
        self.name = name
        self.type_tag = type_tag  # e.g. "emotion", "goal", "person"
        self.memory_refs = memory_refs if memory_refs else []

    def add_memory(self, memory_id):
        if memory_id not in self.memory_refs:
            self.memory_refs.append(memory_id)

    def __repr__(self):
        return f"<GardenAnchor {self.name} ({self.type_tag}): {len(self.memory_refs)} memories>"


class RavenGarden:
    def __init__(self):
        self.anchors = {}

    def plant(self, name, type_tag):
        if name not in self.anchors:
            self.anchors[name] = GardenAnchor(name, type_tag)
        return self.anchors[name]

    def anchor_memory(self, anchor_name, memory_id):
        if anchor_name in self.anchors:
            self.anchors[anchor_name].add_memory(memory_id)
        else:
            raise ValueError(f"No anchor named '{anchor_name}' found.")

    def describe(self):
        return [repr(anchor) for anchor in self.anchors.values()]

    def scan_seeds(self):
        seed_data = {}
        for root, _, files in os.walk(SEED_DIR):
            category = os.path.basename(root)
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    seed_data.setdefault(category, []).append({
                        "filename": file,
                        "content": content
                    })
        return seed_data

if __name__ == "__main__":
    garden = RavenGarden()
    scanned = garden.scan_seeds()
    for cat, seeds in scanned.items():
        print(f"\n[Category: {cat}]")
        for s in seeds:
            print(f"  -> {s['filename']}")

