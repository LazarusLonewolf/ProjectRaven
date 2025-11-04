
PROJECT RAVEN — MVP STRUCTURE & BUILD NOTES

This structure represents a Phase-1 build based on Casey’s original specification.
The focus is modularity, safety, and persona consistency.

==================================================
FOLDER STRUCTURE & ROLES
==================================================

llm/
- LLaMA/MPT/GPTQ model loader (Oobabooga, LM Studio, etc.)
- Wrapper to route mode-based prompts into the model
>> [Code required]: Prompt engine + local model connection logic

memory/
- Secure vector store OR structured JSON for emotional context
- Mode-aware memory logging & retrieval
>> [Code required]: ChromaDB, SQLite, or JSON memory write/read logic

personas/
- Comfort / Muse / Shadow / Intimacy / ChildSafe configs
- CATS Tree logic modules for emotional tone selection
>> [Code required]: Python (or JS) mode router + decision tree

ui/
- Basic interface: mode toggle, vault view, logs
- Standalone or Electron GUI shell
>> [Code required]: Tkinter or Electron app logic

voice/
- Unified voice pipeline (e.g., ElevenLabs or XTTS)
- Tone control for emotional variance
>> [Code optional]: REST API call or CLI integration

safety/
- Safe-word listener
- Trauma fallback logic
- NSFW mode toggle with locks
>> [Code required]: Mode state monitoring + reactive fallback scripting

sandbox/
- Placeholder for future LoRA, plugin, or WASM upgrades
- Directory watching stub
>> [Code optional]: Simulated loader stub

docs/
- User guide, setup instruction, persona descriptions
- Developer onboarding notes

logs/
- Session transcripts, persona usage logs
- Vault snapshot state tracker

==================================================
NOTES
==================================================

This is a low-code-to-mid-code build.
Total code will remain under ~1000 lines across the project.
All logic should be modular, readable, and supported with inline comments.

Casey should be able to follow configuration files, mode definitions, and read logs—without needing to alter source code unless upgrading.
