from pathlib import Path, _ignore_error as pathlib_ignore_error  # type: ignore
from typing import Union

import aiofiles.os


async def path_exists(path: Union[Path, str]) -> bool:
    try:
        await aiofiles.os.stat(str(path))
    except OSError as e:
        if not pathlib_ignore_error(e):
            raise
        return False
    except ValueError:
        # Non-encodable path
        return False
    return True
