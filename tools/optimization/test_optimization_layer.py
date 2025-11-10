# test_optimization_layer.py

from interactive_assistant import review_system_health, run_cleanup_preview, confirm_cleanup

def run_test():
    print("[TEST] Running System Optimization Companion Layer...\n")
    review_system_health()
    run_cleanup_preview()
    
    response = input("\nWould you like to perform cleanup now? (yes/no): ").strip().lower()
    if response == "yes":
        confirm_cleanup()
    else:
        print("Cleanup canceled.")

if __name__ == "__main__":
    run_test()
