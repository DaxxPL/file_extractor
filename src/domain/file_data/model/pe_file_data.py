from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PeFileData:
    file_type: str
    arch: str
    num_imports: int
    num_exports: int
