"""Finite public-result protocol; no allocator or native qualification claim."""
import sys

MAX_BYTES = 16_384
MAX_LINE = 128
EXPECTED_ROWS = (
    b"SEARCH C01 EXPECTED 3 ORACLE 3 ACTUAL 3", b"FREE C01 COMPLETED 2",
    b"SEARCH C02 EXPECTED -1 ORACLE -1 ACTUAL -1", b"FREE C02 COMPLETED 2",
    b"SEARCH C03 EXPECTED -1 ORACLE -1 ACTUAL -1", b"FREE C03 COMPLETED 2",
    b"SEARCH C04 EXPECTED 3 ORACLE 3 ACTUAL 3", b"FREE C04 COMPLETED 2",
    b"SEARCH C05 EXPECTED 1 ORACLE 1 ACTUAL 1", b"FREE C05 COMPLETED 2",
    b"SEARCH C06 EXPECTED -1 ORACLE -1 ACTUAL -1", b"FREE C06 COMPLETED 2",
    b"SEARCH C07 EXPECTED 7 ORACLE 7 ACTUAL 7", b"FREE C07 COMPLETED 2",
    b"SEARCH C08 EXPECTED -1 ORACLE -1 ACTUAL -1", b"FREE C08 COMPLETED 2",
    b"SEARCH C09 EXPECTED -1 ORACLE -1 ACTUAL -1", b"FREE C09 COMPLETED 2",
    b"SEARCH C10 EXPECTED 1 ORACLE 1 ACTUAL 1", b"FREE C10 COMPLETED 2",
    b"SEARCH C10R EXPECTED 3 ORACLE 3 ACTUAL 3", b"FREE C10R COMPLETED 2",
    b"CONSUMER D01 TRUE TRUE FALSE", b"CONSUMER D02 TRUE FALSE",
    b"COMPLETE SEARCH 11 FREE 11 CONSUMER 2",
)


class InvalidResults(ValueError):
    """Rejected, bounded protocol input."""


def validate(data: bytes) -> None:
    """Accept exactly 25 ordered canonical ASCII rows with final LF."""
    if not isinstance(data, bytes):
        raise InvalidResults("INPUT_TYPE")
    if len(data) > MAX_BYTES:
        raise InvalidResults("EXCESS_BYTES")
    if not data.endswith(b"\n"):
        raise InvalidResults("MISSING_FINAL_LF")
    rows = data.split(b"\n", 26)
    if len(rows) != 26 or rows[-1] != b"":
        raise InvalidResults("ROW_COUNT")
    for index in range(25):
        row = rows[index]
        if not 1 <= len(row) <= MAX_LINE:
            raise InvalidResults("LINE_LENGTH")
        if row != EXPECTED_ROWS[index]:
            raise InvalidResults("ROW_MISMATCH")


def emit(stream, message: str) -> None:
    if len(message) > 128:
        raise OSError("OUTPUT_LIMIT")
    if stream.write(message) != len(message):
        raise OSError("INCOMPLETE_OUTPUT")
    stream.flush()


def main() -> int:
    """One bounded read; external admitted harness supplies I/O deadline."""
    try:
        data = sys.stdin.buffer.read(MAX_BYTES + 1)
        validate(data)
    except (InvalidResults, OSError):
        # Do not echo attacker-controlled input or unbounded exception text.
        emit(sys.stderr, "INVALID RESULTS\n")
        return 2
    emit(sys.stdout, "VALID PUBLIC RESULTS\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
