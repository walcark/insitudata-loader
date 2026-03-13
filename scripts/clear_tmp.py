"""
Simply clear all temporary files in the root folder.
"""

import shutil

from insitudata_loader.utils import TMP_PATH, get_logger

logger = get_logger(__name__)


def main():
    logger.info("Deleting temporary files in %s", TMP_PATH)
    for item in TMP_PATH.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    logger.info("Temporary files deleted.")


if __name__ == "__main__":
    main()
