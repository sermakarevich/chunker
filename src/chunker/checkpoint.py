from __future__ import annotations

import json
import tempfile
from pathlib import Path

from chunker.state import PipelineState


class Checkpointer:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, state: PipelineState) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(state.to_dict(), indent=2)
        fd, tmp = tempfile.mkstemp(
            dir=self._path.parent, suffix=".tmp"
        )
        try:
            with open(fd, "w") as f:
                f.write(data)
            Path(tmp).replace(self._path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    def load(self, expected_document_id: str | None = None) -> PipelineState:
        data = json.loads(self._path.read_text())
        if (
            expected_document_id is not None
            and data["document_id"] != expected_document_id
        ):
            raise ValueError(
                f"document_id mismatch: checkpoint has '{data['document_id']}', "
                f"expected '{expected_document_id}'"
            )
        return PipelineState.from_dict(data)

    def exists(self) -> bool:
        return self._path.is_file()
