import subprocess
import json
import os

APP_LIST_PATH = "Data/app_packages.json"

def sync_app_list():
    """
    Gets the list of user-installed apps from the connected device
    and saves it to a JSON file.
    """
    print("🔄 Syncing installed app list from device...")
    try:
        # --- CHANGE 1: The command is updated to the one you found ---
        command = "adb shell cmd package list packages --user 0"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠️ Could not fetch app list. Is the device connected and authorized?")
            return

        lines = result.stdout.strip().split('\n')
        app_dict = {}

        # --- CHANGE 2: The parsing logic is updated for the new command's output ---
        for line in lines:
            # New line format is: package:com.package.name
            if line.startswith("package:"):
                package_name = line.split(':')[-1].strip()
                
                # Create a simple, user-friendly name from the last part of the package name
                app_name = package_name.split('.')[-1]

                app_dict[app_name.lower()] = package_name

        with open(APP_LIST_PATH, "w") as f:
            json.dump(app_dict, f, indent=4)
        
        print(f"✅ App list synced successfully. Found {len(app_dict)} apps.")

    except Exception as e:
        print(f"❌ An error occurred during app sync: {e}")

if __name__ == '__main__':
    # Allows you to run this file directly to test the sync
    sync_app_list()
