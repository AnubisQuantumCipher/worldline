"""Complete owned producer material; this DTO carries no custody authority."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthorityMaterial:
    # Original TerminalJournal.authority_material_full tuple: ordered pending
    # intents, separate current cursor, all history/capture rows, raw streams.
    terminal: tuple
    # Original FinalizationJournal.retained tuple, including unsealed starts
    # and every event payload. None is retained as absence, never a seal.
    finalization: tuple | None
    # Independently provisioned pending-store identity. A missing identity
    # remains absent and cannot be inferred from the speaking capture.
    pending_store: bytes | None
