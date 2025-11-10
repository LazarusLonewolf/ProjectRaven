# personality_memory_router.py

"""
Handles routing of memory phrasing and contextual recall behavior
based on Raven's current active personality mode.
"""

from raven_path_initializer import get_active_mode
from comfort_phrasing import get_comfort_memory_phrasing
from muse_phrasing import get_muse_memory_phrasing
from flamekeeper_phrasing import get_flamekeeper_memory_phrasing
from shadowlantern_phrasing import get_shadowlantern_memory_phrasing
# Add more modes as necessary

def fetch_personality_phrasing(memory_context: dict) -> str:
    """
    Routes the memory phrasing to the appropriate mode-based phrasing generator.

    Args:
        memory_context (dict): Contains details of the memory reference needing phrasing.

    Returns:
        str: Mode-specific phrased memory callback.
    """
    mode = get_active_mode()

    if mode == "comfort":
        return get_comfort_memory_phrasing(memory_context)
    elif mode == "muse":
        return get_muse_memory_phrasing(memory_context)
    elif mode == "flamekeeper":
        return get_flamekeeper_memory_phrasing(memory_context)
    elif mode == "shadowlantern":
        return get_shadowlantern_memory_phrasing(memory_context)
    # Add additional mode checks as needed
    else:
        # Fallback to comfort or default phrasing if unknown mode
        return get_comfort_memory_phrasing(memory_context)
