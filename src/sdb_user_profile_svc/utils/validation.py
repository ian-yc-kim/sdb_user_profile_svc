"""Validation utility functions for user profile data."""

import re
from typing import Pattern

# Compiled regex patterns for performance
# Korean character ranges:
# - Hangul Jamo: \u1100-\u11FF
# - Hangul Compatibility Jamo: \u3130-\u318F
# - Hangul Syllables: \uAC00-\uD7A3
# - Hangul Jamo Extended-A: \uA960-\uA97F
# - Hangul Jamo Extended-B: \uD7B0-\uD7FF
# - Spaces: \s
_KOREAN_ONLY_PATTERN: Pattern[str] = re.compile(r'^[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3\uA960-\uA97F\uD7B0-\uD7FF\s]*$')

# Special characters pattern: anything NOT in Korean ranges, ASCII letters/digits, or spaces
_ALLOWED_PATTERN: Pattern[str] = re.compile(r'^[a-zA-Z0-9\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3\uA960-\uA97F\uD7B0-\uD7FF\s]*$')


def is_korean_only(text: str) -> bool:
    """Check if the given string contains only Korean characters and spaces.
    
    This function validates that the input string consists solely of:
    - Hangul Jamo (\u1100-\u11FF)
    - Hangul Compatibility Jamo (\u3130-\u318F)
    - Hangul Syllables (\uAC00-\uD7A3)
    - Hangul Jamo Extended-A (\uA960-\uA97F)
    - Hangul Jamo Extended-B (\uD7B0-\uD7FF)
    - Whitespace characters (spaces, tabs, etc.)
    
    Args:
        text: The string to validate
        
    Returns:
        True if the string contains only Korean characters and spaces, False otherwise
    """
    if not isinstance(text, str):
        return False
    return bool(_KOREAN_ONLY_PATTERN.match(text))


def has_special_characters(text: str) -> bool:
    """Check if the given string contains special characters.
    
    Special characters are defined as any character that is not:
    - Alphanumeric ASCII characters (a-z, A-Z, 0-9)
    - Korean characters (Hangul blocks)
    - Spaces
    
    Args:
        text: The string to check
        
    Returns:
        True if the string contains special characters, False otherwise
    """
    if not isinstance(text, str):
        return True
    return not bool(_ALLOWED_PATTERN.match(text))
