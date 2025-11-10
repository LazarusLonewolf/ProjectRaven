# intimacy_protocol.py
# Handles relational depth signaling and context-awareness thresholds

class IntimacyState:
    def __init__(self):
        self.intimacy_level = 0
        self.last_shift_reason = None

    def increase_intimacy(self, amount=1, reason="unspecified"):
        self.intimacy_level += amount
        self.last_shift_reason = f"Increased by {amount}: {reason}"

    def decrease_intimacy(self, amount=1, reason="unspecified"):
        self.intimacy_level = max(0, self.intimacy_level - amount)
        self.last_shift_reason = f"Decreased by {amount}: {reason}"

    def get_level(self):
        return self.intimacy_level

    def get_reason(self):
        return self.last_shift_reason
