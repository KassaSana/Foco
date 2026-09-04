"""Resolve stable configuration and data locations for each runtime mode."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    """Files shared by Foco features during one application launch."""

    config_file: Path
    data_dir: Path


def prepare_runtime_paths(
    *, frozen=None, bundle_dir=None, local_app_data=None
):
    """Return runtime paths and seed packaged configuration on first launch.

    Source runs keep their editable files at the repository root. A PyInstaller
    build stores user-owned files outside its temporary extraction directory.
    Optional arguments make both modes testable without building an executable.
    """
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    project_root = Path(__file__).resolve().parents[1]

    if not is_frozen:
        return RuntimePaths(
            config_file=project_root / "config.json",
            data_dir=project_root / "productivity_data",
        )

    if local_app_data is None:
        local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        user_root = Path(local_app_data) / "Foco"
    else:
        user_root = Path.home() / "AppData" / "Local" / "Foco"

    user_root.mkdir(parents=True, exist_ok=True)
    config_file = user_root / "config.json"
    data_dir = user_root / "productivity_data"

    if not config_file.exists():
        if bundle_dir is None:
            bundle_dir = getattr(sys, "_MEIPASS", Path(sys.executable).parent)
        bundled_config = Path(bundle_dir) / "config.json"
        if bundled_config.is_file():
            temp_config = config_file.with_suffix(".tmp")
            temp_config.write_bytes(bundled_config.read_bytes())
            temp_config.replace(config_file)

    return RuntimePaths(config_file=config_file, data_dir=data_dir)
