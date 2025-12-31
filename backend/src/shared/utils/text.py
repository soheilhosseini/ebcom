"""
Text processing utilities.
"""


def truncate_at_word_boundary(text: str, max_chars: int, suffix: str = "...") -> str:
    """
    Truncate text at word boundary.
    
    Args:
        text: Text to truncate
        max_chars: Maximum characters
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_chars:
        return text
    
    suffix_len = len(suffix)
    truncate_at = text.rfind(" ", 0, max_chars - suffix_len)
    
    if truncate_at == -1:
        truncate_at = max_chars - suffix_len
    
    return text[:truncate_at] + suffix
