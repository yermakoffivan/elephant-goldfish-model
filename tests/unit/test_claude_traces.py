# Copyright 2026 Google LLC.
# SPDX-License-Identifier: Apache-2.0

"""Offline regression coverage for Claude's native transcript directory."""

from pathlib import Path, PurePosixPath, PureWindowsPath
import runpy
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("config_mode", ["unset", "default", "custom"])
@pytest.mark.parametrize(
    ("workspace_path", "project_name"),
    [
        (PurePosixPath("/work/egm probe.v1"), "-work-egm-probe-v1"),
        (PureWindowsPath(r"C:\work\egm probe.v1"), "C--work-egm-probe-v1"),
    ],
)
def test_trace_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config_mode: str,
    workspace_path: PurePosixPath | PureWindowsPath, project_name: str,
) -> None:
  trace_directory = runpy.run_path(str(ROOT / "tests/integration/test_claude.py"))[
      "trace_directory"
  ]
  monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
  config = tmp_path / "home" / ".claude"
  if config_mode == "unset":
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
  else:
    if config_mode == "custom":
      config = tmp_path / "custom config"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))

  workspace = Mock(spec=Path)
  workspace.resolve.return_value = workspace_path
  assert trace_directory(workspace) == (
      config / "projects" / project_name
  )
