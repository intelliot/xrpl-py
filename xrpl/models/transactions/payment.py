"""Model for Payment transaction type and related flags."""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from xrpl.models.amounts import Amount, is_xrp
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


class PaymentFlag(int, Enum):
    """
    Transactions of the Payment type support additional values in the Flags field.
    This enum represents those options.

    `See Payment Flags <https://xrpl.org/payment.html#payment-flags>`_
    """

    TF_NO_DIRECT_RIPPLE = 0x00010000
    TF_PARTIAL_PAYMENT = 0x00020000
    TF_LIMIT_QUALITY = 0x00040000


@require_kwargs_on_init
@dataclass(frozen=True)
class Payment(Transaction):
    """
    Represents a Payment <https://xrpl.org/payment.html>`_ transaction, which
    sends value from one account to another. (Depending on the path taken, this
    can involve additional exchanges of value, which occur atomically.) This
    transaction type can be used for several `types of payments
    <http://xrpl.local/payment.html#types-of-payments>`_.

    Payments are also the only way to `create accounts
    <http://xrpl.local/payment.html#creating-accounts>`_.
    """

    #: The amount of currency to deliver. If the Partial Payment flag is set,
    #: deliver *up to* this amount instead. This field is required.
    amount: Amount = REQUIRED  # type: ignore

    #: The address of the account receiving the payment. This field is required.
    destination: str = REQUIRED  # type: ignore

    #: An arbitrary `destination tag
    #: <https://xrpl.org/source-and-destination-tags.html>`_ that
    #: identifies the reason for the Payment, or a hosted recipient to pay.
    destination_tag: Optional[int] = None

    #: Arbitrary 256-bit hash representing a specific reason or identifier for
    #: this Check.
    invoice_id: Optional[str] = None  # TODO: should be a 256 bit hash

    #: Array of payment paths to be used (for a cross-currency payment). Must be
    #: omitted for XRP-to-XRP transactions.
    paths: Optional[List[Any]] = None  # TODO: should be better typed

    #: Maximum amount of source currency this transaction is allowed to cost,
    #: including `transfer fees <http://xrpl.local/transfer-fees.html>`_,
    #: exchange rates, and slippage. Does not include the XRP destroyed as a
    #: cost for submitting the transaction. Must be supplied for cross-currency
    #: or cross-issue payments. Must be omitted for XRP-to-XRP payments.
    send_max: Optional[Amount] = None

    #: Minimum amount of destination currency this transaction should deliver.
    #: Only valid if this is a partial payment. If omitted, any positive amount
    #: is considered a success.
    deliver_min: Optional[Amount] = None

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT,
        init=False,
    )

    def _get_errors(self: Payment) -> Dict[str, str]:
        errors = super()._get_errors()

        # XRP transaction errors
        if is_xrp(self.amount) and self.send_max is None:
            if self.paths is not None:
                errors["paths"] = "An XRP-to-XRP payment cannot contain paths."
            if self.account == self.destination:
                errors["destination"] = (
                    "An XRP payment transaction cannot have the same sender and "
                    "destination."
                )

        # partial payment errors
        elif self.has_flag(PaymentFlag.TF_PARTIAL_PAYMENT) and self.send_max is None:
            errors["send_max"] = "A partial payment must have a `send_max` value."
        elif self.deliver_min is not None and not self.has_flag(
            PaymentFlag.TF_PARTIAL_PAYMENT
        ):
            errors[
                "deliver_min"
            ] = "A non-partial payment cannot have a `deliver_min` field."

        elif (
            is_xrp(self.amount)
            and (self.send_max and is_xrp(self.send_max))
            and not self.has_flag(PaymentFlag.TF_PARTIAL_PAYMENT)
        ):
            errors["send_max"] = (
                "A non-partial payment cannot have both ``amount`` and `send_max` be "
                "XRP."
            )

        # currency conversion errors
        elif self.account == self.destination:
            if self.send_max is None:
                errors[
                    "send_max"
                ] = "A currency conversion requires a `send_max` value."

        return errors
