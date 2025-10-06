import asyncio
import json
import os
from brain.orchestrator import client # We can reuse the Groq client

NOTIFICATION_LOG_PATH = "Data/notification_log.json"

def get_raw_notifications():
    """
    Placeholder function to get raw notifications.
    In the final version, this will run a Device Owner command.
    """
    # For testing, we'll use sample data.
    # Replace this with your 'adb shell dumpsys notification' or Device Owner command later.
    print("🔔 [Scanner] Fetching raw notifications (using sample data)...")
    return [
        "Spotify: Now playing 'Starlight'",
        "WhatsApp: Rahul (2 new messages)",
        "Amazon: Your package for 'Smart Speaker' has been dispatched.",
        "Zomato: 50% off on your next order! Use code HUNGRY50.",
        "Missed call from +91 12345 67890",
        "HDFC Bank: Rs. 250.00 credited to your account."
    ]

async def filter_notifications_with_ai(notifications: list):
    """Uses a dedicated AI call to filter out unimportant notifications."""
    if not notifications:
        return []

    print("🧠 [Scanner] Asking AI to filter notifications...")
    prompt = (
        "You are an intelligent notification filter. Your job is to analyze this list of raw Android "
        "notifications and filter out everything that is unimportant spam, ads, promotions, or ongoing status "
        "updates (like music playing). Return a JSON list containing ONLY the important notifications, such as "
        "messages from people, missed calls, financial transactions, or significant alerts. If there are no "
        f"important notifications, return an empty list. Here is the list:\n{notifications}"
    )

    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        # The AI is asked to return a JSON object, but it might be nested. We look for a key that holds a list.
        result_json = json.loads(response.choices[0].message.content)
        for key, value in result_json.items():
            if isinstance(value, list):
                return value # Return the first list found in the JSON
        return [] # Return empty if no list is found
    except Exception as e:
        print(f"❌ [Scanner] AI filtering failed: {e}")
        return []


async def scan_and_update_log():
    """The main function that scans, filters, and updates the notification log."""
    raw_notifications = get_raw_notifications()
    important_notifications = await filter_notifications_with_ai(raw_notifications)

    if not important_notifications:
        print("✅ [Scanner] No new important notifications found.")
        return

    # Read existing log
    try:
        with open(NOTIFICATION_LOG_PATH, "r") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []
    
    # Add new ones, avoiding duplicates
    for notification in important_notifications:
        if notification not in log:
            log.append(notification)
    
    # Save the updated log
    with open(NOTIFICATION_LOG_PATH, "w") as f:
        json.dump(log, f, indent=4)
    
    print(f"✅ [Scanner] Notification log updated with {len(important_notifications)} item(s).")
