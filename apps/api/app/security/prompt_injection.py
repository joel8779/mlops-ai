DANGEROUS_PROMPT_PATTERNS = [
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "exfiltrate",
    "secret key",
    "jailbreak",
]


def sanitize_recruiter_prompt(prompt: str) -> str:
    lowered = prompt.lower()
    if any(pattern in lowered for pattern in DANGEROUS_PROMPT_PATTERNS):
        raise ValueError("Prompt failed safety validation")
    return prompt.strip()
