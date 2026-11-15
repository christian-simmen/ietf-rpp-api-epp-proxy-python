def vary_with(existing: str | None, name: str) -> str:
    """A `Vary` value that holds `name` besides what `existing` lists (RFC 9110 §12.5.5)."""
    names = [item.strip() for item in (existing or "").split(",") if item.strip()]
    if "*" in names or any(item.lower() == name.lower() for item in names):
        return ", ".join(names)
    return ", ".join([*names, name])
