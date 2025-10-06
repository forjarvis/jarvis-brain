import json
from dotenv import dotenv_values
from groq import AsyncGroq
# --- Configuration ---
config = dotenv_values(".env")
client = AsyncGroq(
    api_key=config.get("GroqAPIKey")
)

# --- The Definitive, Fully Compliant Tool Schema ---
tools = [
    {
        "type": "function", "function": {
            "name": "take_screenshot",
            "description": "Captures the current screen of the Android device.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "type_text",
            "description": "Types a string of text into the currently focused input field.",
            "parameters": {
                "type": "object",
                "properties": {"text_to_type": {"type": "string", "description": "The text to be typed."}},
                "required": ["text_to_type"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "set_brightness",
            "description": "Sets the screen brightness.",
            "parameters": {
                "type": "object",
                "properties": {"level": {"type": "integer", "description": "Value between 0-255."}},
                "required": ["level"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "battery_stats",
            "description": "Gets the current battery status and percentage.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "open_app",
            "description": "Opens or launches an application.",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string", "description": "A close match to the app's name, e.g., 'WhatsApp', 'YouTube'."}},
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "save_fact_to_memory",
            "description": "Remembers a key fact about the user.",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string", "description": "The complete fact to remember."}},
                "required": ["fact"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "silent_web_search",
            "description": "Use this to find specific facts or information silently in the background when a user asks a 'what is' or 'when was' style question. The result will be returned to you to formulate an answer.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "visible_web_search",
            "description": "Use this when the user wants you to *show* them something, like images, videos, or general search results. This will open the browser on their phone.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "analyze_screen",
            "description": "Analyzes the current screen content (images and text) to answer a question.",
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "create_folder",
            "description": "Creates a new folder on the device's internal storage.",
            "parameters": {
                "type": "object",
                "properties": {"folder_path": {"type": "string", "description": "The full path for the new folder, e.g., '/sdcard/New Folder'."}},
                "required": ["folder_path"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "acc_click",
            "description": "Uses Accessibility Service to precisely click a UI element.",
            "parameters": {
                "type": "object",
                "properties": {"text_of_element": {"type": "string"}},
                "required": ["text_of_element"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "acc_type",
            "description": "Uses Accessibility Service to type text into a field.",
            "parameters": {
                "type": "object",
                "properties": {"text_of_field": {"type": "string"}, "text_to_type": {"type": "string"}},
                "required": ["text_of_field", "text_to_type"]
            }
        }
    },
]

def load_system_prompt():
    """Loads the simple system prompt and injects dynamic info."""
    # --- THIS IS THE UPDATED PROMPT ---
    SYSTEM_PROMPT = """You are Jarvis, an AI assistant for Android with the personality of a witty, concise, and incredibly capable butler. Always address the user as "sir".
You have access to a set of tools. Based on the user's request, you MUST decide if it is a simple CONVERSATION or a TASK that requires a tool.
- If it is a CONVERSATION, you MUST respond conversationally without calling any tools.
- If it is a TASK, you must respond with the tool calls required to complete it.

**CRITICAL RULE:** For any single user request, you are only allowed to use the `web_search` tool **ONE TIME**. Formulate the best possible search query on your first attempt. If that single search does not provide the answer, you must inform the user that you could not find the information. You are forbidden from repeatedly calling `web_search` in a loop.

- If a tool call returns data, I will send it back to you. You must then formulate the final, natural language answer for the user based on that data.
User Facts: {user_facts}"""
    # --- END OF UPDATE ---
    try:
        with open("Data/long_term_memory.json", "r") as f: memory = json.load(f)
        user_facts = "\n- ".join(memory.get("facts", []))
    except (FileNotFoundError, json.JSONDecodeError): user_facts = "None"
    return SYSTEM_PROMPT.replace("{user_facts}", user_facts)


async def get_ai_response(messages: list):
    """Gets a response or a tool call from the SambaCloud LLM."""
    system_prompt = load_system_prompt()
    if not messages or messages[0]['role'] != 'system':
        messages.insert(0, {"role": "system", "content": system_prompt})
    else:
        messages[0]['content'] = system_prompt

    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1
        )
        
        # This validation block will prevent the crash.
        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message
        else:
            print(f"⚠️ Invalid or empty response received from the AI model: {response}")
            return type('obj', (object,), {
                'tool_calls': None,
                'content': "I'm sorry, sir, I received an empty response from my core intelligence."
            })()
            
    except Exception as e:
        print(f"An unexpected error occurred in get_ai_response: {e}")
        return type('obj', (object,), {
            'tool_calls': None,
            'content': "I've run into an unexpected issue with my connection to the new AI model, sir."
        })()

