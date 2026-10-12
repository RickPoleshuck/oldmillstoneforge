def format_minutes(mins: int) -> str:
    hours, minutes = divmod(mins, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    return ' '.join(parts) or '0 minutes'
