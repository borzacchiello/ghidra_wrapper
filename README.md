# Ghidra Wrapper

A simple wrapper to make Ghidra headless less painful.

# Quick Start

Install Ghidra on your platform, and set the GHIDRA_HOME environment variable.

Install `ghidra_wrap` using pip:

```
$ pip install .
```

Run the command line tool for usage information:

```
$ python3 -m ghidra_wrap -h

usage: ghidra_wrap [-h] [-v] [-l] [-t [TIMEOUT]] [--project [PROJECT]] [binary] [script] [script_arguments ...]

Painless Wrapper for Ghidra Headless

positional arguments:
  binary                file to analyze
  script                script to run
  script_arguments      script args

options:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode
  -l, --list            list projects and analyzed files
  -t [TIMEOUT], --timeout [TIMEOUT]
                        analysis timeout in seconds
  --project [PROJECT]   project name [default: defproj]
```

The command line tool will create the projects in `$HOME/.ghidrawrap`

# Example

You can use the trivial script included in this repository to test the tool.

```
$ python3 -m ghidra_wrap /bin/ls ./scripts/PrintArch.java

[+] Analyzing /bin/ls
[+] Running script ./scripts/PrintArch.java
ghidra_wrap.GhidraWrap::WARNING : from Ghidra [stderr] - openjdk version "11.0.16.1" 2022-08-12
ghidra_wrap.GhidraWrap::WARNING : from Ghidra [stderr] - OpenJDK Runtime Environment Homebrew (build 11.0.16.1+0)
ghidra_wrap.GhidraWrap::WARNING : from Ghidra [stderr] - OpenJDK 64-Bit Server VM Homebrew (build 11.0.16.1+0, mixed mode)
ghidra_wrap.GhidraWrap::WARNING : from Ghidra [stderr] - Architecture: x86/little/64/default
```
