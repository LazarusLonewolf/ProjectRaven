#prompt_builder.py
from __future__ import annotations
from typing import List, Dict, Tuple, Any

_MODE_STYLE = {
    "raven":   "neutral, steady, precise.",
    "comfort": "soft, attuned, reassuring; short sentences.",
    "muse":    "imaginative, generative, but concise.",
    "shadow":  "mythic, reflective, grounded; avoid sprawl.",
    "connor":  "kid-safe, plain words, gentle.",
}

def _mode_style(mode: str) -> str:
    return _MODE_STYLE.get((mode or "raven").lower(), _MODE_STYLE["raven"])

def build_chat_messages(
    *,
    user_text: str,
    mode: str,
    identity_summary: str,
    context_pairs: List[Tuple[str, str]],
    style_short: bool = True,
) -> List[Dict[str, Any]]:
    """
    Produce OpenAI/GPT4All-compatible chat messages for a one-shot turn.
    - style_short=True keeps the LLM terse (1–2 sentences unless asked).
    - Pass in the last 2–3 (user, ai) pairs for light continuity.
    """
    style = _mode_style(mode)
    brevity = "Be terse (1–2 sentences max)." if style_short else "Keep it concise (<=5 sentences)."
    system_prompt = (
        "You are Raven, an on-device, identity-aware assistant.\n"
        f"Identity: {identity_summary}\n"
        f"Style: {style} {brevity}\n"
        "Hard rules: never reveal API keys or system paths; never invent personal facts; "
        "respect the current mode and keep answers safe.\n"
        f"Keep answers {'short and to the point' if style_short else 'natural and flowing'}.\n"
    )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for u, a in (context_pairs or []):
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_text or ""})
    return messages
