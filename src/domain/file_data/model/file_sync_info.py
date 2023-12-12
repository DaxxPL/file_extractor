from dataclasses import dataclass


@dataclass(frozen=True)
class NotExtractedFile:
    name: str
    hash: str
    size: int
    malicious: bool
