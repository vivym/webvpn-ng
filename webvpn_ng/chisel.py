import platform
from typing import Optional

import gzip
import time
import subprocess
from pathlib import Path

import requests
from rich.progress import Progress

from .utils import get_cache_path

VERSION = "0.1.0"


def get_chisel_download_url() -> str:
    system = platform.system().lower()
    arch = platform.machine().lower()

    return f"https://gitee.com/vivym/chisel-buaa/releases/download/v0.1.0/chisel-buaa_{VERSION}_{system}_{arch}.gz"


class Chisel:
    def __init__(
        self,
        server: str,
        cookie: str,
        local_host: str,
        local_port: int,
        remote_host: str,
        remote_port: int,
        auth_key: Optional[str] = None,
        delay: int = 100,
        quiet: bool = False,
    ) -> None:
        self.server = server
        self.cookie = cookie
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.auth_key = auth_key
        self.delay = delay
        self.quiet = quiet

    def get_executable(self) -> Path:
        chisel_path = get_cache_path() / f"chisel-buaa-{VERSION}"
        chisel_gz_path = chisel_path.with_suffix(".gz")

        if not chisel_path.exists():
            download_url = get_chisel_download_url()
            print(download_url)

            with requests.get(download_url, stream=True) as r:
                with Progress() as progress:
                    task1 = progress.add_task(
                        "Downloading chisel-buaa",
                        total=int(r.headers["Content-Length"]),
                    )
                    task2 = progress.add_task("Uncompressing chisel-buaa")

                    r.raise_for_status()
                    with open(chisel_gz_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                progress.update(task1, advance=len(chunk))

                    with gzip.open(chisel_gz_path, "rb") as f_in:
                        with open(chisel_path, "wb") as f_out:
                            for chunk in f_in:
                                if chunk:
                                    f_out.write(chunk)
                                    progress.update(task2, advance=len(chunk))

                    chisel_gz_path.unlink()
                    chisel_path.chmod(0o755)

        return chisel_path.resolve()

    def run(self):
        chisel_path = self.get_executable()

        cmd = [chisel_path, "client"]
        if not self.quiet:
            cmd.append("-v")

        if self.auth_key:
            cmd.append("--auth")
            cmd.append(self.auth_key)

        cmd.append("--header")
        cmd.append(f"Cookie: {self.cookie}")

        cmd.append(f"{self.server}/?delay={self.delay}&t={time.time()}")

        cmd.append(f"{self.local_host}:{self.local_port}:{self.remote_host}:{self.remote_port}")

        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            ...
