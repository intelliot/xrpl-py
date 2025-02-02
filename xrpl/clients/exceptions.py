"""General XRPL Client Exceptions."""
from __future__ import annotations

from typing import Any, Dict

from xrpl.constants import XRPLException


class XRPLRequestFailureException(XRPLException):
    """XRPL Request Exception, when the request fails."""

    def __init__(self: XRPLRequestFailureException, result: Dict[str, Any]) -> None:
        """
        Initializes a XRPLRequestFailureException.

        Args:
            result: the error result returned by the ledger.
        """
        self.error = result["error"]
        if "error_message" in result:
            self.error_message = result["error_message"]
        elif "error_exception" in result:
            self.error_message = result["error_exception"]
        self.message = f"Request failed, {self.error}: {self.error_message}"
        super().__init__(self.message)
