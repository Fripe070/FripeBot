from pathlib import Path


def get_cogs(cog_path: str) -> list[str]:
    cog_path = Path(cog_path)

    if cog_path.is_file():
        return [cog_path.stem]

    return [(path.with_suffix("").as_posix().replace("/", ".")) for path in cog_path.rglob("*.py")]
