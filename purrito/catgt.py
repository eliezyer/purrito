"""Utilities for building and executing CatGt commands."""

from __future__ import annotations

import copy
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union


EXTRACTION_KEYS = ("xa", "xd", "xia", "xid")


def _looks_like_catgt_executable(value: object) -> bool:
    """Best-effort detection for legacy positional constructor calls."""
    name = os.path.basename(str(value))
    return name.lower().startswith("catgt")


def _derive_run_name(basepath: str) -> str:
    """Infer a CatGt run name from the input folder name."""
    folder_name = os.path.basename(os.path.normpath(basepath))
    return re.split(r"_g\d+", folder_name, maxsplit=1)[0] or folder_name


def _normalize_option_name(key: str) -> str:
    """Normalize option keys to CatGt's underscore-based CLI spelling."""
    return key.lstrip("-").replace("-", "_")


class CatGt_wrapper:
    """A Python wrapper for building CatGt command lines."""

    def __init__(
        self,
        *args: object,
        basepath: Optional[Union[str, os.PathLike[str]]] = None,
        run: Optional[str] = None,
        gate: Optional[int] = None,
        trigger: Optional[int] = None,
        catgt_path: Union[str, os.PathLike[str]] = "CatGt",
        run_name: Optional[str] = None,
        prb_fld: Optional[Union[bool, int]] = None,
        **kwargs: Any,
    ) -> None:
        basepath, run, catgt_path = self._parse_constructor_args(
            args=args,
            basepath=basepath,
            run=run,
            catgt_path=catgt_path,
            run_name=run_name,
        )
        resolved_run = run if run is not None else run_name

        if basepath is None:
            raise ValueError("basepath cannot be empty")

        if resolved_run is None:
            resolved_run = _derive_run_name(os.fspath(basepath))

        if not catgt_path:
            raise ValueError("catgt_path cannot be empty")

        self.catgt_path = os.fspath(catgt_path)
        self.basepath = os.path.abspath(os.fspath(basepath))
        self.run = resolved_run
        self.gate = gate
        self.trigger = trigger
        self.options: Dict[str, Any] = {}
        self.extraction: Dict[str, List[str]] = {}

        if prb_fld is not None:
            kwargs["prb_fld"] = prb_fld
        self._update_options(kwargs)

    @staticmethod
    def _parse_constructor_args(
        *,
        args: Sequence[object],
        basepath: Optional[Union[str, os.PathLike[str]]],
        run: Optional[str],
        catgt_path: Union[str, os.PathLike[str]],
        run_name: Optional[str],
    ) -> tuple[Optional[Union[str, os.PathLike[str]]], Optional[str], Union[str, os.PathLike[str]]]:
        """Support both the repo's documented API and the legacy constructor."""
        if run is not None and run_name is not None and run != run_name:
            raise ValueError("run and run_name must match when both are provided")

        if not args:
            return basepath, run, catgt_path

        if len(args) == 1:
            if basepath is not None:
                raise TypeError("basepath was provided both positionally and by keyword")
            return args[0], run, catgt_path

        if len(args) == 2:
            if basepath is not None or run is not None or run_name is not None:
                raise TypeError("ambiguous constructor arguments")
            first, second = args
            if _looks_like_catgt_executable(first):
                return second, None, first
            return first, str(second), catgt_path

        if len(args) == 3:
            if basepath is not None or run is not None or run_name is not None:
                raise TypeError("ambiguous constructor arguments")
            return args[1], str(args[2]), args[0]

        raise TypeError("CatGt accepts at most three positional arguments")

    @property
    def run_name(self) -> str:
        """Backward-compatible alias for the public run name."""
        return self.run

    @run_name.setter
    def run_name(self, value: str) -> None:
        self.run = value

    def set_input(
        self,
        prb: Optional[int] = None,
        prb_fld: Optional[Union[bool, int]] = None,
        t: Optional[str] = None,
        t_cat: Optional[str] = None,
        **kwargs: Any,
    ) -> "CatGt_wrapper":
        self._update_options(
            {
                "prb": prb,
                "prb_fld": prb_fld,
                "t": t,
                "t_cat": t_cat,
                **kwargs,
            }
        )
        return self

    def set_streams(
        self,
        ap: Optional[bool] = None,
        lf: Optional[bool] = None,
        ni: Optional[bool] = None,
        ob: Optional[bool] = None,
        obx: Optional[int] = None,
    ) -> "CatGt_wrapper":
        self._update_options(
            {
                "ap": ap,
                "lf": lf,
                "ni": ni,
                "ob": ob,
                "obx": obx,
            }
        )
        return self

    def set_filters(
        self,
        loccar: Optional[int] = None,
        gblcar: Optional[bool] = None,
        gfix: Optional[Union[float, str]] = None,
        tshift: Optional[int] = None,
        apfilter: Optional[str] = None,
        lffilter: Optional[str] = None,
        **kwargs: Any,
    ) -> "CatGt_wrapper":
        self._update_options(
            {
                "loccar": loccar,
                "gblcar": gblcar,
                "gfix": gfix,
                "tshift": tshift,
                "apfilter": apfilter,
                "lffilter": lffilter,
                **kwargs,
            }
        )
        return self

    def set_car_options(
        self,
        gblcar: Optional[bool] = None,
        loccar: Optional[int] = None,
        loccar_um: Optional[float] = None,
        gbldmx: Optional[bool] = None,
    ) -> "CatGt_wrapper":
        self._update_options(
            {
                "gblcar": gblcar,
                "loccar": loccar,
                "loccar_um": loccar_um,
                "gbldmx": gbldmx,
            }
        )
        return self

    def set_extraction(
        self,
        xa: Optional[Union[str, Sequence[object]]] = None,
        xd: Optional[Union[str, Sequence[object]]] = None,
        xia: Optional[Union[str, Sequence[object]]] = None,
        xid: Optional[Union[str, Sequence[object]]] = None,
        **kwargs: Any,
    ) -> "CatGt_wrapper":
        for key, value in {"xa": xa, "xd": xd, "xia": xia, "xid": xid}.items():
            if value is None:
                continue
            if isinstance(value, str):
                items = [value]
            else:
                items = [str(item) for item in value]
            self.extraction[key] = items

        self._update_options(kwargs)
        return self

    def set_output(
        self,
        dest: Optional[Union[str, os.PathLike[str]]] = None,
        out_prb_fld: Optional[Union[bool, int]] = None,
        gbldmx: Optional[bool] = None,
        **kwargs: Any,
    ) -> "CatGt_wrapper":
        self._update_options(
            {
                "dest": os.fspath(dest) if dest is not None else None,
                "out_prb_fld": out_prb_fld,
                "gbldmx": gbldmx,
                **kwargs,
            }
        )
        return self

    def set_supercat(
        self,
        runs: List[Dict[str, str]],
        trim_edges: bool = False,
        skip_ni_ob_bin: bool = False,
        dest: Optional[Union[str, os.PathLike[str]]] = None,
        **kwargs: Any,
    ) -> "CatGt_wrapper":
        if not runs or not isinstance(runs, list):
            raise ValueError("runs must be a non-empty list of dictionaries")

        if not dest:
            raise ValueError("dest parameter is required for supercat operations")

        supercat_elements = []
        for index, run in enumerate(runs):
            if not isinstance(run, dict):
                raise ValueError(f"Run entry {index} must be a dictionary")
            if "dir" not in run or "run_ga" not in run:
                raise ValueError(f"Run entry {index} must contain 'dir' and 'run_ga' keys")
            supercat_elements.append(f"{{{run['dir']},{run['run_ga']}}}")

        params: Dict[str, Any] = {
            "supercat": "".join(supercat_elements),
            "dest": os.fspath(dest),
        }
        if trim_edges:
            params["supercat_trim_edges"] = True
        if skip_ni_ob_bin:
            params["supercat_skip_ni_ob_bin"] = True

        params.update(kwargs)
        self._update_options(params)
        return self

    def set_option(self, key: str, value: Any) -> "CatGt_wrapper":
        self._update_options({key: value})
        return self

    def set_options(self, options: Dict[str, Any]) -> "CatGt_wrapper":
        if not isinstance(options, dict):
            raise TypeError("options must be a dict")
        self._update_options(options)
        return self

    def remove_option(self, key: str) -> "CatGt_wrapper":
        self.options.pop(_normalize_option_name(key), None)
        return self

    def clear_options(self) -> "CatGt_wrapper":
        self.options.clear()
        self.extraction.clear()
        return self

    def validate(self) -> None:
        """Validate the current command configuration before rendering."""
        if not self.catgt_path:
            raise ValueError("catgt_path cannot be empty")
        if not self.basepath:
            raise ValueError("basepath cannot be empty")
        if not self.run:
            raise ValueError("run cannot be empty")
        if "supercat" in self.options and "dest" not in self.options:
            raise ValueError("supercat commands require dest to be set")

    def _update_options(self, params: Dict[str, Any]) -> None:
        for key, value in params.items():
            if value is None:
                continue
            normalized_key = _normalize_option_name(str(key))
            if isinstance(value, Path):
                self.options[normalized_key] = str(value)
            else:
                self.options[normalized_key] = value

    def _format_options(self) -> List[str]:
        formatted: List[str] = []
        for key, value in self.options.items():
            if isinstance(value, bool):
                if value:
                    formatted.append(f"-{key}")
                continue

            if isinstance(value, (list, tuple)):
                formatted.append(f"-{key}={','.join(map(str, value))}")
                continue

            formatted.append(f"-{key}={value}")
        return formatted

    def get_command_args(
        self,
        catgt_path: Optional[Union[str, os.PathLike[str]]] = None,
    ) -> List[str]:
        self.validate()
        executable = os.fspath(catgt_path) if catgt_path is not None else self.catgt_path

        args = [
            executable,
            f"-dir={self.basepath}",
            f"-run={self.run}",
        ]
        if self.gate is not None:
            args.append(f"-g={self.gate}")
        if self.trigger is not None:
            args.append(f"-t={self.trigger}")

        for key in EXTRACTION_KEYS:
            for item in self.extraction.get(key, []):
                args.append(f"-{key}={item}")

        args.extend(self._format_options())
        return args

    def build_command(
        self,
        catgt_path: Optional[Union[str, os.PathLike[str]]] = None,
    ) -> str:
        return shlex.join(self.get_command_args(catgt_path=catgt_path))

    def dry_run(
        self,
        catgt_path: Optional[Union[str, os.PathLike[str]]] = None,
    ) -> str:
        command = self.build_command(catgt_path=catgt_path)
        print(command)
        return command

    def run(
        self,
        check: bool = True,
        capture_output: bool = True,
        timeout: Optional[float] = None,
        catgt_path: Optional[Union[str, os.PathLike[str]]] = None,
        **subprocess_kwargs: Any,
    ) -> subprocess.CompletedProcess[Any]:
        args = self.get_command_args(catgt_path=catgt_path)
        try:
            return subprocess.run(
                args,
                check=check,
                capture_output=capture_output,
                timeout=timeout,
                **subprocess_kwargs,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"CatGt executable not found at: {args[0]}. "
                "Set catgt_path to the correct executable."
            ) from exc

    def run_async(
        self,
        catgt_path: Optional[Union[str, os.PathLike[str]]] = None,
        **subprocess_kwargs: Any,
    ) -> subprocess.Popen[Any]:
        return subprocess.Popen(
            self.get_command_args(catgt_path=catgt_path),
            **subprocess_kwargs,
        )

    def clone(
        self,
        basepath: Optional[Union[str, os.PathLike[str]]] = None,
        run: Optional[str] = None,
        run_name: Optional[str] = None,
        gate: Optional[int] = None,
        trigger: Optional[int] = None,
        dest: Optional[Union[str, os.PathLike[str]]] = None,
        preserve_dest: bool = True,
        **kwargs: Any,
    ) -> "CatGt_wrapper":
        cloned = CatGt_wrapper(
            catgt_path=self.catgt_path,
            basepath=basepath if basepath is not None else self.basepath,
            run=run if run is not None else (run_name if run_name is not None else self.run),
            gate=self.gate if gate is None else gate,
            trigger=self.trigger if trigger is None else trigger,
        )
        cloned.options = copy.deepcopy(self.options)
        cloned.extraction = copy.deepcopy(self.extraction)

        if dest is not None:
            cloned.options["dest"] = os.fspath(dest)
        elif not preserve_dest:
            cloned.options.pop("dest", None)

        cloned._update_options(kwargs)
        return cloned

    def to_dict(self) -> Dict[str, Any]:
        return {
            "catgt_path": self.catgt_path,
            "basepath": self.basepath,
            "run": self.run,
            "gate": self.gate,
            "trigger": self.trigger,
            "options": copy.deepcopy(self.options),
            "extraction": copy.deepcopy(self.extraction),
        }

    def __str__(self) -> str:
        return self.build_command()

    def __repr__(self) -> str:
        return (
            "CatGt("
            f"basepath={self.basepath!r}, "
            f"run={self.run!r}, "
            f"gate={self.gate!r}, "
            f"trigger={self.trigger!r}, "
            f"catgt_path={self.catgt_path!r}, "
            f"options={self.options!r}"
            ")"
        )

    @staticmethod
    def parse_fyi_supercat_element(fyi_path: Union[str, os.PathLike[str]]) -> Dict[str, str]:
        path = Path(fyi_path)
        if not path.exists():
            raise FileNotFoundError(f"FYI file not found: {path}")

        content = path.read_text(encoding="utf-8")
        match = re.search(r"supercat_element=\{([^,]+),([^}]+)\}", content)
        if not match:
            raise ValueError(f"No supercat_element found in {path}")

        return {
            "dir": match.group(1),
            "run_ga": match.group(2),
        }

    @staticmethod
    def build_supercat_from_fyi_files(
        fyi_paths: Sequence[Union[str, os.PathLike[str]]]
    ) -> List[Dict[str, str]]:
        return [CatGt_wrapper.parse_fyi_supercat_element(path) for path in fyi_paths]


CatGtWrapper = CatGt_wrapper
