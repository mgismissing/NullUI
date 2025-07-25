import subprocess
import os
def is_android() -> bool:
    return os.path.isdir("/data/data/com.termux")
adb = (not is_android())
def run(cmd: str) -> str:
    return subprocess.run((("adb shell " if adb else "") + cmd), capture_output = True, text = True, shell = True).stdout
class Package:
    def __init__(self, name: str) -> None:
        self.name = name
    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        return (("<Package " + self.name) + ">")
class PackageManager:
    def __init__(self) -> None:
        pass
    def list(self) -> list[Package]:
        out = ()
        pkgs = run("pm list packages").splitlines()
        for pkg in pkgs:
            pkg = pkg.removeprefix("package:")
            out.append(type(Package())(pkg))
        return out