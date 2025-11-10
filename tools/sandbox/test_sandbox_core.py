import sys
sys.path.append("/app")

from sandbox.sandbox_core import sandbox_message, get_sandbox_state, reset_sandbox

def run_test():
    print("[TEST] Resetting sandbox...")
    reset_sandbox()

    print("[TEST] Injecting standard messages...")
    sandbox_message("Initializing core sandbox.")
    sandbox_message("Simulated scenario: idle processing.")
    sandbox_message("Environmental hook tested.")

    print("[TEST] Rapid fire injection...")
    for i in range(5):
        sandbox_message(f"RapidFire Message {i+1}")

    print("[TEST] Unicode/encoding injection...")
    sandbox_message("Testing emoji 🌟✨🔥")
    sandbox_message("Multilingual: こんにちは, привет, مرحبا")

    print("[TEST] Fault injection (non-string input)...")
    try:
        sandbox_message(None)
    except Exception as e:
        print(f" - Fault injection handled: {e}")

    print("[TEST] Log length stress test...")
    for i in range(50):
        sandbox_message(f"StressLine {i+1:03}")

    print("[TEST] Fetching sandbox state...")
    logs = get_sandbox_state()
    for line in logs[-10:]:  # Just show the last 10 to avoid overload
        print(f" - {line.strip()}")

if __name__ == "__main__":
    run_test()
