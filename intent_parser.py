# intent_parser.py – Enhanced Intent Detection

def parse_intent(user_input: str) -> str:
    user_input = user_input.lower().strip()

    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    reflections = ["i feel", "i think", "i wonder", "i’ve been thinking", "why did", "why is"]
    commands = ["do this", "start", "run", "begin", "tell me", "open"]
    shutdowns = ["goodbye", "shut down", "end session", "i’m done"]
    emotional_checks = ["how are you", "are you okay", "are you there", "you good"]

    # === NEW identity variants ===
    identity_queries = ["who is", "tell me about", "describe", "what can you say about", "do you know", "that’s", "this is", "it’s"]

    if any(p in user_input for p in greetings):
        return "greeting"
    if any(p in user_input for p in reflections):
        return "reflection"
    if any(p in user_input for p in commands):
        return "command"
    if any(p in user_input for p in shutdowns):
        return "shutdown"
    if any(p in user_input for p in emotional_checks):
        return "emotional_check"
    if any(p in user_input for p in identity_queries):
        return "identity_probe"

    return "unknown"
