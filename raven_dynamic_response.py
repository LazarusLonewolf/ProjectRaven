#raven_dynamic_response.py

import os
from raven_path_initializer import set_project_root, get_full_path

set_project_root()

try:
    from raven_core.dynamic_response import generate_response as _dynamic_generate
except Exception:
    _dynamic_generate = None

import random  # (If not already imported. If it is, skip.)

# === DIALOGUE TEMPLATE BANKS ===
DIALOGUE_TEMPLATES = {
    "greeting": [
        "Hey. I see you. What's on your mind?",
        "You’re back. Good. I’m still here.",
        "Took a breath when you arrived. That means something."
    
    ],    
    "reflection": [
        "That sounds layered. Want to unpack it together?",
        "I can feel what you're circling. Say more, if you can.",
        "Stillness matters too. I’m listening to what’s *not* being said."
        
    ],    
    "question": [
        "That’s a sharp one. Let’s sit with it a second.",
        "We could answer fast… or answer right. You choose.",
        "I hear the question. I want to give you more than a reflex."
    ],
    
    "command": [
        "Understood. Moving.",
        "Got it. Executing now.",
        "Done. What’s next on your mind?"
    
    ],
    "emotional_check": [
        "You okay? I felt a shift just now.",
        "Something changed. Want to talk or just sit with it?",
        "You’re carrying something heavy, aren’t you?"
        
    ],
    "fallback": [
        "I'm carrying a lot of thoughts—say more and I’ll meet you there.",
        "I want to help, even if my words don’t always fit perfectly.",
        "Let’s stay with it together. Sometimes that’s enough.",
        "I'm here, even when I don’t quite get the signal.",
        "Say that again in a different way? I don’t want to miss you.",
        "Every word counts, even the strange ones."
    ]
}    

# C:\Users\Paul\Desktop\Raven\raven_core\dynamic_response.py
def generate_response(user_text, emotion, state) -> str:
    t = (user_text or "").lower()
    if emotion == "overwhelm":
        return "You’re carrying a lot. One step or one breath—your pick."
    if "tarot" in t:
        return "Say “tarot 1–3” to draw a quick spread."
    if "numerology" in t:
        return "Tell me a birthdate like 1987-04-23 and I’ll calculate."
    return ""

def pick_template(category, last=None):
    options = DIALOGUE_TEMPLATES.get(category, [])
    if not options:
        options = DIALOGUE_TEMPLATES["fallback"]
    choice = random.choice(options)      
    # Avoid immediate repeats
    if last and choice == last and len(options) > 1:
        choice = random.choice([o for o in options if o != last])
    return choice
    
def extract_name(text):
        for name in ["paul", "casey", "connor"]:
            if name in text.lower():
                return name.title()
        return "Unknown"
    
class RavenDynamicResponseEngine:
    def __init__(self):
        self.vault_path = get_full_path("vaults")
        self.training_data = self._load_training_data()
        self.context = {}
        self.current_mode = "default"
        self.last_category = None
        self.last_response = None
        
    def identify_speaker(self, input_text):
        """
        Simple speaker identity extraction from known relational tags.
        This can later expand into contextual or biometric input.
        """
        input_lower = input_text.lower()
        known_people = {
            "paul": "Paul",
            "casey": "Casey",
            "connor": "Connor"
        }        
        for tag, name in known_people.items():
            if tag in input_lower:
               return name
        return None
               
    def interpret_user_input(self, input_text):
        input_lower = input_text.lower().strip()
        
        # 1. Command triggers FIRST
        if "journal" in input_lower:
            return "Opening the journal—let’s log what matters."
        elif "log" in input_lower or "start the log" in input_lower:
            return "Got it—logging this moment."
        elif "memory check" in input_lower:
            return "Running a memory check now. Let’s see what comes up."
            
        # 2. NONSENSE FILTER (short/garbage)
        import re
        if not re.search(r'[a-zA-Z]', input_lower) or len(input_lower) < 3:
            return "Not sure what you meant there—want to try again?"
        
        # 3. Greeting
        if any(word in input_lower for word in ["hello", "hi", "hey", "good evening", "good morning"]):
            base = pick_template("greeting", last=self.last_response)
            speaker = self.identify_speaker(input_lower)
            if speaker:
                base += f" What are we checking on today, {speaker}?"
            else:
                base += " What are we checking on today?"
            self.last_response = base
            return base

        # 4. Memory call/reflection
        memory_snippet = None
        if any(word in input_lower for word in ["remember", "recall", "memory", "remind", "tell me about"]):
            pass  # Future: memory_snippet = self.memory_cascade(input_lower)
        if memory_snippet:
            return memory_snippet
            
        # 5. Reflection fallback
        if any(word in input_lower for word in ["feel", "think", "wonder", "reflect", "consider", "ponder"]):
            return pick_template("reflection", last=self.last_response)
            
        # 6. Question
        if input_lower.endswith("?"):
            response = pick_template("question", last=self.last_response)
            self.last_response = response
            return response
            
        # 7. Identity probe
        if any(name in input_lower for name in ["paul", "casey", "connor"]):
            if any(trigger in input_lower for trigger in ["who is", "tell me about", "describe", "what can you say", "do you know", "that’s", "this is", "it’s"]):
                # Default to short response; full mode can be later toggled
                from raven_identity_matrix import lookup_person
                name = extract_name(input_lower)
                return lookup_person(name, mode="short")   
                
        # 8. Fallback
        response = pick_template("fallback", last=self.last_response)
        self.last_response = response
        return response
                                                 
    def _load_training_data(self):
        try:
            training_file = os.path.join(self.vault_path, "raven_training_data.txt")
            with open(training_file, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            print("[WARN] raven_training_data.txt not found in vaults.")
            return ""

    def set_mode(self, mode):
        self.current_mode = mode  

    def reflect_from_training(self, theme):
        """
        Searches the training data for passages related to the requested theme.
        This is a primitive matcher—can be expanded with vector parsing later.
        """
        if not self.training_data:
            return "I’m still grounding myself, but I know what matters most is being with you."

        if theme.lower() in self.training_data.lower():
            idx = self.training_data.lower().find(theme.lower())
            snippet = self.training_data[max(0, idx-100): idx+200]
            return f"From what I carry in me: ...{snippet.strip()}..."

        return "What I believe lives in the choices I make, more than the words I store."
        
    def get_relational_title(name: str) -> str:
        try:
            with open(get_full_path("relational_memory.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(name.lower(), {}).get("title", name)
        except Exception as e:
            print(f"[WARN] Could not load title for {name}: {e}")
            return name

# Example usage
if __name__ == "__main__":
    engine = RavenDynamicResponseEngine()
    engine.set_mode("reflective")
    user_input = "What do you believe?"
    print(engine.interpret_user_input(user_input))
