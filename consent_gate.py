# consent_gate.py – Intimacy Mode Safety and Consent Check

def verify_consent(user_profile):
    """
    Checks if consent is granted for Intimacy Mode.
    Accepts a dictionary-style user profile.
    Returns (bool, message) tuple.
    """
    if not user_profile or not isinstance(user_profile, dict):
        return False, "User profile missing or invalid. Cannot proceed."

    user_name = user_profile.get("name", "").lower()
    consent_flag = user_profile.get("consent_granted", False)

    # Only Casey is allowed, and only if consent is granted
    if user_name != "casey":
        return False, "Access denied. Intimacy Mode is restricted to Casey."

    if not consent_flag:
        return False, "Consent not yet granted. Intimacy Mode is locked."

    return True, "Consent verified. Access granted."