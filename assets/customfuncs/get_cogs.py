from pathlib import Path


def get_cogs(cog_path: str) -> list[str]:
    cog_path = Path(cog_path)

    if not cog_path.is_dir():
        return [Path(cog_path).with_suffix("").as_posix().replace("/", ".")]

    return [(path.with_suffix("").as_posix().replace("/", ".")) for path in cog_path.rglob("*.py")]
