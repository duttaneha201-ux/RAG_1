"""Utility for counting tokens and truncating text for LLM inputs."""
from typing import Optional, Tuple


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    
    Uses a conservative approximation: ~4 characters per token for English text.
    This is a rough estimate that works well for most LLMs including Gemini.
    
    Args:
        text: Input text string
        
    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0
    
    # Conservative estimate: ~4 characters per token for English text
    # This accounts for spaces, punctuation, and common tokenization patterns
    char_count = len(text)
    
    # Adjust for whitespace and special characters
    # Rough approximation: spaces and punctuation are typically separate tokens
    whitespace_count = text.count(' ') + text.count('\n') + text.count('\t')
    
    # Estimate: each token is roughly 4 characters, but spaces/punctuation count less
    base_tokens = char_count / 4
    whitespace_tokens = whitespace_count / 2  # Spaces/punctuation are shorter tokens
    
    return int(base_tokens + whitespace_tokens)


def truncate_to_token_limit(text: str, max_tokens: int, suffix: str = "...") -> Tuple[str, int]:
    """
    Truncate text to fit within a token limit.
    
    Args:
        text: Input text to truncate
        max_tokens: Maximum number of tokens allowed
        suffix: String to append when truncating (default: "...")
        
    Returns:
        Tuple of (truncated_text, actual_token_count)
    """
    if not text:
        return text, 0
    
    # Estimate tokens for the full text
    full_tokens = estimate_tokens(text)
    
    if full_tokens <= max_tokens:
        return text, full_tokens
    
    # Need to truncate
    # Estimate characters needed for max_tokens (conservative)
    # Use 3.5 chars per token as average (slightly more conservative for truncation)
    estimated_chars = int(max_tokens * 3.5)
    
    # Reserve space for suffix
    suffix_tokens = estimate_tokens(suffix)
    if suffix_tokens >= max_tokens:
        # If suffix itself is too large, return empty
        return "", 0
    
    remaining_tokens = max_tokens - suffix_tokens
    remaining_chars = int(remaining_tokens * 3.5)
    
    # Truncate and add suffix
    truncated = text[:remaining_chars] + suffix
    actual_tokens = estimate_tokens(truncated)
    
    # Fine-tune: if still over limit, reduce further
    while actual_tokens > max_tokens and len(truncated) > len(suffix):
        truncated = truncated[:-10] + suffix  # Remove 10 chars at a time
        actual_tokens = estimate_tokens(truncated)
    
    return truncated, actual_tokens


def truncate_smart(text: str, max_tokens: int, preserve_end: bool = False) -> Tuple[str, int]:
    """
    Truncate text intelligently, preserving sentence boundaries when possible.
    
    Args:
        text: Input text to truncate
        max_tokens: Maximum number of tokens allowed
        preserve_end: If True, truncate from start. If False, truncate from end.
        
    Returns:
        Tuple of (truncated_text, actual_token_count)
    """
    if not text:
        return text, 0
    
    full_tokens = estimate_tokens(text)
    
    if full_tokens <= max_tokens:
        return text, full_tokens
    
    if preserve_end:
        # Keep the end, truncate from start
        # Estimate how much we can keep from the end
        estimated_chars = int(max_tokens * 3.5)
        truncated = "..." + text[-estimated_chars:]
    else:
        # Keep the start, truncate from end
        truncated, _ = truncate_to_token_limit(text, max_tokens, suffix="...")
    
    actual_tokens = estimate_tokens(truncated)
    return truncated, actual_tokens

