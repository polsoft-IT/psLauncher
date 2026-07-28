# ─────────────────────────────────────────────────────────────────────────────
# CrossTerm :: Moduł Sandbox
# Autor  : Sebastian Januchowski
# Firma  : polsoft.ITS™ Group
# GitHub : https://github.com/polsoft-seb07uk
# E-mail : polsoft.its@fastservice.com
# Wersja : 1.0.1
# ─────────────────────────────────────────────────────────────────────────────
"""
sandbox.py — izolowane środowisko testowe dla CrossTerm.

Przeznaczenie
─────────────
Moduł dostarcza okno dialogowe (SandboxWindow) pozwalające uruchamiać
polecenia i skrypty (bat, cmd, ps1, py, vbs) w izolowanym buforze
wyjściowym bez wpływu na główną sesję terminala.

Obsługiwane typy skryptów
──────────────────────────
  .bat / .cmd  — cmd.exe /C
  .ps1         — powershell.exe -ExecutionPolicy Bypass -File
  .py          — python.exe / python3
  .vbs         — cscript.exe //NoLogo
  .sh          — bash / sh
  .js          — node (Node.js)
  .lua         — lua / luajit (test składni: luac -p)
  .rb          — ruby (test składni: ruby -c)
  .pl          — perl (test składni: perl -c)
  .php         — php (test składni: php -l)
  .r / .R      — Rscript (test składni: --parse-only)
  .tcl         — tclsh
  .wsf         — cscript.exe //NoLogo  (tylko Windows)
  .hta         — mshta.exe             (tylko Windows, bez weryfikacji składni)
  .reg         — regedit.exe /s        (tylko Windows, wymaga potwierdzenia)
  .go          — go run                (test składni: go vet)
  .java        — java (single-file, Java 11+)  (test składni: javac)
  .cs / .csx   — dotnet-script                (weryfikacja: tylko runtime)
  .ts          — ts-node / deno run    (test składni: tsc --noEmit / deno check)
  .coffee      — coffee                (test składni: coffee -p)
  .exs         — elixir                (test składni: elixir -e)

Struktura
──────────
  SandboxWindow
  ├── _build_toolbar()       ← przyciski: Uruchom / Otwórz / Wyczyść / Zapisz log
  ├── _build_console()       ← obszar wyjścia (scrolled Text) z tagami kolorów
  ├── _build_input()         ← pole polecenia lub ścieżki do pliku
  ├── _run_command()         ← dispatcher: plik skryptu lub wbudowane polecenie
  ├── _run_script(path)      ← uruchamia skrypt w tle (subprocess + threading)
  ├── _stream_output(proc)   ← czyta stdout/stderr na bieżąco
  ├── _test_script(path)     ← tryb testowy: weryfikacja składni przed uruchomieniem
  └── _handle_builtin(cmd)   ← wbudowane komendy (help, clear, version …)
"""

from __future__ import annotations
import weakref

import glob
import os
import platform
import shlex
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog
from pathlib import Path
from tkinter import filedialog, ttk

# Import structured logger
try:
    from logger import get_logger
    _logger = get_logger()
except ImportError:
    _logger = None

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, get_lexer_for_filename, guess_lexer, TextLexer
    from pygments.styles import get_style_by_name
    _PYGMENTS_AVAILABLE = True
except ImportError:
    _PYGMENTS_AVAILABLE = False

# ── Metadane modułu ──────────────────────────────────────────────────────────
__version__   = "1.0.1"
__author__    = "Sebastian Januchowski"
__company__   = "polsoft.ITS™ Group"
__module_id__ = "sandbox"

IS_WINDOWS = platform.system() == "Windows"

# Powłoki / interpretery rozpoznawane jako PIERWSZY token komendy, np.
# "cmd.exe /c plik.bat", "powershell -File skrypt.ps1", "python -O skrypt.py".
# Pozwala traktować sandbox jak prawdziwy terminal, a nie tylko "uruchom plik".
_SHELL_INVOCATIONS = {
    "cmd", "cmd.exe",
    "powershell", "powershell.exe", "pwsh", "pwsh.exe",
    "python", "python.exe", "python3", "py", "py.exe",
    "node", "node.exe",
    "bash", "bash.exe", "sh",
    "wscript", "wscript.exe", "cscript", "cscript.exe",
    "ruby", "perl", "php", "Rscript", "tclsh",
    "go", "java", "dotnet-script",
    "mshta", "mshta.exe",
}


def _split_commandline(text: str) -> list[str]:
    """Split input while preserving quoted Windows paths and arguments."""
    try:
        if IS_WINDOWS:
            # ``posix=False`` preserves Windows backslashes.  Popen receives
            # argv directly, so enclosing quotes must then be removed.
            return [part.strip('"') for part in shlex.split(text, posix=False)]
        return shlex.split(text)
    except ValueError:
        # Do not crash a Tk callback on an unmatched quote.
        return []

# ── Stałe UI ─────────────────────────────────────────────────────────────────
_FONT_CONSOLE = ("Consolas", 10)
_FONT_LABEL   = ("Segoe UI", 9)
_BANNER = (
    "Wpisz polecenie, ścieżkę do skryptu lub kliknij 📂 Otwórz.\n"
    "Obsługiwane: .bat .cmd .ps1 .py .vbs .sh .js .lua .rb .pl .php .r .tcl .wsf .hta .reg .go .java .cs .csx .ts .coffee .exs\n"
)
_LEXER_MAP = {
    ".py": "python", ".ps1": "powershell", ".bat": "batch", ".cmd": "batch",
    ".sh": "bash", ".js": "javascript", ".ts": "typescript", ".rb": "ruby", ".pl": "perl",
    ".php": "php", ".lua": "lua", ".go": "go", ".java": "java", ".cs": "csharp", ".html": "html",
}

# ── Konfiguracja weryfikacji składni ───────────────────────────────────────────
SYNTAX_CHECK_CONFIG = {
    ".bat": {"special": True, "platform": "windows", "ok_msg": "Plik BAT/CMD: wczytany poprawnie"},
    ".cmd": {"special": True, "platform": "windows", "ok_msg": "Plik BAT/CMD: wczytany poprawnie"},
    ".hta": {"special": True, "platform": "windows", "ok_msg": "Plik HTA: wczytany poprawnie"},
    ".reg": {"special": True, "platform": "windows", "ok_msg": "Plik REG: nagłówek poprawny"},
    ".cs": {"special": True, "ok_msg": "Znaleziono dotnet-script"},
    ".csx": {"special": True, "ok_msg": "Znaleziono dotnet-script"},
}

# ── Konfiguracja runnerów dla błędów ───────────────────────────────────────────
RUNNER_CONFIG = {
    ".bat": {"error": "Nie znaleziono cmd.exe"},
    ".cmd": {"error": "Nie znaleziono cmd.exe"},
    ".ps1": {"error": "Nie znaleziono powershell/pwsh"},
    ".py": {"error": "Nie znaleziono python"},
    ".vbs": {"error": "Nie znaleziono cscript.exe"},
    ".sh": {"error": "Nie znaleziono bash/sh"},
    ".js": {"error": "Nie znaleziono node (Node.js)"},
    ".lua": {"error": "Nie znaleziono lua/luac"},
    ".rb": {"error": "Nie znaleziono ruby"},
    ".pl": {"error": "Nie znaleziono perl"},
    ".php": {"error": "Nie znaleziono php"},
    ".r": {"error": "Nie znaleziono Rscript"},
    ".R": {"error": "Nie znaleziono Rscript"},
    ".tcl": {"error": "Nie znaleziono tclsh"},
    ".wsf": {"error": "Nie znaleziono cscript.exe"},
    ".hta": {"error": "Nie znaleziono mshta.exe"},
    ".reg": {"error": "Nie znaleziono regedit.exe"},
    ".go": {"error": "Nie znaleziono go"},
    ".java": {"error": "Nie znaleziono java/javac"},
    ".cs": {"error": "Nie znaleziono dotnet-script"},
    ".csx": {"error": "Nie znaleziono dotnet-script"},
    ".ts": {"error": "Nie znaleziono ts-node ani deno"},
    ".coffee": {"error": "Nie znaleziono coffee"},
    ".exs": {"error": "Nie znaleziono elixir"},
}

# ── Mapowanie rozszerzeń → runner ─────────────────────────────────────────────
def _find_python() -> str:
    """Znajdź interpreter Pythona: najpierw ten sam co bieżący proces."""
    return sys.executable or shutil.which("python") or shutil.which("python3") or "python"


def _find_shell() -> str | None:
    """Znajdź interpreter shell dla skryptów .sh (bash, w razie braku — sh)."""
    return shutil.which("bash") or shutil.which("sh")


def _find_node() -> str | None:
    """Znajdź interpreter Node.js dla skryptów .js."""
    found = shutil.which("node") or shutil.which("nodejs")
    if found:
        return found
    if IS_WINDOWS:
        candidates = [
            r"C:\Program Files\nodejs\node.exe",
            r"C:\Program Files (x86)\nodejs\node.exe",
            os.path.expandvars(r"%APPDATA%\nvm\current\node.exe"),
            os.path.expandvars(r"%ProgramFiles%\nodejs\node.exe"),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
    return None


def _find_lua() -> str | None:
    """Znajdź interpreter Lua dla skryptów .lua (lua, lua5.x, luajit)."""
    for name in ("lua", "lua5.4", "lua5.3", "lua5.1", "luajit"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _find_luac() -> str | None:
    """Znajdź kompilator/parser Lua (luac) używany do weryfikacji składni."""
    for name in ("luac", "luac5.4", "luac5.3", "luac5.1"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _find_ruby() -> str | None:
    """Znajdź interpreter Ruby dla skryptów .rb."""
    found = shutil.which("ruby")
    if found:
        return found
    if IS_WINDOWS:
        candidates = [
            r"C:\Ruby34-x64\bin\ruby.exe",
            r"C:\Ruby33-x64\bin\ruby.exe",
            r"C:\Ruby32-x64\bin\ruby.exe",
            r"C:\Ruby31-x64\bin\ruby.exe",
            r"C:\Ruby30-x64\bin\ruby.exe",
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None


def _find_perl() -> str | None:
    """Znajdź interpreter Perl dla skryptów .pl."""
    found = shutil.which("perl")
    if found:
        return found
    if IS_WINDOWS:
        # Strawberry Perl
        candidates = [
            r"C:\Strawberry\perl\bin\perl.exe",
            r"C:\Perl64\bin\perl.exe",
            r"C:\Perl\bin\perl.exe",
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None


def _find_php() -> str | None:
    """Znajdź interpreter PHP dla skryptów .php."""
    found = shutil.which("php")
    if found:
        return found
    if IS_WINDOWS:
        candidates = [
            r"C:\php\php.exe",
            r"C:\xampp\php\php.exe",
            r"C:\wamp64\bin\php\php8.2.0\php.exe",
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None


def _find_rscript() -> str | None:
    """Znajdź interpreter R (Rscript) dla skryptów .r/.R."""
    found = shutil.which("Rscript")
    if found:
        return found
    if IS_WINDOWS:
        # Typowe ścieżki instalacji R na Windows
        patterns = [
            r"C:\Program Files\R\R-*\bin\x64\Rscript.exe",
            r"C:\Program Files\R\R-*\bin\Rscript.exe",
        ]
        for pat in patterns:
            hits = sorted(glob.glob(pat), reverse=True)  # najnowsza wersja pierwsza
            if hits:
                return hits[0]
    return None


def _find_tclsh() -> str | None:
    """Znajdź interpreter Tcl (tclsh) dla skryptów .tcl."""
    for name in ("tclsh", "tclsh9.0", "tclsh8.6", "tclsh8.5"):
        found = shutil.which(name)
        if found:
            return found
    if IS_WINDOWS:
        candidates = [
            r"C:\Tcl\bin\tclsh.exe",
            r"C:\ActiveTcl\bin\tclsh.exe",
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None


def _find_go() -> str | None:
    """Znajdź narzędzie go dla skryptów .go."""
    found = shutil.which("go")
    if found:
        return found
    if IS_WINDOWS:
        for c in [r"C:\Program Files\Go\bin\go.exe", r"C:\Go\bin\go.exe"]:
            if os.path.isfile(c):
                return c
    else:
        for c in ["/usr/local/go/bin/go", "/usr/lib/go/bin/go"]:
            if os.path.isfile(c):
                return c
    return None


def _find_java() -> tuple[str | None, str | None]:
    """Znajdź java i javac. Zwraca (java, javac)."""
    java  = shutil.which("java")
    javac = shutil.which("javac")
    if IS_WINDOWS and not java:
        patterns = [
            r"C:\Program Files\Java\jdk*\bin\java.exe",
            r"C:\Program Files\Eclipse Adoptium\jdk*\bin\java.exe",
            r"C:\Program Files\Microsoft\jdk*\bin\java.exe",
        ]
        for pat in patterns:
            hits = sorted(glob.glob(pat), reverse=True)
            if hits:
                java = hits[0]
                javac = hits[0].replace("java.exe", "javac.exe") if os.path.isfile(hits[0].replace("java.exe", "javac.exe")) else None
                break
    return java, javac


def _find_dotnet_script() -> str | None:
    """Znajdź dotnet-script lub dotnet dla skryptów .cs."""
    ds = shutil.which("dotnet-script")
    if ds:
        return ds
    # Fallback: sam dotnet (może uruchamiać .csx przez dotnet-script)
    return shutil.which("dotnet")


def _find_ts_runner() -> tuple[str | None, str]:
    """
    Znajdź runner TypeScript. Zwraca (ścieżka, tryb).
    Tryb: 'ts-node' | 'deno' | None
    """
    ts_node = shutil.which("ts-node")
    if ts_node:
        return ts_node, "ts-node"
    deno = shutil.which("deno")
    if deno:
        return deno, "deno"
    return None, ""


def _find_coffee() -> str | None:
    """Znajdź interpreter CoffeeScript (coffee) dla skryptów .coffee."""
    return shutil.which("coffee")


def _find_elixir() -> str | None:
    """Znajdź interpreter Elixir (elixir) dla skryptów .exs."""
    found = shutil.which("elixir")
    if found:
        return found
    if not IS_WINDOWS:
        for c in ["/usr/local/bin/elixir", "/usr/bin/elixir"]:
            if os.path.isfile(c):
                return c
    return None


def _find_mshta() -> str | None:
    """Znajdź mshta.exe dla skryptów .hta (tylko Windows)."""
    if not IS_WINDOWS:
        return None
    found = shutil.which("mshta")
    if found:
        return found
    candidates = [
        r"C:\Windows\System32\mshta.exe",
        r"C:\Windows\SysWOW64\mshta.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def _build_runner(path: Path) -> list[str] | None:
    """Zwraca listę argumentów do subprocess.Popen lub None gdy nieobsługiwany."""
    ext = path.suffix.lower()
    if ext in (".bat", ".cmd"):
        if IS_WINDOWS:
            return ["cmd.exe", "/C", str(path)]
        return None  # .bat/.cmd nie działają poza Windows
    if ext == ".ps1":
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if ps:
            return [ps, "-ExecutionPolicy", "Bypass", "-File", str(path)]
        return None
    if ext == ".py":
        return [_find_python(), str(path)]
    if ext == ".vbs":
        if IS_WINDOWS:
            cs = shutil.which("cscript")
            if cs:
                return [cs, "//NoLogo", str(path)]
        return None
    if ext == ".sh":
        sh = _find_shell()
        if sh:
            return [sh, str(path)]
        return None
    if ext == ".js":
        node = _find_node()
        if node:
            return [node, str(path)]
        return None
    if ext == ".lua":
        lua = _find_lua()
        if lua:
            return [lua, str(path)]
        return None
    if ext == ".rb":
        rb = _find_ruby()
        if rb:
            return [rb, str(path)]
        return None
    if ext == ".pl":
        pl = _find_perl()
        if pl:
            return [pl, str(path)]
        return None
    if ext == ".php":
        php = _find_php()
        if php:
            return [php, str(path)]
        return None
    if ext in (".r", ".R"):
        rs = _find_rscript()
        if rs:
            return [rs, str(path)]
        return None
    if ext == ".tcl":
        tcl = _find_tclsh()
        if tcl:
            return [tcl, str(path)]
        return None
    if ext == ".wsf":
        if IS_WINDOWS:
            cs = shutil.which("cscript")
            if cs:
                return [cs, "//NoLogo", str(path)]
        return None
    if ext == ".hta":
        mshta = _find_mshta()
        if mshta:
            return [mshta, str(path)]
        return None
    if ext == ".reg":
        if IS_WINDOWS:
            regedit = shutil.which("regedit") or r"C:\Windows\regedit.exe"
            if os.path.isfile(regedit) or shutil.which("regedit"):
                return [regedit, "/s", str(path)]
        return None
    if ext == ".go":
        go = _find_go()
        if go:
            # go run obsługuje single-file od Go 1.0; -mod=mod potrzebny poza modułem
            return [go, "run", str(path)]
        return None
    if ext == ".java":
        java, _ = _find_java()
        if java:
            # java <plik.java> działa dla single-file source programs od Java 11
            return [java, str(path)]
        return None
    if ext in (".cs", ".csx"):
        ds = _find_dotnet_script()
        if ds:
            name = os.path.basename(ds)
            if "dotnet-script" in name:
                # dotnet-script <plik>
                return [ds, str(path)]
            # sam dotnet nie obsługuje .cs/.csx bez projektu — wymagany dotnet-script
        return None
    if ext == ".ts":
        runner_ts, mode = _find_ts_runner()
        if runner_ts:
            if mode == "deno":
                return [runner_ts, "run", "--allow-all", str(path)]
            return [runner_ts, str(path)]
        return None
    if ext == ".coffee":
        coffee = _find_coffee()
        if coffee:
            return [coffee, str(path)]
        return None
    if ext == ".exs":
        elixir = _find_elixir()
        if elixir:
            return [elixir, str(path)]
        return None
    return None


def _syntax_check(path: Path) -> tuple[bool, str]:
    """
    Weryfikacja składni przed uruchomieniem.
    Zwraca (ok: bool, komunikat: str).
    """
    ext = path.suffix.lower()
    config = SYNTAX_CHECK_CONFIG.get(ext)
    if not config:
        return False, f"Nieobsługiwane rozszerzenie: {ext!r}"

    if ext == ".py":
        py = _find_python()
        result = subprocess.run(
            [py, "-m", "py_compile", str(path)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, "Składnia Python: OK"
        return False, result.stderr.strip() or "Błąd składni Python"

    if ext == ".ps1":
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if ps:
            # PowerShell: parsuj skrypt bez wykonywania
            result = subprocess.run(
                [ps, "-NoProfile", "-NonInteractive", "-Command",
                 f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{path}', [ref]$null, [ref]$errs); $errs | ForEach-Object {{ $_.Message }}"],
                capture_output=True, text=True, timeout=10
            )
            errs = result.stdout.strip()
            if not errs:
                return True, "Składnia PowerShell: OK"
            return False, errs
        return False, "Nie znaleziono powershell/pwsh"

    if ext in (".bat", ".cmd"):
        if not IS_WINDOWS:
            return False, ".bat/.cmd — dostępne tylko na Windows"
        # Minimalna weryfikacja: sprawdź czy plik nie jest pusty i kodowanie
    if config.get("special"):
        if config.get("platform") == "windows" and not IS_WINDOWS:
            return False, f"{ext.upper()} — dostępne tylko na Windows"
        # Special handling for types without a simple checker command
        try:
            content = path.read_text(encoding="cp1250", errors="replace")
            if not content.strip():
                return False, "Plik jest pusty"
            return True, "Plik BAT/CMD: wczytany poprawnie (pełna weryfikacja tylko w runtime)"
            if ext in (".bat", ".cmd", ".hta"):
                if not path.read_text(encoding="cp1250", errors="replace").strip():
                    return False, "Plik jest pusty"
            elif ext == ".reg":
                raw = path.read_bytes()
                content = raw.decode("utf-16" if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else "utf-8", errors="replace")
                first_line = content.strip().splitlines()[0] if content.strip() else ""
                if not any(first_line.startswith(h) for h in ("Windows Registry Editor Version 5.00", "REGEDIT4")):
                    return False, f"Nieprawidłowy nagłówek .reg: {first_line!r}"
            elif ext in (".cs", ".csx"):
                if not _find_dotnet_script():
                    return False, "Wymagany dotnet-script: dotnet tool install -g dotnet-script"
            return True, config["ok_msg"]
        except Exception as exc:
            return False, str(exc)

    if ext == ".vbs":
        if not IS_WINDOWS:
            return False, ".vbs — dostępne tylko na Windows"
        cs = shutil.which("cscript")
        if cs:
            # cscript //NoExecute sprawdza składnię
            result = subprocess.run(
                [cs, "//NoLogo", "//NoExecute", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia VBScript: OK"
            return False, (result.stderr or result.stdout).strip() or "Błąd składni VBS"
        return False, "Nie znaleziono cscript.exe"
    runner_path = config["runner"]() if "runner" in config else None
    if not runner_path:
        return False, config.get("err_msg", f"Brak interpretera dla {ext}")

    if ext == ".sh":
        sh = _find_shell()
        if sh:
            # bash/sh -n: sprawdzenie składni bez wykonywania
            result = subprocess.run(
                [sh, "-n", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia Shell: OK"
            return False, result.stderr.strip() or "Błąd składni Shell"
        return False, "Nie znaleziono bash/sh"

    if ext == ".js":
        node = _find_node()
        if node:
            # node --check: sprawdzenie składni bez wykonywania
            result = subprocess.run(
                [node, "--check", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia JavaScript: OK"
            return False, result.stderr.strip() or "Błąd składni JavaScript"
        return False, "Nie znaleziono node (Node.js)"

    if ext == ".lua":
        luac = _find_luac()
        if luac:
            # luac -p: parsowanie ("precompile") bez tworzenia pliku wyjściowego
            result = subprocess.run(
                [luac, "-p", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia Lua: OK"
            return False, (result.stderr or result.stdout).strip() or "Błąd składni Lua"
        if _find_lua():
            return False, "Nie znaleziono luac — weryfikacja składni Lua wymaga luac"
        return False, "Nie znaleziono lua/luac"

    if ext == ".rb":
        rb = _find_ruby()
        if rb:
            # ruby -c: sprawdzenie składni bez wykonywania
            result = subprocess.run(
                [rb, "-c", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia Ruby: OK"
            return False, result.stderr.strip() or result.stdout.strip() or "Błąd składni Ruby"
        return False, "Nie znaleziono ruby"

    if ext == ".pl":
        pl = _find_perl()
        if pl:
            # perl -c: sprawdzenie składni — wypisuje "syntax OK" na stderr nawet przy sukcesie
            result = subprocess.run(
                [pl, "-c", str(path)],
                capture_output=True, text=True, timeout=10
            )
            out = (result.stderr + result.stdout).strip()
            if result.returncode == 0:
                return True, f"Składnia Perl: {out}" if out else "Składnia Perl: OK"
            return False, out or "Błąd składni Perl"
        return False, "Nie znaleziono perl"

    if ext == ".php":
        php = _find_php()
        if php:
            # php -l: lint — sprawdzenie składni bez wykonywania
            result = subprocess.run(
                [php, "-l", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia PHP: OK"
            return False, result.stdout.strip() or result.stderr.strip() or "Błąd składni PHP"
        return False, "Nie znaleziono php"

    if ext in (".r", ".R"):
        rs = _find_rscript()
        if rs:
            # Rscript --parse-only: parsowanie bez wykonywania (R >= 3.6)
            result = subprocess.run(
                [rs, "--parse-only", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia R: OK"
            return False, result.stderr.strip() or result.stdout.strip() or "Błąd składni R"
        return False, "Nie znaleziono Rscript"

    if ext == ".tcl":
        tcl = _find_tclsh()
        if tcl:
            # tclsh nie ma dedykowanej flagi składni — weryfikujemy przez parse w subinterpreterze
            check_script = f'if {{[catch {{set fd [open "{str(path).replace(chr(92), "/")}" r]; set src [read $fd]; close $fd; parse $src}} err]}} {{puts stderr $err; exit 1}} else {{exit 0}}'
            result = subprocess.run(
                [tcl],
                input=check_script,
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia Tcl: OK (wczytany)"
            # Fallback: sam tclsh parsuje plik przy załadowaniu — nie ma statycznej weryfikacji
            return False, result.stderr.strip() or "Nie można zweryfikować składni Tcl (brak parse)"
        return False, "Nie znaleziono tclsh"

    if ext == ".wsf":
        if not IS_WINDOWS:
            return False, ".wsf — dostępne tylko na Windows"
        cs = shutil.which("cscript")
        if cs:
            # cscript //NoExecute sprawdza składnię bez wykonywania
            result = subprocess.run(
                [cs, "//NoLogo", "//NoExecute", str(path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Składnia WSF: OK"
            return False, (result.stderr or result.stdout).strip() or "Błąd składni WSF"
        return False, "Nie znaleziono cscript.exe"

    if ext == ".hta":
        if not IS_WINDOWS:
            return False, ".hta — dostępne tylko na Windows"
        mshta = _find_mshta()
        if mshta:
            # mshta nie ma trybu weryfikacji składni — sprawdzamy tylko czy plik jest czytelny
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                if not content.strip():
                    return False, "Plik HTA jest pusty"
                return True, "Plik HTA: wczytany (pełna weryfikacja tylko w runtime)"
            except Exception as exc:
                return False, str(exc)
        return False, "Nie znaleziono mshta.exe"

    if ext == ".reg":
        if not IS_WINDOWS:
            return False, ".reg — dostępne tylko na Windows"
        try:
            # Weryfikacja: plik musi zaczynać się od nagłówka Windows Registry Editor
            raw = path.read_bytes()
            # Obsługa BOM UTF-16 LE (typowe dla plików .reg z Windows)
            if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
                content = raw.decode("utf-16", errors="replace")
            else:
                content = raw.decode("utf-8", errors="replace")
            first_line = content.strip().splitlines()[0] if content.strip() else ""
            valid_headers = (
                "Windows Registry Editor Version 5.00",
                "REGEDIT4",
            )
            if not any(first_line.startswith(h) for h in valid_headers):
                return False, f"Nieprawidłowy nagłówek .reg: {first_line!r}"
            return True, "Plik REG: nagłówek poprawny (uruchomienie wymaga potwierdzenia)"
        except Exception as exc:
            return False, str(exc)

    if ext == ".go":
        go = _find_go()
        if go:
            # go vet: analiza statyczna; go build -o /dev/null: kompilacja bez pliku wyjściowego
            result = subprocess.run(
                [go, "vet", str(path)],
                capture_output=True, text=True, timeout=30,
                cwd=str(path.parent),
            )
            if result.returncode == 0:
                return True, "Składnia Go: OK (go vet)"
            return False, (result.stderr or result.stdout).strip() or "Błąd go vet"
        return False, "Nie znaleziono go"

    if ext == ".java":
        _, javac = _find_java()
        if javac:
            result = subprocess.run(
                [javac, "-proc:none", str(path)],
                capture_output=True, text=True, timeout=30,
                cwd=str(path.parent),
            )
            if result.returncode == 0:
                # Usuń wygenerowany .class z katalogu skryptu
                class_file = path.with_suffix(".class")
                if class_file.exists():
                    try:
                        class_file.unlink()
                    except OSError:
                        pass
                return True, "Składnia Java: OK (javac)"
            return False, result.stderr.strip() or result.stdout.strip() or "Błąd javac"
        java, _ = _find_java()
        if java:
            return False, "Nie znaleziono javac — wymagany JDK (nie tylko JRE)"
        return False, "Nie znaleziono java/javac"

    if ext in (".cs", ".csx"):
        ds = _find_dotnet_script()
        if ds and "dotnet-script" in os.path.basename(ds):
            # dotnet-script --help nie kompiluje — nie ma trybu dry-run; informujemy tylko
            return True, "Znaleziono dotnet-script (weryfikacja składni C# tylko w runtime)"
        dotnet = shutil.which("dotnet")
        if dotnet:
            return False, "Wymagany dotnet-script: dotnet tool install -g dotnet-script"
        return False, "Nie znaleziono dotnet-script ani dotnet"

    # Special case for TypeScript
    if ext == ".ts":
        runner_ts, mode = _find_ts_runner()
        if runner_ts:
            if mode == "deno":
                result = subprocess.run(
                    [runner_ts, "check", str(path)],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0:
                    return True, "Składnia TypeScript: OK (deno check)"
                return False, (result.stderr or result.stdout).strip() or "Błąd deno check"
            # ts-node: sprawdź przez tsc jeśli dostępny
        _, mode = _find_ts_runner()
        if mode == "deno":
            cmd = [runner_path, "check", str(path)]
        else: # ts-node
            tsc = shutil.which("tsc")
            if tsc:
                result = subprocess.run(
                    [tsc, "--noEmit", "--allowJs", "--checkJs", str(path)],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(path.parent),
                )
                if result.returncode == 0:
                    return True, "Składnia TypeScript: OK (tsc --noEmit)"
                return False, result.stdout.strip() or result.stderr.strip() or "Błąd tsc"
            return True, "Znaleziono ts-node (brak tsc — weryfikacja składni TS ograniczona)"
        return False, "Nie znaleziono ts-node ani deno"
    else:
        path_esc = str(path).replace(chr(92), "/")
        cmd = [arg.format(runner=runner_path, path=str(path), path_esc=path_esc) for arg in config["template"]]

    if ext == ".coffee":
        coffee = _find_coffee()
        if coffee:
            # coffee -p: kompiluje do JS na stdout bez zapisywania — weryfikacja składni
            result = subprocess.run(
                [coffee, "-p", str(path)],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return True, "Składnia CoffeeScript: OK (coffee -p)"
            return False, result.stderr.strip() or result.stdout.strip() or "Błąd składni CoffeeScript"
        return False, "Nie znaleziono coffee (npm i -g coffeescript)"
    result = subprocess.run(
        cmd, input=config.get("input", "").format(path_esc=path_esc),
        capture_output=True, text=True, timeout=30, cwd=str(path.parent)
    )

    if ext == ".exs":
        elixir = _find_elixir()
        if elixir:
            # elixir --no-halt -e: compile_string sprawdza składnię bez uruchamiania skryptu
            check_code = (
                f'try do\n'
                f'  Code.compile_file("{str(path).replace(chr(92), "/")}")\n'
                f'  IO.puts("OK")\n'
                f'rescue e ->\n'
                f'  IO.puts(:stderr, Exception.message(e))\n'
                f'  System.halt(1)\n'
                f'end'
            )
            result = subprocess.run(
                [elixir, "-e", check_code],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return True, "Składnia Elixir: OK"
            return False, result.stderr.strip() or result.stdout.strip() or "Błąd składni Elixir"
        return False, "Nie znaleziono elixir"
    if result.returncode == 0:
        # Perl -c prints "syntax OK" on success, so we might want to show it
        out = (result.stderr + result.stdout).strip()
        return True, f"{config['ok_msg']}: {out}" if out and ext == ".pl" else config["ok_msg"]
    return False, (result.stderr or result.stdout).strip() or config["err_msg"]

    return False, f"Nieobsługiwane rozszerzenie: {ext!r}"


# ── Wykrywanie kodowania ───────────────────────────────────────────────────────
def _detect_encoding(path: Path) -> str:
    """
    Wykryj kodowanie pliku skryptu.
    Kolejność: BOM → heurystyka Windows (cp1250 dla .bat/.cmd/.vbs/.wsf)
    → próba UTF-8 → fallback cp1250 / latin-2.
    Nie wymaga chardet; działa w 100% na stdlib.
    """
    try:
        raw = path.read_bytes()
    except OSError:
        return "utf-8"

    # BOM — jednoznaczna identyfikacja
    if raw[:3] == b'\xef\xbb\xbf':
        return "utf-8-sig"
    if raw[:2] == b'\xff\xfe':
        return "utf-16-le"
    if raw[:2] == b'\xfe\xff':
        return "utf-16-be"
    if raw[:4] == b'\x00\x00\xfe\xff':
        return "utf-32-be"
    if raw[:4] == b'\xff\xfe\x00\x00':
        return "utf-32-le"

    # Pliki Windows Script — zawsze CP1250 na polskim systemie
    if IS_WINDOWS and path.suffix.lower() in (".bat", ".cmd", ".vbs", ".wsf"):
        return "cp1250"

    # Próba UTF-8 (strict — brak replace)
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass

    # Heurystyka CP1250 — polskie znaki mają konkretne bajty w CP1250:
    # ą=0xa5 ć=0xe6 ę=0xea ł=0xb3 ń=0xf1 ó=0xf3 ś=0x9c ź=0x9f ż=0xbf
    # Ą=0xa4 Ć=0xc6 Ę=0xca Ł=0xa3 Ń=0xd1 Ó=0xd3 Ś=0x8c Ź=0x8f Ż=0xaf
    _CP1250_PL = frozenset((
        0xa5, 0xe6, 0xea, 0xb3, 0xf1, 0xf3, 0x9c, 0x9f, 0xbf,
        0xa4, 0xc6, 0xca, 0xa3, 0xd1, 0xd3, 0x8c, 0x8f, 0xaf,
    ))
    if any(b in _CP1250_PL for b in raw):
        return "cp1250"
    return "utf-8"


# ── Parser sekwencji ANSI ESC ─────────────────────────────────────────────────
import re as _re

# Regex dopasowujący sekwencje ESC CSI: ESC [ <params> <final_byte>
_ANSI_RE = _re.compile(r'\x1b\[([\d;]*)([A-Za-z])')

# Predefiniowane kolory ANSI 3/4-bit → hex (ciemne tło)
_ANSI_FG = {
    30: "#1e1e2e",  # black  → tło (widoczne jako ciemny)
    31: "#f87171",  # red
    32: "#4ade80",  # green
    33: "#fbbf24",  # yellow
    34: "#60a5fa",  # blue
    35: "#c084fc",  # magenta
    36: "#34d399",  # cyan
    37: "#e2e8f0",  # white
    90: "#64748b",  # bright black (gray)
    91: "#fca5a5",  # bright red
    92: "#86efac",  # bright green
    93: "#fde68a",  # bright yellow
    94: "#93c5fd",  # bright blue
    95: "#d8b4fe",  # bright magenta
    96: "#6ee7b7",  # bright cyan
    97: "#f8fafc",  # bright white
}
_ANSI_BG = {k + 10: v for k, v in _ANSI_FG.items()}  # 40–47, 100–107

# Paleta 256-kolorowa (6×6×6 kostka + skale szarości)
def _ansi_256_to_hex(n: int) -> str:
    if n < 16:
        base = [
            "#000000","#800000","#008000","#808000",
            "#000080","#800080","#008080","#c0c0c0",
            "#808080","#ff0000","#00ff00","#ffff00",
            "#0000ff","#ff00ff","#00ffff","#ffffff",
        ]
        return base[n]
    if n < 232:
        n -= 16
        b = n % 6;  n //= 6
        g = n % 6;  r = n // 6
        def _c(x): return 0 if x == 0 else 55 + x * 40
        return f"#{_c(r):02x}{_c(g):02x}{_c(b):02x}"
    # skala szarości 232–255
    v = 8 + (n - 232) * 10
    return f"#{v:02x}{v:02x}{v:02x}"


def _ansi_to_spans(text: str, base_tag: str) -> list[tuple[str, str]]:
    """
    Parsuj sekwencje ANSI ESC w `text`.
    Zwraca listę (fragment_tekstu, tag_name) gotową do insert() w tk.Text.
    Tagi dynamiczne tworzone on-the-fly: 'ansi_fg_#rrggbb', 'ansi_bg_#rrggbb',
    'ansi_bold', 'ansi_ul', 'ansi_italic', base_tag (reset/domyślny).
    Sekwencje nieobsługiwane (cursor move, erase itp.) są usuwane z tekstu.
    """
    spans: list[tuple[str, str]] = []
    # Stan bieżący
    fg: str | None = None
    bg: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False

    def _make_tag() -> str:
        """Zbuduj unikalną nazwę tagu z bieżącego stanu."""
        parts = [base_tag]
        if fg:   parts.append(f"fg{fg.replace('#','')}")
        if bg:   parts.append(f"bg{bg.replace('#','')}")
        if bold: parts.append("bold")
        if italic: parts.append("it")
        if underline: parts.append("ul")
        return "_".join(parts) if len(parts) > 1 else base_tag

    pos = 0
    for m in _ANSI_RE.finditer(text):
        start, end = m.span()
        # Tekst przed sekwencją
        if start > pos:
            spans.append((text[pos:start], _make_tag()))
        pos = end

        cmd = m.group(2)
        if cmd != 'm':
            # Ignoruj sekwencje inne niż SGR (Set Graphics Rendition)
            continue

        params_raw = m.group(1)
        params = [int(x) for x in params_raw.split(';') if x.isdigit()] if params_raw else [0]

        i = 0
        while i < len(params):
            p = params[i]
            if p == 0:
                fg = bg = None; bold = italic = underline = False
            elif p == 1:
                bold = True
            elif p == 2:
                bold = False  # faint — traktuj jako reset bold
            elif p == 3:
                italic = True
            elif p == 4:
                underline = True
            elif p == 22:
                bold = False
            elif p == 23:
                italic = False
            elif p == 24:
                underline = False
            elif p in _ANSI_FG:
                fg = _ANSI_FG[p]
            elif p in _ANSI_BG:
                bg = _ANSI_BG[p]
            elif p == 39:
                fg = None
            elif p == 49:
                bg = None
            elif p in (38, 48):
                # 256-kolor: 38;5;N lub truecolor: 38;2;R;G;B
                is_fg = (p == 38)
                if i + 1 < len(params) and params[i+1] == 5 and i + 2 < len(params):
                    color = _ansi_256_to_hex(params[i+2])
                    if is_fg: fg = color
                    else:     bg = color
                    i += 2
                elif i + 1 < len(params) and params[i+1] == 2 and i + 4 < len(params):
                    r, g, b = params[i+2], params[i+3], params[i+4]
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    if is_fg: fg = color
                    else:     bg = color
                    i += 4
            i += 1

    # Reszta tekstu po ostatniej sekwencji
    if pos < len(text):
        spans.append((text[pos:], _make_tag()))

    return spans


# ─────────────────────────────────────────────────────────────────────────────
class SandboxWindow(tk.Toplevel):
    """Okno sandbox — uruchamianie i testowanie skryptów (.bat/.cmd/.ps1/.py/.vbs/.sh/.js/.lua/.rb/.pl/.php/.r/.tcl/.wsf/.hta/.reg/.go/.java/.cs/.csx/.ts/.coffee/.exs)."""
    def __init__(self, parent: tk.Widget, theme: dict, *, title: str = "🧪 Sandbox", initial_path: str | None = None) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.minsize(640, 440)
        self.geometry("800x540")
        self.geometry("800x600")

        self._theme    = theme
        self._history: list[str] = []
        self._hist_idx: int = -1
        self._running_proc: subprocess.Popen | None = None
        self._last_script: Path | None = None
        self._pygments_tag_cache: set[str] = set()
        self._current_lexer = None
        self._main_app_ref = weakref.ref(parent) if hasattr(parent, "scripts") else None
        self._always_on_top: bool = False

        self._apply_theme()
        self._build_toolbar()
        self._build_input()
        self._build_panes()
        self._print_banner()

        self._entry.focus_set()
        if _PYGMENTS_AVAILABLE:
            self._configure_pygments_tags()
            self._editor.bind("<<Modified>>", self._on_editor_modified, add=True)

        if initial_path:
            self.after(100, lambda p=initial_path: self._load_file(p))

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_file(self, path_str: str):
        path = Path(path_str)
        if not path.is_file():
            return
        content, _ = _read_source(path)
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", content)
        self._update_lexer_from_path(path_str)

    # ── Motyw ──────────────────────────────────────────────────────────────
    def _apply_theme(self) -> None:
        t = self._theme
        self.configure(bg=t.get("DARK", "#0f1117"))

    # ── Toolbar ────────────────────────────────────────────────────────────
    def _build_toolbar(self) -> None:
        t = self._theme
        bar = tk.Frame(self, bg=t.get("PANEL", "#181c27"), pady=4)
        bar.pack(fill=tk.X, side=tk.TOP)

        btn_kw = dict(
            bg=t.get("CARD", "#1e2233"),
            fg=t.get("TEXT", "#e2e8f0"),
            activebackground=t.get("ACCENT", "#4ade80"),
            activeforeground=t.get("DARK", "#0f1117"),
            relief=tk.FLAT, padx=10, pady=2, cursor="hand2"
        )
        btn_red = {**btn_kw, "activebackground": t.get("RED", "#f87171")}
        btn_yel = {**btn_kw, "activebackground": t.get("YELLOW", "#fbbf24")}

        tk.Button(bar, text="▶  Uruchom",    command=self._run_command,   **btn_kw).pack(side=tk.LEFT, padx=(8, 2))
        tk.Button(bar, text="🔬  Testuj",    command=self._test_current,  **btn_yel).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="📂  Otwórz",    command=self._browse_script, **btn_kw).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="⛔  Stop",      command=self._stop_process,  **btn_red).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="🗑  Wyczyść",   command=self._clear,         **btn_kw).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="💾  Zapisz log",command=self._save_log,      **btn_kw).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="📌  Zawsze na wierzchu", command=self._toggle_always_on_top, **btn_kw).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="▶ Uruchom", command=self._run_editor_content, **btn_kw).pack(side=tk.LEFT, padx=(8, 2))
        tk.Button(bar, text="🔬 Testuj", command=self._test_editor_content, **btn_yel).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="📂 Otwórz", command=self._browse_script, **btn_kw).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="💾 Zapisz", command=self._save_editor_content, **btn_kw).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="⛔ Stop", command=self._stop_process, **btn_red).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="🗑 Wyczyść", command=self._clear, **btn_kw).pack(side=tk.LEFT, padx=2)
        # Store reference to "Add to psLauncher" button for safe hiding
        self._add_to_pslauncher_btn = tk.Button(bar, text="✚ Dodaj do psLauncher", command=self._add_to_pslauncher, **btn_kw)
        self._add_to_pslauncher_btn.pack(side=tk.LEFT, padx=2)

        self._status_lbl = tk.Label(
            bar, text="Gotowy.", font=(_FONT_LABEL[0], _FONT_LABEL[1]),
            bg=t.get("PANEL", "#181c27"), fg=t.get("DIM", "#64748b")
        )
        self._status_lbl.pack(side=tk.RIGHT, padx=8)
        if self._main_app_ref is None or self._main_app_ref() is None:
            if self._add_to_pslauncher_btn:
                self._add_to_pslauncher_btn.pack_forget()

    def _build_panes(self) -> None:
        t = self._theme
        panes = tk.PanedWindow(self, orient="vertical", bg=t.get("DARK", "#0f1117"), sashwidth=4, sashrelief="flat")
        panes.pack(fill="both", expand=True, padx=6, pady=6)

        # Top pane: Editor
        editor_frame = tk.Frame(panes, bg=t.get("DARK", "#0f1117"))
        self._editor = tk.Text(
            editor_frame, font=_FONT_CONSOLE, bg=t.get("DARK", "#0f1117"),
            fg=t.get("TEXT", "#e2e8f0"), insertbackground=t.get("ACCENT", "#4ade80"),
            selectbackground=t.get("ACCENT2", "#38bdf8"), relief=tk.FLAT,
            wrap="word", undo=True,
        )
        self._editor.pack(fill="both", expand=True)
        panes.add(editor_frame, minsize=100)

        # Bottom pane: Console
        console_frame = tk.Frame(panes, bg=t.get("DARK", "#0f1117"))
        self._build_console(console_frame) # Pass the correct parent
        panes.add(console_frame, minsize=100)

    # ── Konsola ────────────────────────────────────────────────────────────
    def _build_console(self, parent: tk.Frame) -> None:
        t = self._theme
        sb = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._console = tk.Text(
            parent,
            font=_FONT_CONSOLE,
            bg=t.get("DARK", "#0f1117"),
            fg=t.get("TEXT", "#e2e8f0"),
            insertbackground=t.get("ACCENT", "#4ade80"),
            selectbackground=t.get("ACCENT2", "#38bdf8"),
            relief=tk.FLAT, wrap=tk.WORD, state=tk.DISABLED,
            yscrollcommand=sb.set,
        )
        self._console.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._console.yview)

        # Ctrl+C: kopiowanie zaznaczonego tekstu z wyłączonego widgetu
        self._console.bind("<Control-c>", self._copy_selection)

        # Tagi kolorów wyjścia
        self._console.tag_config("prompt",  foreground=t.get("ACCENT",  "#4ade80"))
        self._console.tag_config("output",  foreground=t.get("TEXT",    "#e2e8f0"))
        self._console.tag_config("stderr",  foreground=t.get("RED",     "#f87171"))
        self._console.tag_config("error",   foreground=t.get("RED",     "#f87171"))
        self._console.tag_config("info",    foreground=t.get("ACCENT2", "#38bdf8"))
        self._console.tag_config("dim",     foreground=t.get("DIM",     "#64748b"))
        self._console.tag_config("banner",  foreground=t.get("YELLOW",  "#fbbf24"))
        self._console.tag_config("ok",      foreground=t.get("ACCENT",  "#4ade80"))
        self._console.tag_config("warn",    foreground=t.get("YELLOW",  "#fbbf24"))
        self._console.tag_config("header",  foreground=t.get("ACCENT2", "#38bdf8"))

        # Stałe tagi ANSI SGR (atrybuty)
        self._console.tag_config("ansi_bold",   font=(_FONT_CONSOLE[0], _FONT_CONSOLE[1], "bold"))
        self._console.tag_config("ansi_italic", font=(_FONT_CONSOLE[0], _FONT_CONSOLE[1], "italic"))
        self._console.tag_config("ansi_ul",     underline=True)

        # Cache tagów dynamicznych (fg/bg/kombinacje) — unikamy duplikowania tag_config
        self._ansi_tag_cache: set[str] = set()

    # ── Pole wejściowe ─────────────────────────────────────────────────────
    def _build_input(self) -> None:
        t = self._theme
        frame = tk.Frame(self, bg=t.get("PANEL", "#181c27"), pady=4)
        frame.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=4)

        tk.Label(
            frame, text="sandbox>", font=(_FONT_LABEL[0], _FONT_LABEL[1], "bold"),
            bg=t.get("PANEL", "#181c27"), fg=t.get("ACCENT", "#4ade80")
        ).pack(side=tk.LEFT, padx=(0, 6))

        self._input_var = tk.StringVar()
        self._entry = tk.Entry(
            frame, textvariable=self._input_var,
            font=_FONT_CONSOLE,
            bg=t.get("CARD", "#1e2233"),
            fg=t.get("TEXT", "#e2e8f0"),
            insertbackground=t.get("ACCENT", "#4ade80"),
            relief=tk.FLAT,
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._entry.bind("<Return>",    lambda _e: self._run_command())
        self._entry.bind("<Up>",        lambda _e: self._hist_prev())
        self._entry.bind("<Down>",      lambda _e: self._hist_next())
        self._entry.bind("<Control-l>", lambda _e: self._clear())

    # ── Drukowanie ─────────────────────────────────────────────────────────
    def _print(self, text: str, tag: str = "output") -> None:
        self._console.config(state=tk.NORMAL)
        self._console.insert(tk.END, text, tag)
        self._console.see(tk.END)
        self._console.config(state=tk.DISABLED)

    def _println(self, text: str, tag: str = "output") -> None:
        self._print(text + "\n", tag)

    def _ensure_ansi_tag(self, tag_name: str) -> None:
        """
        Zarejestruj tag dynamiczny (ANSI kolor/styl) jeśli jeszcze nie istnieje.
        Nazwa tagu koduje atrybuty, np.:
          'output_fgf87171_bold'  → fg=#f87171, bold
          'stderr_bg1e1e2e'       → bg=#1e1e2e
        """
        if tag_name in self._ansi_tag_cache:
            return
        self._ansi_tag_cache.add(tag_name)

        kw: dict = {}
        parts = tag_name.split("_")

        # Zbierz fg/bg/bold/italic/underline z nazwy tagu
        font_bold   = "bold"   in parts
        font_italic = "it"     in parts
        has_ul      = "ul"     in parts

        for part in parts:
            if part.startswith("fg") and len(part) == 8:
                kw["foreground"] = "#" + part[2:]
            elif part.startswith("bg") and len(part) == 8:
                kw["background"] = "#" + part[2:]

        if font_bold and font_italic:
            kw["font"] = (_FONT_CONSOLE[0], _FONT_CONSOLE[1], "bold italic")
        elif font_bold:
            kw["font"] = (_FONT_CONSOLE[0], _FONT_CONSOLE[1], "bold")
        elif font_italic:
            kw["font"] = (_FONT_CONSOLE[0], _FONT_CONSOLE[1], "italic")

        if has_ul:
            kw["underline"] = True

        # Jeśli brak fg w tagu — dziedzicz kolor z base_tag (pierwsza część)
        if "foreground" not in kw:
            base = parts[0] if parts else "output"
            base_fg = {
                "output": self._theme.get("TEXT",    "#e2e8f0"),
                "stderr": self._theme.get("RED",     "#f87171"),
                "error":  self._theme.get("RED",     "#f87171"),
                "info":   self._theme.get("ACCENT2", "#38bdf8"),
                "dim":    self._theme.get("DIM",     "#64748b"),
                "ok":     self._theme.get("ACCENT",  "#4ade80"),
                "warn":   self._theme.get("YELLOW",  "#fbbf24"),
            }.get(base, self._theme.get("TEXT", "#e2e8f0"))
            kw["foreground"] = base_fg

        self._console.tag_config(tag_name, **kw)

    def _print_ansi(self, text: str, base_tag: str = "output") -> None:
        """
        Wypisz tekst z obsługą sekwencji ANSI ESC do konsoli.
        Jeśli brak sekwencji ESC — działa identycznie jak _println.
        """
        if '\x1b' not in text:
            self._println(text, base_tag)
            return
        self._console.config(state=tk.NORMAL)
        spans = _ansi_to_spans(text, base_tag)
        for fragment, tag_name in spans:
            self._ensure_ansi_tag(tag_name)
            self._console.insert(tk.END, fragment, tag_name)
        self._console.insert(tk.END, "\n")
        self._console.see(tk.END)
        self._console.config(state=tk.DISABLED)

    def _copy_selection(self, _event=None) -> str:
        """Kopiuj zaznaczony tekst z konsoli do schowka (Ctrl+C)."""
        try:
            text = self._console.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass  # Brak zaznaczenia — ignoruj
        return "break"  # Zablokuj domyślne zachowanie

    def _print_banner(self) -> None:
        self._print(_BANNER, "dim")

    def _print_separator(self) -> None:
        self._println("─" * 44, "dim")

    # ── Główny dispatcher ──────────────────────────────────────────────────
    def _run_command(self) -> None:
        raw = self._input_var.get().strip()
        if not raw:
            return

        if not self._history or self._history[-1] != raw:
            self._history.append(raw)
        self._hist_idx = len(self._history)
        self._input_var.set("")

        ts = datetime.now().strftime("%H:%M:%S")
        self._println(f"[{ts}] sandbox> {raw}", "prompt")

        # Sprawdź czy to ścieżka do skryptu
        path, extra_args = self._resolve_script_path(raw)
        if path:
            self._last_script = path
            self._run_script(path, extra_args)
            return

        # Sprawdź czy to bezpośrednia inwokacja powłoki/interpretera,
        # np. "cmd.exe /c plik.bat" albo "powershell -File skrypt.ps1"
        argv = self._resolve_shell_invocation(raw)
        if argv:
            self._run_raw_command(argv)
            return

        self._handle_builtin(raw)

    def _resolve_shell_invocation(self, text: str) -> list[str] | None:
        """Rozpoznaje komendy zaczynające się od znanej powłoki/interpretera
        (cmd.exe, powershell, python, node, bash, ...) i zwraca pełną listę
        argumentów do subprocess.Popen, albo None jeśli pierwszy token nie
        jest rozpoznaną powłoką."""
        parts = _split_commandline(text)
        if not parts:
            return None
        head = parts[0]
        # Wyciągnij samą nazwę pliku z ewentualnej pełnej ścieżki, niezależnie
        # od separatora (\ na Windows, / na innych platformach) — Path().name
        # nie rozdzieli backslashy poza WindowsPath, więc robimy to jawnie.
        head_name = head.replace("\\", "/").rsplit("/", 1)[-1]
        if head_name.lower() not in {s.lower() for s in _SHELL_INVOCATIONS}:
            return None
        return parts

    def _resolve_script_path(self, text: str) -> tuple[Path | None, list[str]]:
        """Sprawdź czy tekst wskazuje na plik skryptu; zwraca (path, extra_args)."""
        parts = _split_commandline(text)
        if not parts:
            return None, []
        p = Path(parts[0])
        if p.exists() and p.is_file():
            if p.suffix.lower() in (".bat", ".cmd", ".ps1", ".py", ".vbs", ".sh", ".js", ".lua",
                                    ".rb", ".pl", ".php", ".r", ".tcl",
                                    ".wsf", ".hta", ".reg",
                                    ".go", ".java", ".cs", ".csx", ".ts", ".coffee", ".exs"):
                return p, parts[1:]
        return None, []

    def _run_editor_content(self):
        """Uruchom zawartość edytora jako skrypt tymczasowy."""
        code = self._editor.get("1.0", "end-1c")
        if not code.strip():
            return

        # Zgadnij typ skryptu na podstawie shebangu lub zawartości
        first_line = code.splitlines()[0] if code else ""
        ext = ".txt"
        if first_line.startswith("#!/"):
            if "python" in first_line: ext = ".py"
            elif "bash" in first_line or "sh" in first_line: ext = ".sh"
            elif "node" in first_line: ext = ".js"
        elif self._current_lexer:
            ext = f".{self._current_lexer.aliases[0]}"

        # Zapisz do pliku tymczasowego
        temp_dir = Path(os.environ.get("TEMP", "/tmp"))
        temp_file = temp_dir / f"sandbox_{os.getpid()}{ext}"
        temp_file.write_text(code, encoding="utf-8")

        self._last_script = temp_file
        self._run_script(temp_file)
        # Plik tymczasowy zostanie usunięty w _on_process_done

    # ── Uruchamianie skryptów ──────────────────────────────────────────────
    def _run_script(self, path: Path, extra_args: list[str] | None = None) -> None:
        """Uruchom skrypt w tle; strumieniuj stdout i stderr na bieżąco."""
        if _logger:
            _logger.start_performance(f"script_execution_{path.name}")
        runner = _build_runner(path)
        ext = path.suffix.lower()
        if runner is None:
            ext = path.suffix.lower()
            if ext in (".bat", ".cmd", ".vbs") and not IS_WINDOWS:
                self._println(f"❌  {ext.upper()} — dostępne tylko na Windows.", "error")
            elif ext == ".ps1":
                self._println("❌  PowerShell nie znaleziony (powershell / pwsh).", "error")
            elif ext == ".sh":
                self._println("❌  Nie znaleziono interpretera shell (bash / sh).", "error")
            elif ext == ".js":
                self._println("❌  Nie znaleziono interpretera Node.js (node).", "error")
            elif ext == ".lua":
                self._println("❌  Nie znaleziono interpretera Lua (lua / luajit).", "error")
            elif ext == ".rb":
                self._println("❌  Nie znaleziono interpretera Ruby (ruby).", "error")
            elif ext == ".pl":
                self._println("❌  Nie znaleziono interpretera Perl (perl).", "error")
            elif ext == ".php":
                self._println("❌  Nie znaleziono interpretera PHP (php).", "error")
            elif ext in (".r", ".R"):
                self._println("❌  Nie znaleziono interpretera R (Rscript).", "error")
            elif ext == ".tcl":
                self._println("❌  Nie znaleziono interpretera Tcl (tclsh).", "error")
            elif ext == ".wsf":
                if not IS_WINDOWS:
                    self._println("❌  .wsf — dostępne tylko na Windows.", "error")
                else:
                    self._println("❌  Nie znaleziono cscript.exe.", "error")
            elif ext == ".hta":
                if not IS_WINDOWS:
                    self._println("❌  .hta — dostępne tylko na Windows.", "error")
                else:
                    self._println("❌  Nie znaleziono mshta.exe.", "error")
            elif ext == ".reg":
                if not IS_WINDOWS:
                    self._println("❌  .reg — dostępne tylko na Windows.", "error")
                else:
                    self._println("❌  Nie znaleziono regedit.exe.", "error")
            elif ext == ".go":
                self._println("❌  Nie znaleziono narzędzia go (https://go.dev/dl/).", "error")
            elif ext == ".java":
                self._println("❌  Nie znaleziono java/javac (JDK 11+).", "error")
            elif ext in (".cs", ".csx"):
                self._println("❌  Nie znaleziono dotnet-script (uruchom: dotnet tool install -g dotnet-script).", "error")
            elif ext == ".ts":
                self._println("❌  Nie znaleziono ts-node ani deno (uruchom: npm i -g ts-node).", "error")
            elif ext == ".coffee":
                self._println("❌  Nie znaleziono coffee (uruchom: npm i -g coffeescript).", "error")
            elif ext == ".exs":
                self._println("❌  Nie znaleziono elixir (https://elixir-lang.org/install.html).", "error")
            else:
                self._println(f"❌  Nieobsługiwane rozszerzenie: {ext!r}", "error")
            config = RUNNER_CONFIG.get(ext)
            error_msg = config.get("error") if config else f"❌  Nieobsługiwane rozszerzenie: {ext!r}"
            self._println(error_msg, "error")
            if _logger:
                _logger.error(f"SANDBOX: {error_msg}", context={"file": str(path), "extension": ext})
            return

        # ── Specjalna obsługa .reg: obowiązkowe potwierdzenie ──────────────
        if path.suffix.lower() == ".reg":
            if self._running_proc and self._running_proc.poll() is None:
                self._println("⚠️  Poprzedni proces wciąż działa. Kliknij ⛔ Stop.", "warn")
                return
            from tkinter import messagebox as _mb
            confirmed = _mb.askyesno(
                "⚠️  Operacja na rejestrze",
                f"Plik '{path.name}' zmodyfikuje rejestr systemu Windows.\n\n"
                "Nieprawidłowe wpisy mogą uszkodzić system.\n\n"
                "Czy na pewno chcesz kontynuować?",
                icon="warning",
            )
            if not confirmed:
                self._println("⛔  Anulowano — rejestr nie został zmieniony.", "warn")
                self._set_status("Anulowano.")
                return
            # regedit /s nie zwraca stdout/stderr — uruchom i czekaj na exit code
            self._println(f"▶  Importowanie do rejestru: {path.name}", "header")
            self._println(f"   Polecenie: {' '.join(runner)}", "dim")
            self._print_separator()
            self._set_status(f"Importowanie: {path.name} …")

            def _run_reg() -> None:
                try:
                    proc = subprocess.run(runner, capture_output=True, timeout=30)
                    rc = proc.returncode
                    self.after(0, lambda: self._on_process_done(rc))
                    if rc == 0:
                        self.after(0, lambda: self._println("✅  Rejestr zaktualizowany pomyślnie.", "ok"))
                    else:
                        self.after(0, lambda: self._println(f"❌  regedit zakończył się kodem {rc}.", "error"))
                except subprocess.TimeoutExpired:
                    self.after(0, lambda: self._println("⏱  Timeout — regedit nie odpowiedział.", "warn"))
                except Exception as exc:
                    self.after(0, lambda e=exc: self._println(f"❌  Błąd: {e}", "error"))

            threading.Thread(target=_run_reg, daemon=True).start()
            return

        if self._running_proc and self._running_proc.poll() is None:
            self._println("⚠️  Poprzedni proces wciąż działa. Kliknij ⛔ Stop.", "warn")
            return

        self._println(f"▶  Uruchamianie: {path.name}  [{path.suffix.upper()}]", "header")
        if extra_args:
            runner = runner + extra_args
        self._println(f"   Polecenie: {' '.join(runner)}", "dim")
        self._print_separator()
        self._set_status(f"Uruchamianie: {path.name} …")
        if _logger:
            _logger.info(f"SANDBOX: Running script {path.name}", context={"command": ' '.join(runner), "working_dir": str(path.parent)})

        def _run() -> None:
            try:
                enc = _detect_encoding(path)
                proc = subprocess.Popen(
                    runner,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding=enc,
                    errors="replace",
                    cwd=str(path.parent),
                    env=os.environ.copy(),
                )
                self._running_proc = proc
                self._stream_output(proc)
            except FileNotFoundError as exc:
                self.after(0, lambda e=exc: self._println(f"❌  Nie znaleziono: {e}", "error"))
                if _logger:
                    _logger.error(f"SANDBOX: File not found: {exc}", context={"file": str(path)})
            except Exception as exc:
                self.after(0, lambda e=exc: self._println(f"❌  Błąd uruchomienia: {e}", "error"))
                if _logger:
                    _logger.error(f"SANDBOX: Launch error: {exc}", context={"file": str(path)})

        threading.Thread(target=_run, daemon=True).start()

    def _run_raw_command(self, argv: list[str]) -> None:
        """Uruchom dowolną komendę powłoki podaną bezpośrednio przez użytkownika
        (np. ['cmd.exe', '/c', 'D:\\skrypt.bat'], ['powershell', '-File', '...']).
        Działa identycznie jak _run_script (streaming stdout/stderr na żywo),
        ale bez wykrywania interpretera na podstawie rozszerzenia — argv jest
        już kompletne."""
        if self._running_proc and self._running_proc.poll() is None:
            self._println("⚠️  Poprzedni proces wciąż działa. Kliknij ⛔ Stop.", "warn")
            return

        self._println("▶  Uruchamianie polecenia powłoki", "header")
        self._println(f"   Polecenie: {' '.join(argv)}", "dim")
        self._print_separator()
        self._set_status("Uruchamianie polecenia powłoki …")
        if _logger:
            _logger.info(f"SANDBOX: Running shell command", context={"command": ' '.join(argv)})

        def _run() -> None:
            try:
                proc = subprocess.Popen(
                    argv,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=str(Path.cwd()),
                    env=os.environ.copy(),
                )
                self._running_proc = proc
                self._stream_output(proc)
            except FileNotFoundError as exc:
                self.after(0, lambda e=exc: self._println(f"❌  Nie znaleziono: {e}", "error"))
            except Exception as exc:
                self.after(0, lambda e=exc: self._println(f"❌  Błąd uruchomienia: {e}", "error"))

        threading.Thread(target=_run, daemon=True).start()

    def _stream_output(self, proc: subprocess.Popen) -> None:
        """Czytaj stdout i stderr proc w osobnych wątkach; drukuj do konsoli z obsługą ANSI."""
        lock = threading.Lock()

        def _read(stream, tag: str) -> None:
            for line in stream:
                line_s = line.rstrip("\n")
                with lock:
                    self.after(0, lambda l=line_s, t=tag: self._print_ansi(l, t))
            stream.close()

        t_out = threading.Thread(target=_read, args=(proc.stdout, "output"), daemon=True)
        t_err = threading.Thread(target=_read, args=(proc.stderr, "stderr"), daemon=True)
        t_out.start()
        t_err.start()

        def _wait() -> None:
            t_out.join()
            t_err.join()
            rc = proc.wait()
            self.after(0, lambda: self._on_process_done(rc))

        threading.Thread(target=_wait, daemon=True).start()

    def _on_process_done(self, returncode: int) -> None:
        self._print_separator()
        tag = "ok" if returncode == 0 else "error"
        icon = "✅" if returncode == 0 else "❌"
        self._println(f"{icon}  Zakończono. Kod wyjścia: {returncode}", tag)
        self._set_status(f"Zakończono (kod {returncode})")
        # Usuń plik tymczasowy, jeśli to był on
        if self._last_script and self._last_script.name.startswith("sandbox_"):
            if self._last_script.exists():
                self._last_script.unlink()
        self._running_proc = None

    # ── Stop ───────────────────────────────────────────────────────────────
    def _stop_process(self) -> None:
        proc = self._running_proc
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    self._println("⛔  Proces zabity (SIGKILL).", "warn")
                    if _logger:
                        _logger.warning("SANDBOX: Process killed (SIGKILL)")
                else:
                    self._println("⛔  Proces przerwany.", "warn")
                    if _logger:
                        _logger.info("SANDBOX: Process terminated")
                self._set_status("Przerwano.")
            except Exception as exc:
                self._println(f"⚠️  Nie można zatrzymać: {exc}", "error")
                if _logger:
                    _logger.error(f"SANDBOX: Failed to stop process: {exc}")
        else:
            self._println("ℹ️  Brak aktywnego procesu.", "dim")

    # ── Test / weryfikacja składni ──────────────────────────────────────────
    def _test_current(self) -> None:
        """Testuj skrypt z pola wejściowego lub ostatni uruchomiony."""
        raw = self._input_var.get().strip()
        path, _ = self._resolve_script_path(raw) if raw else (self._last_script, [])
        if not path:
            self._println("ℹ️  Wpisz ścieżkę do skryptu lub najpierw go uruchom.", "dim")
            return
        self._test_script(path)
    def _test_editor_content(self) -> None:
        """Testuj składnię zawartości edytora."""
        # Działa tak samo jak _run_editor_content, ale wywołuje _test_script
        # zamiast _run_script.
        # Ta logika jest niemal identyczna, więc dla zwięzłości można by ją połączyć,
        # ale na razie zostawiam oddzielnie dla jasności.
        code = self._editor.get("1.0", "end-1c")
        if not code.strip(): return
        first_line = code.splitlines()[0] if code else ""
        ext = ".txt"
        if first_line.startswith("#!/"):
            if "python" in first_line: ext = ".py"
            elif "bash" in first_line or "sh" in first_line: ext = ".sh"
        elif self._current_lexer:
            ext = f".{self._current_lexer.aliases[0]}"

        temp_dir = Path(os.environ.get("TEMP", "/tmp"))
        temp_file = temp_dir / f"sandbox_test_{os.getpid()}{ext}"
        temp_file.write_text(code, encoding="utf-8")

        self._test_script(temp_file)
        # Plik tymczasowy zostanie usunięty w _test_script

    def _test_script(self, path: Path) -> None:
        """Weryfikacja składni bez uruchamiania."""
        if _logger:
            _logger.start_performance(f"syntax_check_{path.name}")
        self._println(f"🔬  Testowanie: {path.name}", "header")
        self._set_status(f"Testowanie: {path.name} …")

        def _run_test() -> None:
            try:
                ok, msg = _syntax_check(path)
                tag = "ok" if ok else "error"
                icon = "✅" if ok else "❌"
                self.after(0, lambda: self._println(f"   {icon}  {msg}", tag))
                self.after(0, lambda: self._set_status(f"Test: {'OK' if ok else 'BŁĄD'}"))
                if _logger:
                    if ok:
                        _logger.info(f"SANDBOX: Syntax check passed for {path.name}")
                    else:
                        _logger.error(f"SANDBOX: Syntax check failed for {path.name}: {msg}")
            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._println("   ⏱  Timeout weryfikacji składni.", "warn"))
                if _logger:
                    _logger.warning(f"SANDBOX: Syntax check timeout for {path.name}")
            except Exception as exc:
                self.after(0, lambda e=exc: self._println(f"   ❌  Błąd testu: {e}", "error"))
                if _logger:
                    _logger.error(f"SANDBOX: Syntax check error for {path.name}: {exc}")
            finally:
                if _logger:
                    _logger.end_performance(f"syntax_check_{path.name}")
                if path.name.startswith("sandbox_test_"):
                    if path.exists():
                        path.unlink()

        threading.Thread(target=_run_test, daemon=True).start()

    # ── Otwórz plik przez dialog ────────────────────────────────────────────
    def _browse_script(self) -> None:
        ftypes = [
            ("Skrypty",           "*.bat;*.cmd;*.ps1;*.py;*.vbs;*.sh;*.js;*.lua;*.rb;*.pl;*.php;*.r;*.tcl;*.wsf;*.hta;*.reg;*.go;*.java;*.cs;*.csx;*.ts;*.coffee;*.exs"),
            ("Batch / CMD",       "*.bat;*.cmd"),
            ("PowerShell",        "*.ps1"),
            ("Python",            "*.py"),
            ("VBScript",          "*.vbs"),
            ("Shell",             "*.sh"),
            ("JavaScript",        "*.js"),
            ("Lua",               "*.lua"),
            ("Ruby",              "*.rb"),
            ("Perl",              "*.pl"),
            ("PHP",               "*.php"),
            ("R",                 "*.r;*.R"),
            ("Tcl",               "*.tcl"),
            ("Windows Script",    "*.wsf"),
            ("HTA",               "*.hta"),
            ("Registry",          "*.reg"),
            ("Go",                "*.go"),
            ("Java",              "*.java"),
            ("C# Script",         "*.cs;*.csx"),
            ("TypeScript",        "*.ts"),
            ("CoffeeScript",      "*.coffee"),
            ("Elixir",            "*.exs"),
            ("Wszystkie pliki",   "*.*"),
        ]
        _default_dir = Path(__file__).parent.parent.parent / "scripts"
        _default_dir.mkdir(parents=True, exist_ok=True)
        path = filedialog.askopenfilename(
            title="Wybierz skrypt do uruchomienia",
            filetypes=ftypes,
            initialdir=str(_default_dir.resolve()),
        )
        if path:
            p = Path(path)
            self._input_var.set(str(p))
            self._last_script = p
            content, _ = _read_source(p)
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", content)
            self._println(f"📂  Załadowano: {p.name}  ({p.suffix.upper()})", "info")
            self._set_status(f"Gotowy: {p.name}")
            self._update_lexer_from_path(path)

    # ── Wbudowane polecenia ─────────────────────────────────────────────────
    def _handle_builtin(self, cmd: str) -> None:
        lower = cmd.lower().strip()

        if lower in ("help", "?", "pomoc"):
            self._println(
                "Dostępne komendy sandbox:\n"
                "  help / ?          — ta lista\n"
                "  clear / cls       — wyczyść konsolę\n"
                "  version           — wersja modułu\n"
                "  env               — zmienne środowiska\n"
                "  runners           — pokaż dostępne interpretery\n"
                "  stop              — przerwij aktywny proces\n"
                "  test <plik>       — sprawdź składnię bez uruchamiania\n"
                "  run  <plik>       — uruchom skrypt (.bat .cmd .ps1 .py .vbs .sh .js .lua .rb .pl .php .r .tcl .wsf .hta .reg .go .java .cs .csx .ts .coffee .exs)\n"
                "  <plik>            — uruchom wpisując samą ścieżkę do pliku\n"
                "  cmd.exe /c <plik> — uruchom przez powłokę (też: powershell, pwsh, bash, python, node, ...)\n"
                "  Ctrl+L            — wyczyść konsolę (skrót)\n",
                "info"
            )

        elif lower in ("clear", "cls"):
            self._clear()
            return

        elif lower == "version":
            self._println(f"sandbox v{__version__}  ·  {__author__}  ·  {__company__}", "info")

        elif lower == "env":
            lines = [f"  {k}={v}" for k, v in sorted(os.environ.items())]
            self._println("Zmienne środowiska:\n" + "\n".join(lines[:40]), "dim")
            if len(lines) > 40:
                self._println(f"  … (+{len(lines)-40} więcej)", "dim")

        elif lower == "runners":
            self._show_runners()

        elif lower == "stop":
            self._stop_process()

        elif lower.startswith("test "):
            arg = lower[5:].strip().strip("'\"")
            path = Path(arg)
            if path.exists():
                self._test_script(path)
            else:
                self._println(f"❌  Plik nie istnieje: {arg!r}", "error")

        elif lower.startswith("run "):
            arg = cmd[4:].strip().strip("'\"")
            parts = arg.split()
            path = Path(parts[0]) if parts else Path(arg)
            extra = parts[1:] if len(parts) > 1 else []
            if path.exists():
                self._last_script = path
                self._run_script(path, extra)
            else:
                self._println(f"❌  Plik nie istnieje: {arg!r}", "error")

        else:
            self._println(f"[sandbox] Nieznane polecenie: '{cmd}'", "error")
            self._println("  Wpisz 'help' aby zobaczyć dostępne komendy.", "dim")

        self._set_status(f"Ostatnie: {cmd!r}")

    def _show_runners(self) -> None:
        """Wyświetl dostępnych interpreterów/runnerów."""
        self._println("Dostępne interpretery:", "header")

        py = _find_python()
        self._println(f"  Python  : {py}", "info" if py else "dim")

        ps = shutil.which("powershell") or shutil.which("pwsh")
        self._println(f"  PS      : {ps or '(niedostępny)'}", "info" if ps else "dim")

        if IS_WINDOWS:
            cmd_exe = shutil.which("cmd")
            cs = shutil.which("cscript")
            self._println(f"  CMD     : {cmd_exe or '(niedostępny)'}", "info" if cmd_exe else "dim")
            self._println(f"  cscript : {cs or '(niedostępny)'}", "info" if cs else "dim")
        else:
            self._println("  CMD/VBS : (tylko Windows)", "dim")

        sh = _find_shell()
        self._println(f"  Shell   : {sh or '(niedostępny — bash/sh)'}", "info" if sh else "dim")

        node = _find_node()
        self._println(f"  Node    : {node or '(niedostępny)'}", "info" if node else "dim")

        lua = _find_lua()
        self._println(f"  Lua     : {lua or '(niedostępny)'}", "info" if lua else "dim")

        luac = _find_luac()
        self._println(
            f"  luac    : {luac or '(niedostępny — test składni Lua niedostępny)'}",
            "info" if luac else "dim"
        )

        rb = _find_ruby()
        self._println(f"  Ruby    : {rb or '(niedostępny)'}", "info" if rb else "dim")

        pl = _find_perl()
        self._println(f"  Perl    : {pl or '(niedostępny)'}", "info" if pl else "dim")

        php = _find_php()
        self._println(f"  PHP     : {php or '(niedostępny)'}", "info" if php else "dim")

        rs = _find_rscript()
        self._println(f"  Rscript : {rs or '(niedostępny)'}", "info" if rs else "dim")

        tcl = _find_tclsh()
        self._println(f"  Tcl     : {tcl or '(niedostępny)'}", "info" if tcl else "dim")

        if IS_WINDOWS:
            cs = shutil.which("cscript")
            self._println(f"  WSF     : {cs or '(niedostępny — cscript.exe)'}", "info" if cs else "dim")
            mshta = _find_mshta()
            self._println(f"  HTA     : {mshta or '(niedostępny — mshta.exe)'}", "info" if mshta else "dim")
            regedit = shutil.which("regedit") or (r"C:\Windows\regedit.exe" if os.path.isfile(r"C:\Windows\regedit.exe") else None)
            self._println(f"  REG     : {regedit or '(niedostępny — regedit.exe)'}", "info" if regedit else "dim")
        else:
            self._println("  WSF/HTA/REG : (tylko Windows)", "dim")

        go = _find_go()
        self._println(f"  Go      : {go or '(niedostępny)'}", "info" if go else "dim")

        java, javac = _find_java()
        self._println(f"  Java    : {java or '(niedostępny)'}", "info" if java else "dim")
        self._println(f"  javac   : {javac or '(niedostępny — test składni Java niedostępny)'}", "info" if javac else "dim")

        ds = _find_dotnet_script()
        self._println(f"  C#/CSX  : {ds or '(niedostępny — dotnet-script)'}", "info" if ds else "dim")

        ts_runner, ts_mode = _find_ts_runner()
        ts_label = f"{ts_runner} [{ts_mode}]" if ts_runner else "(niedostępny — ts-node / deno)"
        self._println(f"  TS      : {ts_label}", "info" if ts_runner else "dim")

        coffee = _find_coffee()
        self._println(f"  Coffee  : {coffee or '(niedostępny)'}", "info" if coffee else "dim")

        elixir = _find_elixir()
        self._println(f"  Elixir  : {elixir or '(niedostępny)'}", "info" if elixir else "dim")

    # ── Akcje toolbar ──────────────────────────────────────────────────────
    def _clear(self) -> None:
        self._console.config(state=tk.NORMAL)
        self._console.delete("1.0", tk.END)
        self._console.config(state=tk.DISABLED)
        self._set_status("Wyczyszczono.")

    def _toggle_always_on_top(self) -> None:
        """Toggle always on top window state."""
        self._always_on_top = not self._always_on_top
        self.attributes('-topmost', self._always_on_top)
        status = "włączony" if self._always_on_top else "wyłączony"
        self._set_status(f"Zawsze na wierzchu: {status}")
        if _logger:
            _logger.info(f"SANDBOX: Always on top {status}")

    def _save_log(self) -> None:
        """Zapisz zawartość konsoli do pliku."""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Plik tekstowy", "*.txt"), ("Wszystkie pliki", "*.*")],
            title="Zapisz log sandbox",
        )
        if not path:
            return
        try:
            content = self._console.get("1.0", tk.END)
            Path(path).write_text(content, encoding="utf-8")
            self._set_status(f"Log zapisany: {path}")
        except Exception as exc:
            self._println(f"[błąd zapisu] {exc}", "error")

    def _save_editor_content(self) -> Path | None:
        """Zapisz zawartość edytora do pliku."""
        path = filedialog.asksaveasfilename(
            filetypes=[("Wszystkie pliki", "*.*")],
            title="Zapisz skrypt z sandboxa",
        )
        if not path:
            return None
        try:
            content = self._editor.get("1.0", "end-1c")
            Path(path).write_text(content, encoding="utf-8")
            self._set_status(f"Skrypt zapisany: {path}")
            self._update_lexer_from_path(path)
            return Path(path)
        except Exception as exc:
            self._println(f"[błąd zapisu] {exc}", "error")
            return None

    # ── Historia poleceń ───────────────────────────────────────────────────
    def _hist_prev(self) -> None:
        if not self._history:
            return
        self._hist_idx = max(0, self._hist_idx - 1)
        self._input_var.set(self._history[self._hist_idx])
        self._entry.icursor(tk.END)

    def _hist_next(self) -> None:
        if not self._history:
            return
        self._hist_idx = min(len(self._history), self._hist_idx + 1)
        self._input_var.set(
            self._history[self._hist_idx] if self._hist_idx < len(self._history) else ""
        )
        self._entry.icursor(tk.END)

    def _add_to_pslauncher(self):
        """Zapisz skrypt i dodaj go do głównej aplikacji."""
        app = self._main_app_ref() if self._main_app_ref else None
        if not app:
            return
        # Najpierw zapisz plik
        saved_path = self._save_editor_content()
        if not saved_path:
            return
        # Dodaj do psLauncher
        app._add_script_entry(str(saved_path))
        app._refresh_tree()
        app._schedule_save()
        self._set_status(f"Dodano do psLauncher: {saved_path.name}")

    # ── Syntax Highlighting ────────────────────────────────────────────────
    def _configure_pygments_tags(self):
        is_dark = self._theme.get("DARK", "#0f1117").startswith("#0")
        style_name = "monokai" if is_dark else "default"
        try:
            style = get_style_by_name(style_name)
        except Exception:
            return

        for ttype, sdef in style:
            tag_name = str(ttype)
            kw = {}
            if sdef['color']: kw['foreground'] = f"#{sdef['color']}"
            if sdef['bold']: kw['font'] = (_FONT_CONSOLE[0], _FONT_CONSOLE[1], "bold")
            if sdef['italic']: kw['font'] = (_FONT_CONSOLE[0], _FONT_CONSOLE[1], "italic")
            if sdef['underline']: kw['underline'] = True
            self._editor.tag_configure(tag_name, **kw)

    def _on_editor_modified(self, event=None):
        self._editor.edit_modified(False) # reset flag
        if not _PYGMENTS_AVAILABLE or not self._current_lexer:
            return
        # Proste podświetlanie całego tekstu przy każdej zmianie.
        # Dla dużych plików można to zoptymalizować do podświetlania tylko zmienionej linii.
        code = self._editor.get("1.0", "end-1c")
        self._editor.mark_set("range_start", "1.0")
        for ttype, value in self._current_lexer.get_tokens(code):
            self._editor.mark_set("range_end", f"range_start + {len(value)}c")
            self._editor.tag_add(str(ttype), "range_start", "range_end")
            self._editor.mark_set("range_start", "range_end")

    def _update_lexer_from_path(self, path: str | Path):
        if not _PYGMENTS_AVAILABLE: return
        try:
            self._current_lexer = get_lexer_for_filename(str(path))
            self._on_editor_modified()
        except Exception:
            self._current_lexer = TextLexer()

    # ── Status ─────────────────────────────────────────────────────────────
    def _set_status(self, text: str) -> None:
        self._status_lbl.config(text=text)

    # ── Zamknięcie okna ────────────────────────────────────────────────────
    def _on_close(self) -> None:
        self._stop_process()
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Publiczne API modułu
# ─────────────────────────────────────────────────────────────────────────────

_sandbox_ref: "weakref.ref[SandboxWindow] | None" = None


def open_sandbox(parent: tk.Widget, theme: dict, initial_path: str | None = None) -> SandboxWindow:
    """Otwiera okno sandbox. Jeśli już istnieje i jest widoczne, przywraca fokus."""
    global _sandbox_ref
    if _sandbox_ref is not None:
        win = _sandbox_ref()
        if win is not None and win.winfo_exists():
            win.lift()
            win.focus_set()
            if initial_path: win._load_file(initial_path)
            return win
    win = SandboxWindow(parent, theme, initial_path=initial_path)
    win.transient(parent)
    _sandbox_ref = weakref.ref(win)
    return win
