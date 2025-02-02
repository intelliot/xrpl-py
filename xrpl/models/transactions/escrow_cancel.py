"""Model for EscrowCancel transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowCancel(Transaction):
    """
    Represents an `EscrowCancel <https://xrpl.org/escrowcancel.html>`_
    transaction, which returns escrowed XRP to the sender after the Escrow has
    expired.
    """

    #: The address of the account that funded the Escrow. This field is required.
    owner: str = REQUIRED  # type: ignore
    #: Transaction sequence (or Ticket number) of the EscrowCreate transaction
    #: that created the Escrow. This field is required.
    offer_sequence: int = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.ESCROW_CANCEL,
        init=False,
    )
