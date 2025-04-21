from typing import List

MAX_MESSAGE_LENGTH = 4096


async def split_long_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> List[str]:
    if not text:
        return [""]
    if len(text) <= max_length:
        return [text]
    parts = []
    while len(text) > max_length:
        cut_point = max_length
        for i in range(max_length - 1, max_length // 2, -1):
            if text[i] in ['.', '!', '?', '\n'] and (i + 1 >= len(text) or text[i + 1] in [' ', '\n']):
                cut_point = i + 1
                break
        parts.append(text[:cut_point])
        text = text[cut_point:]
    if text:
        parts.append(text)
    return parts
