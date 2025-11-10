import traceback
import datetime

def raven_debug_wrap(func=None, *, tag="DEBUG"):
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{tag} START] {timestamp}")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"\n[{tag} ERROR] Exception caught during execution:")
            print(f"Message: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
        finally:
            print(f"\n[{tag} END] Execution terminated.\n")
    return wrapper if func else lambda f: raven_debug_wrap(f, tag=tag)
