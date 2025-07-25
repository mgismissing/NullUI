import subprocess
import os

def is_android():
    return os.path.isdir("/data/data/com.termux")

adb = not is_android()

def run(cmd: str) -> str:
    return subprocess.run(("adb shell " if adb else "") + cmd, capture_output=True, text=True, shell=True).stdout

class Package:
    def __init__(self, name: str):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"<Package {self.name}>"

class PackageManager:
    def __init__(self):
        pass

    def list(self) -> list[Package]:
        out = []
        pkgs = run("pm list packages").splitlines()
        for pkg in pkgs:
            pkg = pkg.removeprefix("package:")
            out.append(Package(pkg))
        return out