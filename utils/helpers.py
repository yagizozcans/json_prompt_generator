import json
import re

def extract_json(text):
    """
    Extracts JSON object from a string.
    Handles markdown code blocks and raw JSON strings.
    """
    try:
        # First try to parse as is
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Look for markdown code blocks
    pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
            
    # Look for raw JSON object structure
    pattern = r"(\{.*\})"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
            
    return None

def format_prompt_for_display(json_data):
    """
    Helper to format the JSON prompt for display if needed.
    """
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except:
            return json_data
            
    return json.dumps(json_data, indent=2)






