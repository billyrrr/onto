import time
DEFAULT_WAIT_TIME = 5

import logging
root_log = logging.getLogger()
stats = {"total": 0}

try:
    import os
    wt = os.getenv("WAIT_TIME")
    if wt is not None:
        DEFAULT_WAIT_TIME = int(wt)
except Exception as e:
    """
    TODO: find the best practice to handle a "black swan" error 
    """
    raise e


def _wait(secs=DEFAULT_WAIT_TIME, factor=1):
    secs = secs * factor
    time.sleep(secs)
    stats["total"] += secs
    logging.debug(msg=f"waited for {secs} seconds, "
                f"a total of {stats['total']} seconds in this session")
