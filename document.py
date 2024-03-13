from dataclasses import dataclass

@dataclass
class Document:
    id: int
    title: str
    file_name: str
    has_grid_tag: bool
