from contextlib import contextmanager
from pathlib import Path
import os


def file_write(fn, data):
    with open(fn, 'w') as f:
        f.write(data)


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
