from pathlib import Path


def get_extension(extension_path: str | Path) -> str:
    extension_path = Path(extension_path)

    if not extension_path.is_file():
        raise FileNotFoundError

    return ".".join(extension_path.with_suffix("").parts)


def get_extensions(extension_directory: str | Path) -> list[str]:
    extension_directory = Path(extension_directory)

    if not extension_directory.is_dir():
        raise NotADirectoryError

    return sorted(get_extension(file_path) for file_path in extension_directory.rglob("*.py"))
