from typing import Any, cast

import pandas as pd

def is_valid_data(obj: Any) -> bool:
    """
    Returns True if obj is:
      - a non-empty pandas DataFrame
      - a dict without an 'error' key and non-empty
      - any other non-None, truthy value
    """
    if obj is None:
        return False

    if isinstance(obj, pd.DataFrame):
        return not obj.empty

    if isinstance(obj, dict):
        d = cast(dict[str, Any], obj)
        return bool(d) and 'error' not in d

    return bool(obj)
