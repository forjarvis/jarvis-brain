import asyncio
import json
from brain.orchestrator import client # Reuse our Groq client
from utils.skills.information_skills import web_search

async def learn_new_skill(skill_name: str, user_query: str):
    """
    The main protocol for learning a new, unknown skill.
    """
    print(f"🔬 Entering learning protocol for new skill: '{skill_name}'")
    
    # === Phase 1: Intelligent Research ===
    # Formulate a high-level research query
    research_query = (
        f"What is the most reliable and modern method to achieve the goal '{skill_name}' on an Android device "
        f"using a single, direct 'adb shell' command? The user's original request was '{user_query}'."
    )
    
    # Use the web_search skill to find information
    search_results = await asyncio.to_thread(web_search, research_query)
    if not search_results or "Sorry sir" in search_results:
        print(" L-1: Web research failed or yielded no results.")
        return False

    # === Phase 2: Synthesis & Selection ===
    # Send the results to the AI to extract and select the best command
    synthesis_prompt = (
        "You are an expert Android developer. Your job is to analyze the following web search results and extract the "
        "single, most accurate 'adb shell' command to achieve the goal of '{skill_name}'. "
        "The command should be a template that can accept arguments if necessary (use placeholders like {{arg1}}, {{arg2}}). "
        "Your output MUST be a single JSON object with one key: 'command'.\n\n"
        f"SEARCH RESULTS:\n{search_results[:2000]}" # Use first 2000 chars of results
    )
    
    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b", messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.0, response_format={"type": "json_object"}
        )
        new_command_obj = json.loads(response.choices[0].message.content)
        new_command = new_command_obj.get("command")
        
        if not new_command:
            print(" L-2: AI could not synthesize a command from search results.")
            return False
            
        print(f" L-2: AI synthesized new command: '{new_command}'")

    except Exception as e:
        print(f" L-2: AI synthesis failed: {e}")
        return False
        
    # === Phase 3 & 4: Sandbox Verification & Memory Update (Placeholders for now) ===
    print(" L-3: [Placeholder] Verifying new skill in a sandbox...")
    # In a real implementation, you would execute the new_command here in a safe way.
    
    print(" L-4: [Placeholder] Saving new skill to permanent memory...")
    # Here, we would write the new skill to skills.json or a new file.
    
    print(f"✅ Learning protocol for '{skill_name}' complete.")
    # For now, we will return False because the saving part is not implemented yet.
    return False
