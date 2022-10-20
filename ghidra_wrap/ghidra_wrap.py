import xml.etree.ElementTree as ET
import subprocess
import logging
import os

from pathlib import Path

class GhidraWrapOptions(object):
    def __init__(self):
        self.timeout = None

class GhidraWrap(object):
    log = logging.getLogger("ghidra_wrap.GhidraWrap")

    def __init__(self, ghidra_home:str=None, project_folder:str=None, opt:GhidraWrapOptions=None):
        if ghidra_home is None:
            if not "GHIDRA_HOME" in os.environ:
                raise ValueError("GHIDRA_HOME environment variable not set")
            ghidra_home = os.environ["GHIDRA_HOME"]

        ghidra_home = Path(ghidra_home).resolve()
        if not ghidra_home.exists():
            raise ValueError("ghidra_home folder is not correct")

        headless_script = (ghidra_home / "support" / "analyzeHeadless").resolve()
        if not os.path.exists(headless_script):
            raise ValueError("unable to find analyzeHeadless")

        if project_folder is None:
            project_folder = (Path.home() / ".ghidrawrap").resolve()
            if not project_folder.exists():
                project_folder.mkdir()
        else:
            project_folder = Path(project_folder).resolve()

        if not project_folder.exists():
            raise ValueError("project folder does not exist")

        if not opt:
            opt = GhidraWrapOptions()

        os.environ["GHIDRA_HOME"] = ghidra_home.as_posix()

        self.ghidra_home     = ghidra_home
        self.headless_script = headless_script
        self.project_folder  = project_folder
        self.opt             = opt

        GhidraWrap.log.debug(
            f"GhidraWrap created: ghidra_home={self.ghidra_home}, project_folder={self.project_folder}")

    def _get_project_folder(self, project_name):
        proj_folder = (self.project_folder / project_name).resolve()
        if proj_folder.parent != Path(self.project_folder).resolve():
            raise ValueError(f"invalid project name \"{project_name}\"")
        return proj_folder

    def _run_and_log(self, cmd):
        stdout = ""
        stderr = ""

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with proc.stdout:
            with proc.stderr:
                for line in proc.stdout:
                    stdout_l = line.decode("ascii", errors="ignore")
                    stdout += stdout_l
                    GhidraWrap.log.debug("from Ghidra [stdout] - " + stdout_l.replace("\n", ""))

                for line in proc.stderr:
                    stderr_l = line.decode("ascii", errors="ignore")
                    stderr += stderr_l
                    GhidraWrap.log.warning("from Ghidra [stderr] - " + stderr_l.replace("\n", ""))

        proc.wait()
        return stdout, stderr

    def project_exists(self, project_name:str):
        proj_folder = self._get_project_folder(project_name)
        return proj_folder.exists()

    def delete_project(self, name:str):
        if not self.project_exists(name):
            return

        proj_folder = self._get_project_folder(name)
        proj_folder.rmdir()

    def create_project(self, name:str):
        proj_folder = self._get_project_folder(name)
        if proj_folder.exists():
            raise ValueError(f"project {proj_folder} exists")

        proj_folder.mkdir()

    def list_projects(self):
        return next(os.walk(self.project_folder))[1]

    def list_files_in_project(self, project_name:str):
        proj_folder = self._get_project_folder(project_name)
        if not proj_folder.exists():
            raise ValueError(f"project {proj_folder} does not exists")

        res = list()
        for path in proj_folder.rglob("*.prp"):
            tree = ET.parse(path.as_posix())
            root = tree.getroot()
            for child in root.iter():
                if "NAME" in child.attrib and child.attrib["NAME"] == "NAME":
                    res.append(child.attrib["VALUE"])
        return res

    def analyze_file(self, project_name:str, to_analyze:str):
        if not self.project_exists(project_name):
            raise ValueError(f"project \"{project_name}\" does not exist")

        if not os.path.exists(to_analyze):
            raise ValueError(f"file {to_analyze} does not exist")
        to_analyze = os.path.realpath(to_analyze)

        proj_folder = self._get_project_folder(project_name)
        to_analyze_name = os.path.basename(to_analyze)
        if to_analyze_name in self.list_files_in_project(project_name):
            raise ValueError(f"file {to_analyze} was already analyzed")

        cmd = [
            self.headless_script.as_posix(),
            proj_folder.as_posix(), project_name,
            "-import", to_analyze
        ]
        if self.opt.timeout:
            cmd += [ "-analysisTimeoutPerFile", str(self.opt.timeout) ]

        self._run_and_log(cmd)

    def run_script(self, project_name:str, to_analyze:str, script:str, *script_args):
        script_args = list(script_args)
        if not os.path.exists(script):
            raise ValueError(f"script \"{script}\" does not exist")
        script = os.path.realpath(script)

        if not self.project_exists(project_name):
            self.create_project(project_name)

        proj_folder     = self._get_project_folder(project_name)
        to_analyze_name = os.path.basename(to_analyze)
        script_path     = os.path.dirname(script)
        script_name     = os.path.basename(script)

        if to_analyze_name not in self.list_files_in_project(project_name):
            self.analyze_file(project_name, to_analyze)

        cmd = [
            self.headless_script.as_posix(),
            proj_folder.as_posix(), project_name,
            "-noanalysis",
            "-process", to_analyze_name,
            "-scriptPath", script_path
        ]
        if self.opt.timeout:
            cmd += [ "-analysisTimeoutPerFile", str(self.opt.timeout) ]
        cmd += [ "-postScript", script_name ] + script_args

        stdout, stderr = self._run_and_log(cmd)
        return stdout, stderr
