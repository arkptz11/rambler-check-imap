from functools import wraps
from loguru import logger
from typing import Callable, Any
from dataclasses import dataclass
import traceback


def true_false(method: Callable) -> Callable:
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        try:
            method(self, *method_args, **method_kwargs)
            return True
        except:
            return False
    return _impl
