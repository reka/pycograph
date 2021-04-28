"""Pycograph input schemas.

Validation and adjustment of input data should happen here.
"""

import os
from typing import Any, Optional

from pydantic import BaseModel, DirectoryPath


class PycographLoadInput(BaseModel):
    """Input data for the pycograph load command."""

    project_dir_path: Optional[DirectoryPath] = None
    graph_name: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        """Initialize model and adjust values."""
        super().__init__(**data)
        if not self.project_dir_path:
            self.project_dir_path = os.getcwd()  # type: ignore
        if not self.graph_name:
            self.graph_name = os.path.split(self.project_dir_path)[-1]  # type: ignore
