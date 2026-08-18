#!/usr/bin/env python3
"""
Consolidated Homebrew Manifest and Environment Orchestrator.
Provides a unified CLI for adding packages, reconciling/formatting manifests,
snapshotting live environments, checking system status, and executing sync actions.
Handles SIGINT / KeyboardInterrupt gracefully without traceback noise.
"""

import argparse
import dataclasses
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path


def handle_sigint(sig, frame):
    """Graceful handler for Ctrl-C termination."""
    sys.stderr.write("\n\n==> Operation cancelled by user. Exiting.\n")
    sys.exit(130)


# Register signal handler for immediate termination
signal.signal(signal.SIGINT, handle_sigint)


@dataclasses.dataclass
class BrewItem:
    directive: str
    name: str
    options: str = ""
    description: str = ""

    def sort_key(self) -> str:
        return self.name.lower()

    def to_lines(self) -> list[str]:
        lines = []
        if self.description:
            lines.append(f"# {self.description}")
        if self.options:
            lines.append(f'{self.directive} "{self.name}", {self.options}')
        else:
            lines.append(f'{self.directive} "{self.name}"')
        return lines


class BrewfileManager:
    def __init__(self, brewfile_path: Path):
        self.brewfile_path = brewfile_path.resolve()
        self.taps: dict[str, BrewItem] = {}
        self.brews: dict[str, BrewItem] = {}
        self.casks: dict[str, BrewItem] = {}
        self.mas_apps: dict[str, BrewItem] = {}
        self.raw_other: list[str] = []

    def ensure_homebrew_installed(self) -> None:
        """Verifies Homebrew installation, installing if missing."""
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("==> Homebrew not found. Installing Homebrew...")
            install_cmd = [
                "/bin/bash",
                "-c",
                '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'
            ]
            subprocess.run(install_cmd, check=True)
            # Add brew to PATH for current process
            brew_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
            for bp in brew_paths:
                if os.path.exists(bp) and bp not in os.environ["PATH"]:
                    os.environ["PATH"] = f"{bp}:{os.environ['PATH']}"

    def parse(self) -> None:
        """Parses the target Brewfile extracting all directives and attached comments."""
        self.taps.clear()
        self.brews.clear()
        self.casks.clear()
        self.mas_apps.clear()
        self.raw_other.clear()

        if not self.brewfile_path.exists():
            return

        lines = self.brewfile_path.read_text(encoding="utf-8").splitlines()
        current_comment = ""
        entry_regex = re.compile(
            r'^(tap|brew|cask|mas)\s+["\']([^"\']+)["\'](?:\s*,\s*(.*))?$',
            re.IGNORECASE,
        )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_comment = ""
                continue

            if stripped.startswith("#"):
                if not any(
                    stripped.lower().startswith(h)
                    for h in [
                        "# taps",
                        "# cli tools",
                        "# desktop applications",
                        "# mac app store",
                        "# casks",
                        "# formulae",
                        "# brews",
                    ]
                ):
                    current_comment = stripped.lstrip("#").strip()
                continue

            match = entry_regex.match(stripped)
            if match:
                directive = match.group(1).lower()
                name = match.group(2)
                options = match.group(3) or ""
                desc = current_comment

                item = BrewItem(
                    directive=directive,
                    name=name,
                    options=options.strip(),
                    description=desc,
                )

                if directive == "tap":
                    self.taps[name.lower()] = item
                elif directive == "brew":
                    self.brews[name.lower()] = item
                elif directive == "cask":
                    self.casks[name.lower()] = item
                elif directive == "mas":
                    self.mas_apps[name.lower()] = item

                current_comment = ""
            else:
                self.raw_other.append(line)
                current_comment = ""

    def fetch_missing_descriptions(self) -> None:
        """Batch-queries Homebrew JSON API for items lacking description comments."""
        missing_brews = [k for k, v in self.brews.items() if not v.description]
        missing_casks = [k for k, v in self.casks.items() if not v.description]
        query_targets = missing_brews + missing_casks

        if not query_targets:
            return

        print(f"==> Fetching metadata descriptions for {len(query_targets)} unannotated items...")
        chunk_size = 50
        for i in range(0, len(query_targets), chunk_size):
            chunk = query_targets[i : i + chunk_size]
            cmd = ["brew", "info", "--json=v2"] + chunk
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                data = json.loads(res.stdout)

                for f in data.get("formulae", []):
                    name_key = f.get("name", "").lower()
                    if name_key in self.brews and not self.brews[name_key].description:
                        self.brews[name_key].description = f.get("desc", "").strip()

                for c in data.get("casks", []):
                    token_key = c.get("token", "").lower()
                    if token_key in self.casks and not self.casks[token_key].description:
                        self.casks[token_key].description = c.get("desc", "").strip()
            except Exception:
                continue

    def format_brewfile(self) -> str:
        """Renders canonical Brewfile format sorted into sections."""
        sections: list[str] = []

        if self.taps:
            tap_lines = ["# Taps"]
            for _, item in sorted(self.taps.items(), key=lambda x: x[1].sort_key()):
                tap_lines.extend(item.to_lines())
            sections.append("\n".join(tap_lines))

        if self.brews:
            brew_lines = ["# CLI Tools (Formulae)"]
            for _, item in sorted(self.brews.items(), key=lambda x: x[1].sort_key()):
                brew_lines.extend(item.to_lines())
            sections.append("\n".join(brew_lines))

        if self.casks:
            cask_lines = ["# Desktop Applications & GUI Tools (Casks)"]
            for _, item in sorted(self.casks.items(), key=lambda x: x[1].sort_key()):
                cask_lines.extend(item.to_lines())
            sections.append("\n".join(cask_lines))

        if self.mas_apps:
            mas_lines = ["# Mac App Store Applications (mas)"]
            for _, item in sorted(self.mas_apps.items(), key=lambda x: x[1].sort_key()):
                mas_lines.extend(item.to_lines())
            sections.append("\n".join(mas_lines))

        if self.raw_other:
            sections.append("\n".join(self.raw_other))

        return "\n\n".join(sections) + "\n"

    def reconcile(self) -> None:
        """Reconciles, sorts, and annotates the Brewfile."""
        self.parse()
        self.fetch_missing_descriptions()
        output = self.format_brewfile()
        self.brewfile_path.write_text(output, encoding="utf-8")
        print(f"==> Reconciled and sorted {self.brewfile_path.name}.")

    def add_package(self, name: str, pkg_type: str | None = None) -> None:
        """Adds a package dynamically without installing it."""
        self.ensure_homebrew_installed()
        cmd = ["brew", "info", "--json=v2", name]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
        except subprocess.CalledProcessError:
            sys.stderr.write(f"Error: Package '{name}' not found in Homebrew index.\n")
            sys.exit(1)

        formulae = data.get("formulae", [])
        casks = data.get("casks", [])

        if pkg_type == "formula" and formulae:
            directive, canonical, desc = "brew", formulae[0].get("name", name), formulae[0].get("desc", "")
        elif pkg_type == "cask" and casks:
            directive, canonical, desc = "cask", casks[0].get("token", name), casks[0].get("desc", "")
        elif formulae and not casks:
            directive, canonical, desc = "brew", formulae[0].get("name", name), formulae[0].get("desc", "")
        elif casks and not formulae:
            directive, canonical, desc = "cask", casks[0].get("token", name), casks[0].get("desc", "")
        elif formulae and casks:
            sys.stderr.write(f"'{name}' exists as both formula and cask. Use --formula or --cask.\n")
            sys.exit(1)
        else:
            sys.stderr.write(f"No package matched '{name}'.\n")
            sys.exit(1)

        self.parse()
        item = BrewItem(directive=directive, name=canonical, description=desc.strip())

        if directive == "brew":
            self.brews[canonical.lower()] = item
        elif directive == "cask":
            self.casks[canonical.lower()] = item

        self.brewfile_path.write_text(self.format_brewfile(), encoding="utf-8")
        print(f"==> Successfully added {directive} '{canonical}' to {self.brewfile_path.name}.")

    def snapshot(self, non_interactive: bool = False) -> None:
        """Performs dry-run live system dump, displays unified diff, and updates."""
        self.ensure_homebrew_installed()
        with tempfile.NamedTemporaryFile(mode="w+", prefix="Brewfile.snapshot.", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            print("==> Capturing live Homebrew environment snapshot...")
            subprocess.run(
                ["brew", "bundle", "dump", f"--file={tmp_path}", "--no-vscode", "--force"],
                check=True,
            )

            if not self.brewfile_path.exists():
                tmp_path.replace(self.brewfile_path)
                print(f"==> Initial Brewfile created at {self.brewfile_path}.")
                return

            print("==> Performing diff against working Brewfile...")
            print("----------------------------------------------------------------------")
            diff_cmd = ["git", "--no-pager", "diff", "--no-index", "--color=always", str(self.brewfile_path), str(tmp_path)]
            try:
                subprocess.run(diff_cmd)
            except FileNotFoundError:
                subprocess.run(["diff", "-u", str(self.brewfile_path), str(tmp_path)])
            print("----------------------------------------------------------------------")

            if self.brewfile_path.read_bytes() == tmp_path.read_bytes():
                print("==> System state is identical to working Brewfile. No updates needed.")
                return

            if non_interactive:
                tmp_path.replace(self.brewfile_path)
                print("==> Working Brewfile updated from snapshot.")
                return

            choice = input("==> Apply changes to working Brewfile? [y/N]: ").strip().lower()
            if choice in ["y", "yes"]:
                tmp_path.replace(self.brewfile_path)
                print("==> Working Brewfile updated.")
            else:
                print("==> Aborted. No changes written.")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def get_status(self) -> tuple[list[str], list[str]]:
        """Returns (missing_packages, unmanaged_packages)."""
        self.ensure_homebrew_installed()
        missing = []
        check_proc = subprocess.run(
            ["brew", "bundle", "check", f"--file={self.brewfile_path}", "--verbose"],
            capture_output=True,
            text=True,
        )
        if check_proc.returncode != 0:
            for line in check_proc.stderr.splitlines() + check_proc.stdout.splitlines():
                if "→" in line:
                    missing.append(line.strip())

        unmanaged = []
        cleanup_proc = subprocess.run(
            ["brew", "bundle", "cleanup", f"--file={self.brewfile_path}"],
            capture_output=True,
            text=True,
        )
        for line in cleanup_proc.stdout.splitlines():
            if "Would uninstall" in line:
                unmanaged.append(line.replace("Would uninstall", "").strip())

        return missing, unmanaged

    def status(self) -> None:
        """Displays categorized diagnostic overview."""
        print("======================================================================")
        print("                   Homebrew Environment Status                        ")
        print("======================================================================")
        missing, unmanaged = self.get_status()

        if missing:
            print(f"  [!] Missing Packages ({len(missing)} declared items not installed):")
            for item in missing:
                print(f"      {item}")
        else:
            print("  [✓] All packages declared in Brewfile are currently installed.")

        print()
        if unmanaged:
            print(f"  [!] Unmanaged Packages ({len(unmanaged)} local items not in Brewfile):")
            for item in unmanaged:
                print(f"      → {item}")
        else:
            print("  [✓] No unmanaged packages detected on this system.")
        print("======================================================================")

    def sync(
        self,
        install: bool = False,
        cleanup: bool = False,
        import_unmanaged: bool = False,
        full: bool = False,
    ) -> None:
        """Executes targeted or interactive sync operations."""
        self.reconcile()

        if full:
            install = True
            cleanup = True

        if not any([install, cleanup, import_unmanaged]):
            # Interactive menu
            self.status()
            print("\nSelect a reconciliation action:")
            print("  1) Install missing packages (Apply Brewfile idempotently)")
            print("  2) Import unmanaged packages into Brewfile (Snapshot & reconcile)")
            print("  3) Prune unmanaged packages from system (Uninstall untracked software)")
            print("  4) Full Synchronize (Install missing packages AND prune untracked)")
            print("  5) Exit")

            choice = input("\nEnter choice [1-5]: ").strip()
            if choice == "1":
                install = True
            elif choice == "2":
                import_unmanaged = True
            elif choice == "3":
                cleanup = True
            elif choice == "4":
                install = True
                cleanup = True
            else:
                print("==> Exiting.")
                return

        if import_unmanaged:
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            subprocess.run(["brew", "bundle", "dump", f"--file={tmp_path}", "--no-vscode", "--force"], check=True)
            appended = self.brewfile_path.read_text(encoding="utf-8") + "\n" + tmp_path.read_text(encoding="utf-8")
            self.brewfile_path.write_text(appended, encoding="utf-8")
            tmp_path.unlink()
            self.reconcile()
            print("==> Unmanaged packages imported and reconciled.")

        if install:
            print("==> Installing missing packages...")
            subprocess.run(["brew", "bundle", f"--file={self.brewfile_path}"], check=True)

        if cleanup:
            print("==> Pruning untracked packages from system...")
            subprocess.run(["brew", "bundle", "cleanup", f"--file={self.brewfile_path}", "--force"], check=True)

        print("==> Synchronization complete.")


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            description="Unified Homebrew Manifest & Environment CLI Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "--file",
            "-f",
            default="Brewfile",
            help="Path to target Brewfile (default: ./Brewfile)",
        )

        subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

        # Subcommand: add
        add_parser = subparsers.add_parser("add", help="Add a formula or cask without installing")
        add_parser.add_argument("package", help="Name or token of the formula or cask")
        type_group = add_parser.add_mutually_exclusive_group()
        type_group.add_argument("--formula", action="store_true", help="Treat as formula")
        type_group.add_argument("--cask", action="store_true", help="Treat as cask")

        # Subcommand: reconcile
        subparsers.add_parser("reconcile", help="Reconcile, deduplicate, annotate, and sort Brewfile")

        # Subcommand: snapshot
        snap_parser = subparsers.add_parser("snapshot", help="Dry-run live system dump with visual diff")
        snap_parser.add_argument("--apply", "-y", action="store_true", help="Apply snapshot without prompt")

        # Subcommand: status
        subparsers.add_parser("status", help="Inspect missing and unmanaged packages")

        # Subcommand: sync
        sync_parser = subparsers.add_parser("sync", help="Synchronize system with Brewfile")
        sync_parser.add_argument("--install", action="store_true", help="Install missing packages")
        sync_parser.add_argument("--cleanup", action="store_true", help="Prune unmanaged packages")
        sync_parser.add_argument("--import-unmanaged", action="store_true", help="Import live packages into Brewfile")
        sync_parser.add_argument("--full", action="store_true", help="Install missing AND cleanup unmanaged")

        args = parser.parse_args()

        if not args.command:
            # Default behavior with no subcommands: launch sync dashboard
            manager = BrewfileManager(Path(args.file))
            manager.sync()
            return

        manager = BrewfileManager(Path(args.file))

        if args.command == "add":
            pkg_type = "formula" if args.formula else ("cask" if args.cask else None)
            manager.add_package(args.package, pkg_type)
        elif args.command == "reconcile":
            manager.reconcile()
        elif args.command == "snapshot":
            manager.snapshot(non_interactive=args.apply)
        elif args.command == "status":
            manager.status()
        elif args.command == "sync":
            manager.sync(
                install=args.install,
                cleanup=args.cleanup,
                import_unmanaged=args.import_unmanaged,
                full=args.full,
            )
    except KeyboardInterrupt:
        sys.stderr.write("\n\n==> Operation cancelled by user. Exiting.\n")
        sys.exit(130)


if __name__ == "__main__":
    main()
