"""SOURCE ONLY: future controls must run in a separately admitted harness."""
from validate_results import EXPECTED_ROWS, InvalidResults, validate


def wrong_expectation() -> bytes:
    rows = list(EXPECTED_ROWS)
    rows[0] = b"SEARCH C01 EXPECTED 4 ORACLE 3 ACTUAL 3"
    return b"\n".join(rows) + b"\n"


def missing_row() -> bytes:
    return b"\n".join(EXPECTED_ROWS[:-1]) + b"\n"


def require_rejection(data: bytes) -> None:
    rejected = False
    try:
        validate(data)
    except InvalidResults:
        rejected = True
    if not rejected:
        raise AssertionError("NEGATIVE_CONTROL_ACCEPTED")


def main() -> None:
    require_rejection(wrong_expectation())
    require_rejection(missing_row())


if __name__ == "__main__":
    main()
