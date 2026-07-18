"""
TellMe Auto-Reloading Development Server.

Monitors Python, QSS, and JSON files in the frontend and backend directories
and automatically restarts the application when modifications are detected.
"""
import os
import sys
import time
import subprocess

WATCH_DIRS = ["backend", "frontend"]
WATCH_EXTENSIONS = (".py", ".qss", ".json")

def get_last_modified():
    max_mtime = 0
    modified_file = None
    for d in WATCH_DIRS:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            if "__pycache__" in root or ".git" in root or ".nuitka-build" in root:
                continue
            for f in files:
                if f.endswith(WATCH_EXTENSIONS):
                    path = os.path.join(root, f)
                    try:
                        mtime = os.path.getmtime(path)
                        if mtime > max_mtime:
                            max_mtime = mtime
                            modified_file = path
                    except OSError:
                        pass
    return max_mtime, modified_file

def main():
    print("==================================================")
    print("  TellMe Auto-Reloading Development Server  ")
    print("  Watching: backend/, frontend/ for changes...  ")
    print("==================================================")
    
    last_mtime, _ = get_last_modified()
    process = None
    cmd = [sys.executable, "-m", "frontend.app"]
    
    # Start the app initially
    process = subprocess.Popen(cmd)
    app_exited_printed = False
    
    try:
        while True:
            time.sleep(1.0)
            
            # Check if process exited
            ret = process.poll()
            if ret is not None:
                if not app_exited_printed:
                    print("\n[Auto-Reload] Application window closed. Waiting for changes to restart...")
                    app_exited_printed = True
            
            current_mtime, modified_file = get_last_modified()
            if current_mtime > last_mtime:
                print(f"\n[Auto-Reload] Changes detected in: {modified_file}")
                print("[Auto-Reload] Restarting application...")
                
                # Terminate running instance if any
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        process.kill()
                
                # Launch new instance
                process = subprocess.Popen(cmd)
                last_mtime = current_mtime
                app_exited_printed = False
                
    except KeyboardInterrupt:
        print("\n[Auto-Reload] Stopping development server...")
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    main()
