import re


def extract_json_from_text(text: str) -> str:
    code_block_pattern = r"```json(.*?)```"
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    if matches:
        # Extract the first JSON block found
        return matches[0].strip()
    else:
        # No JSON block found; use the entire text
        return text.strip()
