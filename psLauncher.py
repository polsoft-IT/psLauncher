#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║                         psLauncher v2.0.1                            ║
║              Universal Script Launcher & Manager                     ║
╠══════════════════════════════════════════════════════════════════════╣
║  Author   : Sebastian Januchowski                                    ║
║  Company  : polsoft.ITS™ Group                                       ║
║  Email    : polsoft.its@fastservice.com                              ║
║  GitHub   : https://github.com/seb07uk                               ║
║  License  : 2026© Sebastian Januchowski & polsoft.ITS™               ║
║             All rights reserved.                                     ║
╚══════════════════════════════════════════════════════════════════════╝
"""

__version__    = "2.1.0"
__author__     = "Sebastian Januchowski"
__company__    = "polsoft.ITS™ Group"
__email__      = "polsoft.its@fastservice.com"
__github__     = "https://github.com/seb07uk"
__copyright__  = "2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved."
__app_name__   = "psLauncher"
__description__= "Universal Script Launcher & Manager"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import sys
import shutil
import subprocess
import threading
import json
import re
import csv
import platform
import shlex
import webbrowser
from pathlib import Path
from datetime import datetime
import queue
import time
import traceback

# ANSI color engine for enhanced log output
try:
    from ansi import ANSIEngine, Color, Style, ColorPalette
    _ANSI_AVAILABLE = True
except ImportError:
    _ANSI_AVAILABLE = False

# Structured logging system
try:
    from logger import get_logger, setup_logger, performance_context
    _LOGGER_AVAILABLE = True
except ImportError:
    _LOGGER_AVAILABLE = False

# Sandbox module for isolated script execution
try:
    from sandbox import SandboxWindow
    _SANDBOX_AVAILABLE = True
except ImportError:
    _SANDBOX_AVAILABLE = False

# Debugger module for advanced debugging
try:
    from debugger import DebuggerConfig, ExecutionController, StateInspector, Profiler
    _DEBUGGER_AVAILABLE = True
except ImportError:
    _DEBUGGER_AVAILABLE = False

# Script runner module for advanced script execution
try:
    from script_runner import ScriptRunner, ScriptTemplateManager, ExecutionHistory, EnvironmentManager
    _SCRIPT_RUNNER_AVAILABLE = True
except ImportError:
    _SCRIPT_RUNNER_AVAILABLE = False

# Optional drag & drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

# Optional desktop notification support (plyer fallback)
try:
    from plyer import notification as _plyer_notif
    _PLYER_AVAILABLE = True
except ImportError:
    _PLYER_AVAILABLE = False

# Linux notify-send fallback (no extra deps needed)
_NOTIFY_SEND_AVAILABLE = (
    platform.system() == "Linux" and shutil.which("notify-send") is not None
)

# Optional global hotkey support
try:
    import keyboard as _keyboard_lib
    _KEYBOARD_AVAILABLE = True
except ImportError:
    _KEYBOARD_AVAILABLE = False

# Optional sandbox module support
try:
    import sandbox as _sandbox_mod
    _SANDBOX_AVAILABLE = True
except ImportError:
    _sandbox_mod = None  # type: ignore
    _SANDBOX_AVAILABLE = False

# ──────────────────────────────────────────────
#  TRANSLATIONS
# ──────────────────────────────────────────────
TRANSLATIONS = {
    "pl": {
        "title": "psLauncher – Uniwersalny Uruchamiacz Skryptów",
        "menu_file": "Plik",
        "menu_add_script": "Dodaj skrypt…          Ctrl+O",
        "menu_add_from_template": "Nowy z szablonu…",
        "menu_scan_dir": "Skanuj katalog…         Ctrl+S",
        "menu_exit": "Zakończ                  Ctrl+W",
        "menu_view": "Widok",
        "menu_toggle_panel": "Panel boczny           Ctrl+B",
        "menu_lang": "Język",
        "menu_lang_pl": "Polski",
        "menu_lang_en": "English",
        "menu_tools": "Narzędzia",
        "menu_ps_policy": "Polityka PowerShell…",
        "menu_clear_log": "Wyczyść log            Ctrl+L",
        "menu_export_log": "Eksportuj log do pliku…",
        "menu_debugger": "🐛  Debugger",
        "menu_sandbox": "Sandbox",
        "menu_sandbox_open": "🧪  Otwórz Sandbox",
        "menu_sandbox_runners": "📋  Dostępne interpretery",
        "menu_sandbox_unavail": "⚠  sandbox.py niedostępny",
        "menu_help": "Pomoc",
        "menu_help_about": "ℹ  O programie",
        "menu_help_shortcuts": "⌨  Skróty klawiszowe",
        "menu_help_features": "✨  Funkcje",
        "menu_help_description": "📄  Opis programu",
        "col_name": "Nazwa",
        "col_type": "Typ",
        "col_path": "Ścieżka",
        "col_desc": "Opis",
        "btn_add": "Dodaj",
        "btn_scan": "Skanuj",
        "btn_run": "▶  Uruchom",
        "btn_remove": "Usuń",
        "btn_edit_opts": "⚙  Opcje",
        "btn_hide_panel": "◀",
        "btn_show_panel": "▶",
        "search_placeholder": "Szukaj skryptu…",
        "panel_title": "Informacje o skrypcie",
        "panel_meta_name": "Nazwa:",
        "panel_meta_type": "Typ:",
        "panel_meta_path": "Ścieżka:",
        "panel_meta_size": "Rozmiar:",
        "panel_meta_modified": "Zmodyfikowano:",
        "panel_meta_author": "Autor (meta):",
        "panel_meta_desc": "Opis (meta):",
        "panel_meta_version": "Wersja (meta):",
        "panel_meta_none": "—",
        "log_title": "Log wykonania",
        "dlg_scan_title": "Skanuj katalog w poszukiwaniu skryptów",
        "dlg_scan_found": "Znaleziono skryptów",
        "dlg_add_title": "Dodaj skrypt",
        "dlg_opts_title": "Opcje skryptu",
        "opts_interpreter": "Interpreter:",
        "opts_args": "Argumenty:",
        "opts_workdir": "Katalog roboczy:",
        "opts_run_as_admin": "Uruchom jako administrator",
        "opts_hidden_window": "Ukryte okno",
        "opts_wait": "Czekaj na zakończenie",
        "opts_encoding": "Kodowanie wyjścia:",
        "opts_ps_exec_policy": "Polityka wykonania PS:",
        "opts_ps_bypass": "Bypass (pomiń)",
        "opts_ps_unrestricted": "Unrestricted",
        "opts_ps_remotesigned": "RemoteSigned",
        "opts_ps_allsigned": "AllSigned",
        "opts_ps_restricted": "Restricted",
        "opts_ps_undefined": "Undefined",
        "btn_ok": "OK",
        "btn_cancel": "Anuluj",
        "btn_browse": "Przeglądaj…",
        "msg_no_selection": "Wybierz skrypt z listy.",
        "msg_not_found": "Plik skryptu nie istnieje:\n",
        "msg_running": "Uruchamianie:",
        "msg_done": "Zakończono (kod:",
        "msg_error": "Błąd:",
        "msg_tool_missing": "Nie znaleziono interpretera/programu:",
        "msg_ps_policy_info": (
            "Aby uruchomić skrypty PowerShell, może być wymagana\n"
            "zmiana polityki wykonania.\n\n"
            "Dostępne polecenia:\n"
            "  Set-ExecutionPolicy Bypass -Scope Process\n"
            "  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser\n\n"
            "Aktualna polityka (CurrentUser):"
        ),
        "about_title": "O programie – psLauncher",
        "about_text": (
            f"psLauncher v{__version__}\n"
            "Uniwersalny Uruchamiacz Skryptów\n\n"
            f"Autor: {__author__}\n"
            f"Firma: {__company__}\n"
            f"E-mail: {__email__}\n"
            f"GitHub: {__github__}\n\n"
            f"{__copyright__}"
        ),
        "help_title": "Pomoc – psLauncher",
        "help_text": (
            f"PSLAUNCHER v{__version__} – POMOC\n"
            "========================\n\n"
            "Funkcje:\n"
            "  • Skanowanie katalogów, wyszukiwanie w czasie rzeczywistym\n"
            "  • Indywidualne opcje uruchomienia per skrypt\n"
            "  • Odczyt metadanych (autor, opis, wersja)\n"
            "  • Polityka PowerShell, uruchamianie jako admin\n"
            "  • Panel boczny, log z timestampem\n"
            "  • Grupy skryptów + pasek filtrowania\n"
            "  • Przypinanie (📌) na górze listy\n"
            "  • Zmiana nazwy / duplikowanie wpisu\n"
            "  • Historia uruchomień (Narzędzia → Historia)\n"
            "  • Eksport/Import listy skryptów (JSON)\n"
            "  • Eksport logu do pliku (💾 w panelu)\n"
            "  • Zmiana kolejności skryptów przeciąganiem (bez filtrów/sort)\n"
            "  • Profile uruchamiania: args, env, workdir, timeout, interpreter\n"
            "  • Tryb Dry Run – podgląd komendy bez uruchamiania (PPM)\n"
            "  • Powiadomienia: Windows / macOS / plyer / notify-send (Linux)\n"
            "  • Uruchomienie całej grupy (▶▶)\n"
            "  • Auto-restart przy crash (opcja per-skrypt)\n"
            "  • Timeout uruchamiania (kill po N sekundach)\n"
            "  • Kolejka uruchomień – sekwencyjny runner\n"
            "  • Harmonogram – odpalaj o godzinie lub co N s\n"
            "  • Przyciski ⏹ Zatrzymaj / 🔄 Restart procesu\n"
            "  • Podgląd kodu skryptu (👁 w panelu)\n\n"
            "Skróty klawiszowe:\n"
            "  Uruchamianie\n"
            "  F5 / Enter     – Uruchom wybrany skrypt\n"
            "  F6             – Zatrzymaj proces\n"
            "  F7             – Restart procesu\n"
            "  Ctrl+Enter     – Opcje skryptu\n"
            "\n"
            "  Lista skryptów\n"
            "  Ctrl+O         – Dodaj skrypt\n"
            "  Ctrl+S         – Skanuj katalog\n"
            "  Del            – Usuń z listy\n"
            "  Ctrl+D         – Duplikuj skrypt\n"
            "  Ctrl+P         – Przypnij / odepnij\n"
            "  F2             – Zmień nazwę\n"
            "\n"
            "  Nawigacja\n"
            "  Ctrl+F         – Szukaj\n"
            "  Escape         – Wyczyść wyszukiwanie\n"
            "  Ctrl+B         – Panel boczny\n"
            "  Ctrl+L         – Wyczyść log\n"
            "  F11            – Pełny ekran\n"
            "\n"
            "  Narzędzia\n"
            "  Ctrl+H         – Historia uruchomień\n"
            "  Ctrl+Q         – Kolejka\n"
            "  Ctrl+T         – Harmonogram\n"
            "  Ctrl+K         – Tryb kiosk\n"
            "  Ctrl+E         – Eksportuj log\n"
            "  Ctrl+,         – Ustawienia\n"
            "  Ctrl+F2        – Zmień motyw\n"
            "\n"
            "  Eksport / Import\n"
            "  Ctrl+Shift+E   – Eksportuj listę\n"
            "  Ctrl+Shift+I   – Importuj listę\n"
            "\n"
            "  Pomoc\n"
            "  F1             – Pomoc\n"
            "  Ctrl+F1        – O programie\n"
            "  Ctrl+W         – Zamknij\n"
            "  PPM            – Menu kontekstowe\n"
        ),
        "shortcuts_title": "Skróty klawiszowe – psLauncher",
        "shortcuts_text": (
            f"PSLAUNCHER v{__version__} – SKRÓTY KLAWISZOWE\n"
            "================================\n\n"
            "Uruchamianie\n"
            "  F5 / Enter     – Uruchom wybrany skrypt\n"
            "  F6             – Zatrzymaj proces\n"
            "  F7             – Restart procesu\n"
            "  Ctrl+Enter     – Opcje skryptu\n"
            "\n"
            "Lista skryptów\n"
            "  Ctrl+O         – Dodaj skrypt\n"
            "  Ctrl+S         – Skanuj katalog\n"
            "  Del            – Usuń z listy\n"
            "  Ctrl+D         – Duplikuj skrypt\n"
            "  Ctrl+P         – Przypnij / odepnij\n"
            "  F2             – Zmień nazwę\n"
            "\n"
            "Nawigacja\n"
            "  Ctrl+F         – Szukaj\n"
            "  Escape         – Wyczyść wyszukiwanie\n"
            "  Ctrl+B         – Panel boczny\n"
            "  Ctrl+L         – Wyczyść log\n"
            "  F11            – Pełny ekran\n"
            "\n"
            "Narzędzia\n"
            "  Ctrl+H         – Historia uruchomień\n"
            "  Ctrl+Q         – Kolejka\n"
            "  Ctrl+T         – Harmonogram\n"
            "  Ctrl+K         – Tryb kiosk\n"
            "  Ctrl+E         – Eksportuj log\n"
            "  Ctrl+,         – Ustawienia\n"
            "  Ctrl+F2        – Zmień motyw\n"
            "\n"
            "Eksport / Import\n"
            "  Ctrl+Shift+E   – Eksportuj listę\n"
            "  Ctrl+Shift+I   – Importuj listę\n"
            "\n"
            "Pomoc\n"
            "  F1             – Pomoc\n"
            "  Ctrl+F1        – O programie\n"
            "  Ctrl+W         – Zamknij\n"
            "  PPM            – Menu kontekstowe\n"
        ),
        "features_title": "Funkcje – psLauncher",
        "features_text": (
            f"PSLAUNCHER v{__version__} – FUNKCJE\n"
            "=========================\n\n"
            "  • Skanowanie katalogów, wyszukiwanie w czasie rzeczywistym\n"
            "  • Indywidualne opcje uruchomienia per skrypt\n"
            "  • Odczyt metadanych (autor, opis, wersja)\n"
            "  • Polityka PowerShell, uruchamianie jako admin\n"
            "  • Panel boczny, log z timestampem\n"
            "  • Grupy skryptów + pasek filtrowania\n"
            "  • Przypinanie (📌) na górze listy\n"
            "  • Zmiana nazwy / duplikowanie wpisu\n"
            "  • Historia uruchomień (Narzędzia → Historia)\n"
            "  • Eksport/Import listy skryptów (JSON)\n"
            "  • Eksport logu do pliku (💾 w panelu)\n"
            "  • Zmiana kolejności skryptów przeciąganiem (bez filtrów/sort)\n"
            "  • Profile uruchamiania: args, env, workdir, timeout, interpreter\n"
            "  • Tryb Dry Run – podgląd komendy bez uruchamiania (PPM)\n"
            "  • Powiadomienia: Windows / macOS / plyer / notify-send (Linux)\n"
            "  • Uruchomienie całej grupy (▶▶)\n"
            "  • Auto-restart przy crash (opcja per-skrypt)\n"
            "  • Timeout uruchamiania (kill po N sekundach)\n"
            "  • Kolejka uruchomień – sekwencyjny runner\n"
            "  • Harmonogram – odpalaj o godzinie lub co N s\n"
            "  • Przyciski ⏹ Zatrzymaj / 🔄 Restart procesu\n"
            "  • Podgląd kodu skryptu (👁 w panelu)\n"
        ),
        "desc_title": "Opis programu – psLauncher",
        "desc_text": (
            f"PSLAUNCHER v{__version__} – OPIS\n"
            "=======================\n\n"
            "psLauncher to przenośny, wielofunkcyjny uruchamiacz skryptów\n"
            "obsługujący m.in.: Python (.py), PowerShell (.ps1),\n"
            "Batch (.bat/.cmd), VBScript (.vbs), JavaScript (.js),\n"
            "Ruby (.rb), Perl (.pl), Bash/Shell (.sh), R (.r/.R),\n"
            "PHP (.php) i wiele innych.\n\n"
            "Pozwala zbudować własną bibliotekę skryptów z indywidualnymi\n"
            "opcjami uruchomienia (argumenty, zmienne środowiskowe, katalog\n"
            "roboczy, timeout, wybrany interpreter), grupować je, planować\n"
            "ich uruchamianie w harmonogramie, śledzić historię wykonań\n"
            "oraz monitorować działające procesy z poziomu jednego okna.\n\n"
            f"Autor: {__author__}\n"
            f"Firma: {__company__}"
        ),
        "filetypes_all": "Wszystkie skrypty",
        "filetypes_py": "Python",
        "filetypes_ps1": "PowerShell",
        "filetypes_bat": "Batch",
        "filetypes_vbs": "VBScript",
        "filetypes_all_files": "Wszystkie pliki",
        "scan_extensions": "Rozszerzenia do skanowania:",
        "scan_recursive": "Rekurencyjnie (podkatalogi)",
        "scan_btn": "Skanuj",
        "status_ready": "Gotowy",
        "status_scanning": "Skanowanie…",
        "ctx_run": "▶  Uruchom",
        "ctx_options": "⚙  Opcje",
        "ctx_debugger": "🐛  Debugger",
        "ctx_ps_policy": "🛡  Polityka PowerShell",
        "ctx_open_explorer": "📂  Otwórz w Eksploratorze",
        "ctx_open_terminal": "🖥  Otwórz terminal tutaj",
        "ctx_copy_path": "📋  Kopiuj ścieżkę",
        "ctx_export_launcher": "🚀  Eksportuj launcher (.bat/.sh)",
        "ctx_remove": "🗑  Usuń",
        "ctx_dry_run": "🔬  Dry run (pokaż komendę)",
        "ctx_run_sandbox": "🧪  Uruchom w Sandbox",
        "dry_run_title": "Dry Run – podgląd komendy",
        "dry_run_cmd": "Komenda:",
        "dry_run_cwd": "Katalog roboczy:",
        "dry_run_env_diff": "Dodane zmienne środowiskowe:",
        "dry_run_no_env": "(brak zmian)",
        "dry_run_copy": "📋  Kopiuj komendę",
        "dry_run_copied": "Skopiowano do schowka.",
        "status_count": "Skryptów: {total} / widocznych: {visible}",
        "status_last_run": "Ostatnie uruchomienie: {name} | kod: {code} | czas: {elapsed}s",
        "btn_open_explorer": "📂  Otwórz w Eksploratorze",
        "tooltip_add": "Dodaj skrypt (Ctrl+O)",
        "tooltip_scan": "Skanuj katalog (Ctrl+S)",
        "tooltip_run": "Uruchom zaznaczony skrypt (F5)",
        "tooltip_help": "Pomoc (F1)",
        "tooltip_about": "O programie (Ctrl+F1)",
        "menu_theme": "Motyw",
        "menu_theme_dark": "🌑  Ciemny (Dark)",
        "menu_theme_light": "☀  Jasny (Light)",
        # --- v1.2 additions ---
        "menu_groups": "Grupy",
        "menu_group_new": "Nowa grupa…",
        "menu_group_manage": "Zarządzaj grupami…",
        "menu_export": "Eksportuj listę…",
        "menu_import": "Importuj listę…",
        "menu_run_history": "Historia uruchomień    Ctrl+H",
        "menu_validate_all": "Sprawdź wszystkie skrypty",
        "validate_title": "Wyniki sprawdzania",
        "validate_ok": "OK – wszystkie skrypty poprawne ({total})",
        "validate_missing_file": "Plik nie istnieje",
        "validate_missing_interp": "Brak interpretera/programu",
        "ctx_rename": "✏  Zmień nazwę",
        "ctx_duplicate": "📋  Duplikuj",
        "ctx_move_to_group": "📁  Przenieś do grupy",
        "ctx_pin": "📌  Przypnij na górze",
        "ctx_unpin": "📌  Odepnij",
        "ctx_preview_run": "👁  Podgląd i uruchom",
        "group_all": "Wszystkie",
        "group_ungrouped": "Bez grupy",
        "dlg_rename_title": "Zmień nazwę skryptu",
        "dlg_rename_label": "Nowa nazwa:",
        "dlg_new_group_title": "Nowa grupa",
        "dlg_new_group_label": "Nazwa grupy:",
        "dlg_manage_groups_title": "Zarządzaj grupami",
        "dlg_history_title": "Historia uruchomień",
        "history_col_name": "Skrypt",
        "history_col_time": "Czas",
        "history_col_code": "Kod",
        "history_col_elapsed": "Czas [s]",
        "history_clear": "Wyczyść historię",
        "menu_dashboard": "📊  Dashboard statystyk",
        "dashboard_title": "Dashboard statystyk",
        "dashboard_col_name": "Skrypt",
        "dashboard_col_runs": "Uruchomień",
        "dashboard_col_success": "Sukces %",
        "dashboard_col_avg": "Śr. czas [s]",
        "dashboard_col_last": "Ostatni czas [s]",
        "dashboard_col_lastrc": "Ostatni kod",
        "dashboard_top_slowest": "Najdłużej działające (śr.)",
        "dashboard_summary": "Łącznie skryptów: {total}  •  Uruchomień: {runs}  •  Śr. wsk. sukcesu: {success}%",
        "dashboard_no_data": "Brak danych — uruchom skrypty, aby zobaczyć statystyki.",
        "template_dlg_title": "Nowy skrypt z szablonu",
        "template_dlg_name": "Nazwa skryptu:",
        "template_dlg_type": "Typ:",
        "template_dlg_desc": "Opis:",
        "template_dlg_create": "Utwórz",
        "template_ps_basic": "PowerShell - Podstawowy",
        "template_ps_advanced": "PowerShell - Zaawansowany",
        "template_py_basic": "Python - Podstawowy",
        "template_py_advanced": "Python - Zaawansowany",
        "template_bat_basic": "Batch - Podstawowy",
        "template_bat_advanced": "Batch - Zaawansowany",
        "search_advanced": "🔍  Zaawansowane wyszukiwanie",
        "search_dlg_title": "Zaawansowane wyszukiwanie",
        "search_dlg_name": "Nazwa:",
        "search_dlg_type": "Typ:",
        "search_dlg_group": "Grupa:",
        "search_dlg_tag": "Tag:",
        "search_dlg_status": "Status:",
        "search_dlg_status_all": "Wszystkie",
        "search_dlg_status_success": "Ostatni sukces",
        "search_dlg_status_failed": "Ostatni błąd",
        "search_dlg_status_never": "Nigdy nie uruchomiony",
        "search_dlg_apply": "Szukaj",
        "search_dlg_reset": "Reset",
        "ctx_rerun": "🔄  Uruchom ponownie",
        "backup_auto": "Auto-backup przed zmianami",
        "backup_created": "Utworzono kopię zapasową:",
        "preview_before_run": "Podgląd przed uruchomieniem",
        "preview_dlg_title": "Podgląd: {name}",
        "preview_dlg_run": "Uruchom",
        "preview_dlg_cancel": "Anuluj",
        "favorite_add": "⭐  Dodaj do ulubionych",
        "favorite_remove": "☆  Usuń z ulubionych",
        "favorites_title": "Ulubione",
        "batch_run_title": "Uruchom wybrane skrypty",
        "batch_run_selected": "Uruchom wybrane",
        "batch_run_all": "Uruchom wszystkie",
        "batch_dlg_title": "Uruchomienie zbiorcze",
        "batch_dlg_info": "Wybrane skrypty zostaną uruchomione sekwencyjnie.",
        "batch_dlg_concurrent": "Uruchom równolegle",
        "batch_dlg_stop_on_error": "Zatrzymaj przy błędzie",
        "batch_run_no_selection": "Wybierz skrypty najpierw",
        "env_editor_title": "Edytor zmiennych środowiskowych",
        "env_editor_key": "Klucz",
        "env_editor_value": "Wartość",
        "env_editor_add": "Dodaj",
        "env_editor_remove": "Usuń",
        "env_editor_clear": "Wyczyść",
        "global_env_vars": "Globalne zmienne środowiskowe",
        "global_env_vars_hint": "Zastosowane do wszystkich skryptów",
        "git_menu": "Git",
        "git_init": "Inicjalizuj repozytorium",
        "git_status": "Status",
        "git_add": "Dodaj do indeksu",
        "git_commit": "Zatwierdź zmiany (commit)",
        "git_log": "Historia zmian",
        "git_diff": "Pokaż różnice",
        "git_checkout": "Przywróć wersję",
        "git_not_available": "Git nie jest dostępny w systemie",
        "git_init_success": "Repozytorium zainicjowane",
        "git_add_success": "Dodano do indeksu",
        "git_commit_success": "Zatwierdzono zmiany",
        "git_commit_msg": "Wiadomość commitu:",
        "plugins_menu": "Pluginy",
        "plugins_load": "Załaduj plugin",
        "plugins_list": "Lista pluginów",
        "plugins_folder": "Folder pluginów",
        "plugins_none": "Brak załadowanych pluginów",
        "plugins_loaded": "Załadowane pluginy:",
        "plugins_error": "Błąd ładowania pluginu:",
        "plugins_hook_error": "Błąd hooka pluginu:",
        "search_placeholder": "Szukaj skryptów…",
        "search_no_results": "Brak wyników",
        "search_clear": "Wyczyść",
        "history_menu": "Historia",
        "history_title": "Historia uruchomień",
        "history_date": "Data",
        "history_script": "Skrypt",
        "history_status": "Status",
        "history_duration": "Czas",
        "history_rerun": "Uruchom ponownie",
        "history_clear": "Wyczyść historię",
        "history_empty": "Historia jest pusta",
        "config_export": "Eksportuj konfigurację…",
        "config_import": "Importuj konfigurację…",
        "config_export_success": "Konfiguracja zapisana:",
        "config_import_success": "Konfiguracja wczytana:",
        "config_import_confirm": "Czy na pewno chcesz zaimportować konfigurację? Obecna konfiguracja zostanie zastąpiona.",
        "notifications_menu": "Powiadomienia",
        "notifications_enable": "Włącz powiadomienia systemowe",
        "notifications_title": "psLauncher",
        "notifications_script_started": "Uruchomiono skrypt:",
        "notifications_script_finished": "Zakończono skrypt:",
        "notifications_script_failed": "Błąd skryptu:",
        "ansi_colors_enable": "Włącz kolory w logu",
        "export_saved": "Lista skryptów zapisana:",
        "launcher_export_saved": "Launcher zapisany:",
        "import_loaded": "Wczytano skryptów:",
        "msg_duplicate_done": "Zduplikowano:",
        "msg_pinned": "Przypięto:",
        "msg_unpinned": "Odpięto:",
        "opts_env_vars": "Zmienne środowiskowe (KEY=VAL …):",
        "log_export": "Eksportuj log…",
        "log_exported": "Log zapisany:",
        "log_copied":  "Log skopiowany do schowka.",
        "status_group": "Grupa: {group}",
        "btn_run_all_group": "▶▶  Uruchom grupę",
        # --- v1.3 additions ---
        "opts_auto_restart": "Auto-restart przy błędzie (kod ≠ 0)",
        "opts_max_retries": "Maks. prób restartu:",
        "opts_timeout": "Timeout [s] (0 = brak):",
        "btn_stop": "⏹  Zatrzymaj",
        "btn_restart": "🔄  Restart",
        "msg_process_killed": "Proces zatrzymany:",
        "msg_process_restarted": "Restart:",
        "msg_timeout_killed": "Timeout – zabito po",
        "msg_auto_restart": "Auto-restart (próba",
        "msg_no_running": "Brak działającego procesu.",
        "msg_already_running": "Już działa:",
        "dlg_queue_title": "Kolejka uruchomień",
        "queue_col_script": "Skrypt",
        "queue_col_status": "Status",
        "queue_status_pending": "Oczekuje",
        "queue_status_running": "Uruchomiony",
        "queue_status_done": "Gotowy",
        "queue_status_error": "Błąd",
        "queue_btn_add": "Dodaj zaznaczony",
        "queue_btn_run": "▶  Uruchom kolejkę",
        "queue_btn_clear": "Wyczyść",
        "menu_queue": "Kolejka uruchomień",
        "dlg_sched_title": "Harmonogram",
        "sched_col_script": "Skrypt",
        "sched_col_trigger": "Wyzwalacz",
        "sched_col_next": "Następne",
        "sched_col_status": "Status",
        "sched_type_time": "O godzinie",
        "sched_type_interval": "Co N sekund",
        "sched_label_time": "Godzina (HH:MM):",
        "sched_label_interval": "Interwał [s]:",
        "sched_btn_add": "Dodaj harmonogram",
        "sched_btn_remove": "Usuń",
        "sched_btn_close": "Zamknij",
        "menu_scheduler": "Harmonogram",
        "sched_status_active": "Aktywny",
        "sched_status_inactive": "Nieaktywny",
        "sched_fired": "Harmonogram → uruchomiono:",
        # --- code preview ---
        "btn_preview": "👁  Podgląd kodu",
        "btn_preview_back": "◀  Lista skryptów",
        "preview_title": "Podgląd kodu",
        "preview_no_selection": "Wybierz skrypt z listy, aby zobaczyć podgląd kodu.",
        "preview_not_found": "Plik nie istnieje lub nie można go odczytać.",
        "preview_too_large": "Plik jest zbyt duży do podglądu (> 512 KB).",
        "ctx_preview": "👁  Podgląd kodu",
        # --- v1.5 additions ---
        "opts_tags": "Tagi (oddziel przecinkiem):",
        "opts_note": "Notatka:",
        "opts_profiles": "Profile uruchamiania:",
        "opts_profile_name": "Nazwa profilu:",
        "opts_profile_args": "Argumenty:",
        "opts_profile_env": "Zmienne środowiskowe:",
        "btn_profile_add": "Dodaj profil",
        "btn_profile_edit": "Edytuj",
        "btn_profile_del": "Usuń",
        "btn_profile_activate": "Aktywuj",
        "ctx_profiles": "🎛  Profile uruchamiania",
        "profile_field_name":       "Nazwa:",
        "profile_field_args":       "Argumenty:",
        "profile_field_env":        "Zmienne środ. (KEY=VAL …):",
        "profile_field_workdir":    "Katalog roboczy:",
        "profile_field_timeout":    "Timeout [s] (0=brak):",
        "profile_field_interpreter":"Interpreter:",
        "profile_ok_cancel":        "Anuluj",
        "panel_meta_tags": "Tagi:",
        "panel_meta_note": "Notatka:",
        "filter_tag_all": "Wszystkie tagi",
        "msg_profile_activated": "Aktywny profil:",
        # --- v1.5 monitoring ---
        "opts_watchdog":          "Watchdog – restart jeśli nie żyje (co N s):",
        "opts_notify_on_finish":  "Powiadomienie po zakończeniu",
        "opts_notify_min_sec":    "… tylko gdy trwa dłużej niż [s]:",
        "col_runs":               "Uruch.",
        "col_avg":                "Śr. [s]",
        "col_last_rc":            "Kod",
        "stats_sparkline_title":  "Historia exit-kodów",
        "notify_title":           "psLauncher",
        "notify_done":            "Zakończono",
        "notify_code":            "Kod wyjścia",
        "watchdog_restarting":    "Watchdog → restart:",
        # --- v1.6 management ---
        "menu_export_csv":        "Eksportuj listę jako CSV…",
        "menu_import_csv":        "Importuj listę z CSV…",
        "menu_export_full":       "Eksportuj pełny backup…",
        "menu_import_full":       "Importuj pełny backup…",
        "full_backup_saved":      "Backup zapisany:",
        "full_backup_loaded":     "Backup wczytany.",
        "full_backup_confirm_title": "Importuj pełny backup",
        "full_backup_confirm_msg": (
            "Import zastąpi listę skryptów, grupy, harmonogramy,\n"
            "historię, język i temat aktualnymi danymi z pliku.\n\n"
            "Kontynuować?"
        ),
        "export_fmt_title":       "Format eksportu",
        "export_fmt_label":       "Wybierz format:",
        "csv_saved":              "Lista CSV zapisana:",
        "csv_loaded":             "Wczytano z CSV:",
        "opts_run_after":         "Uruchom po sukcesie skryptu:",
        "opts_run_after_hint":    "(wpisz nazwę skryptu; puste = brak)",
        "dep_chain_fired":        "Zależność → uruchomiono:",
        "dlg_dup_title":          "Duplikuj skrypt",
        "dlg_dup_label":          "Nazwa kopii:",
        # --- v1.7 UI ---
        "menu_kiosk":             "🎛  Tryb kiosk",
        "menu_kiosk_exit":        "✖  Wyjdź z kiosku",
        "kiosk_title":            "psLauncher – Kiosk",
        "kiosk_no_scripts":       "Brak skryptów do wyświetlenia.",
        "kiosk_group_label":      "Grupa:",
        "kiosk_all_groups":       "Wszystkie",
        "kiosk_btn_exit":         "⬅  Powrót",
        "kiosk_running":          "Uruchamianie…",
        "opts_hotkey":            "Globalny skrót (np. ctrl+f1):",
        "opts_hotkey_hint":       "(wymaga: pip install keyboard)",
        "opts_kiosk_visible":     "Widoczny w trybie kiosk",
        "hotkey_registered":      "Skrót zarejestrowany:",
        "hotkey_error":           "Błąd skrótu:",
        "hotkey_lib_missing":     "Brak biblioteki 'keyboard' – skróty globalne wyłączone",
        "msg_hotkey_conflict":    "Skrót zajęty przez inny skrypt:",
        # --- Settings dialog ---
        "menu_settings":              "⚙  Ustawienia",
        "settings_title":             "Ustawienia – psLauncher",
        "settings_tab_general":       "Ogólne",
        "settings_tab_paths":         "Ścieżki",
        "settings_tab_run":           "Uruchamianie",
        "settings_tab_notifications": "Powiadomienia",
        "settings_tab_ui":            "Interfejs",
        "settings_lang":              "Język interfejsu:",
        "settings_theme":             "Motyw:",
        "settings_confirm_delete":    "Pytaj o potwierdzenie przy usuwaniu skryptu",
        "settings_save_on_exit":      "Zapisz konfigurację przy zamknięciu",
        "settings_autostart":         "Uruchamiaj psLauncher razem z systemem (Windows)",
        "settings_work_dir":          "Katalog roboczy (config, backup, cache):",
        "settings_work_dir_hint":     "(wymaga restartu programu; pliki zostaną skopiowane)",
        "settings_work_dir_browse":   "Zmień…",
        "settings_work_dir_migrate":  "Kopiuj istniejące pliki do nowego katalogu",
        "settings_default_timeout":   "Domyślny timeout skryptu [s] (0 = brak):",
        "settings_default_retries":   "Domyślna liczba prób auto-restart:",
        "settings_default_restart":   "Domyślnie włącz auto-restart dla nowych skryptów",
        "settings_default_encoding":  "Domyślne kodowanie wyjścia:",
        "settings_notify_global":     "Włącz powiadomienia systemowe",
        "settings_notify_min_sec":    "Powiadamiaj tylko gdy skrypt trwa dłużej niż [s]:",
        "settings_log_max_lines":     "Maks. linii w logu (0 = bez limitu):",
        "settings_panel_on_start":    "Panel boczny widoczny przy starcie",
        "settings_tree_row_height":   "Wysokość wiersza listy [px]:",
        "settings_btn_apply":         "Zastosuj",
        "settings_btn_ok":            "OK",
        "settings_btn_cancel":        "Anuluj",
        "settings_restart_needed":    "Niektóre zmiany wymagają restartu programu.",
        "settings_migrate_done":      "Pliki skopiowane do:",
        "settings_migrate_err":       "Błąd kopiowania plików:",
        "settings_autostart_err":     "Błąd konfiguracji autostartu:",
        "menu_requirements":          "📦  Requirements",
        "menu_req_install":           "📂  Instaluj z pliku…",
        "req_dlg_title":              "Instalacja bibliotek",
        "req_select_title":           "Wybierz plik requirements",
        "req_installing":             "Instalowanie bibliotek z:",
        "req_done_ok":                "✅  Instalacja zakończona pomyślnie.",
        "req_done_err":               "❌  pip zakończył się kodem:",
        "req_pip_missing":            "❌  pip nie jest dostępny w tym środowisku.",
        "req_line":                   "→",
    },
    "en": {
        "title": "psLauncher – Universal Script Launcher",
        "menu_file": "File",
        "menu_add_script": "Add script…              Ctrl+O",
        "menu_add_from_template": "New from template…",
        "menu_scan_dir": "Scan directory…          Ctrl+S",
        "menu_exit": "Exit                      Ctrl+W",
        "menu_view": "View",
        "menu_toggle_panel": "Side panel               Ctrl+B",
        "menu_lang": "Language",
        "menu_lang_pl": "Polski",
        "menu_lang_en": "English",
        "menu_tools": "Tools",
        "menu_ps_policy": "PowerShell Policy…",
        "menu_clear_log": "Clear log                Ctrl+L",
        "menu_export_log": "Export log to file…",
        "menu_debugger": "🐛  Debugger",
        "menu_sandbox": "Sandbox",
        "menu_sandbox_open": "🧪  Open Sandbox",
        "menu_sandbox_runners": "📋  Available interpreters",
        "menu_sandbox_unavail": "⚠  sandbox.py not available",
        "menu_help": "Help",
        "menu_help_about": "ℹ  About",
        "menu_help_shortcuts": "⌨  Keyboard shortcuts",
        "menu_help_features": "✨  Features",
        "menu_help_description": "📄  Description",
        "col_name": "Name",
        "col_type": "Type",
        "col_path": "Path",
        "col_desc": "Description",
        "btn_add": "Add",
        "btn_scan": "Scan",
        "btn_run": "▶  Run",
        "btn_remove": "Remove",
        "btn_edit_opts": "⚙  Options",
        "btn_hide_panel": "◀",
        "btn_show_panel": "▶",
        "search_placeholder": "Search script…",
        "panel_title": "Script information",
        "panel_meta_name": "Name:",
        "panel_meta_type": "Type:",
        "panel_meta_path": "Path:",
        "panel_meta_size": "Size:",
        "panel_meta_modified": "Modified:",
        "panel_meta_author": "Author (meta):",
        "panel_meta_desc": "Description (meta):",
        "panel_meta_version": "Version (meta):",
        "panel_meta_none": "—",
        "log_title": "Execution log",
        "dlg_scan_title": "Scan directory for scripts",
        "dlg_scan_found": "Scripts found",
        "dlg_add_title": "Add script",
        "dlg_opts_title": "Script options",
        "opts_interpreter": "Interpreter:",
        "opts_args": "Arguments:",
        "opts_workdir": "Working directory:",
        "opts_run_as_admin": "Run as administrator",
        "opts_hidden_window": "Hidden window",
        "opts_wait": "Wait for completion",
        "opts_encoding": "Output encoding:",
        "opts_ps_exec_policy": "PS execution policy:",
        "opts_ps_bypass": "Bypass",
        "opts_ps_unrestricted": "Unrestricted",
        "opts_ps_remotesigned": "RemoteSigned",
        "opts_ps_allsigned": "AllSigned",
        "opts_ps_restricted": "Restricted",
        "opts_ps_undefined": "Undefined",
        "btn_ok": "OK",
        "btn_cancel": "Cancel",
        "btn_browse": "Browse…",
        "msg_no_selection": "Please select a script from the list.",
        "msg_not_found": "Script file not found:\n",
        "msg_running": "Running:",
        "msg_done": "Finished (exit code:",
        "msg_error": "Error:",
        "msg_tool_missing": "Interpreter/program not found:",
        "msg_ps_policy_info": (
            "To run PowerShell scripts, you may need to\n"
            "change the execution policy.\n\n"
            "Available commands:\n"
            "  Set-ExecutionPolicy Bypass -Scope Process\n"
            "  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser\n\n"
            "Current policy (CurrentUser):"
        ),
        "about_title": "About – psLauncher",
        "about_text": (
            f"psLauncher v{__version__}\n"
            "Universal Script Launcher\n\n"
            f"Author: {__author__}\n"
            f"Company: {__company__}\n"
            f"E-mail: {__email__}\n"
            f"GitHub: {__github__}\n\n"
            f"{__copyright__}"
        ),
        "help_title": "Help – psLauncher",
        "help_text": (
            f"PSLAUNCHER v{__version__} – HELP\n"
            "======================\n\n"
            "Description:\n"
            "  psLauncher is a portable, multi-function script launcher\n"
            "  supporting: Python (.py), PowerShell (.ps1), Batch (.bat/.cmd),\n"
            "  VBScript (.vbs), JavaScript (.js), Ruby (.rb), Perl (.pl),\n"
            "  Bash/Shell (.sh), R (.r/.R), PHP (.php) and many more.\n\n"
            "Features:\n"
            "  • Directory scanning for scripts\n"
            "  • Real-time script search\n"
            "  • Individual run options per script\n"
            "  • Script metadata reading (author, description, version)\n"
            "  • PowerShell execution policy configuration\n"
            "  • Side panel with script information\n"
            "  • Execution log with timestamps\n"
            "  • Run as administrator (Windows)\n"
            "  • Output encoding selection\n"
            "  • Script groups + filter bar\n"
            "  • Pin (📌) scripts to top of list\n"
            "  • Rename / duplicate entries\n"
            "  • Run history (Tools → History)\n"
            "  • Export/Import script list (JSON)\n"
            "  • Export log to file (💾 in panel)\n"
            "  • Environment variables per script\n"
            "  • Run entire group (▶▶)\n"
            "  • Auto-restart on crash (per-script option)\n"
            "  • Launch timeout (kill after N seconds)\n"
            "  • Run queue – sequential runner\n"
            "  • Scheduler – run at time or every N seconds\n"
            "  • ⏹ Stop / 🔄 Restart process buttons\n"
            "  • Script code preview (👁 in panel)\n\n"
            "Keyboard shortcuts:\n"
            "  Run\n"
            "  F5 / Enter     – Run selected script\n"
            "  F6             – Stop process\n"
            "  F7             – Restart process\n"
            "  Ctrl+Enter     – Script options\n"
            "\n"
            "  Script list\n"
            "  Ctrl+O         – Add script\n"
            "  Ctrl+S         – Scan directory\n"
            "  Del            – Remove from list\n"
            "  Ctrl+D         – Duplicate script\n"
            "  Ctrl+P         – Pin / unpin\n"
            "  F2             – Rename\n"
            "\n"
            "  Navigation\n"
            "  Ctrl+F         – Search\n"
            "  Escape         – Clear search\n"
            "  Ctrl+B         – Side panel\n"
            "  Ctrl+L         – Clear log\n"
            "  F11            – Fullscreen\n"
            "\n"
            "  Tools\n"
            "  Ctrl+H         – Run history\n"
            "  Ctrl+Q         – Queue\n"
            "  Ctrl+T         – Scheduler\n"
            "  Ctrl+K         – Kiosk mode\n"
            "  Ctrl+E         – Export log\n"
            "  Ctrl+,         – Settings\n"
            "  Ctrl+F2        – Toggle theme\n"
            "\n"
            "  Export / Import\n"
            "  Ctrl+Shift+E   – Export list\n"
            "  Ctrl+Shift+I   – Import list\n"
            "\n"
            "  Help\n"
            "  F1             – Help\n"
            "  Ctrl+F1        – About\n"
            "  Ctrl+W         – Close\n"
            "  RMB            – Context menu\n"
        ),
        "shortcuts_title": "Keyboard shortcuts – psLauncher",
        "shortcuts_text": (
            f"PSLAUNCHER v{__version__} – KEYBOARD SHORTCUTS\n"
            "==================================\n\n"
            "Run\n"
            "  F5 / Enter     – Run selected script\n"
            "  F6             – Stop process\n"
            "  F7             – Restart process\n"
            "  Ctrl+Enter     – Script options\n"
            "\n"
            "Script list\n"
            "  Ctrl+O         – Add script\n"
            "  Ctrl+S         – Scan directory\n"
            "  Del            – Remove from list\n"
            "  Ctrl+D         – Duplicate script\n"
            "  Ctrl+P         – Pin / unpin\n"
            "  F2             – Rename\n"
            "\n"
            "Navigation\n"
            "  Ctrl+F         – Search\n"
            "  Escape         – Clear search\n"
            "  Ctrl+B         – Side panel\n"
            "  Ctrl+L         – Clear log\n"
            "  F11            – Fullscreen\n"
            "\n"
            "Tools\n"
            "  Ctrl+H         – Run history\n"
            "  Ctrl+Q         – Queue\n"
            "  Ctrl+T         – Scheduler\n"
            "  Ctrl+K         – Kiosk mode\n"
            "  Ctrl+E         – Export log\n"
            "  Ctrl+,         – Settings\n"
            "  Ctrl+F2        – Toggle theme\n"
            "\n"
            "Export / Import\n"
            "  Ctrl+Shift+E   – Export list\n"
            "  Ctrl+Shift+I   – Import list\n"
            "\n"
            "Help\n"
            "  F1             – Help\n"
            "  Ctrl+F1        – About\n"
            "  Ctrl+W         – Close\n"
            "  RMB            – Context menu\n"
        ),
        "features_title": "Features – psLauncher",
        "features_text": (
            f"PSLAUNCHER v{__version__} – FEATURES\n"
            "=========================\n\n"
            "  • Directory scanning for scripts\n"
            "  • Real-time script search\n"
            "  • Individual run options per script\n"
            "  • Script metadata reading (author, description, version)\n"
            "  • PowerShell execution policy configuration\n"
            "  • Side panel with script information\n"
            "  • Execution log with timestamps\n"
            "  • Run as administrator (Windows)\n"
            "  • Output encoding selection\n"
            "  • Script groups + filter bar\n"
            "  • Pin (📌) scripts to top of list\n"
            "  • Rename / duplicate entries\n"
            "  • Run history (Tools → History)\n"
            "  • Export/Import script list (JSON)\n"
            "  • Export log to file (💾 in panel)\n"
            "  • Environment variables per script\n"
            "  • Run entire group (▶▶)\n"
            "  • Auto-restart on crash (per-script option)\n"
            "  • Launch timeout (kill after N seconds)\n"
            "  • Run queue – sequential runner\n"
            "  • Scheduler – run at time or every N seconds\n"
            "  • ⏹ Stop / 🔄 Restart process buttons\n"
            "  • Script code preview (👁 in panel)\n"
        ),
        "desc_title": "Description – psLauncher",
        "desc_text": (
            f"PSLAUNCHER v{__version__} – DESCRIPTION\n"
            "============================\n\n"
            "psLauncher is a portable, multi-function script launcher\n"
            "supporting: Python (.py), PowerShell (.ps1), Batch (.bat/.cmd),\n"
            "VBScript (.vbs), JavaScript (.js), Ruby (.rb), Perl (.pl),\n"
            "Bash/Shell (.sh), R (.r/.R), PHP (.php) and many more.\n\n"
            "It lets you build your own script library with per-script run\n"
            "options (arguments, environment variables, working directory,\n"
            "timeout, chosen interpreter), organize scripts into groups,\n"
            "schedule launches, track execution history, and monitor running\n"
            "processes — all from a single window.\n\n"
            f"Author: {__author__}\n"
            f"Company: {__company__}"
        ),
        "filetypes_all": "All scripts",
        "filetypes_py": "Python",
        "filetypes_ps1": "PowerShell",
        "filetypes_bat": "Batch",
        "filetypes_vbs": "VBScript",
        "filetypes_all_files": "All files",
        "scan_extensions": "Extensions to scan:",
        "scan_recursive": "Recursive (subdirectories)",
        "scan_btn": "Scan",
        "status_ready": "Ready",
        "status_scanning": "Scanning…",
        "ctx_run": "▶  Run",
        "ctx_options": "⚙  Options",
        "ctx_debugger": "🐛  Debugger",
        "ctx_ps_policy": "🛡  PowerShell Policy",
        "ctx_open_explorer": "📂  Open in Explorer",
        "ctx_open_terminal": "🖥  Open terminal here",
        "ctx_copy_path": "📋  Copy path",
        "ctx_export_launcher": "🚀  Export launcher (.bat/.sh)",
        "ctx_remove": "🗑  Remove",
        "ctx_dry_run": "🔬  Dry run (show command)",
        "ctx_run_sandbox": "🧪  Run in Sandbox",
        "dry_run_title": "Dry Run – command preview",
        "dry_run_cmd": "Command:",
        "dry_run_cwd": "Working directory:",
        "dry_run_env_diff": "Added environment variables:",
        "dry_run_no_env": "(no changes)",
        "dry_run_copy": "📋  Copy command",
        "dry_run_copied": "Copied to clipboard.",
        "status_count": "Scripts: {total} / visible: {visible}",
        "status_last_run": "Last run: {name} | exit: {code} | time: {elapsed}s",
        "btn_open_explorer": "📂  Open in Explorer",
        "tooltip_add": "Add script (Ctrl+O)",
        "tooltip_scan": "Scan directory (Ctrl+S)",
        "tooltip_run": "Run selected script (F5)",
        "tooltip_help": "Help (F1)",
        "tooltip_about": "About (Ctrl+F1)",
        "menu_theme": "Theme",
        "menu_theme_dark": "🌑  Dark",
        "menu_theme_light": "☀  Light",
        # --- v1.2 additions ---
        "menu_groups": "Groups",
        "menu_group_new": "New group…",
        "menu_group_manage": "Manage groups…",
        "menu_export": "Export list…",
        "menu_import": "Import list…",
        "menu_run_history": "Run history",
        "menu_validate_all": "Validate all scripts",
        "validate_title": "Validation results",
        "validate_ok": "OK – all scripts valid ({total})",
        "validate_missing_file": "File not found",
        "validate_missing_interp": "Interpreter/program not found",
        "ctx_rename": "✏  Rename",
        "ctx_duplicate": "📋  Duplicate",
        "ctx_move_to_group": "📁  Move to group",
        "ctx_pin": "📌  Pin to top",
        "ctx_unpin": "📌  Unpin",
        "ctx_preview_run": "👁  Preview & run",
        "group_all": "All",
        "group_ungrouped": "Ungrouped",
        "dlg_rename_title": "Rename script",
        "dlg_rename_label": "New name:",
        "dlg_new_group_title": "New group",
        "dlg_new_group_label": "Group name:",
        "dlg_manage_groups_title": "Manage groups",
        "dlg_history_title": "Run history",
        "history_col_name": "Script",
        "history_col_time": "Time",
        "history_col_code": "Code",
        "history_col_elapsed": "Elapsed [s]",
        "history_clear": "Clear history",
        "menu_dashboard": "📊  Statistics dashboard",
        "dashboard_title": "Statistics dashboard",
        "dashboard_col_name": "Script",
        "dashboard_col_runs": "Runs",
        "dashboard_col_success": "Success %",
        "dashboard_col_avg": "Avg time [s]",
        "dashboard_col_last": "Last time [s]",
        "dashboard_col_lastrc": "Last code",
        "dashboard_top_slowest": "Slowest scripts (avg)",
        "dashboard_summary": "Total scripts: {total}  •  Total runs: {runs}  •  Avg success rate: {success}%",
        "dashboard_no_data": "No data yet — run some scripts to see statistics.",
        "template_dlg_title": "New script from template",
        "template_dlg_name": "Script name:",
        "template_dlg_type": "Type:",
        "template_dlg_desc": "Description:",
        "template_dlg_create": "Create",
        "template_ps_basic": "PowerShell - Basic",
        "template_ps_advanced": "PowerShell - Advanced",
        "template_py_basic": "Python - Basic",
        "template_py_advanced": "Python - Advanced",
        "template_bat_basic": "Batch - Basic",
        "template_bat_advanced": "Batch - Advanced",
        "search_advanced": "🔍  Advanced search",
        "search_dlg_title": "Advanced search",
        "search_dlg_name": "Name:",
        "search_dlg_type": "Type:",
        "search_dlg_group": "Group:",
        "search_dlg_tag": "Tag:",
        "search_dlg_status": "Status:",
        "search_dlg_status_all": "All",
        "search_dlg_status_success": "Last success",
        "search_dlg_status_failed": "Last failed",
        "search_dlg_status_never": "Never run",
        "search_dlg_apply": "Search",
        "search_dlg_reset": "Reset",
        "ctx_rerun": "🔄  Re-run",
        "backup_auto": "Auto-backup before changes",
        "backup_created": "Backup created:",
        "preview_before_run": "Preview before run",
        "preview_dlg_title": "Preview: {name}",
        "preview_dlg_run": "Run",
        "preview_dlg_cancel": "Cancel",
        "favorite_add": "⭐  Add to favorites",
        "favorite_remove": "☆  Remove from favorites",
        "favorites_title": "Favorites",
        "batch_run_title": "Run selected scripts",
        "batch_run_selected": "Run selected",
        "batch_run_all": "Run all",
        "batch_dlg_title": "Batch run",
        "batch_dlg_info": "Selected scripts will be run sequentially.",
        "batch_dlg_concurrent": "Run concurrently",
        "batch_dlg_stop_on_error": "Stop on error",
        "batch_run_no_selection": "Select scripts first",
        "env_editor_title": "Environment Variable Editor",
        "env_editor_key": "Key",
        "env_editor_value": "Value",
        "env_editor_add": "Add",
        "env_editor_remove": "Remove",
        "env_editor_clear": "Clear",
        "global_env_vars": "Global environment variables",
        "global_env_vars_hint": "Applied to all scripts",
        "git_menu": "Git",
        "git_init": "Initialize repository",
        "git_status": "Status",
        "git_add": "Add to index",
        "git_commit": "Commit changes",
        "git_log": "History",
        "git_diff": "Show diff",
        "git_checkout": "Checkout version",
        "git_not_available": "Git is not available in the system",
        "git_init_success": "Repository initialized",
        "git_add_success": "Added to index",
        "git_commit_success": "Changes committed",
        "git_commit_msg": "Commit message:",
        "plugins_menu": "Plugins",
        "plugins_load": "Load plugin",
        "plugins_list": "Plugin list",
        "plugins_folder": "Plugins folder",
        "plugins_none": "No plugins loaded",
        "plugins_loaded": "Loaded plugins:",
        "plugins_error": "Plugin loading error:",
        "plugins_hook_error": "Plugin hook error:",
        "search_placeholder": "Search scripts…",
        "search_no_results": "No results",
        "search_clear": "Clear",
        "history_menu": "History",
        "history_title": "Run History",
        "history_date": "Date",
        "history_script": "Script",
        "history_status": "Status",
        "history_duration": "Duration",
        "history_rerun": "Rerun",
        "history_clear": "Clear history",
        "history_empty": "History is empty",
        "config_export": "Export configuration…",
        "config_import": "Import configuration…",
        "config_export_success": "Configuration saved:",
        "config_import_success": "Configuration loaded:",
        "config_import_confirm": "Are you sure you want to import configuration? Current configuration will be replaced.",
        "notifications_menu": "Notifications",
        "notifications_enable": "Enable system notifications",
        "notifications_title": "psLauncher",
        "notifications_script_started": "Script started:",
        "notifications_script_finished": "Script finished:",
        "notifications_script_failed": "Script failed:",
        "ansi_colors_enable": "Enable log colors",
        "export_saved": "Script list saved:",
        "launcher_export_saved": "Launcher saved:",
        "import_loaded": "Scripts loaded:",
        "msg_duplicate_done": "Duplicated:",
        "msg_pinned": "Pinned:",
        "msg_unpinned": "Unpinned:",
        "opts_env_vars": "Environment variables (KEY=VAL …):",
        "log_export": "Export log…",
        "log_exported": "Log saved:",
        "log_copied":  "Log copied to clipboard.",
        "status_group": "Group: {group}",
        "btn_run_all_group": "▶▶  Run group",
        # --- v1.3 additions ---
        "opts_auto_restart": "Auto-restart on error (exit ≠ 0)",
        "opts_max_retries": "Max restart attempts:",
        "opts_timeout": "Timeout [s] (0 = none):",
        "btn_stop": "⏹  Stop",
        "btn_restart": "🔄  Restart",
        "msg_process_killed": "Process stopped:",
        "msg_process_restarted": "Restarting:",
        "msg_timeout_killed": "Timeout – killed after",
        "msg_auto_restart": "Auto-restart (attempt",
        "msg_no_running": "No running process.",
        "msg_already_running": "Already running:",
        "dlg_queue_title": "Run queue",
        "queue_col_script": "Script",
        "queue_col_status": "Status",
        "queue_status_pending": "Pending",
        "queue_status_running": "Running",
        "queue_status_done": "Done",
        "queue_status_error": "Error",
        "queue_btn_add": "Add selected",
        "queue_btn_run": "▶  Run queue",
        "queue_btn_clear": "Clear",
        "menu_queue": "Run queue",
        "dlg_sched_title": "Scheduler",
        "sched_col_script": "Script",
        "sched_col_trigger": "Trigger",
        "sched_col_next": "Next run",
        "sched_col_status": "Status",
        "sched_type_time": "At time",
        "sched_type_interval": "Every N sec",
        "sched_label_time": "Time (HH:MM):",
        "sched_label_interval": "Interval [s]:",
        "sched_btn_add": "Add schedule",
        "sched_btn_remove": "Remove",
        "sched_btn_close": "Close",
        "menu_scheduler": "Scheduler",
        "sched_status_active": "Active",
        "sched_status_inactive": "Inactive",
        "sched_fired": "Scheduler → launched:",
        # --- code preview ---
        "btn_preview": "👁  Code preview",
        "btn_preview_back": "◀  Script list",
        "preview_title": "Code preview",
        "preview_no_selection": "Select a script from the list to see its code preview.",
        "preview_not_found": "File not found or cannot be read.",
        "preview_too_large": "File is too large to preview (> 512 KB).",
        "ctx_preview": "👁  Code preview",
        # --- v1.5 additions ---
        "opts_tags": "Tags (comma-separated):",
        "opts_note": "Note:",
        "opts_profiles": "Run profiles:",
        "opts_profile_name": "Profile name:",
        "opts_profile_args": "Arguments:",
        "opts_profile_env": "Environment variables:",
        "btn_profile_add": "Add profile",
        "btn_profile_edit": "Edit",
        "btn_profile_del": "Remove",
        "btn_profile_activate": "Activate",
        "ctx_profiles": "🎛  Run profiles",
        "profile_field_name":       "Name:",
        "profile_field_args":       "Arguments:",
        "profile_field_env":        "Env vars (KEY=VAL …):",
        "profile_field_workdir":    "Working directory:",
        "profile_field_timeout":    "Timeout [s] (0=none):",
        "profile_field_interpreter":"Interpreter:",
        "profile_ok_cancel":        "Cancel",
        "panel_meta_tags": "Tags:",
        "panel_meta_note": "Note:",
        "filter_tag_all": "All tags",
        "msg_profile_activated": "Active profile:",
        # --- v1.5 monitoring ---
        "opts_watchdog":          "Watchdog – restart if dead (every N s):",
        "opts_notify_on_finish":  "Notify on finish",
        "opts_notify_min_sec":    "… only when running longer than [s]:",
        "col_runs":               "Runs",
        "col_avg":                "Avg [s]",
        "col_last_rc":            "RC",
        "stats_sparkline_title":  "Exit code history",
        "notify_title":           "psLauncher",
        "notify_done":            "Finished",
        "notify_code":            "Exit code",
        "watchdog_restarting":    "Watchdog → restarting:",
        # --- v1.6 management ---
        "menu_export_csv":        "Export list as CSV…",
        "menu_import_csv":        "Import list from CSV…",
        "menu_export_full":       "Export full backup…",
        "menu_import_full":       "Import full backup…",
        "full_backup_saved":      "Backup saved:",
        "full_backup_loaded":     "Backup loaded.",
        "full_backup_confirm_title": "Import full backup",
        "full_backup_confirm_msg": (
            "Importing will replace the script list, groups, schedules,\n"
            "history, language and theme with the data from the file.\n\n"
            "Continue?"
        ),
        "export_fmt_title":       "Export format",
        "export_fmt_label":       "Choose format:",
        "csv_saved":              "CSV list saved:",
        "csv_loaded":             "Loaded from CSV:",
        "opts_run_after":         "Run after success of script:",
        "opts_run_after_hint":    "(enter script name; empty = none)",
        "dep_chain_fired":        "Dependency → launched:",
        "dlg_dup_title":          "Duplicate script",
        "dlg_dup_label":          "Copy name:",
        # --- v1.7 UI ---
        "menu_kiosk":             "🎛  Kiosk mode",
        "menu_kiosk_exit":        "✖  Exit kiosk",
        "kiosk_title":            "psLauncher – Kiosk",
        "kiosk_no_scripts":       "No scripts to display.",
        "kiosk_group_label":      "Group:",
        "kiosk_all_groups":       "All",
        "kiosk_btn_exit":         "⬅  Back",
        "kiosk_running":          "Running…",
        "opts_hotkey":            "Global hotkey (e.g. ctrl+f1):",
        "opts_hotkey_hint":       "(requires: pip install keyboard)",
        "opts_kiosk_visible":     "Visible in kiosk mode",
        "hotkey_registered":      "Hotkey registered:",
        "hotkey_error":           "Hotkey error:",
        "hotkey_lib_missing":     "Library 'keyboard' missing – global hotkeys disabled",
        "msg_hotkey_conflict":    "Hotkey already used by:",
        # --- Settings dialog ---
        "menu_settings":              "⚙  Settings",
        "settings_title":             "Settings – psLauncher",
        "settings_tab_general":       "General",
        "settings_tab_paths":         "Paths",
        "settings_tab_run":           "Execution",
        "settings_tab_notifications": "Notifications",
        "settings_tab_ui":            "Interface",
        "settings_lang":              "Interface language:",
        "settings_theme":             "Theme:",
        "settings_confirm_delete":    "Ask for confirmation before removing a script",
        "settings_save_on_exit":      "Save config on exit",
        "settings_autostart":         "Launch psLauncher with Windows startup",
        "settings_work_dir":          "Working directory (config, backup, cache):",
        "settings_work_dir_hint":     "(requires restart; existing files will be copied)",
        "settings_work_dir_browse":   "Change…",
        "settings_work_dir_migrate":  "Copy existing files to new directory",
        "settings_default_timeout":   "Default script timeout [s] (0 = none):",
        "settings_default_retries":   "Default auto-restart retries:",
        "settings_default_restart":   "Enable auto-restart by default for new scripts",
        "settings_default_encoding":  "Default output encoding:",
        "settings_notify_global":     "Enable system notifications",
        "settings_notify_min_sec":    "Notify only when script runs longer than [s]:",
        "settings_log_max_lines":     "Max log lines (0 = unlimited):",
        "settings_panel_on_start":    "Show side panel on startup",
        "settings_tree_row_height":   "List row height [px]:",
        "settings_btn_apply":         "Apply",
        "settings_btn_ok":            "OK",
        "settings_btn_cancel":        "Cancel",
        "settings_restart_needed":    "Some changes require a restart.",
        "settings_migrate_done":      "Files copied to:",
        "settings_migrate_err":       "Error copying files:",
        "settings_autostart_err":     "Autostart configuration error:",
        "menu_requirements":          "📦  Requirements",
        "menu_req_install":           "📂  Install from file…",
        "req_dlg_title":              "Install Libraries",
        "req_select_title":           "Select requirements file",
        "req_installing":             "Installing libraries from:",
        "req_done_ok":                "✅  Installation completed successfully.",
        "req_done_err":               "❌  pip exited with code:",
        "req_pip_missing":            "❌  pip is not available in this environment.",
        "req_line":                   "→",
    }
}

# ──────────────────────────────────────────────
#  THEMES
# ──────────────────────────────────────────────
THEMES = {
    "light": {
        "bg_main":        "#eff1f5",
        "bg_panel":       "#e6e9ef",
        "bg_log":         "#dce0e8",
        "bg_entry":       "#ffffff",
        "bg_btn":         "#ccd0da",
        "bg_sep":         "#acb0be",
        "fg_main":        "#4c4f69",
        "fg_dim":         "#8c8fa1",
        "fg_accent":      "#7287fd",
        "fg_green":       "#40a02b",
        "fg_link":        "#209fb5",
        "sel_bg":         "#bcc0cc",
        "sel_fg":         "#7287fd",
        "tree_even":      "#eff1f5",
        "tree_odd":       "#e6e9ef",
        "tree_heading_bg":"#ccd0da",
        "btn_ok_bg":      "#7287fd",
        "btn_ok_fg":      "#ffffff",
        "btn_run_bg":     "#40a02b",
        "btn_run_fg":     "#ffffff",
        "btn_run_active": "#179299",
        "btn_del_bg":     "#d20f39",
        "btn_del_fg":     "#ffffff",
        "insert_fg":      "#4c4f69",
        "menubar_bg":     "#ccd0da",
        "menubar_fg":     "#4c4f69",
        "menu_abg":       "#bcc0cc",
        "menu_afg":       "#7287fd",
        "tooltip_bg":     "#ccd0da",
        "tooltip_fg":     "#4c4f69",
        "placeholder_fg": "#8c8fa1",
        # log tag colors
        "log_header":     "#1e66f5",
        "log_success":    "#40a02b",
        "log_error":      "#d20f39",
        "log_warning":    "#fe640b",
        "log_stdout":     "#4c4f69",
        "log_meta":       "#8c8fa1",
        "log_restart":    "#8839ef",
        "log_sched":      "#df8e1d",
        "scrollbar_bg":   "#dce0e8",
        "scrollbar_fg":   "#ccd0da",
    },
}

# ──────────────────────────────────────────────
#  SCRIPT TYPE DEFINITIONS
# ──────────────────────────────────────────────
SCRIPT_TYPES = {
    ".py":    {"label": "Python",       "color": "#3572A5", "icon": "python"},
    ".ps1":   {"label": "PowerShell",   "color": "#012456", "icon": "powershell"},
    ".bat":   {"label": "Batch",        "color": "#C1501E", "icon": "batch"},
    ".cmd":   {"label": "Batch",        "color": "#C1501E", "icon": "batch"},
    ".vbs":   {"label": "VBScript",     "color": "#7B42BC", "icon": "vbscript"},
    ".js":    {"label": "JavaScript",   "color": "#F1E05A", "icon": "javascript"},
    ".rb":    {"label": "Ruby",         "color": "#CC342D", "icon": "ruby"},
    ".pl":    {"label": "Perl",         "color": "#0298C3", "icon": "perl"},
    ".sh":    {"label": "Shell/Bash",   "color": "#89E051", "icon": "shell"},
    ".bash":  {"label": "Bash",         "color": "#89E051", "icon": "shell"},
    ".r":     {"label": "R",            "color": "#198CE7", "icon": "r"},
    ".R":     {"label": "R",            "color": "#198CE7", "icon": "r"},
    ".php":   {"label": "PHP",          "color": "#4F5D95", "icon": "php"},
    ".lua":   {"label": "Lua",          "color": "#000080", "icon": "lua"},
    ".tcl":   {"label": "Tcl",          "color": "#E4CC98", "icon": "tcl"},
    ".groovy":{"label": "Groovy",       "color": "#4298B8", "icon": "groovy"},
    ".swift": {"label": "Swift",        "color": "#F05138", "icon": "swift"},
    ".go":    {"label": "Go",           "color": "#00ADD8", "icon": "go"},
    ".ts":    {"label": "TypeScript",   "color": "#2B7489", "icon": "typescript"},
    ".awk":   {"label": "AWK",          "color": "#555555", "icon": "awk"},
    ".sed":   {"label": "SED",          "color": "#555555", "icon": "sed"},
}

# ──────────────────────────────────────────────
#  ICON LOADING
# ──────────────────────────────────────────────
_icon_cache = {}
_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

def get_icon(icon_name: str, size: tuple = (16, 16)) -> tk.PhotoImage:
    """Load and cache icon from file"""
    global _icon_cache
    
    cache_key = f"{icon_name}_{size[0]}x{size[1]}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    icon_path = os.path.join(_icons_dir, f"{icon_name}.png")
    try:
        if os.path.exists(icon_path):
            img = tk.PhotoImage(file=icon_path, width=size[0], height=size[1])
            _icon_cache[cache_key] = img
            return img
    except Exception:
        pass
    
    # Fallback to default icon
    default_path = os.path.join(_icons_dir, "default.png")
    try:
        if os.path.exists(default_path):
            img = tk.PhotoImage(file=default_path, width=size[0], height=size[1])
            _icon_cache[cache_key] = img
            return img
    except Exception:
        pass
    
    # Return empty PhotoImage as last resort
    return tk.PhotoImage(width=size[0], height=size[1])

DEFAULT_INTERPRETERS = {
    ".py":    sys.executable,
    ".ps1":   "powershell.exe" if platform.system() == "Windows" else "pwsh",
    ".bat":   "cmd.exe",
    ".cmd":   "cmd.exe",
    ".vbs":   "cscript.exe",
    ".js":    "node",
    ".rb":    "ruby",
    ".pl":    "perl",
    ".sh":    "bash",
    ".bash":  "bash",
    ".r":     "Rscript",
    ".R":     "Rscript",
    ".php":   "php",
    ".lua":   "lua",
    ".tcl":   "tclsh",
    ".ts":    "ts-node",
    ".go":    "go",
    ".swift": "swift",
    ".groovy":"groovy",
    ".awk":   "awk",
    ".sed":   "sed",
}

PS_EXEC_POLICIES = ["Bypass", "Unrestricted", "RemoteSigned", "AllSigned", "Restricted", "Undefined"]

# ──────────────────────────────────────────────
#  METADATA READER
# ──────────────────────────────────────────────
META_PATTERNS = {
    "author":      [r"#\s*author\s*:\s*(.+)", r"@author\s+(.+)", r"Author\s*:\s*(.+)", r"\$Author\s*=\s*['\"](.+)['\"]"],
    "description": [r"#\s*description\s*:\s*(.+)", r"\.SYNOPSIS\s*[\r\n]+\s*(.+)", r"@description\s+(.+)", r"\$Description\s*=\s*['\"](.+)['\"]"],
    "version":     [r"#\s*version\s*:\s*(.+)", r"@version\s+(.+)", r"\$Version\s*=\s*['\"](.+)['\"]", r"__version__\s*=\s*['\"](.+)['\"]"],
}

def read_script_metadata(path: str) -> dict:
    meta = {"author": "", "description": "", "version": ""}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(8192)
        for key, patterns in META_PATTERNS.items():
            for pat in patterns:
                m = re.search(pat, content, re.IGNORECASE | re.MULTILINE)
                if m:
                    meta[key] = m.group(1).strip()
                    break
    except Exception:
        pass
    return meta

def _center_dialog(dlg: tk.Toplevel) -> None:
    """Wyśrodkuj okno dialogowe na ekranie."""
    dlg.update_idletasks()
    w = dlg.winfo_width()
    h = dlg.winfo_height()
    sw = dlg.winfo_screenwidth()
    sh = dlg.winfo_screenheight()
    dlg.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")


# ──────────────────────────────────────────────
#  EXTENDED DEBUGGER DIALOG
# ──────────────────────────────────────────────
class DebuggerDialog(tk.Toplevel):
    """Extended debugger dialog for multiple script types"""
    
    # Function patterns for different languages
    FUNCTION_PATTERNS = {
        ".ps1": r"(?im)^\s*function\s+([\w.-]+)",
        ".js": r"(?im)^\s*(?:async\s+)?function\s+([\w$]+)|^\s*(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s*)?\(?[^=]*\)?\s*=>",
        ".ts": r"(?im)^\s*(?:export\s+)?(?:async\s+)?function\s+([\w$]+)",
        ".sh": r"(?m)^\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\s*\)",
        ".rb": r"(?m)^\s*def\s+([\w!?=]+)",
        ".pl": r"(?m)^\s*sub\s+([\w_]+)",
        ".php": r"(?im)^\s*function\s+([\w_]+)",
        ".lua": r"(?im)^\s*(?:local\s+)?function\s+([\w.:]+)",
        ".go": r"(?m)^\s*func\s+(?:\([^)]*\)\s*)?([\w_]+)",
        ".java": r"(?m)^\s*(?:public|private|protected|static|final|\s)+[\w<>\[\]]+\s+([\w_]+)\s*\(",
        ".cs": r"(?m)^\s*(?:public|private|protected|internal|static|async|\s)+[\w<>\[\]]+\s+([\w_]+)\s*\(",
        ".csx": r"(?m)^\s*(?:public|private|static|async|\s)+[\w<>\[\]]+\s+([\w_]+)\s*\(",
    }
    
    def __init__(self, parent, script_path: str, script_name: str, lang: str, theme: dict | None = None):
        super().__init__(parent)
        self.script_path = script_path
        self.script_name = script_name
        self.lang = lang
        T = TRANSLATIONS[lang]
        C = theme if theme is not None else THEMES["light"]
        
        self.title(f"🐛 Debugger – {script_name}")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.configure(bg=C["bg_main"])
        self.grab_set()
        
        # Debugger state
        self.breakpoints = set()
        self.debugger_process = None
        self.debugger_output = []
        self.analysis_data = None
        self.current_mode = None  # 'trace', 'profile', 'debug'
        
        # Initialize status_var early to avoid AttributeError
        self.status_var = tk.StringVar(value="Initializing...")
        
        # Build UI
        self._build_ui(C, T)
        
        # Load code only (no automatic analysis - user must click Analyse)
        self.after(100, self._load_source_code)
        
    def _build_ui(self, C: dict, T: dict):
        # Top toolbar
        toolbar = tk.Frame(self, bg=C["bg_panel"], pady=4)
        toolbar.pack(fill="x")
        
        # File info
        self.path_var = tk.StringVar(value=self.script_path)
        path_entry = tk.Entry(toolbar, textvariable=self.path_var, width=60, 
                            bg=C["bg_entry"], fg=C["fg_main"], relief="flat", font=("Consolas", 9))
        path_entry.pack(side="left", padx=(8, 4), ipady=4)
        
        # Control buttons
        btn_cfg = {"bg": C["bg_btn"], "fg": C["fg_main"], "relief": "flat",
                   "font": ("Consolas", 9), "padx": 8, "pady": 4, "cursor": "hand2"}
        
        self.btn_analyze = tk.Button(toolbar, text="🔎 Analyse", command=self._analyse, **btn_cfg)
        self.btn_analyze.pack(side="left", padx=2)
        
        self.btn_trace = tk.Button(toolbar, text="▶ Trace", command=lambda: self._run_script("trace"), **btn_cfg)
        self.btn_trace.pack(side="left", padx=2)
        
        self.btn_profile = tk.Button(toolbar, text="⚡ Profile", command=lambda: self._run_script("profile"), **btn_cfg)
        self.btn_profile.pack(side="left", padx=2)
        
        self.btn_debug = tk.Button(toolbar, text="🐛 Debug", command=lambda: self._run_script("debug"), 
                                  bg=C["btn_run_bg"], fg=C["btn_run_fg"], relief="flat",
                                  font=("Consolas", 9), padx=8, pady=4, cursor="hand2")
        self.btn_debug.pack(side="left", padx=2)
        
        self.btn_stop = tk.Button(toolbar, text="⏹ Stop", command=self._stop_script,
                                 bg=C["btn_del_bg"], fg=C["btn_del_fg"], relief="flat",
                                 font=("Consolas", 9), padx=8, pady=4, cursor="hand2")
        self.btn_stop.pack(side="left", padx=2)
        
        # Additional buttons
        tk.Button(toolbar, text="💾 Save Report", command=self._save_report, **btn_cfg).pack(side="left", padx=2)
        self.btn_edit = tk.Button(toolbar, text="✏️ Edit Code", command=self._toggle_edit_mode, **btn_cfg)
        self.btn_edit.pack(side="left", padx=2)
        tk.Button(toolbar, text="🎨 Highlight", command=self._toggle_syntax_highlighting, **btn_cfg).pack(side="left", padx=2)
        
        # Status bar (status_var already initialized in __init__)
        self.status_var.set("Ready")
        tk.Label(self, textvariable=self.status_var, anchor="w", padx=8,
                 bg=C["bg_panel"], fg=C["fg_accent"], font=("Consolas", 9)).pack(fill="x")
        
        # Main content area with paned window
        paned = tk.PanedWindow(self, bg=C["bg_main"], orient="horizontal")
        paned.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Left panel: Code viewer
        left_frame = tk.Frame(paned, bg=C["bg_main"])
        paned.add(left_frame, minsize=450)
        
        tk.Label(left_frame, text="Source Code", bg=C["bg_panel"], fg=C["fg_accent"],
                font=("Consolas", 9, "bold")).pack(fill="x", pady=(0, 4))
        
        self.code_text = tk.Text(left_frame, bg=C["bg_log"], fg=C["fg_main"],
                                 font=("Consolas", 9), wrap="none", state="disabled")
        code_scroll_v = ttk.Scrollbar(left_frame, orient="vertical", command=self.code_text.yview, style="Vertical.TScrollbar")
        code_scroll_h = ttk.Scrollbar(left_frame, orient="horizontal", command=self.code_text.xview, style="Horizontal.TScrollbar")
        self.code_text.configure(yscrollcommand=code_scroll_v.set, xscrollcommand=code_scroll_h.set)
        
        self.code_text.pack(side="left", fill="both", expand=True)
        code_scroll_v.pack(side="right", fill="y")
        code_scroll_h.pack(side="bottom", fill="x")
        
        # Bind right-click for breakpoint menu
        self.code_text.bind("<Button-3>", self._show_breakpoint_menu)
        
        # Configure syntax highlighting tags
        self._configure_syntax_tags(C)
        
        # Right panel with tabs
        right_frame = tk.Frame(paned, bg=C["bg_main"])
        paned.add(right_frame, minsize=350)
        
        self.tabs = ttk.Notebook(right_frame)
        self.tabs.pack(fill="both", expand=True)
        
        # Analysis tab
        self.analysis_frame = tk.Frame(self.tabs, bg=C["bg_main"])
        self.tabs.add(self.analysis_frame, text="Analysis")
        
        tk.Label(self.analysis_frame, text="Static Analysis", bg=C["bg_panel"], fg=C["fg_accent"],
                font=("Consolas", 9, "bold")).pack(fill="x", pady=(0, 4))
        
        self.analysis_text = tk.Text(self.analysis_frame, bg=C["bg_log"], fg=C["fg_main"],
                                     font=("Consolas", 9), wrap="word", state="disabled")
        analysis_scroll = ttk.Scrollbar(self.analysis_frame, orient="vertical", command=self.analysis_text.yview, style="Vertical.TScrollbar")
        self.analysis_text.configure(yscrollcommand=analysis_scroll.set)
        
        self.analysis_text.pack(side="left", fill="both", expand=True)
        analysis_scroll.pack(side="right", fill="y")
        
        # Output tab
        self.output_frame = tk.Frame(self.tabs, bg=C["bg_main"])
        self.tabs.add(self.output_frame, text="Output")
        
        tk.Label(self.output_frame, text="Execution Output", bg=C["bg_panel"], fg=C["fg_accent"],
                font=("Consolas", 9, "bold")).pack(fill="x", pady=(0, 4))
        
        self.output_text = tk.Text(self.output_frame, bg=C["bg_log"], fg=C["fg_main"],
                                   font=("Consolas", 9), wrap="word", state="disabled")
        output_scroll = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview, style="Vertical.TScrollbar")
        self.output_text.configure(yscrollcommand=output_scroll.set)
        
        self.output_text.pack(side="left", fill="both", expand=True)
        output_scroll.pack(side="right", fill="y")
        
        # Variables tab (for Python debug mode)
        self.vars_frame = tk.Frame(self.tabs, bg=C["bg_main"])
        self.tabs.add(self.vars_frame, text="Variables")
        
        tk.Label(self.vars_frame, text="Variables (Debug Mode)", bg=C["bg_panel"], fg=C["fg_accent"],
                font=("Consolas", 9, "bold")).pack(fill="x", pady=(0, 4))
        
        # Use Treeview for variables instead of Text
        self.vars_tree = ttk.Treeview(self.vars_frame, columns=("value",), show="tree headings")
        self.vars_tree.heading("#0", text="Variable")
        self.vars_tree.heading("value", text="Value")
        self.vars_tree.column("#0", width=150)
        self.vars_tree.column("value", width=200)
        
        vars_scroll = ttk.Scrollbar(self.vars_frame, orient="vertical", command=self.vars_tree.yview, style="Vertical.TScrollbar")
        self.vars_tree.configure(yscrollcommand=vars_scroll.set)
        
        self.vars_tree.pack(side="left", fill="both", expand=True)
        vars_scroll.pack(side="right", fill="y")
        
    def _load_and_analyze(self):
        """Load source code and perform static analysis"""
        self._load_source_code()
        self._analyse()
        
    def _load_source_code(self):
        """Load the script source code with encoding detection (no syntax highlighting by default)"""
        import hashlib
        try:
            # Try multiple encodings
            for encoding in ("utf-8-sig", "utf-16", "cp1250", "latin-1", "utf-8"):
                try:
                    with open(self.script_path, 'r', encoding=encoding) as f:
                        code = f.read()
                    self.code_text.config(state="normal")
                    self.code_text.delete("1.0", "end")
                    self.code_text.insert("1.0", code)
                    self.code_text.config(state="disabled")
                    # Don't apply syntax highlighting automatically - user can enable it
                    self.status_var.set(f"Loaded ({encoding})")
                    return
                except UnicodeDecodeError:
                    continue
            
            # Fallback
            with open(self.script_path, 'rb') as f:
                raw = f.read()
            code = raw.decode("utf-8", errors="replace")
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", code)
            self.code_text.config(state="disabled")
            self.status_var.set("Loaded (UTF-8 with replacement)")
            
        except Exception as e:
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", f"Error loading file: {e}")
            self.code_text.config(state="disabled")
            self.status_var.set(f"Error: {e}")
    
    def _analyse(self):
        """Perform static analysis of the script"""
        import re
        from pathlib import Path
        
        self.status_var.set("Analyzing...")
        self.tabs.select(self.analysis_frame)
        
        try:
            with open(self.script_path, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
            
            ext = Path(self.script_path).suffix.lower()
            lines = code.splitlines()
            
            # Basic info
            analysis = [
                f"FILE: {self.script_path}",
                f"TYPE: {ext.upper()}",
                f"LINES: {len(lines)}",
                f"SIZE: {len(code.encode('utf-8'))} bytes",
                ""
            ]
            
            # Function detection
            functions = []
            pattern = self.FUNCTION_PATTERNS.get(ext)
            if pattern:
                for match in re.finditer(pattern, code):
                    func_name = next((part for part in match.groups() if part), "")
                    if func_name:
                        functions.append(func_name)
            
            if ext == ".py":
                # Python-specific analysis
                try:
                    import ast
                    tree = ast.parse(code, filename=self.script_path)
                    functions = [node.name for node in ast.walk(tree)
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    imports = [alias.name for node in ast.walk(tree)
                              if isinstance(node, ast.Import) for alias in node.names]
                    imports += [node.module or "(relative)" for node in ast.walk(tree)
                                if isinstance(node, ast.ImportFrom)]
                    
                    analysis.append("FUNCTIONS:")
                    for func in sorted(set(functions)):
                        analysis.append(f"  • {func}")
                    if not functions:
                        analysis.append("  (none)")
                    
                    analysis.append("\nIMPORTS:")
                    for imp in sorted(set(imports)):
                        analysis.append(f"  • {imp}")
                    if not imports:
                        analysis.append("  (none)")
                    
                    analysis.append("\nSYNTAX: OK (Python AST parsed)")
                except SyntaxError as e:
                    analysis.append(f"SYNTAX ERROR: {e.msg} (line {e.lineno})")
            else:
                # Generic function detection
                if functions:
                    analysis.append("FUNCTIONS / ROUTINES:")
                    for func in sorted(set(functions)):
                        analysis.append(f"  • {func}")
                else:
                    analysis.append("FUNCTIONS: (none detected)")
                
                # Generic import detection
                imports = re.findall(r"(?im)^\s*(?:import|require|using|include|source|\.\s+)\s+['\"]?([^'\"\s;]+)", code)
                if imports:
                    analysis.append("\nIMPORTS / DEPENDENCIES:")
                    for imp in sorted(set(imports)):
                        analysis.append(f"  • {imp}")
                else:
                    analysis.append("\nIMPORTS: (none detected)")
            
            # TODO/FIXME detection
            todos = [{"line": i+1, "text": line.strip()}
                     for i, line in enumerate(lines)
                     if re.search(r"\b(?:TODO|FIXME|HACK|XXX)\b", line, re.IGNORECASE)]
            
            if todos:
                analysis.append("\nTODO / FIXME:")
                for todo in todos:
                    analysis.append(f"  L{todo['line']}: {todo['text']}")
            else:
                analysis.append("\nTODO / FIXME: (none)")
            
            # Comment lines
            comment_lines = sum(1 for line in lines if line.lstrip().startswith(("#", "//", ";", "::", "REM ")))
            blank_lines = sum(1 for line in lines if not line.strip())
            
            analysis.append(f"\nSTATISTICS: {comment_lines} comments, {blank_lines} blank lines")
            
            self.analysis_text.config(state="normal")
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", "\n".join(analysis))
            self.analysis_text.config(state="disabled")
            
            self.status_var.set("Analysis complete")
            self.analysis_data = {"functions": functions, "imports": imports if ext == ".py" else imports}
            
        except Exception as e:
            self.analysis_text.config(state="normal")
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", f"Analysis error: {e}")
            self.analysis_text.config(state="disabled")
            self.status_var.set(f"Analysis error: {e}")
    
    def _run_script(self, mode: str):
        """Run script in different modes"""
        import subprocess
        import sys
        from pathlib import Path
        
        if self.debugger_process and self.debugger_process.poll() is None:
            self.status_var.set("Process already running")
            return
        
        ext = Path(self.script_path).suffix.lower()
        self.current_mode = mode
        self.tabs.select(self.output_frame)
        
        # Clear output
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        
        if mode == "debug" and ext != ".py":
            self.status_var.set("Debug mode only available for Python scripts")
            self._append_output("Debug mode only available for Python scripts")
            return
        
        if mode == "profile" and ext != ".py":
            self.status_var.set("Profiling only available for Python scripts")
            self._append_output("Profiling only available for Python scripts")
            return
        
        # Build command
        if mode == "profile":
            command = [sys.executable, "-m", "cProfile", "-s", "cumtime", self.script_path]
        elif mode == "debug":
            command = [sys.executable, "-m", "pdb", self.script_path]
        elif mode == "trace":
            if ext == ".py":
                command = [sys.executable, "-m", "trace", "--trace", self.script_path]
            elif ext == ".ps1":
                command = ["powershell", "-NoProfile", "-File", self.script_path]
            elif ext in (".bat", ".cmd"):
                command = ["cmd", "/c", self.script_path]
            elif ext in (".sh", ".bash"):
                command = ["bash", self.script_path]
            else:
                command = None
        else:
            command = None
        
        if not command:
            self.status_var.set(f"No runner available for {ext}")
            self._append_output(f"No runner available for {ext}")
            return
        
        self._append_output(f"$ {' '.join(command)}\n")
        self.status_var.set(f"Running ({mode})...")
        
        try:
            self.debugger_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(Path(self.script_path).parent)
            )
            
            # Start output reader thread
            import threading
            threading.Thread(target=self._read_process_output, daemon=True).start()
            
        except Exception as e:
            self._append_output(f"Error starting process: {e}")
            self.status_var.set(f"Error: {e}")
    
    def _read_process_output(self):
        """Read process output in background thread"""
        if not self.debugger_process:
            return
        
        try:
            for line in self.debugger_process.stdout:
                self._append_output(line)
            
            self.debugger_process.wait()
            self._append_output(f"\n[Process finished with exit code: {self.debugger_process.returncode}]")
            self.debugger_process = None
            self.status_var.set("Process finished")
        except Exception as e:
            self._append_output(f"\n[Error reading output: {e}]")
            self.debugger_process = None
            self.status_var.set(f"Error: {e}")
    
    def _stop_script(self):
        """Stop running process"""
        if self.debugger_process and self.debugger_process.poll() is None:
            self.debugger_process.terminate()
            self._append_output("\n[Process stopped]")
            self.status_var.set("Process stopped")
        else:
            self.status_var.set("No process running")
    
    def _append_output(self, text: str):
        """Append text to output window"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.config(state="disabled")
    
    def _show_breakpoint_menu(self, event):
        """Show context menu for breakpoints"""
        from pathlib import Path
        if Path(self.script_path).suffix.lower() != ".py":
            return  # Breakpoints only for Python
        
        line_str = self.code_text.index(f"@{event.x},{event.y}").split('.')[0]
        try:
            line = int(line_str)
        except ValueError:
            return
        
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Toggle Breakpoint", command=lambda l=line: self._toggle_breakpoint(l))
        if line in self.breakpoints:
            menu.add_command(label="Clear Breakpoint", command=lambda l=line: self._toggle_breakpoint(l))
        menu.tk_popup(event.x_root, event.y_root)
    
    def _toggle_breakpoint(self, line: int):
        """Toggle breakpoint on a line"""
        tag = f"bp_{line}"
        if line in self.breakpoints:
            self.breakpoints.remove(line)
            self.code_text.tag_delete(tag)
            self.status_var.set(f"Breakpoint cleared at line {line}")
        else:
            self.breakpoints.add(line)
            C = THEMES.get(self.master.theme_name if hasattr(self.master, 'theme_name') else "light", THEMES["light"])
            self.code_text.tag_configure(tag, background=C.get("log_error", "#f38ba8"))
            self.code_text.tag_add(tag, f"{line}.0", f"{line}.end")
            self.status_var.set(f"Breakpoint set at line {line}")
    
    def _save_report(self):
        """Save analysis report to file"""
        from tkinter import filedialog
        import json
        from datetime import datetime
        from pathlib import Path
        
        if not self.analysis_data:
            self._analyse()
        
        report = {
            "file": self.script_path,
            "name": self.script_name,
            "generated_at": datetime.now().isoformat(),
            "analysis": self.analysis_data,
            "breakpoints": sorted(self.breakpoints),
        }
        
        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".json",
            filetypes=[("JSON Report", "*.json"), ("Text Report", "*.txt"), ("All Files", "*.*")],
            initialfile=f"{Path(self.script_path).stem}_report.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                self.status_var.set(f"Report saved to {file_path}")
            except Exception as e:
                self.status_var.set(f"Error saving report: {e}")
    
    def _toggle_edit_mode(self):
        """Toggle code editing mode"""
        current_state = self.code_text.cget("state")
        if current_state == "disabled":
            self.code_text.config(state="normal")
            self.status_var.set("Edit mode enabled - Click 'Save' to apply changes")
            # Change button to Save
            self.btn_edit.config(text="💾 Save", command=self._save_code_changes)
        else:
            self.code_text.config(state="disabled")
            self.status_var.set("Edit mode disabled")
            self.btn_edit.config(text="✏️ Edit Code", command=self._toggle_edit_mode)
    
    def _save_code_changes(self):
        """Save code changes to file"""
        try:
            code = self.code_text.get("1.0", "end-1c")
            with open(self.script_path, 'w', encoding='utf-8') as f:
                f.write(code)
            self.code_text.config(state="disabled")
            self.status_var.set("Code saved successfully")
            self.btn_edit.config(text="✏️ Edit Code", command=self._toggle_edit_mode)
            # Re-analyze after save
            self._analyse()
        except Exception as e:
            self.status_var.set(f"Error saving code: {e}")
    
    def _configure_syntax_tags(self, C: dict):
        """Configure basic syntax highlighting tags"""
        # Python syntax highlighting
        self.code_text.tag_configure("keyword", foreground=C.get("fg_accent", "#60a5fa"), font=("Consolas", 9, "bold"))
        self.code_text.tag_configure("string", foreground=C.get("fg_success", "#a6e3a1"))
        self.code_text.tag_configure("comment", foreground=C.get("fg_dim", "#6c7086"), font=("Consolas", 9, "italic"))
        self.code_text.tag_configure("number", foreground=C.get("fg_warning", "#f9e2af"))
        self.code_text.tag_configure("function", foreground=C.get("fg_main", "#e5e7eb"))
        self.code_text.tag_configure("builtin", foreground=C.get("fg_accent", "#89b4fa"))
    
    def _apply_syntax_highlighting(self, code: str):
        """Apply basic syntax highlighting to code"""
        import re
        from pathlib import Path
        
        ext = Path(self.script_path).suffix.lower()
        
        if ext == ".py":
            self._apply_python_highlighting(code)
        elif ext == ".ps1":
            self._apply_powershell_highlighting(code)
        else:
            # No highlighting for other languages
            pass
    
    def _apply_python_highlighting(self, code: str):
        """Apply Python syntax highlighting"""
        import re
        
        self.code_text.config(state="normal")
        self.code_text.delete("1.0", "end")
        
        # Keywords
        keywords = r'\b(def|class|if|else|elif|for|while|try|except|finally|with|import|from|return|yield|raise|pass|break|continue|and|or|not|in|is|lambda|async|await|True|False|None)\b'
        
        # Strings
        strings = r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|"[^"]*"|\'[^\']*\')'
        
        # Comments
        comments = r'(#[^\n]*)'
        
        # Numbers
        numbers = r'\b(\d+\.?\d*)\b'
        
        # Functions
        functions = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        # Apply highlighting
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Remove existing tags
            self.code_text.insert(f"{i}.0", line + '\n')
            
            # Highlight keywords
            for match in re.finditer(keywords, line):
                self.code_text.tag_add("keyword", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            # Highlight strings
            for match in re.finditer(strings, line):
                self.code_text.tag_add("string", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            # Highlight comments
            for match in re.finditer(comments, line):
                self.code_text.tag_add("comment", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            # Highlight numbers
            for match in re.finditer(numbers, line):
                self.code_text.tag_add("number", f"{i}.{match.start()}", f"{i}.{match.end()}")
        
        self.code_text.config(state="disabled")
    
    def _apply_powershell_highlighting(self, code: str):
        """Apply PowerShell syntax highlighting"""
        import re
        
        self.code_text.config(state="normal")
        self.code_text.delete("1.0", "end")
        
        # Keywords
        keywords = r'\b(if|else|elseif|for|foreach|while|do|switch|try|catch|finally|function|filter|param|begin|process|end|return|throw|break|continue|exit|Write-Host|Write-Output|Get-Command|Get-Process|Get-Service)\b'
        
        # Strings
        strings = r'(\"[^"]*\"|\'[^\']*\')'
        
        # Comments
        comments = r'(#[^\n]*)'
        
        # Variables
        variables = r'(\$[a-zA-Z_][a-zA-Z0-9_]*)'
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            self.code_text.insert(f"{i}.0", line + '\n')
            
            for match in re.finditer(keywords, line):
                self.code_text.tag_add("keyword", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            for match in re.finditer(strings, line):
                self.code_text.tag_add("string", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            for match in re.finditer(comments, line):
                self.code_text.tag_add("comment", f"{i}.{match.start()}", f"{i}.{match.end()}")
            
            for match in re.finditer(variables, line):
                self.code_text.tag_add("builtin", f"{i}.{match.start()}", f"{i}.{match.end()}")
        
        self.code_text.config(state="disabled")
    
    def _toggle_syntax_highlighting(self):
        """Toggle syntax highlighting on/off"""
        code = self.code_text.get("1.0", "end-1c")
        if not code:
            return
        
        # Check if highlighting is already applied (check for any tags)
        tags = self.code_text.tag_names("1.0")
        has_highlighting = any(tag in ("keyword", "string", "comment", "number", "function", "builtin") for tag in tags)
        
        if has_highlighting:
            # Remove highlighting - reload plain code
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", code)
            self.code_text.config(state="disabled")
            self.status_var.set("Syntax highlighting disabled")
        else:
            # Apply highlighting
            self._apply_syntax_highlighting(code)
            self.status_var.set("Syntax highlighting enabled")


# ──────────────────────────────────────────────
#  SCRIPT OPTIONS DIALOG
# ──────────────────────────────────────────────
class ScriptOptionsDialog(tk.Toplevel):
    def __init__(self, parent, script_entry: dict, lang: str, theme: dict | None = None):
        super().__init__(parent)
        self.result = None
        self.lang = lang
        T = TRANSLATIONS[lang]
        C = theme if theme is not None else THEMES["light"]
        ext = Path(script_entry.get("path", "")).suffix.lower()
        self.is_ps1 = (ext == ".ps1")

        self.title(T["dlg_opts_title"] + " – " + script_entry.get("name", ""))
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=C["bg_main"])

        pad = {"padx": 8, "pady": 4}
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"], "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}

        row = 0
        # Interpreter
        tk.Label(self, text=T["opts_interpreter"], **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_interp = tk.StringVar(value=script_entry.get("interpreter",
                                        DEFAULT_INTERPRETERS.get(ext, "")))
        entry_interp = tk.Entry(self, textvariable=self.var_interp, width=38, **entry_cfg)
        entry_interp.grid(row=row, column=1, **pad)

        row += 1
        # Arguments
        tk.Label(self, text=T["opts_args"], **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_args = tk.StringVar(value=script_entry.get("args", ""))
        tk.Entry(self, textvariable=self.var_args, width=38, **entry_cfg).grid(row=row, column=1, **pad)

        row += 1
        # Working directory
        tk.Label(self, text=T["opts_workdir"], **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_workdir = tk.StringVar(value=script_entry.get("workdir", ""))
        frm_wd = tk.Frame(self, bg=C["bg_main"])
        frm_wd.grid(row=row, column=1, sticky="w", **pad)
        tk.Entry(frm_wd, textvariable=self.var_workdir, width=30, **entry_cfg).pack(side="left")
        tk.Button(frm_wd, text=T["btn_browse"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 8),
                  command=self._browse_workdir).pack(side="left", padx=(4,0))

        row += 1
        # Encoding
        tk.Label(self, text=T["opts_encoding"], **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_enc = tk.StringVar(value=script_entry.get("encoding", "utf-8"))
        enc_cb = ttk.Combobox(self, textvariable=self.var_enc, width=15,
                              values=["utf-8", "cp1250", "cp852", "latin-1", "ascii", "utf-16"])
        enc_cb.grid(row=row, column=1, sticky="w", **pad)

        row += 1
        # Checkboxes
        self.var_admin   = tk.BooleanVar(value=script_entry.get("run_as_admin", False))
        self.var_hidden  = tk.BooleanVar(value=script_entry.get("hidden_window", False))
        self.var_wait    = tk.BooleanVar(value=script_entry.get("wait", True))

        ck_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "activebackground": C["bg_main"],
                  "activeforeground": C["fg_accent"], "selectcolor": C["bg_entry"], "font": ("Consolas", 9)}
        tk.Checkbutton(self, text=T["opts_run_as_admin"],    variable=self.var_admin,  **ck_cfg).grid(row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1
        tk.Checkbutton(self, text=T["opts_hidden_window"],   variable=self.var_hidden, **ck_cfg).grid(row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1
        tk.Checkbutton(self, text=T["opts_wait"],            variable=self.var_wait,   **ck_cfg).grid(row=row, column=0, columnspan=2, sticky="w", **pad)

        # PowerShell specific
        if self.is_ps1:
            row += 1
            sep = tk.Frame(self, bg=C["bg_sep"], height=1)
            sep.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)

            row += 1
            tk.Label(self, text=T["opts_ps_exec_policy"], **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
            self.var_ps_policy = tk.StringVar(value=script_entry.get("ps_exec_policy", "Bypass"))
            ps_cb = ttk.Combobox(self, textvariable=self.var_ps_policy, width=15,
                                 values=PS_EXEC_POLICIES, state="readonly")
            ps_cb.grid(row=row, column=1, sticky="w", **pad)

        # Environment variables
        row += 1
        sep2 = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep2.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        tk.Label(self, text=T.get("opts_env_vars", "Env vars (KEY=VAL …):"), **lbl_cfg).grid(
            row=row, column=0, sticky="nw", **pad)
        self.var_env = tk.StringVar(value=script_entry.get("env_vars", ""))
        frm_env = tk.Frame(self, bg=C["bg_main"])
        frm_env.grid(row=row, column=1, sticky="w", **pad)
        tk.Entry(frm_env, textvariable=self.var_env, width=30, **entry_cfg).pack(side="left")
        tk.Button(frm_env, text="…", bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 8), width=3,
                  command=self._open_env_editor).pack(side="left", padx=(4,0))

        row += 1
        sep3 = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep3.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        self.var_auto_restart = tk.BooleanVar(value=script_entry.get("auto_restart", False))
        tk.Checkbutton(self, text=T.get("opts_auto_restart", "Auto-restart on error"),
                       variable=self.var_auto_restart, **ck_cfg).grid(
            row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1
        tk.Label(self, text=T.get("opts_max_retries", "Max retries:"), **lbl_cfg).grid(
            row=row, column=0, sticky="w", **pad)
        self.var_max_retries = tk.StringVar(value=str(script_entry.get("max_retries", 3)))
        tk.Spinbox(self, textvariable=self.var_max_retries, from_=1, to=99, width=6,
                   bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                   buttonbackground=C["bg_btn"], relief="flat", font=("Consolas", 9)).grid(
            row=row, column=1, sticky="w", **pad)
        row += 1
        tk.Label(self, text=T.get("opts_timeout", "Timeout [s]:"), **lbl_cfg).grid(
            row=row, column=0, sticky="w", **pad)
        self.var_timeout = tk.StringVar(value=str(script_entry.get("timeout", 0)))
        tk.Spinbox(self, textvariable=self.var_timeout, from_=0, to=86400, width=8,
                   bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                   buttonbackground=C["bg_btn"], relief="flat", font=("Consolas", 9)).grid(
            row=row, column=1, sticky="w", **pad)

        # ── Watchdog ────────────────────────────
        row += 1
        sep_wd = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep_wd.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        tk.Label(self, text=T.get("opts_watchdog", "Watchdog (ping every N s, 0=off):"),
                 **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_watchdog = tk.StringVar(value=str(script_entry.get("watchdog_interval", 0)))
        tk.Spinbox(self, textvariable=self.var_watchdog, from_=0, to=3600, width=8,
                   bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                   buttonbackground=C["bg_btn"], relief="flat", font=("Consolas", 9)).grid(
            row=row, column=1, sticky="w", **pad)

        # ── Notify on finish ────────────────────
        row += 1
        self.var_notify = tk.BooleanVar(value=script_entry.get("notify_on_finish", False))
        tk.Checkbutton(self, text=T.get("opts_notify_on_finish", "Notify on finish"),
                       variable=self.var_notify, **ck_cfg).grid(
            row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1
        tk.Label(self, text=T.get("opts_notify_min_sec", "… only when longer than [s]:"),
                 **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_notify_min = tk.StringVar(value=str(script_entry.get("notify_min_sec", 0)))
        tk.Spinbox(self, textvariable=self.var_notify_min, from_=0, to=86400, width=8,
                   bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                   buttonbackground=C["bg_btn"], relief="flat", font=("Consolas", 9)).grid(
            row=row, column=1, sticky="w", **pad)

        # ── Dependencies: run_after (multiple, comma-separated) ──────────────
        row += 1
        sep_dep = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep_dep.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        tk.Label(self, text=T.get("opts_run_after", "Run after success of:"),
                 **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_run_after = tk.StringVar(value=script_entry.get("run_after", ""))
        # Combobox populated with existing script names
        all_names = sorted({s.get("name", "") for s in getattr(parent, "scripts", [])
                            if s.get("name", "") and s is not script_entry})
        cb_run_after = ttk.Combobox(self, textvariable=self.var_run_after,
                                     values=[""] + all_names, width=30, font=("Consolas", 9))
        cb_run_after.grid(row=row, column=1, sticky="w", **pad)
        row += 1
        tk.Label(self, text=T.get("opts_run_after_hint", "(empty = no dependency, comma-separated for multiple)"),
                 bg=C["bg_main"], fg=C["fg_dim"], font=("Consolas", 8)).grid(
            row=row, column=1, sticky="w", padx=8)

        # ── Hotkey ──────────────────────────────
        row += 1
        sep_hk = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep_hk.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        tk.Label(self, text=T.get("opts_hotkey", "Global hotkey:"),
                 **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        self.var_hotkey = tk.StringVar(value=script_entry.get("hotkey", ""))
        frm_hk = tk.Frame(self, bg=C["bg_main"])
        frm_hk.grid(row=row, column=1, sticky="w", **pad)
        ent_hk = tk.Entry(frm_hk, textvariable=self.var_hotkey, width=22, **entry_cfg)
        ent_hk.pack(side="left")
        # Record button — captures next keypress
        def _record_hk():
            ent_hk.config(bg="#4a3f55")
            ent_hk.focus_set()
            def _on_key(ev):
                parts = []
                if ev.state & 0x4:   parts.append("ctrl")
                if ev.state & 0x8:   parts.append("alt")
                if ev.state & 0x1:   parts.append("shift")
                key = ev.keysym.lower()
                if key not in ("control_l","control_r","alt_l","alt_r",
                               "shift_l","shift_r","super_l","super_r"):
                    parts.append(key)
                    combo = "+".join(parts)
                    self.var_hotkey.set(combo)
                    ent_hk.config(bg=C["bg_entry"])
                    ent_hk.unbind("<KeyPress>")
            ent_hk.bind("<KeyPress>", _on_key)
        tk.Button(frm_hk, text="⏺", bg=C["bg_btn"], fg=C["fg_accent"],
                  relief="flat", font=("Consolas", 9), padx=4, pady=1,
                  cursor="hand2", command=_record_hk).pack(side="left", padx=(4, 0))
        row += 1
        tk.Label(self, text=T.get("opts_hotkey_hint", "(requires: pip install keyboard)"),
                 bg=C["bg_main"], fg=C["fg_dim"], font=("Consolas", 8)).grid(
            row=row, column=1, sticky="w", padx=8)

        # ── Kiosk visibility ─────────────────────
        row += 1
        self.var_kiosk_visible = tk.BooleanVar(value=script_entry.get("kiosk_visible", True))
        tk.Checkbutton(self, text=T.get("opts_kiosk_visible", "Visible in kiosk mode"),
                       variable=self.var_kiosk_visible, **ck_cfg).grid(
            row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1
        sep4 = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep4.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        tk.Label(self, text=T.get("opts_tags", "Tags:"), **lbl_cfg).grid(
            row=row, column=0, sticky="w", **pad)
        self.var_tags = tk.StringVar(value=script_entry.get("tags", ""))
        tk.Entry(self, textvariable=self.var_tags, width=38, **entry_cfg).grid(
            row=row, column=1, sticky="w", **pad)

        # ── Note ────────────────────────────────
        row += 1
        tk.Label(self, text=T.get("opts_note", "Note:"), **lbl_cfg).grid(
            row=row, column=0, sticky="nw", **pad)
        self.txt_note = tk.Text(self, width=30, height=3,
                                bg=C["bg_entry"], fg=C["fg_main"],
                                insertbackground=C["insert_fg"],
                                relief="flat", font=("Consolas", 9), wrap="word")
        self.txt_note.insert("1.0", script_entry.get("note", ""))
        self.txt_note.grid(row=row, column=1, sticky="w", **pad)

        # ── Run profiles ────────────────────────
        row += 1
        sep5 = tk.Frame(self, bg=C["bg_sep"], height=1)
        sep5.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6, padx=8)
        row += 1
        tk.Label(self, text=T.get("opts_profiles", "Run profiles:"), **lbl_cfg).grid(
            row=row, column=0, sticky="nw", **pad)

        frm_prof = tk.Frame(self, bg=C["bg_main"])
        frm_prof.grid(row=row, column=1, sticky="w", **pad)

        self._profiles = list(script_entry.get("profiles", []))
        self._active_profile = script_entry.get("active_profile", "")

        self.lb_profiles = tk.Listbox(frm_prof, width=26, height=4,
                                       bg=C["bg_entry"], fg=C["fg_main"],
                                       selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
                                       relief="flat", font=("Consolas", 9),
                                       activestyle="none")
        self.lb_profiles.pack(side="left")
        self._reload_profile_list()

        frm_prof_btns = tk.Frame(frm_prof, bg=C["bg_main"])
        frm_prof_btns.pack(side="left", fill="y", padx=(4, 0))
        btn_mini = {"relief": "flat", "font": ("Consolas", 8), "padx": 6, "pady": 2,
                    "cursor": "hand2", "bg": C["bg_btn"], "fg": C["fg_main"]}
        tk.Button(frm_prof_btns, text=T.get("btn_profile_add", "Add"),
                  command=self._add_profile, **btn_mini).pack(fill="x", pady=1)
        tk.Button(frm_prof_btns, text=T.get("btn_profile_edit", "Edit"),
                  command=self._edit_profile, **btn_mini).pack(fill="x", pady=1)
        tk.Button(frm_prof_btns, text=T.get("btn_profile_del", "Remove"),
                  command=self._del_profile, **btn_mini).pack(fill="x", pady=1)
        tk.Button(frm_prof_btns, text=T.get("btn_profile_activate", "Activate"),
                  command=self._activate_profile, **btn_mini).pack(fill="x", pady=1)

        # Buttons (OK / Cancel)
        row += 1
        btn_frm = tk.Frame(self, bg=C["bg_main"])
        btn_frm.grid(row=row, column=0, columnspan=2, pady=10)
        btn_s = {"bg": C["btn_ok_bg"], "fg": C["btn_ok_fg"], "relief": "flat",
                 "font": ("Consolas", 9, "bold"), "padx": 14, "pady": 4, "cursor": "hand2"}
        tk.Button(btn_frm, text=T["btn_ok"],     **btn_s, command=self._ok).pack(side="left", padx=4)
        tk.Button(btn_frm, text=T["btn_cancel"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9), padx=14, pady=4,
                  cursor="hand2", command=self.destroy).pack(side="left", padx=4)

        self._entry_data = script_entry.copy()
        _center_dialog(self)

    def center(self):
        _center_dialog(self)

    def _reload_profile_list(self):
        self.lb_profiles.delete(0, "end")
        for p in self._profiles:
            marker = "✓ " if p["name"] == self._active_profile else "  "
            self.lb_profiles.insert("end", marker + p["name"])

    def _add_profile(self):
        dlg = _ProfileEditDialog(self, {"name": "", "args": "", "env_vars": "",
                                         "workdir": "", "timeout": 0, "interpreter": ""})
        self.wait_window(dlg)
        if dlg.result:
            self._profiles.append(dlg.result)
            self._reload_profile_list()

    def _edit_profile(self):
        sel = self.lb_profiles.curselection()
        if not sel:
            return
        idx = sel[0]
        dlg = _ProfileEditDialog(self, self._profiles[idx])
        self.wait_window(dlg)
        if dlg.result:
            old_name = self._profiles[idx]["name"]
            self._profiles[idx] = dlg.result
            if self._active_profile == old_name:
                self._active_profile = dlg.result["name"]
            self._reload_profile_list()

    def _del_profile(self):
        sel = self.lb_profiles.curselection()
        if not sel:
            return
        idx = sel[0]
        removed = self._profiles.pop(idx)
        if removed["name"] == self._active_profile:
            self._active_profile = ""
        self._reload_profile_list()

    def _activate_profile(self):
        sel = self.lb_profiles.curselection()
        if not sel:
            return
        p = self._profiles[sel[0]]
        self._active_profile = p["name"]
        self.var_args.set(p.get("args", ""))
        self.var_env.set(p.get("env_vars", ""))
        if p.get("workdir"):
            self.var_workdir.set(p["workdir"])
        if p.get("timeout"):
            self.var_timeout.set(str(p["timeout"]))
        if p.get("interpreter"):
            self.var_interp.set(p["interpreter"])
        self._reload_profile_list()

    def _browse_workdir(self):
        d = filedialog.askdirectory(parent=self)
        if d:
            self.var_workdir.set(d)

    def _open_env_editor(self):
        """Open environment variable editor dialog."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        dlg = _EnvVarEditorDialog(self, self.var_env.get(), self.lang, theme=C)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.var_env.set(dlg.result)

    def _ok(self):
        self.result = self._entry_data.copy()
        self.result.update({
            "interpreter":   self.var_interp.get(),
            "args":          self.var_args.get(),
            "workdir":       self.var_workdir.get(),
            "encoding":      self.var_enc.get(),
            "run_as_admin":  self.var_admin.get(),
            "hidden_window": self.var_hidden.get(),
            "wait":          self.var_wait.get(),
            "env_vars":      self.var_env.get(),
        })
        if self.is_ps1:
            self.result["ps_exec_policy"] = self.var_ps_policy.get()
        self.result["auto_restart"]       = self.var_auto_restart.get()
        self.result["max_retries"]        = int(self.var_max_retries.get() or 3)
        self.result["timeout"]            = int(self.var_timeout.get() or 0)
        self.result["tags"]               = self.var_tags.get().strip()
        self.result["note"]               = self.txt_note.get("1.0", "end-1c").strip()
        self.result["profiles"]           = self._profiles
        self.result["active_profile"]     = self._active_profile
        self.result["watchdog_interval"]  = int(self.var_watchdog.get() or 0)
        self.result["notify_on_finish"]   = self.var_notify.get()
        self.result["notify_min_sec"]     = int(self.var_notify_min.get() or 0)
        self.result["run_after"]          = self.var_run_after.get().strip()
        self.result["hotkey"]             = self.var_hotkey.get().strip().lower()
        self.result["kiosk_visible"]      = self.var_kiosk_visible.get()
        self.destroy()

# ──────────────────────────────────────────────
#  PROFILE EDIT DIALOG
# ──────────────────────────────────────────────
class _ProfileEditDialog(tk.Toplevel):
    def __init__(self, parent, profile: dict):
        super().__init__(parent)
        self.result = None
        # inherit theme and language from parent if available
        C = getattr(parent, "_C", None) or THEMES["light"]
        lang = getattr(parent, "lang", "pl")
        # ScriptOptionsDialog doesn't store lang directly; walk up to PSLauncher
        if not hasattr(parent, "lang"):
            p = parent.master
            while p is not None:
                if hasattr(p, "lang"):
                    lang = p.lang
                    break
                p = getattr(p, "master", None)
        T = TRANSLATIONS.get(lang, TRANSLATIONS["pl"])
        self.title(T.get("opts_profiles", "Run profiles"))
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=C["bg_main"])
        pad = {"padx": 8, "pady": 4}
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"],
                     "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}

        tk.Label(self, text=T.get("profile_field_name", "Name:"), **lbl_cfg).grid(row=0, column=0, sticky="w", **pad)
        self.var_name = tk.StringVar(value=profile.get("name", ""))
        tk.Entry(self, textvariable=self.var_name, width=30, **entry_cfg).grid(row=0, column=1, **pad)

        tk.Label(self, text=T.get("profile_field_args", "Arguments:"), **lbl_cfg).grid(row=1, column=0, sticky="w", **pad)
        self.var_args = tk.StringVar(value=profile.get("args", ""))
        tk.Entry(self, textvariable=self.var_args, width=30, **entry_cfg).grid(row=1, column=1, **pad)

        tk.Label(self, text=T.get("profile_field_env", "Env vars (KEY=VAL …):"), **lbl_cfg).grid(row=2, column=0, sticky="w", **pad)
        self.var_env = tk.StringVar(value=profile.get("env_vars", ""))
        tk.Entry(self, textvariable=self.var_env, width=30, **entry_cfg).grid(row=2, column=1, **pad)

        tk.Label(self, text=T.get("profile_field_workdir", "Working directory:"), **lbl_cfg).grid(row=3, column=0, sticky="w", **pad)
        self.var_workdir = tk.StringVar(value=profile.get("workdir", ""))
        frm_wd = tk.Frame(self, bg=C["bg_main"])
        frm_wd.grid(row=3, column=1, sticky="w", **pad)
        tk.Entry(frm_wd, textvariable=self.var_workdir, width=22, **entry_cfg).pack(side="left")
        tk.Button(frm_wd, text="…", command=self._browse_workdir,
                  bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                  font=("Consolas", 9), padx=6, cursor="hand2").pack(side="left", padx=(4, 0))

        tk.Label(self, text=T.get("profile_field_timeout", "Timeout [s] (0=none):"), **lbl_cfg).grid(row=4, column=0, sticky="w", **pad)
        self.var_timeout = tk.StringVar(value=str(profile.get("timeout", "") or ""))
        tk.Entry(self, textvariable=self.var_timeout, width=10, **entry_cfg).grid(row=4, column=1, sticky="w", **pad)

        tk.Label(self, text=T.get("profile_field_interpreter", "Interpreter:"), **lbl_cfg).grid(row=5, column=0, sticky="w", **pad)
        self.var_interp = tk.StringVar(value=profile.get("interpreter", ""))
        tk.Entry(self, textvariable=self.var_interp, width=30, **entry_cfg).grid(row=5, column=1, **pad)

        frm_btns = tk.Frame(self, bg=C["bg_main"])
        frm_btns.grid(row=6, column=0, columnspan=2, pady=8)
        tk.Button(frm_btns, text="OK", command=self._ok,
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"),
                  padx=12, pady=3, cursor="hand2").pack(side="left", padx=4)
        tk.Button(frm_btns, text=T.get("profile_ok_cancel", "Cancel"), command=self.destroy,
                  bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9),
                  padx=12, pady=3, cursor="hand2").pack(side="left", padx=4)

        self.update_idletasks()
        pw, ph = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-pw)//2}+{(sh-ph)//2}")

    def _browse_workdir(self):
        d = filedialog.askdirectory(parent=self)
        if d:
            self.var_workdir.set(d)

    def _ok(self):
        name = self.var_name.get().strip()
        if not name:
            return
        timeout_val = 0
        try:
            timeout_val = int(self.var_timeout.get().strip() or "0")
        except ValueError:
            timeout_val = 0
        self.result = {
            "name":        name,
            "args":        self.var_args.get(),
            "env_vars":    self.var_env.get(),
            "workdir":     self.var_workdir.get(),
            "timeout":     timeout_val,
            "interpreter": self.var_interp.get(),
        }
        self.destroy()

# ──────────────────────────────────────────────
#  ENVIRONMENT VARIABLE EDITOR DIALOG (v1.7)
# ──────────────────────────────────────────────
class _EnvVarEditorDialog(tk.Toplevel):
    def __init__(self, parent, env_string: str, lang: str, theme: dict | None = None):
        super().__init__(parent)
        self.result = None
        T = TRANSLATIONS.get(lang, TRANSLATIONS["pl"])
        C = theme if theme is not None else THEMES["light"]
        
        self.title(T.get("env_editor_title", "Environment Variable Editor"))
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=C["bg_main"])
        self.geometry("500x350")
        
        pad = {"padx": 8, "pady": 4}
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"], "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}
        
        # Parse existing env vars
        self.env_vars = []
        if env_string:
            for pair in env_string.split():
                if "=" in pair:
                    key, val = pair.split("=", 1)
                    self.env_vars.append([key, val])
        
        # Treeview for env vars
        tree_frame = tk.Frame(self, bg=C["bg_main"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("key", "value")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("key", text=T.get("env_editor_key", "Key"))
        self.tree.heading("value", text=T.get("env_editor_value", "Value"))
        self.tree.column("key", width=150)
        self.tree.column("value", width=280)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._refresh_tree()
        
        # Buttons
        btn_frame = tk.Frame(self, bg=C["bg_main"])
        btn_frame.pack(side="bottom", pady=10)
        
        tk.Button(btn_frame, text=T.get("env_editor_add", "Add"),
                  command=self._add_var, bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9), padx=8, pady=3).pack(side="left", padx=4)
        tk.Button(btn_frame, text=T.get("env_editor_remove", "Remove"),
                  command=self._remove_var, bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9), padx=8, pady=3).pack(side="left", padx=4)
        tk.Button(btn_frame, text=T.get("env_editor_clear", "Clear"),
                  command=self._clear_vars, bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9), padx=8, pady=3).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text=T["btn_ok"], command=self._ok,
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                  font=("Consolas", 9, "bold"), padx=12, pady=3).pack(side="right", padx=4)
        tk.Button(btn_frame, text=T["btn_cancel"], command=self.destroy,
                  bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                  font=("Consolas", 9), padx=12, pady=3).pack(side="right", padx=4)
        
        _center_dialog(self)
    
    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for key, val in self.env_vars:
            self.tree.insert("", "end", values=(key, val))
    
    def _add_var(self):
        dlg = _EnvVarEditDialog(self, "", "")
        self.wait_window(dlg)
        if dlg.result:
            self.env_vars.append([dlg.result[0], dlg.result[1]])
            self._refresh_tree()
    
    def _remove_var(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            if 0 <= idx < len(self.env_vars):
                self.env_vars.pop(idx)
                self._refresh_tree()
    
    def _clear_vars(self):
        self.env_vars = []
        self._refresh_tree()
    
    def _ok(self):
        self.result = " ".join(f"{k}={v}" for k, v in self.env_vars)
        self.destroy()

class _EnvVarEditDialog(tk.Toplevel):
    def __init__(self, parent, key: str, value: str):
        super().__init__(parent)
        self.result = None
        C = THEMES.get("light", THEMES["light"])
        
        self.title("Edit Environment Variable")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=C["bg_main"])
        
        pad = {"padx": 8, "pady": 4}
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"], "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}
        
        tk.Label(self, text="Key:", **lbl_cfg).grid(row=0, column=0, sticky="w", **pad)
        self.var_key = tk.StringVar(value=key)
        tk.Entry(self, textvariable=self.var_key, width=30, **entry_cfg).grid(row=0, column=1, **pad)
        
        tk.Label(self, text="Value:", **lbl_cfg).grid(row=1, column=0, sticky="w", **pad)
        self.var_value = tk.StringVar(value=value)
        tk.Entry(self, textvariable=self.var_value, width=30, **entry_cfg).grid(row=1, column=1, **pad)
        
        btn_frame = tk.Frame(self, bg=C["bg_main"])
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="OK", command=self._ok,
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                  font=("Consolas", 9, "bold"), padx=12, pady=3).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Cancel", command=self.destroy,
                  bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                  font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=4)
        
        _center_dialog(self)
    
    def _ok(self):
        key = self.var_key.get().strip()
        value = self.var_value.get()
        if key:
            self.result = (key, value)
            self.destroy()


# ──────────────────────────────────────────────
#  SCAN DIALOG
# ──────────────────────────────────────────────
class ScanDialog(tk.Toplevel):
    def __init__(self, parent, lang: str, callback, theme: dict | None = None):
        super().__init__(parent)
        self.callback = callback
        self.lang = lang
        # Use provided theme, or inherit from parent, or fall back to dark
        C = theme or getattr(parent, "_C", None) or THEMES["light"]
        T = TRANSLATIONS[lang]
        self.title(T["dlg_scan_title"])
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=C["bg_main"])

        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"], "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}

        frm_dir = tk.Frame(self, bg=C["bg_main"])
        frm_dir.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(frm_dir, text="Katalog / Directory:", **lbl_cfg).pack(anchor="w")
        frm_d2 = tk.Frame(frm_dir, bg=C["bg_main"])
        frm_d2.pack(fill="x")
        self.var_dir = tk.StringVar()
        tk.Entry(frm_d2, textvariable=self.var_dir, width=40, **entry_cfg).pack(side="left")
        tk.Button(frm_d2, text=T["btn_browse"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 8),
                  command=self._browse).pack(side="left", padx=(4,0))

        frm_ext = tk.Frame(self, bg=C["bg_main"])
        frm_ext.pack(fill="x", padx=10, pady=4)
        tk.Label(frm_ext, text=T["scan_extensions"], **lbl_cfg).pack(anchor="w")
        self.var_ext = tk.StringVar(value=".py .ps1 .bat .cmd .vbs .sh .js .rb .pl .r .php .lua")
        tk.Entry(frm_ext, textvariable=self.var_ext, width=50, **entry_cfg).pack(fill="x")

        self.var_recursive = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text=T["scan_recursive"],
                       variable=self.var_recursive,
                       bg=C["bg_main"], fg=C["fg_main"],
                       activebackground=C["bg_main"], activeforeground=C["fg_accent"],
                       selectcolor=C["bg_entry"], font=("Consolas", 9)).pack(anchor="w", padx=10, pady=4)

        self.progress = ttk.Progressbar(self, mode="indeterminate", length=350)
        self.progress.pack(padx=10, pady=4)

        self.lbl_status = tk.Label(self, text="", bg=C["bg_main"], fg=C["fg_green"], font=("Consolas", 8))
        self.lbl_status.pack(padx=10)

        btn_frm = tk.Frame(self, bg=C["bg_main"])
        btn_frm.pack(pady=10)
        self.btn_scan = tk.Button(btn_frm, text=T["scan_btn"],
                                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                                  font=("Consolas", 9, "bold"), padx=14, pady=4,
                                  cursor="hand2", command=self._start_scan)
        self.btn_scan.pack(side="left", padx=4)
        tk.Button(btn_frm, text=T["btn_cancel"],
                  bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                  font=("Consolas", 9), padx=14, pady=4,
                  cursor="hand2", command=self.destroy).pack(side="left", padx=4)
        self.center()

    def center(self):
        _center_dialog(self)

    def _browse(self):
        d = filedialog.askdirectory(parent=self)
        if d:
            self.var_dir.set(d)

    def _start_scan(self):
        d = self.var_dir.get()
        if not d or not os.path.isdir(d):
            return
        exts = [e.strip().lower() for e in self.var_ext.get().split()]
        recursive = self.var_recursive.get()
        self.btn_scan.config(state="disabled")
        self.progress.start(10)
        t = threading.Thread(target=self._scan, args=(d, exts, recursive), daemon=True)
        t.start()

    def _scan(self, directory, exts, recursive):
        found = []
        try:
            if recursive:
                for root, _, files in os.walk(directory):
                    for f in files:
                        if Path(f).suffix.lower() in exts:
                            found.append(os.path.join(root, f))
            else:
                for f in os.listdir(directory):
                    if Path(f).suffix.lower() in exts:
                        found.append(os.path.join(directory, f))
        except Exception:
            pass
        T = TRANSLATIONS[self.lang]
        self.after(0, lambda: self._scan_done(found, T))

    def _scan_done(self, found, T):
        self.progress.stop()
        self.btn_scan.config(state="normal")
        self.lbl_status.config(text=f"{T['dlg_scan_found']}: {len(found)}")
        self.callback(found)
        self.destroy()

# ──────────────────────────────────────────────
#  TOOLTIP
# ──────────────────────────────────────────────
class Tooltip:
    """Simple hover tooltip for tk widgets."""
    def __init__(self, widget, text: str, theme: dict | None = None):
        self.widget = widget
        self.text = text
        self.theme = theme or THEMES["light"]
        self._tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self._tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify="left",
                 background=self.theme["tooltip_bg"],
                 foreground=self.theme["tooltip_fg"],
                 relief="flat", borderwidth=1,
                 font=("Consolas", 8), padx=6, pady=3).pack()

    def _hide(self, event=None):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


# ──────────────────────────────────────────────
#  HOTKEY MANAGER
# ──────────────────────────────────────────────
class HotkeyManager:
    """Registers / unregisters global hotkeys via the `keyboard` library.
    Falls back to a no-op if the library is missing or registration fails
    (common without root / on macOS without accessibility permissions)."""

    def __init__(self, callback):
        """callback(script_entry) called on hotkey press (from non-main thread)."""
        self._cb = callback
        # hotkey_str → script_entry
        self._registered: dict[str, dict] = {}

    def register(self, hotkey: str, script: dict) -> str | None:
        """Register a hotkey. Returns None on success, error string on failure."""
        if not hotkey:
            return None
        if not _KEYBOARD_AVAILABLE:
            return "keyboard_missing"
        hotkey = hotkey.lower().strip()
        # Unhook previous binding for this hotkey (different script might own it)
        if hotkey in self._registered:
            try:
                _keyboard_lib.remove_hotkey(hotkey)
            except Exception:
                pass
        try:
            _keyboard_lib.add_hotkey(hotkey, lambda s=script: self._cb(s),
                                     suppress=False)
            self._registered[hotkey] = script
            return None
        except Exception as e:
            return str(e)

    def unregister(self, hotkey: str):
        if not hotkey or not _KEYBOARD_AVAILABLE:
            return
        hotkey = hotkey.lower().strip()
        if hotkey in self._registered:
            try:
                _keyboard_lib.remove_hotkey(hotkey)
            except Exception:
                pass
            del self._registered[hotkey]

    def unregister_all(self):
        if not _KEYBOARD_AVAILABLE:
            return
        for hk in list(self._registered):
            try:
                _keyboard_lib.remove_hotkey(hk)
            except Exception:
                pass
        self._registered.clear()

    def reload(self, scripts: list[dict]):
        """Re-register all hotkeys from a fresh script list."""
        self.unregister_all()
        for s in scripts:
            hk = s.get("hotkey", "").strip()
            if hk:
                self.register(hk, s)


# ──────────────────────────────────────────────
#  KIOSK WINDOW
# ──────────────────────────────────────────────
class KioskWindow(tk.Toplevel):
    """Full-screen (or maximised) launcher with one big button per script.
    Users can only press RUN buttons; no list, no log, no menu."""

    _BTN_W  = 200
    _BTN_H  = 80
    _PAD    = 14
    _COLS   = 4   # max buttons per row (auto-wraps)

    def __init__(self, parent: "PSLauncher"):
        super().__init__(parent)
        self._app = parent
        T = TRANSLATIONS[parent.lang]
        C = THEMES.get(parent.theme_name, THEMES["light"])
        self._C = C
        self._T = T

        self.title(T.get("kiosk_title", "psLauncher – Kiosk"))
        self.configure(bg=C["bg_main"])
        self.attributes("-topmost", True)
        self.state("zoomed")          # maximise; works on Win/Linux
        self.resizable(True, True)

        # Prevent closing with Alt+F4 except through Back button
        self.protocol("WM_DELETE_WINDOW", self._exit_kiosk)

        # ── Header bar ──
        hdr = tk.Frame(self, bg=C["bg_panel"], pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text=T.get("kiosk_title", "psLauncher – Kiosk"),
                 bg=C["bg_panel"], fg=C["fg_accent"],
                 font=("Consolas", 14, "bold"), padx=16).pack(side="left")

        # Group filter
        tk.Label(hdr, text=T.get("kiosk_group_label", "Group:"),
                 bg=C["bg_panel"], fg=C["fg_dim"],
                 font=("Consolas", 10), padx=6).pack(side="left")
        self._var_group = tk.StringVar(value=T.get("kiosk_all_groups", "All"))
        groups = [T.get("kiosk_all_groups", "All")] + parent._groups
        self._cb_group = ttk.Combobox(hdr, textvariable=self._var_group,
                                       values=groups, state="readonly",
                                       width=18, font=("Consolas", 10))
        self._cb_group.pack(side="left", padx=4)
        self._cb_group.bind("<<ComboboxSelected>>", lambda e: self._rebuild_buttons())

        # Status label (shows "Running…" briefly)
        self._var_status = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._var_status,
                 bg=C["bg_panel"], fg=C["fg_green"],
                 font=("Consolas", 10), padx=12).pack(side="left")

        tk.Button(hdr, text=T.get("kiosk_btn_exit", "⬅  Back"),
                  bg=C["btn_del_bg"], fg=C["btn_del_fg"],
                  relief="flat", font=("Consolas", 10, "bold"),
                  padx=12, pady=4, cursor="hand2",
                  command=self._exit_kiosk).pack(side="right", padx=12)

        # ── Scrollable canvas for buttons ──
        self._canvas = tk.Canvas(self, bg=C["bg_main"], highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview, style="Vertical.TScrollbar")
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", lambda e: self._rebuild_buttons())
        self._canvas.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(
            -1 if e.delta > 0 else 1, "units"))

        self._btn_frame = tk.Frame(self._canvas, bg=C["bg_main"])
        self._btn_frame_id = self._canvas.create_window(
            (0, 0), window=self._btn_frame, anchor="nw")
        self._btn_frame.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))

        self._rebuild_buttons()

    def _visible_scripts(self):
        T = self._T
        grp_val = self._var_group.get()
        all_lbl = T.get("kiosk_all_groups", "All")
        out = []
        for s in self._app.scripts:
            if not s.get("kiosk_visible", True):
                continue
            if grp_val != all_lbl:
                if s.get("group", "") != grp_val:
                    continue
            out.append(s)
        return out

    def _rebuild_buttons(self):
        C = self._C
        T = self._T
        for w in self._btn_frame.winfo_children():
            w.destroy()

        scripts = self._visible_scripts()
        if not scripts:
            tk.Label(self._btn_frame,
                     text=T.get("kiosk_no_scripts", "No scripts to display."),
                     bg=C["bg_main"], fg=C["fg_dim"],
                     font=("Consolas", 12)).grid(padx=20, pady=40)
            return

        canvas_w = self._canvas.winfo_width() or 800
        btn_w    = self._BTN_W + self._PAD * 2
        cols = max(1, canvas_w // btn_w)

        for i, s in enumerate(scripts):
            row = i // cols
            col = i % cols
            ext  = Path(s.get("path", "")).suffix.lower()
            info = SCRIPT_TYPES.get(ext, {"icon": "default", "color": "#888888"})
            icon_name = info["icon"]
            color = info.get("color", C["btn_run_bg"])

            frm = tk.Frame(self._btn_frame, bg=C["bg_main"],
                           padx=self._PAD, pady=self._PAD)
            frm.grid(row=row, column=col, padx=2, pady=2)

            icon_img = get_icon(icon_name, size=(32, 32))
            btn = tk.Button(
                frm,
                text=s.get('name', ''),
                image=icon_img,
                compound="top",
                width=14, height=4,
                bg=C["bg_btn"], fg=C["fg_main"],
                activebackground=color, activeforeground="#ffffff",
                relief="flat", font=("Consolas", 10, "bold"),
                wraplength=180, justify="center",
                cursor="hand2",
                command=lambda sc=s: self._run(sc))
            btn.pack()

            # Hotkey hint label under button
            hk = s.get("hotkey", "")
            if hk:
                tk.Label(frm, text=f"[{hk}]",
                         bg=C["bg_main"], fg=C["fg_dim"],
                         font=("Consolas", 7)).pack()

        # Resize canvas window to fill width
        self._canvas.itemconfig(
            self._btn_frame_id,
            width=self._canvas.winfo_width())

    def _run(self, s: dict):
        T = self._T
        path = s.get("path", "")
        if not os.path.exists(path):
            self._var_status.set(f"✘ {s.get('name','')} – plik nie istnieje")
            return
        self._var_status.set(f"▶ {T.get('kiosk_running','Running…')} {s.get('name','')}")
        self.after(2500, lambda: self._var_status.set(""))
        threading.Thread(target=self._app._run_script, args=(s,), daemon=True).start()

    def _exit_kiosk(self):
        self._app.deiconify()
        self.destroy()


# ──────────────────────────────────────────────
#  MAIN APPLICATION
# ──────────────────────────────────────────────
_BaseApp = TkinterDnD.Tk if _DND_AVAILABLE else tk.Tk

# ── Stały katalog roboczy aplikacji ──────────────────────────────────────────
APP_DIR = Path(r"C:\.polsoft\psLauncher") if platform.system() == "Windows" \
          else Path.home() / ".polsoft" / "psLauncher"
APP_DIR.mkdir(parents=True, exist_ok=True)

class PSLauncher(_BaseApp):
    CONFIG_FILE = str(APP_DIR / "pslauncher_config.json")

    def __init__(self):
        super().__init__()
        # Hide the real window and show a lightweight splash immediately,
        # before any of the (potentially slow) UI construction below runs.
        self.withdraw()
        splash = self._show_splash()

        self.lang = "en"
        self.theme_name = "light"
        self.scripts: list[dict] = []
        self.panel_visible = True
        self.log_queue = queue.Queue()
        self._sort_col = None
        self._sort_reverse = False
        self._last_run_info = None  # dict: name, code, elapsed
        self._groups: list[str] = []          # v1.2: user-defined groups
        self._active_group: str = ""          # v1.2: "" = All
        self._run_history: list[dict] = []    # v1.2: execution history
        self._group_btns: list = []           # v1.2: group bar buttons (populated in _build_ui)
        # v1.3: process control
        self._active_proc: subprocess.Popen | None = None  # currently tracked process
        self._active_script: dict | None = None             # script entry for active proc
        # v1.6: per-path registry of running processes (prevents duplicate
        # concurrent launches from queue/watchdog/hotkey/dependents and lets
        # Stop/Restart target the right process even when several scripts
        # run at once)
        self._running_procs: dict[str, subprocess.Popen] = {}
        self._running_lock = threading.Lock()
        # v1.6: cache resolved interpreter/tool paths (path or ext -> exe)
        # to avoid repeated shutil.which() disk lookups on every run
        self._tool_cache: dict[str, str] = {}
        # v1.3: run queue  [(script_dict, iid_var)]
        self._run_queue: list[dict] = []
        # v1.3: scheduler entries [{name, script, type, value, next_ts, active}]
        self._schedules: list[dict] = []
        self._sched_timer_id = None
        # v1.5: watchdog stop-events keyed by script path
        self._watchdog_stop: dict[str, threading.Event] = {}
        # v1.7 UI: hotkey manager + kiosk
        self._hotkey_mgr = HotkeyManager(self._hotkey_triggered)
        self._kiosk_win: KioskWindow | None = None
        # debounce save timer
        self._save_timer_id = None
        # statusbar auto-clear timer
        self._status_clear_timer = None
        # code preview state
        self._preview_mode = False
        # app-level settings (persist in config)
        self.app_settings: dict = self._default_app_settings()
        # v1.8: plugin system
        self._plugins: list[dict] = []  # loaded plugins: {name, module, hooks}
        self._plugins_dir = APP_DIR / "plugins"
        self._plugins_dir.mkdir(exist_ok=True)
        # v1.8: system notifications
        self._notifications_enabled = False
        # v1.8: ANSI color engine for enhanced log output
        if _ANSI_AVAILABLE:
            self._ansi_engine = ANSIEngine(enabled=True)
            self._ansi_enabled = self.app_settings.get("ansi_colors_enabled", True)
            self.var_ansi_colors_enabled = tk.BooleanVar(value=self._ansi_enabled)
        else:
            self._ansi_engine = None
            self._ansi_enabled = False
            self.var_ansi_colors_enabled = tk.BooleanVar(value=False)
        # v1.8: structured logging system
        if _LOGGER_AVAILABLE:
            self._structured_logger = setup_logger(
                log_dir=str(APP_DIR / "logs"),
                log_file="pslauncher.log",
                console_level="INFO",
                file_level="DEBUG",
                enable_colors=True
            )
        else:
            self._structured_logger = None
        # v1.8: debugger integration
        if _DEBUGGER_AVAILABLE:
            self._debugger_config = DebuggerConfig(
                enable_ai_assistance=False,
                enable_time_travel=False,
                enable_remote_debugging=False,
                enable_chaos_engineering=False,
                enable_security_auditing=False,
                enable_collaboration=False
            )
            self._debugger_enabled = self.app_settings.get("debugger_enabled", False)
            self._execution_controller = None
            self._state_inspector = None
            self._profiler = None
        else:
            self._debugger_config = None
            self._debugger_enabled = False
        # v1.8: script runner integration
        if _SCRIPT_RUNNER_AVAILABLE:
            self._script_runner = ScriptRunner(
                templates_dir=str(APP_DIR / "templates"),
                history_file=str(APP_DIR / "execution_history.json"),
                scheduler_file=str(APP_DIR / "scheduler.json"),
                backup_dir=str(APP_DIR / "backups")
            )
        else:
            self._script_runner = None
        # Cache for frequently accessed data
        self._script_cache: dict[str, dict] = {}  # path -> script metadata
        self._icon_cache: dict[str, tk.PhotoImage] = {}  # name -> icon image
        # Log window dock state
        self._log_window: tk.Toplevel | None = None  # undocked log window
        self._log_docked = True  # current dock state

        try:
            self._load_config()
        except Exception as e:
            print(f"[WARNING] Failed to load config: {e}", file=sys.stderr)
            self.app_settings = self._default_app_settings()
        
        try:
            self._apply_global_scrollbar_style()
        except Exception as e:
            print(f"[WARNING] Failed to apply scrollbar style: {e}", file=sys.stderr)
        
        try:
            self._build_ui()
        except Exception as e:
            print(f"[ERROR] Failed to build UI: {e}", file=sys.stderr)
            raise
        
        try:
            self._apply_lang()
        except Exception as e:
            print(f"[WARNING] Failed to apply language: {e}", file=sys.stderr)
        
        try:
            self._bind_keys()
        except Exception as e:
            print(f"[WARNING] Failed to bind keys: {e}", file=sys.stderr)
        
        try:
            self._setup_dnd()
        except Exception as e:
            print(f"[WARNING] Failed to setup DND: {e}", file=sys.stderr)
        
        try:
            self._process_log_queue()
        except Exception as e:
            print(f"[WARNING] Failed to process log queue: {e}", file=sys.stderr)
        
        try:
            self._scheduler_tick()
        except Exception as e:
            print(f"[WARNING] Failed to start scheduler: {e}", file=sys.stderr)

        # Base UI exists and is already styled (built directly with the
        # active theme's colors) — swap the splash for the real window now,
        # then finish the heavier startup work off the critical path so the
        # window appears responsive immediately instead of after everything
        # below has run.
        self._close_splash(splash)
        self.deiconify()
        self.lift()
        self.after(0, self._finish_startup)

    # ── SPLASH SCREEN ───────────────────────
    def _show_splash(self):
        """Tiny borderless 'loading' window shown the instant the app
        starts, before config is read or the main UI is built."""
        splash = tk.Toplevel(self)
        splash.overrideredirect(True)
        w, h = 320, 110
        sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
        splash.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")
        splash.configure(bg="#1e1e1e")
        try:
            splash.attributes("-topmost", True)
        except Exception:
            pass
        tk.Label(splash, text=f"psLauncher v{__version__}",
                 bg="#1e1e1e", fg="#39ff7a",
                 font=("Consolas", 13, "bold")).pack(pady=(26, 6))
        tk.Label(splash, text="Ładowanie…",
                 bg="#1e1e1e", fg="#9da5b4",
                 font=("Consolas", 9)).pack()
        # Force an immediate redraw so the splash is actually painted
        # before the (synchronous) UI-building work below begins.
        splash.update_idletasks()
        splash.update()
        return splash

    def _close_splash(self, splash):
        try:
            splash.destroy()
        except Exception:
            pass

    # ── DEFERRED STARTUP TAIL ───────────────
    def _finish_startup(self):
        """Runs once, right after the window is first shown. Populates the
        tree (the genuinely expensive part) and registers global hotkeys on
        a background thread. Does NOT call _apply_theme() here — _build_ui
        already constructed every widget with the correct theme colors, so
        re-running the full theme pass would just redo ~50 configure()
        calls for no visible change. _apply_theme() is reserved for actual
        runtime theme switches (_set_theme, full-backup import, etc.)."""
        # Apply startup settings that depend on loaded config
        S = self.app_settings
        if not S.get("panel_on_start", True):
            self._toggle_panel()
        rh = S.get("tree_row_height", 22)
        if rh != 22:
            ttk.Style().configure("Treeview", rowheight=rh)
        self._refresh_tree()
        threading.Thread(
            target=self._hotkey_mgr.reload, args=(self.scripts,), daemon=True
        ).start()
        
        # v2.1: Setup new features
        self._setup_quick_actions_toolbar()
        self._setup_system_notifications()
        self._setup_keyboard_shortcuts()

        # Show config recovery/corruption warning, if any, now that UI exists
        if getattr(self, "_pending_config_warning", None):
            now = lambda: datetime.now().strftime("%H:%M:%S")
            self.log_queue.put(f"\n[{now()}] ⚠ {self._pending_config_warning}\n")
            self._set_status(f"⚠ {self._pending_config_warning}")
            self._pending_config_warning = None


    # ── CONFIG ──────────────────────────────
    def _config_defaults(self):
        return {
            "scripts": [], "lang": "pl", "theme": "light",
            "groups": [], "run_history": [], "schedules": [],
            "app_settings": {},
        }

    def _default_app_settings(self) -> dict:
        return {
            "work_dir":           str(APP_DIR),
            "confirm_delete":     True,
            "save_on_exit":       True,
            "autostart":          False,
            "default_timeout":    0,
            "default_retries":    3,
            "default_restart":    False,
            "default_encoding":   "utf-8",
            "notify_global":      True,
            "notify_min_sec":     0,
            "log_max_lines":      0,
            "panel_on_start":     True,
            "tree_row_height":    22,
        }

    def _read_config_file(self, path: str):
        """Read & validate a config JSON file. Returns dict or raises."""
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        if not isinstance(cfg, dict):
            raise ValueError("Config root is not an object")
        if not isinstance(cfg.get("scripts", []), list):
            raise ValueError("'scripts' is not a list")
        for s in cfg.get("scripts", []):
            if not isinstance(s, dict):
                raise ValueError("Invalid script entry")
        return cfg

    def _load_config(self):
        cfg = None
        load_error = None

        if os.path.exists(self.CONFIG_FILE):
            try:
                cfg = self._read_config_file(self.CONFIG_FILE)
            except Exception as e:
                load_error = e

        # ── Fallback to backup if main config missing/corrupt ──
        if cfg is None:
            bak_file = self.CONFIG_FILE + ".bak"
            if os.path.exists(bak_file):
                try:
                    cfg = self._read_config_file(bak_file)
                    if load_error is not None:
                        # quarantine the corrupt main file for inspection
                        try:
                            corrupt_path = self.CONFIG_FILE + ".corrupt"
                            shutil.copy2(self.CONFIG_FILE, corrupt_path)
                        except Exception:
                            pass
                        load_error = (
                            f"Config corrupted ({load_error}); "
                            f"restored from backup. Corrupt file saved as "
                            f"'{os.path.basename(self.CONFIG_FILE)}.corrupt'."
                        )
                except Exception as e2:
                    load_error = e2 if load_error is None else load_error

        if cfg is None:
            cfg = self._config_defaults()

        self.scripts       = cfg.get("scripts", [])
        self.lang          = cfg.get("lang", "en")
        self.theme_name    = cfg.get("theme", "light")
        self._groups       = cfg.get("groups", [])
        self._run_history  = cfg.get("run_history", [])
        self._schedules    = cfg.get("schedules", self._schedules)
        self._global_env_vars = cfg.get("global_env_vars", "")
        # merge saved app_settings over defaults (so new keys get default values)
        saved_s = cfg.get("app_settings", {})
        self.app_settings  = {**self._default_app_settings(), **saved_s}
        self._notifications_enabled = self.app_settings.get("notifications_enabled", False)
        # v1.8: load ANSI colors setting
        if _ANSI_AVAILABLE:
            self._ansi_enabled = self.app_settings.get("ansi_colors_enabled", True)
            self.var_ansi_colors_enabled.set(self._ansi_enabled)

        # migrate old entries without new fields
        for s in self.scripts:
            s.setdefault("group", "")
            s.setdefault("pinned", False)
            s.setdefault("env_vars", "")
            s.setdefault("auto_restart", False)
            s.setdefault("max_retries", 3)
            s.setdefault("timeout", 0)
            s.setdefault("tags", "")
            s.setdefault("note", "")
            s.setdefault("profiles", [])
            s.setdefault("active_profile", "")
            s.setdefault("favorite", False)
            # v1.5 monitoring
            s.setdefault("run_count", 0)
            s.setdefault("run_times", [])
            s.setdefault("last_rc", None)
            s.setdefault("watchdog_interval", 0)
            s.setdefault("notify_on_finish", False)
            s.setdefault("notify_min_sec", 0)
            s.setdefault("run_after", "")
            # v1.7 UI
            s.setdefault("hotkey", "")
            s.setdefault("kiosk_visible", True)

        # Defer status reporting until the UI/status bar exists
        if load_error is not None:
            self._pending_config_warning = str(load_error)
        else:
            self._pending_config_warning = None

    def _save_config(self):
        try:
            cfg = {
                "scripts": self.scripts,
                "lang": self.lang,
                "theme": self.theme_name,
                "groups": self._groups,
                "run_history": self._run_history[-200:],  # keep last 200 entries
                "schedules": self._schedules,
                "app_settings": self.app_settings,
                "global_env_vars": self._global_env_vars,
            }
            tmp_file = self.CONFIG_FILE + ".tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)

            # Validate the freshly written file before committing
            self._read_config_file(tmp_file)

            # Rotate previous good config to .bak before replacing
            if os.path.exists(self.CONFIG_FILE):
                try:
                    bak_file = self.CONFIG_FILE + ".bak"
                    shutil.copy2(self.CONFIG_FILE, bak_file)
                except Exception:
                    pass

            os.replace(tmp_file, self.CONFIG_FILE)
        except Exception as e:
            try:
                self._set_status(f"⚠ Config save error: {e}")
            except Exception:
                pass

    def _schedule_save(self, delay: int = 300):
        """Debounced save — cancels any pending timer and schedules a new one."""
        if self._save_timer_id is not None:
            self.after_cancel(self._save_timer_id)
        self._save_timer_id = self.after(delay, self._flush_save)

    def _flush_save(self):
        self._save_timer_id = None
        self._save_config()

    def _set_status(self, msg: str, autoclear: int = 4000):
        """Sets the statusbar text and, unless autoclear=0, schedules it to
        automatically revert after `autoclear` ms — back to the last-run
        summary if one exists, otherwise to the neutral 'Ready' text.
        Without this, a one-off confirmation (e.g. "✔ Saved") would stay
        in the statusbar forever, hiding more recent/relevant state."""
        self.var_status.set(msg)
        if self._status_clear_timer is not None:
            self.after_cancel(self._status_clear_timer)
            self._status_clear_timer = None
        if autoclear:
            self._status_clear_timer = self.after(autoclear, self._status_revert)

    def _status_revert(self):
        self._status_clear_timer = None
        T = TRANSLATIONS[self.lang]
        if self._last_run_info:
            try:
                self.var_status.set(T["status_last_run"].format(**self._last_run_info))
                return
            except Exception:
                pass
        self.var_status.set(T.get("status_ready", ""))

    # ── GLOBAL SCROLLBAR STYLING ────────────────────
    def _apply_global_scrollbar_style(self):
        """Apply consistent dark scrollbar styling globally"""
        C = THEMES.get(self.theme_name, THEMES["light"])
        style = ttk.Style()
        style.theme_use("clam")
        
        # Use darker colors for better visibility
        sb_bg = C.get("scrollbar_bg", "#11111b")
        sb_fg = C.get("scrollbar_fg", "#45475a")
        
        style.configure("TScrollbar",
                         background=sb_bg,
                         troughcolor=sb_bg,
                         bordercolor=sb_bg,
                         arrowcolor=C["fg_dim"],
                         darkcolor=sb_fg,
                         lightcolor=sb_fg)
        style.configure("Vertical.TScrollbar",
                         background=sb_bg,
                         troughcolor=sb_bg,
                         bordercolor=sb_bg,
                         arrowcolor=C["fg_dim"],
                         darkcolor=sb_fg,
                         lightcolor=sb_fg)
        style.configure("Horizontal.TScrollbar",
                         background=sb_bg,
                         troughcolor=sb_bg,
                         bordercolor=sb_bg,
                         arrowcolor=C["fg_dim"],
                         darkcolor=sb_fg,
                         lightcolor=sb_fg)

    # ── UI BUILD ────────────────────────────
    def _build_ui(self):
        C = THEMES.get(self.theme_name, THEMES["light"])
        self.configure(bg=C["bg_main"])
        self.minsize(820, 500)
        self.geometry("1080x640")
        # Icon from .ico file
        try:
            icon_path = Path(__file__).parent / "icons" / "psl-ico.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
            else:
                # Fallback to inline base64 icon
                icon_data = (
                    "R0lGODlhIAAgAPcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0NDQ4ODg8P"
                    "DxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8fHyAgICEhISIiIiMj"
                    "IyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDExMTIyMjMzMzQ0NDU1NTY2Njc3"
                    "Nzg4ODk5OTo6Ojs7Ozw8PD09PT4+Pj8/P0BAQEFBQUJCQkNDQ0REREVFRUZGRkdHR0hISElJSUpKSktL"
                    "S0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVVVVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9f"
                    "X2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdnZ2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNz"
                    "c3R0dHV1dXZ2dnd3d3h4eHl5eXp6ent7e3x8fH19fX5+fn9/f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeH"
                    "h4iIiImJiYqKiouLi4yMjI2NjY6Ojo+Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampub"
                    "m5ycnJ2dnZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq+v"
                "r7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8DAwMHBwcLCwsPD"
                "w8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9DQ0NHR0dLS0tPT09TU1NXV1dbW1tfX"
                "19jY2NnZ2dra2tvb29zc3N3d3d7e3t/f3+Dg4OHh4eLi4uPj4+Tk5OXl5ebm5ufn5+jo6Onp6erq6uvr"
                "6+zs7O3t7e7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf39/j4+Pn5+fr6+vv7+/z8/P39/f7+/v//"
                "/yH5BAEKAP8ALAAAAAAgACAAAAj+AP8JHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOK"
                "HEmypMmTKFOqXMmypcuXMGPKnEmzps2bOHPq3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qdOnUKNKnUq1qtWr"
                "WLNq3cq1q9evYMOKHUu2rNmzaNOqXcu2rdu3cOPKnUu3rt27ePPq3cu3r9+/gAMLHky4sOHDiBMrXsy4"
                "sePHkCNLnky5suXLmDNr3sy5s+fPoEOLHk26tOnTqFOrXs26tevXsGPLnk27tu3buHPr3s27t+/fwIML"
                "H068uPHjyJMrX868ufPn0KNLn069uvXr2LNr3869u/fv4MOLHz9OviAAADs="
                )
                icon_img = tk.PhotoImage(data=icon_data)
                self.iconphoto(True, icon_img)
        except Exception:
            pass

        # ── Menu bar ──
        self.menubar = tk.Menu(self, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                               activebackground=C["menu_abg"], activeforeground=C["menu_afg"],
                               relief="flat", borderwidth=0)
        self.config(menu=self.menubar)

        self.menu_file  = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                  activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menu_view  = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                  activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menu_tools = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                  activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menu_lang  = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                  activebackground=C["menu_abg"], activeforeground=C["menu_afg"])

        self.menubar.add_cascade(menu=self.menu_file,  label="File")
        self.menubar.add_cascade(menu=self.menu_view,  label="View")
        self.menu_groups = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                   activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_groups, label="Groups")
        self.menubar.add_cascade(menu=self.menu_tools, label="Tools")
        self.menu_sandbox = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                    activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_sandbox, label="Sandbox")
        self.menubar.add_command(label="🐛  Debugger", command=self._open_debugger)
        self.menubar.add_command(label="⚙  Settings", command=self._show_settings)
        self.menu_requirements = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                         activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_requirements, label="📦  Requirements")
        self.menu_git = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                               activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_git, label="Git")
        self.menu_plugins = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                   activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_plugins, label="Plugins")
        self.menu_history = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                   activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_history, label="History")
        self.menu_notifications = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                       activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_notifications, label="Notifications")
        self.menubar.add_cascade(menu=self.menu_lang,  label="Lang")
        self.menu_help  = tk.Menu(self.menubar, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                  activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        self.menubar.add_cascade(menu=self.menu_help, label="Help")

        # ── Toolbar ──
        self.toolbar = tk.Frame(self, bg=C["bg_panel"], pady=4)
        self.toolbar.pack(fill="x")

        self.btn_add_tb = self._tb_btn(self.toolbar, "➕", self._add_script)
        self.btn_scan_tb = self._tb_btn(self.toolbar, "🔍", self._open_scan_dialog)
        self.btn_run_tb  = self._tb_btn(self.toolbar, "▶", self._run_selected, accent=True)
        self.btn_preview = self._tb_btn(self.toolbar, "👁", self._toggle_preview_mode)
        # Tooltips assigned after _apply_lang so text can be updated; stored for later refresh
        self._tooltip_add     = Tooltip(self.btn_add_tb,  "", theme=C)
        self._tooltip_scan    = Tooltip(self.btn_scan_tb, "", theme=C)
        self._tooltip_run     = Tooltip(self.btn_run_tb,  "", theme=C)
        self._tooltip_preview = Tooltip(self.btn_preview, "", theme=C)

        tk.Frame(self.toolbar, bg=C["bg_sep"], width=1).pack(side="left", fill="y", padx=6)

        # Search
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *_: self._filter_scripts())
        self.entry_search = tk.Entry(self.toolbar, textvariable=self.var_search,
                                     bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                                     relief="flat", font=("Consolas", 10), width=28)
        self.entry_search.pack(side="left", ipady=4, padx=4)
        self.entry_search.bind("<FocusIn>",  self._search_focus_in)
        self.entry_search.bind("<FocusOut>", self._search_focus_out)

        tk.Frame(self.toolbar, bg=C["bg_sep"], width=1).pack(side="left", fill="y", padx=6)

        # Tag filter
        self.var_tag_filter = tk.StringVar()
        self.var_tag_filter.trace_add("write", lambda *_: self._filter_scripts())
        self.cb_tag_filter = ttk.Combobox(self.toolbar, textvariable=self.var_tag_filter,
                                           width=16, state="readonly",
                                           font=("Consolas", 9))
        self.cb_tag_filter.pack(side="left", ipady=2, padx=4)

        tk.Frame(self.toolbar, bg=C["bg_sep"], width=1).pack(side="left", fill="y", padx=6)
        self.btn_about_tb = self._tb_btn(self.toolbar, "ℹ", self._show_about, side="right")
        self._tooltip_about = Tooltip(self.btn_about_tb, "", theme=C)

        # ── Status bar ──
        self._statusbar_frm = tk.Frame(self, bg=C["bg_panel"])
        self._statusbar_frm.pack(side="bottom", fill="x")
        self.var_status = tk.StringVar(value="")
        self.statusbar = tk.Label(self._statusbar_frm, textvariable=self.var_status,
                                   bg=C["bg_panel"], fg=C["fg_green"],
                                   font=("Consolas", 8), anchor="w", padx=8)
        self.statusbar.pack(side="left", fill="x", expand=True)
        self.var_count = tk.StringVar(value="")
        self._lbl_count = tk.Label(self._statusbar_frm, textvariable=self.var_count,
                                    bg=C["bg_panel"], fg=C["fg_dim"],
                                    font=("Consolas", 8), anchor="e", padx=8)
        self._lbl_count.pack(side="right")

        # ── Main paned window ──
        self.paned = tk.PanedWindow(self, orient="horizontal",
                                    bg=C["bg_main"], sashwidth=4, sashrelief="flat")
        self.paned.pack(fill="both", expand=True)

        # ── Left: script list ──
        self.frm_left = tk.Frame(self.paned, bg=C["bg_main"])
        self.paned.add(self.frm_left, minsize=300)

        # ── Group filter bar (v1.2) ──
        self._frm_groups = tk.Frame(self.frm_left, bg=C["bg_panel"], pady=2)
        self._frm_groups.pack(fill="x")
        self._group_btns: list[tk.Button] = []
        self._rebuild_group_bar()

        # ── Advanced search button (v1.7) ──
        T = TRANSLATIONS[self.lang]
        self.btn_advanced_search = tk.Button(self._frm_groups, text=T["search_advanced"],
                                              command=self._show_advanced_search,
                                              bg=C["bg_btn"], fg=C["fg_main"],
                                              relief="flat", font=("Consolas", 8))
        self.btn_advanced_search.pack(side="right", padx=2)

        # ── Favorites filter button (v1.7) ──
        self.btn_favorites = tk.Button(self._frm_groups, text="⭐",
                                        command=self._toggle_favorites_filter,
                                        bg=C["bg_btn"], fg=C["fg_main"],
                                        relief="flat", font=("Consolas", 8))
        self.btn_favorites.pack(side="right", padx=2)
        self._favorites_filter = False

        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                         background=C["bg_main"], foreground=C["fg_main"],
                         fieldbackground=C["bg_main"],
                         rowheight=self.app_settings.get("tree_row_height", 22),
                         font=("Consolas", 9))
        style.configure("Treeview.Heading",
                         background=C["tree_heading_bg"], foreground=C["fg_accent"],
                         font=("Consolas", 9, "bold"), relief="flat")
        style.map("Treeview",
                  background=[("selected", C["sel_bg"])],
                  foreground=[("selected", C["sel_fg"])])

        frm_tree = self.frm_tree = tk.Frame(self.frm_left, bg=C["bg_main"])
        frm_tree.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frm_tree, columns=("icon", "name", "type", "runs", "avg", "last_rc", "path"),
                                  show="headings", selectmode="browse")
        self.tree.column("icon",    width=28,  stretch=False)
        self.tree.column("name",    width=160, stretch=False)
        self.tree.column("type",    width=90,  stretch=False)
        self.tree.column("runs",    width=46,  stretch=False, anchor="center")
        self.tree.column("avg",     width=52,  stretch=False, anchor="center")
        self.tree.column("last_rc", width=36,  stretch=False, anchor="center")
        self.tree.column("path",    width=240, stretch=False)

        vsb = ttk.Scrollbar(frm_tree, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        hsb = ttk.Scrollbar(frm_tree, orient="horizontal", command=self.tree.xview, style="Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._run_selected())
        self.tree.bind("<Button-3>", self._show_context_menu)
        # Manual reordering via drag & drop (only when default order/sort is active)
        self.tree.bind("<ButtonPress-1>", self._on_tree_drag_start, add="+")
        self.tree.bind("<B1-Motion>", self._on_tree_drag_motion, add="+")
        self.tree.bind("<ButtonRelease-1>", self._on_tree_drag_end, add="+")
        self._drag_iid = None

        # Action buttons
        frm_btns = tk.Frame(self.frm_left, bg=C["bg_panel"], pady=4)
        frm_btns.pack(fill="x")
        self.btn_run    = self._action_btn(frm_btns, "", self._run_selected,   accent=True)
        self.btn_run_group = self._action_btn(frm_btns, "", self._run_active_group)
        self.btn_stop   = self._action_btn(frm_btns, "⏹", self._stop_selected,  danger=True)
        self.btn_restart_proc = self._action_btn(frm_btns, "🔄", self._restart_selected)
        self.btn_remove = self._action_btn(frm_btns, "", self._remove_selected, danger=True)
        self.btn_opts   = self._action_btn(frm_btns, "", self._edit_options)

        # Hide/show panel button
        self.btn_toggle_panel = tk.Button(frm_btns, text="",
                                           bg=C["bg_panel"], fg="#000000",
                                           relief="flat", font=("Consolas", 13, "bold"),
                                           cursor="hand2",
                                           command=self._toggle_panel)
        self.btn_toggle_panel.pack(side="right", padx=4)

        # ── Code preview widget (hidden by default, overlays the tree) ──
        self.frm_preview = tk.Frame(self.frm_left, bg=C["bg_main"])
        # NOT packed yet – shown on demand

        frm_preview_hdr = tk.Frame(self.frm_preview, bg=C["bg_panel"])
        frm_preview_hdr.pack(fill="x")
        self.lbl_preview_title = tk.Label(
            frm_preview_hdr, text="", bg=C["bg_panel"], fg=C["fg_accent"],
            font=("Consolas", 9, "bold"), pady=4, padx=6, anchor="w")
        self.lbl_preview_title.pack(side="left", fill="x", expand=True)

        self.code_text = scrolledtext.ScrolledText(
            self.frm_preview,
            bg=C["bg_log"], fg=C["fg_main"],
            font=("Consolas", 9),
            relief="flat", state="disabled",
            wrap="none")
        self.code_text.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # ── Right: side panel ──
        self.frm_right = tk.Frame(self.paned, bg=C["bg_panel"], width=280)
        self.paned.add(self.frm_right, minsize=200)

        # Panel title
        self.lbl_panel_title = tk.Label(self.frm_right, text="",
                                         bg=C["bg_panel"], fg=C["fg_accent"],
                                         font=("Consolas", 10, "bold"), pady=6)
        self.lbl_panel_title.pack(fill="x", padx=8)

        tk.Frame(self.frm_right, bg=C["bg_sep"], height=1).pack(fill="x", padx=8)

        # Metadata grid
        self.meta_frm = tk.Frame(self.frm_right, bg=C["bg_panel"])
        self.meta_frm.pack(fill="x", padx=8, pady=6)
        self.meta_labels = {}
        meta_keys = ["panel_meta_name", "panel_meta_type", "panel_meta_path",
                     "panel_meta_size", "panel_meta_modified",
                     "panel_meta_author", "panel_meta_desc", "panel_meta_version",
                     "panel_meta_tags", "panel_meta_note"]
        for i, k in enumerate(meta_keys):
            lbl_k = tk.Label(self.meta_frm, text="", bg=C["bg_panel"], fg=C["fg_dim"],
                             font=("Consolas", 8), anchor="w")
            lbl_k.grid(row=i, column=0, sticky="w", pady=1)
            lbl_v = tk.Label(self.meta_frm, text="", bg=C["bg_panel"], fg=C["fg_main"],
                             font=("Consolas", 8), anchor="w", wraplength=200, justify="left")
            lbl_v.grid(row=i, column=1, sticky="w", pady=1, padx=(4, 0))
            self.meta_labels[k] = (lbl_k, lbl_v)
        self.meta_frm.columnconfigure(1, weight=1)

        # Open in Explorer button (side panel)
        self.btn_panel_explorer = tk.Button(
            self.frm_right, text="",
            bg=C["bg_btn"], fg=C["fg_link"],
            relief="flat", font=("Consolas", 8), padx=8, pady=3,
            cursor="hand2", borderwidth=0,
            command=self._open_in_explorer)
        self.btn_panel_explorer.pack(anchor="w", padx=8, pady=(4, 0))

        # Log
        tk.Frame(self.frm_right, bg=C["bg_sep"], height=1).pack(fill="x", padx=8, pady=(6,0))
        frm_log_hdr = tk.Frame(self.frm_right, bg=C["bg_panel"])
        frm_log_hdr.pack(fill="x", padx=8)
        self.lbl_log_title = tk.Label(frm_log_hdr, text="",
                                       bg=C["bg_panel"], fg=C["fg_accent"],
                                       font=("Consolas", 9, "bold"), pady=4)
        self.lbl_log_title.pack(side="left")
        # Copy-to-clipboard button
        self.btn_log_copy = tk.Button(frm_log_hdr, text="📋",
                                       bg=C["bg_panel"], fg=C["fg_dim"],
                                       relief="flat", font=("Segoe UI Emoji", 9),
                                       padx=4, pady=2, cursor="hand2", borderwidth=0,
                                       command=self._copy_log)
        self.btn_log_copy.pack(side="right")
        self.btn_log_export = tk.Button(frm_log_hdr, text="💾",
                                         bg=C["bg_panel"], fg=C["fg_dim"],
                                         relief="flat", font=("Segoe UI Emoji", 9),
                                         padx=4, pady=2, cursor="hand2", borderwidth=0,
                                         command=self._export_log)
        self.btn_log_export.pack(side="right")
        # Dock/Undock button
        self.btn_log_undock = tk.Button(frm_log_hdr, text="🔓",
                                        bg=C["bg_panel"], fg=C["fg_dim"],
                                        relief="flat", font=("Segoe UI Emoji", 9),
                                        padx=4, pady=2, cursor="hand2", borderwidth=0,
                                        command=self._toggle_log_window)
        self.btn_log_undock.pack(side="right")

        # Log widget — manual Text + ttk.Scrollbar for custom styling
        log_frame = tk.Frame(self.frm_right, bg=C["bg_log"])
        log_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        self.log_text = tk.Text(
            log_frame,
            bg=C["bg_log"], fg=C["log_stdout"],
            font=("Consolas", 9),
            relief="flat", state="disabled",
            wrap="none",          # horizontal scroll instead of word-wrap
            height=10,
            padx=6, pady=4,
            cursor="xterm",
            selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
        )
        
        log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview, style="Vertical.TScrollbar")
        log_hsb = ttk.Scrollbar(log_frame, orient="horizontal", command=self.log_text.xview, style="Horizontal.TScrollbar")
        self.log_text.configure(yscrollcommand=log_vsb.set, xscrollcommand=log_hsb.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_vsb.pack(side="right", fill="y")
        log_hsb.pack(side="bottom", fill="x")
        # Configure syntax-coloring tags (colours applied per-line in _process_log_queue)
        self._apply_log_tags()

        # NOTE: tree rows are intentionally NOT inserted here. Population
        # happens lazily after the window is shown (see _finish_startup),
        # so the window paints instantly even with a large script list.

    def _tb_btn(self, parent, text, cmd, side="left", accent=False):
        C = THEMES.get(self.theme_name, THEMES["light"])
        cfg = dict(text=text, command=cmd, relief="flat",
                   font=("Segoe UI Emoji", 13), padx=6, pady=2,
                   cursor="hand2", borderwidth=0)
        if accent:
            cfg.update(bg=C["btn_run_bg"], fg=C["btn_run_fg"], activebackground=C["btn_run_active"])
        else:
            cfg.update(bg=C["bg_panel"], fg=C["fg_main"], activebackground=C["bg_btn"])
        b = tk.Button(parent, **cfg)
        b.pack(side=side, padx=2)
        return b

    def _action_btn(self, parent, text, cmd, accent=False, danger=False):
        C = THEMES.get(self.theme_name, THEMES["light"])
        if accent:
            bg, fg = C["btn_run_bg"], C["btn_run_fg"]
        elif danger:
            bg, fg = C["btn_del_bg"], C["btn_del_fg"]
        else:
            bg, fg = C["bg_btn"], C["fg_main"]
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=fg, relief="flat",
                      font=("Consolas", 9, "bold"), padx=10, pady=4,
                      cursor="hand2", borderwidth=0)
        b.pack(side="left", padx=4)
        return b

    # ── LANGUAGE ────────────────────────────
    def _apply_lang(self):
        T = TRANSLATIONS[self.lang]
        self.title(T["title"])
        # Menus (fixed order: File=0, View=1, Groups=2, Tools=3, Sandbox=4, Debugger=5, Settings=6, Requirements=7, Lang=8, Help=9)
        self.menubar.entryconfig(0, label=T["menu_file"])
        self.menubar.entryconfig(1, label=T["menu_view"])
        self.menubar.entryconfig(2, label=T["menu_groups"])
        self.menubar.entryconfig(3, label=T["menu_tools"])
        self.menubar.entryconfig(4, label=T["menu_sandbox"])
        self.menubar.entryconfig(5, label="🐛  Debugger")
        self.menubar.entryconfig(6, label=T.get("menu_settings", "⚙  Settings"))
        self.menubar.entryconfig(7, label=T.get("menu_requirements", "📦  Requirements"))
        self.menubar.entryconfig(8, label=T.get("git_menu", "Git"))
        self.menubar.entryconfig(9, label=T.get("plugins_menu", "Plugins"))
        self.menubar.entryconfig(10, label=T.get("history_menu", "History"))
        self.menubar.entryconfig(11, label=T.get("notifications_menu", "Notifications"))
        self.menubar.entryconfig(12, label=T["menu_lang"])
        self.menubar.entryconfig(13, label=T.get("menu_help", "Pomoc"))

        self.menu_file.delete(0, "end")
        self.menu_file.add_command(label=T["menu_add_script"],  command=self._add_script)
        self.menu_file.add_command(label=T.get("menu_add_from_template", "New from template…"), command=self._create_from_template)
        self.menu_file.add_command(label=T["menu_scan_dir"],    command=self._open_scan_dialog)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=T.get("config_export", "Export configuration…"), command=self._export_config)
        self.menu_file.add_command(label=T.get("config_import", "Import configuration…"), command=self._import_config)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=T["menu_exit"],        command=self._on_close)

        self.menu_view.delete(0, "end")
        self.menu_view.add_command(label=T["menu_toggle_panel"], command=self._toggle_panel)
        self.menu_view.add_command(label=T.get("menu_kiosk", "🎛  Kiosk mode"),
                                   command=self._enter_kiosk)
        self.menu_view.add_separator()
        self.menu_tools.delete(0, "end")
        self.menu_tools.add_command(label=T["menu_ps_policy"],  command=self._show_ps_policy)
        self.menu_tools.add_command(label=T["menu_clear_log"],  command=self._clear_log)
        self.menu_tools.add_command(label=T.get("menu_export_log", "Export log to file…"), command=self._export_log)
        self.menu_tools.add_command(label=T.get("global_env_vars", "Global environment variables"), command=self._edit_global_env_vars)
        self.menu_tools.add_separator()
        self.menu_tools.add_command(label=T["menu_export"],     command=self._export_list)
        self.menu_tools.add_command(label=T["menu_import"],     command=self._import_list)
        self.menu_tools.add_command(label=T.get("menu_export_csv","Eksportuj CSV…"),
                                    command=lambda: self._export_list_format("csv"))
        self.menu_tools.add_command(label=T.get("menu_import_csv","Importuj CSV…"),
                                    command=lambda: self._import_list_format("csv"))
        self.menu_tools.add_separator()
        self.menu_tools.add_command(label=T.get("menu_export_full","Eksportuj pełny backup…"),
                                    command=self._export_full_config)
        self.menu_tools.add_command(label=T.get("menu_import_full","Importuj pełny backup…"),
                                    command=self._import_full_config)
        self.menu_tools.add_separator()
        self.menu_tools.add_command(label=T["menu_run_history"],command=self._show_history)
        self.menu_tools.add_command(label=T.get("menu_dashboard","📊  Statistics dashboard"),
                                    command=self._show_dashboard)
        self.menu_tools.add_separator()
        self.menu_tools.add_command(label=T.get("batch_run_title","Run selected scripts"),
                                    command=self._show_batch_run_dialog)
        self.menu_tools.add_separator()
        self.menu_tools.add_command(label=T.get("menu_queue","Run queue"),    command=self._show_queue_dialog)
        self.menu_tools.add_command(label=T.get("menu_scheduler","Scheduler"),command=self._show_scheduler_dialog)
        self.menu_tools.add_separator()
        self.menu_tools.add_command(label=T["menu_validate_all"],command=self._validate_all_scripts)

        # Sandbox menu
        self.menu_sandbox.delete(0, "end")
        if _SANDBOX_AVAILABLE:
            self.menu_sandbox.add_command(
                label=T.get("menu_sandbox_open", "🧪  Open Sandbox"),
                command=self._open_sandbox
            )
            self.menu_sandbox.add_separator()
            self.menu_sandbox.add_command(
                label=T.get("menu_sandbox_runners", "📋  Available interpreters"),
                command=self._sandbox_show_runners
            )
        else:
            self.menu_sandbox.add_command(
                label=T.get("menu_sandbox_unavail", "⚠  sandbox.py not available"),
                state="disabled"
            )

        # Groups menu
        self.menu_groups.delete(0, "end")
        self.menu_groups.add_command(label=T["menu_group_new"],    command=self._new_group)
        self.menu_groups.add_command(label=T["menu_group_manage"], command=self._manage_groups)

        # Requirements menu
        self.menu_requirements.delete(0, "end")
        self.menu_requirements.add_command(
            label=T.get("menu_req_install", "📂  Install from file…"),
            command=self._install_requirements
        )

        self.menu_lang.delete(0, "end")
        self.menu_lang.add_command(label=T["menu_lang_pl"],     command=lambda: self._set_lang("pl"))
        self.menu_lang.add_command(label=T["menu_lang_en"],     command=lambda: self._set_lang("en"))

        self.menu_git.delete(0, "end")
        self.menu_git.add_command(label=T.get("git_init", "Initialize repository"), command=self._git_init)
        self.menu_git.add_command(label=T.get("git_status", "Status"), command=self._git_status)
        self.menu_git.add_command(label=T.get("git_add", "Add to index"), command=self._git_add)
        self.menu_git.add_command(label=T.get("git_commit", "Commit changes"), command=self._git_commit)
        self.menu_git.add_separator()
        self.menu_git.add_command(label=T.get("git_log", "History"), command=self._git_log)
        self.menu_git.add_command(label=T.get("git_diff", "Show diff"), command=self._git_diff)
        self.menu_git.add_command(label=T.get("git_checkout", "Checkout version"), command=self._git_checkout)

        self.menu_plugins.delete(0, "end")
        self.menu_plugins.add_command(label=T.get("plugins_load", "Load plugin"), command=self._load_plugin)
        self.menu_plugins.add_command(label=T.get("plugins_list", "Plugin list"), command=self._show_plugins)
        self.menu_plugins.add_command(label=T.get("plugins_folder", "Plugins folder"), command=self._open_plugins_folder)

        self.menu_history.delete(0, "end")
        self.menu_history.add_command(label=T.get("history_title", "Run History"), command=self._show_history)
        self.menu_history.add_command(label=T.get("history_clear", "Clear history"), command=self._clear_history)

        self.menu_notifications.delete(0, "end")
        self.var_notifications_enabled = tk.BooleanVar(value=self.app_settings.get("notifications_enabled", False))
        self.menu_notifications.add_checkbutton(label=T.get("notifications_enable", "Enable system notifications"),
                                               variable=self.var_notifications_enabled,
                                               command=self._toggle_notifications)
        self.menu_notifications.add_separator()
        if _ANSI_AVAILABLE:
            self.var_ansi_colors_enabled = tk.BooleanVar(value=self.app_settings.get("ansi_colors_enabled", True))
            self.menu_notifications.add_checkbutton(label=T.get("ansi_colors_enable", "Enable log colors"),
                                                   variable=self.var_ansi_colors_enabled,
                                                   command=self._toggle_ansi_colors)
        self.menu_notifications.add_separator()
        if _SANDBOX_AVAILABLE:
            self.menu_notifications.add_command(label="Open Sandbox", command=self._open_sandbox)
        self.menu_notifications.add_separator()
        if _DEBUGGER_AVAILABLE:
            self.var_debugger_enabled = tk.BooleanVar(value=self._debugger_enabled)
            self.menu_notifications.add_checkbutton(label="Enable Debugger",
                                                   variable=self.var_debugger_enabled,
                                                   command=self._toggle_debugger)
            self.menu_notifications.add_command(label="Start Profiling", command=self._start_profiling)
            self.menu_notifications.add_command(label="Stop Profiling", command=self._stop_profiling)
        self.menu_notifications.add_separator()
        self.menu_notifications.add_command(label="Check Dependencies", command=self._check_dependencies)
        self.menu_notifications.add_separator()
        if _SCRIPT_RUNNER_AVAILABLE:
            self.menu_notifications.add_command(label="Script Templates", command=self._show_script_templates)
            self.menu_notifications.add_command(label="Execution History", command=self._show_execution_history)
            self.menu_notifications.add_command(label="Available Interpreters", command=self._show_interpreters_info)
            self.menu_notifications.add_separator()
            self.menu_notifications.add_command(label="Script Validator", command=self._show_script_validator)
            self.menu_notifications.add_command(label="Backup Manager", command=self._show_backup_manager)
            self.menu_notifications.add_command(label="Task Scheduler", command=self._show_task_scheduler)
        self.menu_notifications.add_separator()
        self.menu_notifications.add_command(label="Advanced Search", command=self._show_advanced_search)
        self.menu_notifications.add_command(label="Tag Manager", command=self._show_tag_manager)

        self.menu_help.delete(0, "end")
        self.menu_help.add_command(label=T.get("menu_help_about", "ℹ  O programie"),
                                   command=self._show_about)
        self.menu_help.add_command(label=T.get("menu_help_shortcuts", "⌨  Skróty klawiszowe"),
                                   command=self._show_shortcuts)
        self.menu_help.add_command(label=T.get("menu_help_features", "✨  Funkcje"),
                                   command=self._show_features)
        self.menu_help.add_command(label=T.get("menu_help_description", "📄  Opis programu"),
                                   command=self._show_description)

        # Treeview headings
        self.tree.heading("icon", text="")
        self.tree.heading("name", text=T["col_name"],
                          command=lambda: self._sort_by("name"))
        self.tree.heading("type", text=T["col_type"],
                          command=lambda: self._sort_by("type"))
        self.tree.heading("path", text=T["col_path"],
                          command=lambda: self._sort_by("path"))
        self.tree.heading("runs",    text=T.get("col_runs",    "Runs"))
        self.tree.heading("avg",     text=T.get("col_avg",     "Avg"))
        self.tree.heading("last_rc", text=T.get("col_last_rc", "RC"))

        # Buttons
        self.btn_run.config(text=T["btn_run"])
        self.btn_run_group.config(text=T.get("btn_run_all_group", "▶▶ Group"))
        self.btn_opts.config(text=T["btn_edit_opts"])
        self.btn_stop.config(text=T.get("btn_stop", "⏹  Stop"))
        self.btn_restart_proc.config(text=T.get("btn_restart", "🔄  Restart"))
        self.btn_remove.config(text=T["btn_remove"])
        self.btn_toggle_panel.config(
            text=T["btn_hide_panel"] if self.panel_visible else T["btn_show_panel"])

        # Entry placeholder – zaktualizuj tylko gdy pole jest puste lub zawiera stary placeholder
        old_val = self.entry_search.get()
        old_T = None
        for lng in TRANSLATIONS:
            if old_val == TRANSLATIONS[lng].get("search_placeholder", ""):
                old_T = lng
                break
        if not old_val or old_T is not None:
            C = THEMES.get(self.theme_name, THEMES["light"])
            self.entry_search.delete(0, "end")
            self.entry_search.insert(0, T["search_placeholder"])
            self.entry_search.config(fg=C["placeholder_fg"])

        # Side panel labels
        self.lbl_panel_title.config(text=T["panel_title"])
        self.lbl_log_title.config(text=T["log_title"])
        meta_keys = ["panel_meta_name", "panel_meta_type", "panel_meta_path",
                     "panel_meta_size", "panel_meta_modified",
                     "panel_meta_author", "panel_meta_desc", "panel_meta_version",
                     "panel_meta_tags", "panel_meta_note"]
        for k in meta_keys:
            if k in self.meta_labels:
                self.meta_labels[k][0].config(text=T[k])
                self.meta_labels[k][1].config(text=T["panel_meta_none"])

        # Rebuild tag filter
        self._rebuild_tag_filter()

        self._set_status(T["status_ready"], autoclear=0)

        # Update tooltips
        self._tooltip_add.text  = T["tooltip_add"]
        self._tooltip_scan.text = T["tooltip_scan"]
        self._tooltip_run.text  = T["tooltip_run"]
        self._tooltip_about.text = T["tooltip_about"]
        self._tooltip_preview.text = T.get("btn_preview", "👁  Preview")

        # Update panel explorer button
        self.btn_panel_explorer.config(text=T["btn_open_explorer"])

        # Rebuild group bar labels
        self._rebuild_group_bar()

        # Restore last-run status if available
        if self._last_run_info:
            self._set_status(T["status_last_run"].format(**self._last_run_info), autoclear=0)

    def _set_theme(self, name: str):
        self.theme_name = name
        self._apply_theme(name)
        self._schedule_save()

    def _apply_theme(self, name: str):
        C = THEMES.get(name, THEMES["light"])

        # Reapply global scrollbar styling for theme change
        self._apply_global_scrollbar_style()

        # ── Root / toolbar / statusbar ──
        self.configure(bg=C["bg_main"])
        self.toolbar.configure(bg=C["bg_panel"])
        self._statusbar_frm.configure(bg=C["bg_panel"])
        self.statusbar.configure(bg=C["bg_panel"], fg=C["fg_green"])
        self._lbl_count.configure(bg=C["bg_panel"], fg=C["fg_dim"])

        # ── Toolbar buttons ──
        for btn in (self.btn_add_tb, self.btn_scan_tb, self.btn_preview):
            btn.configure(bg=C["bg_panel"], fg=C["fg_main"], activebackground=C["bg_btn"])
        self.btn_run_tb.configure(bg=C["btn_run_bg"], fg=C["btn_run_fg"],
                                  activebackground=C["btn_run_active"])
        self.btn_about_tb.configure(bg=C["bg_panel"], fg=C["fg_main"], activebackground=C["bg_btn"])

        # ── Search entry ──
        self.entry_search.configure(bg=C["bg_entry"], fg=C["fg_main"],
                                    insertbackground=C["insert_fg"])

        # ── Separators in toolbar (Frame width=1) ──
        for w in self.toolbar.winfo_children():
            if isinstance(w, tk.Frame):
                w.configure(bg=C["bg_sep"])

        # ── Paned / frames ──
        self.paned.configure(bg=C["bg_main"])
        self.frm_left.configure(bg=C["bg_main"])
        self.frm_right.configure(bg=C["bg_panel"])

        # ── Treeview style ──
        style = ttk.Style()
        style.configure("Treeview",
                         background=C["bg_main"], foreground=C["fg_main"],
                         fieldbackground=C["bg_main"],
                         rowheight=self.app_settings.get("tree_row_height", 22),
                         font=("Consolas", 9))
        style.configure("Treeview.Heading",
                         background=C["tree_heading_bg"], foreground=C["fg_accent"],
                         font=("Consolas", 9, "bold"), relief="flat")
        style.map("Treeview",
                  background=[("selected", C["sel_bg"])],
                  foreground=[("selected", C["sel_fg"])])
        self.tree.tag_configure("even", background=C["tree_even"])
        self.tree.tag_configure("odd",  background=C["tree_odd"])

        # Action buttons frame bg
        for w in self.frm_left.winfo_children():
            if isinstance(w, tk.Frame):
                w.configure(bg=C["bg_panel"])

        # Action buttons
        self.btn_run.configure(bg=C["btn_run_bg"], fg=C["btn_run_fg"])
        self.btn_run_group.configure(bg=C["bg_btn"], fg=C["fg_main"])
        self.btn_opts.configure(bg=C["bg_btn"], fg=C["fg_main"])
        self.btn_stop.configure(bg=C["btn_del_bg"], fg=C["btn_del_fg"])
        self.btn_restart_proc.configure(bg=C["bg_btn"], fg=C["fg_main"])
        self.btn_remove.configure(bg=C["btn_del_bg"], fg=C["btn_del_fg"])
        self.btn_toggle_panel.configure(
            bg=C["bg_panel"],
            fg="#000000")

        # ── Right panel widgets ──
        self.lbl_panel_title.configure(bg=C["bg_panel"], fg=C["fg_accent"])
        self.lbl_log_title.configure(bg=C["bg_panel"], fg=C["fg_accent"])
        self.btn_panel_explorer.configure(bg=C["bg_btn"], fg=C["fg_link"])
        self.btn_log_export.configure(bg=C["bg_panel"], fg=C["fg_dim"])
        self.btn_log_copy.configure(bg=C["bg_panel"], fg=C["fg_dim"])
        self.log_text.configure(
            bg=C["bg_log"], fg=C["log_stdout"],
            selectbackground=C["sel_bg"], selectforeground=C["sel_fg"])
        self._apply_log_tags()   # re-apply tag colours for new theme

        # ── Code preview widgets ──
        self.frm_preview.configure(bg=C["bg_main"])
        self.lbl_preview_title.configure(bg=C["bg_panel"], fg=C["fg_accent"])
        self.code_text.configure(bg=C["bg_log"], fg=C["fg_main"])

        # Separators in frm_right
        for w in self.frm_right.winfo_children():
            if isinstance(w, tk.Frame):
                w.configure(bg=C["bg_sep"])

        # Meta frame
        self.meta_frm.configure(bg=C["bg_panel"])
        for _k, (lbl_k, lbl_v) in self.meta_labels.items():
            lbl_k.configure(bg=C["bg_panel"], fg=C["fg_dim"])
            lbl_v.configure(bg=C["bg_panel"], fg=C["fg_main"])

        # ── Menubar ──
        self.menubar.configure(bg=C["menubar_bg"], fg=C["menubar_fg"],
                               activebackground=C["menu_abg"], activeforeground=C["menu_afg"])
        for m in (self.menu_file, self.menu_view,
                  self.menu_tools, self.menu_sandbox, self.menu_lang, self.menu_help):
            m.configure(bg=C["menubar_bg"], fg=C["menubar_fg"],
                        activebackground=C["menu_abg"], activeforeground=C["menu_afg"])

        # ── Tooltips ──
        for tt in (self._tooltip_add, self._tooltip_scan, self._tooltip_run,
                   self._tooltip_about):
            tt.theme = C

        # ── Search placeholder color ──
        T = TRANSLATIONS[self.lang]
        if self.entry_search.get() == T["search_placeholder"]:
            self.entry_search.configure(fg=C["placeholder_fg"])

        # Group bar
        self._frm_groups.configure(bg=C["bg_panel"])
        self._rebuild_group_bar()

        # Force treeview redraw with updated stripe colors
        self._refresh_tree()

    def _set_lang(self, lang):
        self.lang = lang
        self._apply_lang()
        self._save_config()  # zmiana języka → natychmiastowy zapis

    def _search_focus_in(self, e):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        if self.entry_search.get() == T["search_placeholder"]:
            self.entry_search.delete(0, "end")
            self.entry_search.config(fg=C["fg_main"])

    def _search_focus_out(self, e):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        if not self.entry_search.get():
            self.entry_search.insert(0, T["search_placeholder"])
            self.entry_search.config(fg=C["placeholder_fg"])

    # ── TREE ────────────────────────────────
    def _refresh_tree(self):
        if getattr(self, "_refreshing_tree", False):
            return
        self._refreshing_tree = True
        try:
            self._refresh_tree_impl()
        finally:
            self._refreshing_tree = False

    def _refresh_tree_impl(self):
        self.tree.delete(*self.tree.get_children())
        T = TRANSLATIONS[self.lang]
        q = self.var_search.get().lower()
        if q == T["search_placeholder"].lower():
            q = ""

        # Parse advanced search filters
        filters = {
            "text": "",
            "type": "",
            "group": "",
            "tag": "",
            "status": ""
        }
        
        if q:
            parts = q.split()
            for part in parts:
                if part.startswith("type:"):
                    filters["type"] = part[5:].lower()
                elif part.startswith("group:"):
                    filters["group"] = part[6:].lower()
                elif part.startswith("tag:"):
                    filters["tag"] = part[4:].lower()
                elif part.startswith("status:"):
                    filters["status"] = part[7:].lower()
                else:
                    filters["text"] += " " + part
            filters["text"] = filters["text"].strip()

        # Build list of (display_values, original_index)
        rows = []
        for i, s in enumerate(self.scripts):
            # Favorites filter (v1.7)
            if getattr(self, "_favorites_filter", False):
                if not s.get("favorite", False):
                    continue
            # Group filter
            if self._active_group:
                if self._active_group == "__ungrouped__":
                    if s.get("group", ""):
                        continue
                else:
                    if s.get("group", "") != self._active_group:
                        continue
            
            # Advanced search filters
            if filters["text"]:
                if filters["text"] not in s.get("name", "").lower() and filters["text"] not in s.get("path", "").lower():
                    continue
            
            if filters["type"]:
                ext = Path(s.get("path", "")).suffix.lower()
                if filters["type"] not in ext:
                    continue
            
            if filters["group"]:
                if filters["group"] not in s.get("group", "").lower():
                    continue
            
            if filters["tag"]:
                script_tags = [t.strip().lower() for t in s.get("tags", "").split(",") if t.strip()]
                if filters["tag"] not in script_tags:
                    continue
            
            if filters["status"]:
                last_rc = s.get("last_rc")
                if filters["status"] == "success" and last_rc != 0:
                    continue
                elif filters["status"] == "failed" and last_rc == 0:
                    continue
                elif filters["status"] == "never" and last_rc is not None:
                    continue
            
            # Tag filter (from dropdown)
            active_tag = self.var_tag_filter.get()
            T_tmp = TRANSLATIONS[self.lang]
            if active_tag and active_tag != T_tmp.get("filter_tag_all", ""):
                script_tags = [t.strip() for t in s.get("tags", "").split(",") if t.strip()]
                if active_tag not in script_tags:
                    continue
            ext  = Path(s.get("path", "")).suffix.lower()
            info = SCRIPT_TYPES.get(ext, {"label": ext.lstrip(".").upper(), "icon": "default"})
            icon_name = "pinned" if s.get("pinned") else info["icon"]
            # stat columns
            run_count = s.get("run_count", 0)
            run_times = s.get("run_times", [])
            avg_str = f"{sum(run_times)/len(run_times):.1f}" if run_times else "—"
            last_rc = s.get("last_rc")
            rc_str = ("✓" if last_rc == 0 else f"✘{last_rc}") if last_rc is not None else "—"
            rows.append((icon_name, s.get("name", ""), info["label"], s.get("path", ""),
                         str(run_count) if run_count else "—", avg_str, rc_str,
                         i, s.get("pinned", False)))

        # Pinned entries always first, then sort
        col_idx = {"name": 1, "type": 2, "path": 3}.get(self._sort_col)
        if col_idx is not None:
            rows.sort(key=lambda r: (not r[8], r[col_idx].lower()), reverse=self._sort_reverse)
            if self._sort_reverse:
                pinned_rows = [r for r in rows if r[8]]
                other_rows  = [r for r in rows if not r[8]]
                rows = pinned_rows + other_rows
        else:
            rows.sort(key=lambda r: (not r[8], 0))

        for i, row in enumerate(rows):
            tag = "odd" if i % 2 else "even"
            icon_img = get_icon(row[0], size=(16, 16))
            self.tree.insert("", "end", iid=str(row[7]),
                             values=("", row[1], row[2], row[4], row[5], row[6], row[3]),
                             image=icon_img,
                             tags=(tag,))
        # Apply stripe colors
        C = THEMES.get(self.theme_name, THEMES["light"])
        self.tree.tag_configure("even", background=C["tree_even"])
        self.tree.tag_configure("odd",  background=C["tree_odd"])

        # Update sort indicator on headings
        col_labels = {"name": T["col_name"], "type": T["col_type"], "path": T["col_path"]}
        for col, base_lbl in col_labels.items():
            if col == self._sort_col:
                arrow = " ▲" if not self._sort_reverse else " ▼"
                self.tree.heading(col, text=base_lbl + arrow)
            else:
                self.tree.heading(col, text=base_lbl)

        # Update counter
        total   = len(self.scripts)
        visible = len(rows)
        self.var_count.set(T["status_count"].format(total=total, visible=visible))

        # Rebuild tag filter after tree is fully populated (avoids reentrant _refresh_tree)
        self._rebuild_tag_filter()

    def _reorder_allowed(self) -> bool:
        """Manual drag reordering is only safe when the tree shows
        self.scripts in its natural (unsorted/unfiltered) order, i.e. no
        column sort, no group filter, no text/tag filter active."""
        if self._sort_col is not None:
            return False
        if self._active_group:
            return False
        T = TRANSLATIONS[self.lang]
        q = self.var_search.get().lower()
        if q and q != T["search_placeholder"].lower():
            return False
        active_tag = self.var_tag_filter.get()
        if active_tag and active_tag != T.get("filter_tag_all", ""):
            return False
        # Pinned items are always shown first, so reordering would be
        # misleading unless no items are pinned.
        if any(s.get("pinned") for s in self.scripts):
            return False
        return True

    def _on_tree_drag_start(self, event):
        self._drag_iid = None
        if not self._reorder_allowed():
            return
        iid = self.tree.identify_row(event.y)
        if iid:
            self._drag_iid = iid
            self.tree.config(cursor="fleur")

    def _on_tree_drag_motion(self, event):
        if not self._drag_iid:
            return
        target = self.tree.identify_row(event.y)
        if not target or target == self._drag_iid:
            return
        # Visually move the row to follow the cursor
        target_index = self.tree.index(target)
        self.tree.move(self._drag_iid, "", target_index)

    def _on_tree_drag_end(self, event):
        self.tree.config(cursor="")
        if not self._drag_iid:
            return
        dragged_iid = self._drag_iid
        self._drag_iid = None

        # Rebuild self.scripts order based on the new tree order
        new_order_indices = []
        for iid in self.tree.get_children(""):
            try:
                new_order_indices.append(int(iid))
            except ValueError:
                # tree order/content changed mid-drag; abort safely
                self._refresh_tree()
                return

        if len(new_order_indices) != len(self.scripts):
            self._refresh_tree()
            return

        self.scripts = [self.scripts[i] for i in new_order_indices]
        self._schedule_save()
        self._refresh_tree()

        # Reselect the dragged item at its new position
        try:
            new_idx = new_order_indices.index(int(dragged_iid))
            self.tree.selection_set(str(new_idx))
            self.tree.see(str(new_idx))
        except Exception:
            pass

    def _filter_scripts(self):
        self._refresh_tree()

    def _rebuild_tag_filter(self):
        """Rebuild the tag filter combobox from all tags in scripts."""
        if getattr(self, "_rebuilding_tags", False):
            return
        self._rebuilding_tags = True
        try:
            T = TRANSLATIONS[self.lang]
            all_tags = set()
            for s in self.scripts:
                for t in s.get("tags", "").split(","):
                    t = t.strip()
                    if t:
                        all_tags.add(t)
            values = [T.get("filter_tag_all", "All tags")] + sorted(all_tags)
            self.cb_tag_filter.configure(values=values)
            if self.var_tag_filter.get() not in values:
                self.var_tag_filter.set(values[0])
        finally:
            self._rebuilding_tags = False

    def _sort_by(self, col: str):
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = False
        self._refresh_tree()

    # ── CONTEXT MENU ────────────────────────
    def _show_context_menu(self, event):
        T = TRANSLATIONS[self.lang]
        # Select the row under cursor first
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.tree.focus(row_id)
        C = THEMES.get(self.theme_name, THEMES["light"])
        menu = tk.Menu(self, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                       activebackground=C["menu_abg"], activeforeground=C["menu_afg"],
                       relief="flat", borderwidth=1)
        if row_id:
            idx = int(row_id)
            s = self.scripts[idx]
            ext = Path(s.get("path", "")).suffix.lower()
            menu.add_command(label=T["ctx_run"],           command=self._run_selected)
            menu.add_command(label=T.get("ctx_preview_run", "👁  Preview & run"),
                             command=self._preview_and_run)
            menu.add_command(label=T.get("ctx_dry_run", "🔬  Dry run"),
                             command=self._dry_run_selected)
            menu.add_command(label=T.get("ctx_run_sandbox", "🧪  Uruchom w Sandbox"),
                             command=self._run_in_sandbox,
                             state="normal" if _SANDBOX_AVAILABLE else "disabled")
            menu.add_command(label=T["ctx_options"],        command=self._edit_options)
            menu.add_command(label=T.get("ctx_preview", "👁  Code preview"),
                             command=self._toggle_preview_mode)
            menu.add_command(label=T.get("ctx_debugger", "🐛  Debugger"),
                             command=self._open_debugger)
            if ext == ".ps1":
                policy_menu = tk.Menu(menu, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                       activebackground=C["menu_abg"], activeforeground=C["menu_afg"],
                                       relief="flat", borderwidth=1)
                current = s.get("ps_exec_policy", "Bypass")
                for policy in ("Bypass", "RemoteSigned", "Unrestricted"):
                    mark = "✓ " if policy == current else "    "
                    policy_menu.add_command(
                        label=mark + policy,
                        command=lambda p=policy, i=idx: self._set_ps_policy(i, p))
                menu.add_cascade(label=T["ctx_ps_policy"], menu=policy_menu)
            menu.add_separator()
            # v1.2 additions
            menu.add_command(label=T["ctx_rename"],        command=self._rename_selected)
            menu.add_command(label=T["ctx_duplicate"],     command=self._duplicate_selected)
            # Profiles submenu
            profiles = s.get("profiles", [])
            if profiles:
                prof_menu = tk.Menu(menu, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                    activebackground=C["menu_abg"], activeforeground=C["menu_afg"],
                                    relief="flat")
                active_prof = s.get("active_profile", "")
                for prof in profiles:
                    mark = "✓ " if prof["name"] == active_prof else "    "
                    prof_menu.add_command(
                        label=mark + prof["name"],
                        command=lambda i=idx, pn=prof["name"]: self._activate_profile(i, pn))
                prof_menu.add_separator()
                prof_menu.add_command(label="— " + T.get("opts_profiles", "Profiles") + " —",
                                      command=lambda: self._edit_options(), state="disabled")
                menu.add_cascade(label=T.get("ctx_profiles", "🎛  Run profiles"), menu=prof_menu)
            # Pin / Unpin
            if s.get("pinned"):
                menu.add_command(label=T["ctx_unpin"], command=lambda i=idx: self._toggle_pin(i))
            else:
                menu.add_command(label=T["ctx_pin"],   command=lambda i=idx: self._toggle_pin(i))
            # Favorite / Unfavorite (v1.7)
            if s.get("favorite"):
                menu.add_command(label=T["favorite_remove"], command=lambda i=idx: self._toggle_favorite(i))
            else:
                menu.add_command(label=T["favorite_add"], command=lambda i=idx: self._toggle_favorite(i))
            # Move to group submenu
            if self._groups:
                grp_menu = tk.Menu(menu, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                                   activebackground=C["menu_abg"], activeforeground=C["menu_afg"],
                                   relief="flat")
                grp_menu.add_command(label=T["group_ungrouped"],
                                     command=lambda i=idx: self._move_to_group(i, ""))
                for g in self._groups:
                    grp_menu.add_command(label=g, command=lambda i=idx, grp=g: self._move_to_group(i, grp))
                menu.add_cascade(label=T["ctx_move_to_group"], menu=grp_menu)
            menu.add_separator()
            menu.add_command(label=T["ctx_open_explorer"],  command=self._open_in_explorer)
            menu.add_command(label=T["ctx_open_terminal"],  command=self._open_terminal_here)
            menu.add_command(label=T["ctx_copy_path"],      command=self._copy_path)
            menu.add_command(label=T["ctx_export_launcher"], command=self._export_launcher)
            menu.add_separator()
            menu.add_command(label=T["ctx_remove"],         command=self._remove_selected)
        else:
            menu.add_command(label=T["btn_add"],  command=self._add_script)
            menu.add_command(label=T["btn_scan"], command=self._open_scan_dialog)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _open_in_explorer(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        path = self.scripts[idx].get("path", "")
        if not path:
            return
        directory = os.path.dirname(path)
        if platform.system() == "Windows":
            # Select the file in Explorer
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-R", path])
        else:
            subprocess.Popen(["xdg-open", directory])

    def _open_terminal_here(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        path = s.get("path", "")
        if not path:
            return
        workdir = s.get("workdir", "") or os.path.dirname(path) or "."
        if not os.path.isdir(workdir):
            workdir = "."
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd.exe", "/K", f"cd /d \"{workdir}\""],
                                  creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Terminal", workdir])
            else:
                term = shutil.which("x-terminal-emulator") or shutil.which("gnome-terminal") \
                       or shutil.which("konsole") or shutil.which("xterm")
                if term and "gnome-terminal" in term:
                    subprocess.Popen([term, "--working-directory", workdir])
                elif term and "konsole" in term:
                    subprocess.Popen([term, "--workdir", workdir])
                elif term:
                    subprocess.Popen([term], cwd=workdir)
                else:
                    messagebox.showerror("", TRANSLATIONS[self.lang]["msg_tool_missing"] + " terminal")
        except Exception as e:
            messagebox.showerror("", str(e))

    def _copy_path(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        path = self.scripts[idx].get("path", "")
        self.clipboard_clear()
        self.clipboard_append(path)
        T = TRANSLATIONS[self.lang]
        self._set_status(f"✔ {T['ctx_copy_path']}: {path}")

    def _export_launcher(self):
        """Export a standalone .bat (Windows) or .sh (other) wrapper that
        runs the selected script with its saved options (interpreter,
        args, working dir, env vars, PS policy)."""
        T = TRANSLATIONS[self.lang]
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("", T["msg_no_selection"])
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        path = s.get("path", "")
        if not path:
            return
        ext = Path(path).suffix.lower()
        interp = s.get("interpreter", DEFAULT_INTERPRETERS.get(ext, ""))
        args = s.get("args", "")
        workdir = s.get("workdir", "")
        env_vars_str = s.get("env_vars", "").strip()
        is_windows = (platform.system() == "Windows")

        if is_windows:
            default_ext = ".bat"
            filetypes = [("Batch", "*.bat"), ("All files", "*.*")]
        else:
            default_ext = ".sh"
            filetypes = [("Shell script", "*.sh"), ("All files", "*.*")]

        out_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=Path(s.get("name", "launcher")).stem + default_ext,
            title=T["ctx_export_launcher"],
        )
        if not out_path:
            return

        try:
            if is_windows:
                lines = ["@echo off"]
                if env_vars_str:
                    for token in shlex.split(env_vars_str, posix=False):
                        if "=" in token:
                            k, v = token.split("=", 1)
                            lines.append(f'set "{k}={v}"')
                if workdir:
                    lines.append(f'cd /d "{workdir}"')
                if ext == ".ps1":
                    policy = s.get("ps_exec_policy", "Bypass")
                    ps_exe = interp or "powershell"
                    cmd_line = f'"{ps_exe}" -ExecutionPolicy {policy} -File "{path}"'
                elif ext in (".bat", ".cmd"):
                    cmd_line = f'call "{path}"'
                elif ext == ".vbs":
                    cmd_line = f'cscript //Nologo "{path}"'
                elif interp:
                    cmd_line = f'"{interp}" "{path}"'
                else:
                    cmd_line = f'"{path}"'
                if args:
                    cmd_line += " " + args
                lines.append(cmd_line)
                lines.append("pause")
                content = "\r\n".join(lines) + "\r\n"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                lines = ["#!/usr/bin/env bash"]
                if env_vars_str:
                    for token in shlex.split(env_vars_str, posix=True):
                        if "=" in token:
                            k, v = token.split("=", 1)
                            lines.append(f'export {k}="{v}"')
                if workdir:
                    lines.append(f'cd "{workdir}"')
                if interp:
                    cmd_line = f'"{interp}" "{path}"'
                else:
                    cmd_line = f'"{path}"'
                if args:
                    cmd_line += " " + args
                lines.append(cmd_line)
                content = "\n".join(lines) + "\n"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
                try:
                    st = os.stat(out_path)
                    os.chmod(out_path, st.st_mode | 0o111)
                except OSError:
                    pass

            self._set_status(f"✔ {T['launcher_export_saved']} {out_path}")
        except Exception as e:
            messagebox.showerror("", str(e))

    def _set_ps_policy(self, idx: int, policy: str):
        self.scripts[idx]["ps_exec_policy"] = policy
        self._schedule_save()
        T = TRANSLATIONS[self.lang]
        self._set_status(f"✔ {T['ctx_ps_policy']}: {policy}")


    # ── CODE PREVIEW ────────────────────────
    def _toggle_preview_mode(self):
        """Toggle between script list view and code preview view."""
        T = TRANSLATIONS[self.lang]
        if not self._preview_mode:
            # Switch to preview mode
            sel = self.tree.selection()
            if not sel:
                messagebox.showinfo("", T.get("preview_no_selection",
                                              "Select a script first."))
                return
            idx = int(sel[0])
            if idx >= len(self.scripts):
                return
            self._preview_mode = True
            # Hide tree, show preview
            self.frm_tree.pack_forget()
            self.frm_preview.pack(fill="both", expand=True, after=self._frm_groups)
            # Load the file
            self._load_code_preview(self.scripts[idx])
        else:
            # Back to list
            self._preview_mode = False
            self.frm_preview.pack_forget()
            self.frm_tree.pack(fill="both", expand=True)

    def _load_code_preview(self, s: dict):
        """Load file content into the code preview widget."""
        T = TRANSLATIONS[self.lang]
        path = s.get("path", "")
        name = s.get("name", path)
        MAX_BYTES = 512 * 1024  # 512 KB

        self.lbl_preview_title.config(
            text=f"  {T.get('preview_title','Code preview')}:  {name}")

        self.code_text.config(state="normal")
        self.code_text.delete("1.0", "end")

        if not path or not os.path.exists(path):
            self.code_text.insert("end",
                T.get("preview_not_found", "File not found or cannot be read."))
            self.code_text.config(state="disabled")
            return

        if os.path.getsize(path) > MAX_BYTES:
            self.code_text.insert("end",
                T.get("preview_too_large", "File is too large to preview (> 512 KB)."))
            self.code_text.config(state="disabled")
            return

        # Try several encodings
        content = None
        for enc in ("utf-8", "cp1250", "cp852", "latin-1"):
            try:
                with open(path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
            except OSError:
                break  # file unreadable — bail out immediately

        if content is None:
            self.code_text.insert("end",
                T.get("preview_not_found", "File not found or cannot be read."))
        else:
            self.code_text.insert("end", content)

        self.code_text.config(state="disabled")
        self.code_text.see("1.0")  # Scroll to top

    # ── PREVIEW & RUN (v1.7) ───────────────────
    def _preview_and_run(self):
        """Show preview dialog before running script."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        path = s.get("path", "")
        name = s.get("name", path)
        
        # Create preview dialog
        dlg = tk.Toplevel(self)
        dlg.title(T["preview_dlg_title"].format(name=name))
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("600x400")
        
        # Preview text widget
        txt = scrolledtext.ScrolledText(dlg, bg=C["bg_log"], fg=C["fg_main"],
                                         font=("Consolas", 9), wrap="none")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load file content
        MAX_BYTES = 512 * 1024
        if path and os.path.exists(path) and os.path.getsize(path) <= MAX_BYTES:
            content = None
            for enc in ("utf-8", "cp1250", "cp852", "latin-1"):
                try:
                    with open(path, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, OSError):
                    continue
            if content:
                txt.insert("end", content)
            else:
                txt.insert("end", T.get("preview_not_found", "File not found or cannot be read."))
        else:
            txt.insert("end", T.get("preview_too_large", "File is too large to preview (> 512 KB)."))
        
        txt.config(state="disabled")
        
        # Buttons
        btn_frm = tk.Frame(dlg, bg=C["bg_main"])
        btn_frm.pack(side="bottom", pady=10)
        
        def _run():
            dlg.destroy()
            self._run_selected()
        
        tk.Button(btn_frm, text=T["preview_dlg_run"], command=_run,
                 bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                 font=("Consolas", 9, "bold"), padx=12, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frm, text=T["preview_dlg_cancel"], command=dlg.destroy,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)
        
        _center_dialog(dlg)

    def _on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx >= len(self.scripts):
            return
        s = self.scripts[idx]
        self._update_panel(s)
        # If preview mode is active, refresh the code display
        if self._preview_mode:
            self._load_code_preview(s)

    def _update_panel(self, s: dict):
        T = TRANSLATIONS[self.lang]
        path = s.get("path", "")
        ext  = Path(path).suffix.lower()
        info = SCRIPT_TYPES.get(ext, {"label": ext.lstrip(".").upper()})

        size_str = T["panel_meta_none"]
        modified_str = T["panel_meta_none"]
        if os.path.exists(path):
            sz = os.path.getsize(path)
            size_str = f"{sz:,} B" if sz < 1024 else f"{sz/1024:.1f} KB"
            mtime = os.path.getmtime(path)
            modified_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

        meta = read_script_metadata(path) if os.path.exists(path) else {}

        vals = {
            "panel_meta_name":     s.get("name", T["panel_meta_none"]),
            "panel_meta_type":     info["label"],
            "panel_meta_path":     path or T["panel_meta_none"],
            "panel_meta_size":     size_str,
            "panel_meta_modified": modified_str,
            "panel_meta_author":   meta.get("author", "")  or T["panel_meta_none"],
            "panel_meta_desc":     meta.get("description","") or T["panel_meta_none"],
            "panel_meta_version":  meta.get("version","")  or T["panel_meta_none"],
            "panel_meta_tags":     s.get("tags", "") or T["panel_meta_none"],
            "panel_meta_note":     s.get("note", "") or T["panel_meta_none"],
        }
        for k, v in vals.items():
            if k in self.meta_labels:
                self.meta_labels[k][1].config(text=v)

    # ── ADD / SCAN ──────────────────────────
    def _add_script(self):
        T = TRANSLATIONS[self.lang]
        ft = [
            (T["filetypes_all"], " ".join(f"*{e}" for e in SCRIPT_TYPES)),
            (T["filetypes_py"],  "*.py"),
            (T["filetypes_ps1"], "*.ps1"),
            (T["filetypes_bat"], "*.bat *.cmd"),
            (T["filetypes_vbs"], "*.vbs"),
            (T["filetypes_all_files"], "*.*"),
        ]
        paths = filedialog.askopenfilenames(title=T["dlg_add_title"], filetypes=ft)
        for p in paths:
            self._add_script_entry(p)
        self._refresh_tree()
        self._schedule_save()

    def _add_script_entry(self, path: str, group: str = ""):
        name = Path(path).name
        if not any(s.get("path") == path for s in self.scripts):
            ext = Path(path).suffix.lower()
            self.scripts.append({
                "name": name, "path": path,
                "interpreter": DEFAULT_INTERPRETERS.get(ext, ""),
                "args": "", "workdir": "",
                "encoding": "utf-8",
                "run_as_admin": False, "hidden_window": False, "wait": True,
                "ps_exec_policy": "Bypass",
                "group": group,
                "pinned": False,
                "env_vars": "",
                "auto_restart": False,
                "max_retries": 3,
                "timeout": 0,
                "tags": "",
                "note": "",
                "profiles": [],
                "active_profile": "",
                # v1.5 monitoring
                "run_count": 0,
                "run_times": [],       # last N elapsed seconds (for avg + sparkline)
                "last_rc": None,       # last exit code
                "watchdog_interval": 0,  # 0 = disabled
                "notify_on_finish": False,
                "notify_min_sec": 0,
                # v1.6 dependencies
                "run_after": "",       # name of script that must succeed first
                # v1.7 UI
                "hotkey": "",          # global hotkey string, e.g. "ctrl+f1"
                "kiosk_visible": True, # show button in kiosk mode
            })

    # ── SCRIPT TEMPLATES ─────────────────────────
    def _create_from_template(self):
        """Create a new script from a template."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        dlg = tk.Toplevel(self)
        dlg.title(T.get("template_dlg_title", "New script from template"))
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("500x350")
        
        pad = {"padx": 8, "pady": 4}
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"], "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}
        
        row = 0
        tk.Label(dlg, text=T.get("template_dlg_name", "Script name:"), **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        var_name = tk.StringVar(value="")
        tk.Entry(dlg, textvariable=var_name, width=40, **entry_cfg).grid(row=row, column=1, **pad)
        row += 1
        
        tk.Label(dlg, text=T.get("template_dlg_type", "Type:"), **lbl_cfg).grid(row=row, column=0, sticky="w", **pad)
        var_type = tk.StringVar(value=T.get("template_ps_basic", "PowerShell - Basic"))
        templates = [
            T.get("template_ps_basic", "PowerShell - Basic"),
            T.get("template_ps_advanced", "PowerShell - Advanced"),
            T.get("template_py_basic", "Python - Basic"),
            T.get("template_py_advanced", "Python - Advanced"),
            T.get("template_bat_basic", "Batch - Basic"),
            T.get("template_bat_advanced", "Batch - Advanced"),
        ]
        ttk.Combobox(dlg, textvariable=var_type, values=templates, state="readonly", width=30).grid(row=row, column=1, sticky="w", **pad)
        row += 1
        
        tk.Label(dlg, text=T.get("template_dlg_desc", "Description:"), **lbl_cfg).grid(row=row, column=0, sticky="nw", **pad)
        var_desc = tk.StringVar(value="")
        tk.Entry(dlg, textvariable=var_desc, width=40, **entry_cfg).grid(row=row, column=1, **pad)
        row += 1
        
        def _create():
            name = var_name.get().strip()
            template = var_type.get()
            desc = var_desc.get().strip()
            
            if not name:
                messagebox.showerror("", T.get("msg_error", "Error") + ": " + T.get("template_dlg_name", "Script name:"))
                return
            
            # Determine file extension and content based on template
            if "PowerShell" in template:
                ext = ".ps1"
                if "Advanced" in template:
                    content = self._get_ps_advanced_template(name, desc)
                else:
                    content = self._get_ps_basic_template(name, desc)
            elif "Python" in template:
                ext = ".py"
                if "Advanced" in template:
                    content = self._get_py_advanced_template(name, desc)
                else:
                    content = self._get_py_basic_template(name, desc)
            elif "Batch" in template:
                ext = ".bat"
                if "Advanced" in template:
                    content = self._get_bat_advanced_template(name, desc)
                else:
                    content = self._get_bat_basic_template(name, desc)
            else:
                ext = ".ps1"
                content = self._get_ps_basic_template(name, desc)
            
            # Save to file
            default_dir = os.path.expanduser("~")
            path = filedialog.asksaveasfilename(
                defaultextension=ext,
                initialdir=default_dir,
                initialfile=name + ext,
                filetypes=[(ext.upper(), "*" + ext), ("All files", "*.*")],
                title=T.get("dlg_add_title", "Add script")
            )
            
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    self._add_script_entry(path)
                    self._refresh_tree()
                    self._schedule_save()
                    dlg.destroy()
                    self._set_status(f"✔ {T.get('template_dlg_create', 'Created')}: {name}")
                except Exception as e:
                    messagebox.showerror("", str(e))
        
        btn_frm = tk.Frame(dlg, bg=C["bg_main"])
        btn_frm.grid(row=row, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frm, text=T.get("template_dlg_create", "Create"),
                 bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                 font=("Consolas", 9, "bold"), padx=12, pady=3,
                 command=_create).pack(side="left", padx=5)
        tk.Button(btn_frm, text=T["btn_cancel"],
                 bg=C["btn_cancel_bg"], fg=C["btn_cancel_fg"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3,
                 command=dlg.destroy).pack(side="left", padx=5)
        
        _center_dialog(dlg)
    
    def _get_ps_basic_template(self, name, desc):
        return f"""# {name}
# {desc if desc else 'PowerShell Script'}
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

param(
    [string]$Param1 = "default"
)

Write-Host "Starting {name}..."
Write-Host "Parameter: $Param1"

# Your code here
Write-Host "Done."
"""
    
    def _get_ps_advanced_template(self, name, desc):
        return f"""# {name}
# {desc if desc else 'Advanced PowerShell Script'}
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$RequiredParam,
    
    [Parameter()]
    [string]$OptionalParam = "default",
    
    [Parameter()]
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Log-Message {{
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}}

try {{
    Log-Message "Starting {name}..."
    Log-Message "RequiredParam: $RequiredParam"
    Log-Message "OptionalParam: $OptionalParam"
    
    # Your advanced code here
    
    Log-Message "Completed successfully."
    exit 0
}} catch {{
    Log-Message "Error: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}}
"""
    
    def _get_py_basic_template(self, name, desc):
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name}
{desc if desc else 'Python Script'}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import sys
from pathlib import Path

def main():
    print(f"Starting {name}...")
    
    # Your code here
    
    print("Done.")

if __name__ == "__main__":
    main()
'''
    
    def _get_py_advanced_template(self, name, desc):
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name}
{desc if desc else 'Advanced Python Script'}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ScriptError(Exception):
    """Custom exception for script errors."""
    pass

def main(param1: str = "default", param2: Optional[int] = None) -> int:
    """
    Main function.
    
    Args:
        param1: First parameter
        param2: Optional second parameter
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        logger.info(f"Starting {name}...")
        logger.info(f"param1: {{param1}}")
        logger.info(f"param2: {{param2}}")
        
        # Your advanced code here
        
        logger.info("Completed successfully.")
        return 0
        
    except ScriptError as e:
        logger.error(f"Script error: {{e}}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {{e}}")
        return 2

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=desc if desc else name)
    parser.add_argument("--param1", default="default", help="First parameter")
    parser.add_argument("--param2", type=int, help="Second parameter")
    
    args = parser.parse_args()
    sys.exit(main(args.param1, args.param2))
'''
    
    def _get_bat_basic_template(self, name, desc):
        return f'''@echo off
REM {name}
REM {desc if desc else 'Batch Script'}
REM Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

setlocal

echo Starting {name}...
REM Your code here
echo Done.

endlocal
'''
    
    def _get_bat_advanced_template(self, name, desc):
        return f'''@echo off
REM {name}
REM {desc if desc else 'Advanced Batch Script'}
REM Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

setlocal enabledelayedexpansion

set "SCRIPT_NAME={name}"
set "VERSION=1.0.0"

:main
    call :log "INFO" "Starting %SCRIPT_NAME%..."
    
    REM Your advanced code here
    
    call :log "INFO" "Completed successfully."
    exit /b 0

:error
    call :log "ERROR" "%*"
    exit /b 1

:log
    set "LEVEL=%~1"
    set "MESSAGE=%~2"
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (set "DATE=%%c-%%a-%%b")
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set "TIME=%%a:%%b")
    echo [%DATE% %TIME%] [%LEVEL%] %MESSAGE%
    goto :eof
'''

    def _open_scan_dialog(self):
        ScanDialog(self, self.lang, self._on_scan_done, theme=THEMES.get(self.theme_name, THEMES["light"]))

    def _on_scan_done(self, paths: list):
        for p in paths:
            self._add_script_entry(p)
        self._refresh_tree()
        self._schedule_save()

    # ── REMOVE ──────────────────────────────
    def _remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx >= len(self.scripts):
            return
        if self.app_settings.get("confirm_delete", True):
            T = TRANSLATIONS[self.lang]
            name = self.scripts[idx].get("name", "")
            if not messagebox.askyesno(
                    T.get("ctx_remove", "Remove"),
                    f"{T.get('ctx_remove', 'Remove')}: {name}?"):
                return
        del self.scripts[idx]
        self._refresh_tree()
        self._schedule_save()

    # ── OPTIONS ─────────────────────────────
    def _edit_options(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("", TRANSLATIONS[self.lang]["msg_no_selection"])
            return
        idx = int(sel[0])
        dlg = ScriptOptionsDialog(self, self.scripts[idx], self.lang,
                                   theme=THEMES.get(self.theme_name, THEMES["light"]))
        self.wait_window(dlg)
        if dlg.result:
            self.scripts[idx] = dlg.result
            self._schedule_save()
            self._update_panel(self.scripts[idx])
            self._rebuild_tag_filter()
            self._hotkey_mgr.reload(self.scripts)

    # ── PROFILES ────────────────────────────
    def _activate_profile(self, script_idx: int, profile_name: str):
        T = TRANSLATIONS[self.lang]
        self.scripts[script_idx]["active_profile"] = profile_name
        self._schedule_save()
        self._set_status(f"✔ {T.get('msg_profile_activated', 'Active profile:')} {profile_name}")

    # ── RUN ─────────────────────────────────
    def _find_tool(self, *candidates: str) -> str | None:
        """Resolve tool path using cache + PATH lookup. Thread-safe."""
        cache_key = "|".join(c for c in candidates if c)
        cached = self._tool_cache.get(cache_key)
        if cached:
            if (os.path.isabs(cached) and os.path.exists(cached)) or shutil.which(cached):
                return cached
            # cached entry stale — remove and re-resolve
            del self._tool_cache[cache_key]
        for c in candidates:
            if not c:
                continue
            if os.path.isabs(c) and os.path.exists(c):
                self._tool_cache[cache_key] = c
                return c
            found = shutil.which(c)
            if found:
                self._tool_cache[cache_key] = found
                return found
        return None

    def _run_selected(self):
        T = TRANSLATIONS[self.lang]
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("", T["msg_no_selection"])
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        path = s.get("path", "")
        if not os.path.exists(path):
            messagebox.showerror("", T["msg_not_found"] + path)
            return
        if path in self._running_procs and self._running_procs[path].poll() is None:
            self._set_status(
                f"⚠ {T.get('msg_already_running', 'Already running:')} {s.get('name', '')}")
            return
        threading.Thread(target=self._run_script, args=(s,), daemon=True).start()

    def _run_script(self, s: dict, _retry: int = 0):
        T = TRANSLATIONS[self.lang]
        path     = s.get("path", "")

        # v1.6: prevent duplicate concurrent launches of the same script —
        # queue, watchdog, hotkey and dependency-chain can all try to start
        # the same path at once
        with self._running_lock:
            existing = self._running_procs.get(path)
            if existing is not None and existing.poll() is None:
                self.log_queue.put(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ "
                    f"{T.get('msg_already_running', 'Already running:')} {s.get('name','')}\n")
                return

        if not os.path.exists(path):
            self.log_queue.put(
                f"[{datetime.now().strftime('%H:%M:%S')}] {T['msg_error']} "
                f"{T['msg_not_found']}{path}\n")
            self.after(0, lambda: self._set_status(f"✘ {T['msg_not_found']}{path}"))
            return

        ext      = Path(path).suffix.lower()
        interp   = s.get("interpreter", DEFAULT_INTERPRETERS.get(ext, ""))
        args     = s.get("args", "")
        workdir  = s.get("workdir", "") or os.path.dirname(path) or "."
        timeout_sec  = int(s.get("timeout", 0))

        # v1.5: apply active run profile (overrides args/env_vars/workdir/timeout/interpreter)
        active_profile_name = s.get("active_profile", "")
        active_profile = None
        if active_profile_name:
            for p in s.get("profiles", []):
                if p["name"] == active_profile_name:
                    active_profile = p
                    break
        if active_profile:
            if active_profile.get("args"):
                args = active_profile["args"]
            if active_profile.get("workdir"):
                workdir = active_profile["workdir"]
            if active_profile.get("interpreter"):
                interp = active_profile["interpreter"]
            if active_profile.get("timeout") not in (None, "", 0):
                try:
                    timeout_sec = int(active_profile["timeout"])
                except (TypeError, ValueError):
                    pass
        is_windows = (platform.system() == "Windows")
        auto_restart = s.get("auto_restart", False)
        max_retries  = int(s.get("max_retries", 3))
        now = lambda: datetime.now().strftime("%H:%M:%S")

        enc      = s.get("encoding", "utf-8")
        # For Windows batch/cmd files, use system default encoding instead of UTF-8
        if ext in (".bat", ".cmd") and is_windows:
            import locale
            enc = s.get("encoding", locale.getpreferredencoding() or "cp1252")
        try:
            "".encode(enc)
        except LookupError:
            enc = "utf-8"
        wait     = s.get("wait", True)
        is_ps1   = (ext == ".ps1")
        hidden   = s.get("hidden_window", False)
        admin    = s.get("run_as_admin", False)
        ps_policy= s.get("ps_exec_policy", "Bypass")

        # v1.2: build custom environment
        env_vars_str = s.get("env_vars", "").strip()
        # v1.5: active profile env_vars override
        if active_profile and active_profile.get("env_vars"):
            env_vars_str = active_profile["env_vars"].strip()
        # v1.8: add global env vars first
        if self._global_env_vars:
            env_vars_str = self._global_env_vars.strip() + " " + env_vars_str
        run_env = None
        if env_vars_str:
            run_env = os.environ.copy()
            for token in shlex.split(env_vars_str, posix=(platform.system() != "Windows")):
                if "=" in token:
                    k, v = token.split("=", 1)
                    run_env[k] = v

        def find_tool(*candidates):
            return self._find_tool(*candidates)

        # ── Build command (cross-platform) ──
        cmd = None
        required_tool = None

        if ext in (".bat", ".cmd"):
            if is_windows:
                cmd = [find_tool("cmd.exe", "cmd") or "cmd.exe", "/c", path]
            else:
                required_tool = "bash"
                sh = find_tool("bash", "sh")
                if sh:
                    cmd = [sh, path]
        elif ext == ".vbs":
            if is_windows:
                cmd = [find_tool("cscript.exe", "cscript") or "cscript.exe", "//Nologo", path]
            else:
                required_tool = "cscript"
        elif is_ps1:
            ps_exe = find_tool(interp, "pwsh", "powershell.exe", "powershell")
            required_tool = "pwsh / powershell"
            if ps_exe:
                cmd = [ps_exe, "-ExecutionPolicy", ps_policy, "-File", path]
        elif ext == ".go":
            go_exe = find_tool(interp, "go")
            required_tool = "go"
            if go_exe:
                cmd = [go_exe, "run", path]
        elif ext == ".awk":
            awk_exe = find_tool(interp, "awk", "gawk", "mawk")
            required_tool = "awk"
            if awk_exe:
                cmd = [awk_exe, "-f", path]
        elif ext == ".sed":
            sed_exe = find_tool(interp, "sed", "gsed")
            required_tool = "sed"
            if sed_exe:
                cmd = [sed_exe, "-f", path]
        elif ext == ".swift":
            swift_exe = find_tool(interp, "swift")
            required_tool = "swift"
            if swift_exe:
                cmd = [swift_exe, path]
        elif ext == ".ts":
            ts_exe = find_tool(interp, "ts-node", "tsx")
            required_tool = "ts-node"
            if ts_exe:
                cmd = [ts_exe, path]
        elif interp:
            interp_exe = find_tool(interp)
            required_tool = interp
            if interp_exe:
                cmd = [interp_exe, path]
        else:
            cmd = [path]

        if cmd is None:
            self.log_queue.put(
                f"\n[{now()}] {T['msg_error']} {T['msg_tool_missing']} "
                f"{required_tool or ext}\n")
            self.after(0, lambda: self._set_status(
                f"✘ {T['msg_tool_missing']} {required_tool or ext}"))
            return

        if args:
            cmd += shlex.split(args, posix=(platform.system() != "Windows"))

        # Validate working directory (v1.7)
        if not os.path.isdir(workdir):
            # Try to use script directory as fallback
            script_dir = os.path.dirname(path)
            if script_dir and os.path.isdir(script_dir):
                workdir = script_dir
                self.log_queue.put(f"[{now()}] ℹ {T.get('msg_using_script_dir', 'Using script directory as working dir')}\n")
            else:
                workdir = "."
                self.log_queue.put(f"[{now()}] ℹ {T.get('msg_using_current_dir', 'Using current directory as working dir')}\n")

        retry_sfx = f" (próba {_retry+1}/{max_retries})" if _retry > 0 else ""
        _sep = "─" * 60
        self.log_queue.put(f"\n{_sep}\n")
        self.log_queue.put(f"[{now()}] ▶  {T['msg_running']} {s.get('name','')}{retry_sfx}\n")
        
        # v1.8: notification on script start
        self._show_notification(
            T.get("notifications_title", "psLauncher"),
            f"{T.get('notifications_script_started', 'Script started:')} {s.get('name','')}"
        )

        # Run with elevated privileges
        if admin:
            if is_windows:
                try:
                    import ctypes
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", cmd[0],
                                                         subprocess.list2cmdline(cmd[1:]),
                                                         workdir, 0 if hidden else 1)
                    self.log_queue.put(f"[{now()}] Launched as admin.\n")
                except Exception as e:
                    self.log_queue.put(f"[{now()}] {T['msg_error']} {e}\n")
                return
            else:
                sudo = find_tool("sudo")
                if sudo:
                    cmd = [sudo] + cmd
                else:
                    self.log_queue.put(f"[{now()}] {T['msg_error']} sudo {T['msg_tool_missing']}\n")

        try:
            flags = {}
            if is_windows:
                if hidden:
                    flags["creationflags"] = subprocess.CREATE_NO_WINDOW
            else:
                if cmd[0] == path:
                    try:
                        st = os.stat(path)
                        if not (st.st_mode & 0o111):
                            os.chmod(path, st.st_mode | 0o111)
                    except OSError:
                        pass

            t_start = time.monotonic()
            try:
                proc = subprocess.Popen(cmd, cwd=workdir,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        env=run_env,
                                        **flags)
            except FileNotFoundError:
                self.log_queue.put(
                    f"[{now()}] {T['msg_error']} {T['msg_tool_missing']} {cmd[0]}\n")
                self.after(0, lambda: self._set_status(
                    f"✘ {T['msg_tool_missing']} {cmd[0]}"))
                return
            except PermissionError as e:
                self.log_queue.put(f"[{now()}] {T['msg_error']} {e}\n")
                self.after(0, lambda _e=e: self._set_status(f"✘ {T['msg_error']} {_e}"))
                return
            except OSError as e:
                self.log_queue.put(f"[{now()}] {T['msg_error']} {e}\n")
                self.after(0, lambda _e=e: self._set_status(f"✘ {T['msg_error']} {_e}"))
                return

            # Track active process for Stop/Restart (legacy single-slot fields,
            # kept for the existing Stop/Restart buttons which act on "the
            # most recently touched" script) and the per-path registry that
            # makes concurrent runs safe.
            self._active_proc   = proc
            self._active_script = s
            with self._running_lock:
                self._running_procs[path] = proc

            # ── Timeout watchdog ──
            killed_by_timeout = threading.Event()
            if timeout_sec > 0:
                def _watchdog():
                    if proc.poll() is None:
                        try:
                            # Try to terminate gracefully first
                            proc.terminate()
                            # Wait a bit for graceful shutdown
                            proc.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            # Force kill if graceful shutdown fails
                            try:
                                if is_windows:
                                    # On Windows, use taskkill to ensure process tree is killed
                                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                                                 capture_output=True)
                                else:
                                    # On Unix, kill the process group
                                    try:
                                        os.killpg(os.getpgid(proc.pid), 9)
                                    except (ProcessLookupError, PermissionError):
                                        proc.kill()
                            except Exception:
                                # Fallback to simple kill
                                proc.kill()
                        killed_by_timeout.set()
                        self.log_queue.put(
                            f"[{now()}] ⏱ {T.get('msg_timeout_killed','Timeout – killed after')} "
                            f"{timeout_sec}s\n")
                wd_timer = threading.Timer(timeout_sec, _watchdog)
                wd_timer.daemon = True
                wd_timer.start()
            else:
                wd_timer = None

            if wait:
                if proc.stdout is not None:
                    for line in iter(proc.stdout.readline, b""):
                        try:
                            text = line.decode(enc, errors="replace")
                        except (LookupError, TypeError):
                            text = line.decode("utf-8", errors="replace")
                        self.log_queue.put(text)
                proc.wait()
                if wd_timer:
                    wd_timer.cancel()
                elapsed = round(time.monotonic() - t_start, 2)
                rc = proc.returncode

                # ── Auto-restart (before finalize, which fires dependents on rc==0) ──
                auto_restart = s.get("auto_restart", False)
                max_retries  = int(s.get("max_retries", 3))
                if (auto_restart and rc != 0
                        and not killed_by_timeout.is_set()
                        and _retry < max_retries - 1):
                    self.log_queue.put(
                        f"[{now()}] 🔄 {T.get('msg_auto_restart','Auto-restart (attempt')} "
                        f"{_retry+2}/{max_retries})\n")
                    threading.Thread(
                        target=self._run_script, args=(s, _retry + 1), daemon=True).start()

                self._finalize_run(s, proc, path, rc, elapsed, killed_by_timeout)

                # ── Start/cancel watchdog ──
                wd_interval = int(s.get("watchdog_interval", 0))
                script_path = s.get("path", "")
                old_stop = self._watchdog_stop.pop(script_path, None)
                if old_stop:
                    old_stop.set()
                if wd_interval > 0:
                    stop_evt = threading.Event()
                    self._watchdog_stop[script_path] = stop_evt
                    threading.Thread(
                        target=self._watchdog_loop,
                        args=(s, wd_interval, stop_evt),
                        daemon=True).start()
            else:
                if wd_timer:
                    # Detach watchdog – still runs independently
                    pass
                self.log_queue.put(f"[{now()}] Launched (no-wait).\n")

                # ── Live log tail for detached (no-wait) processes ──
                def _tail_nowait(proc=proc, s=s, t_start=t_start,
                                  enc=enc, name=s.get("name", ""),
                                  killed_by_timeout=killed_by_timeout,
                                  wd_timer=wd_timer):
                    try:
                        if proc.stdout is not None:
                            for line in iter(proc.stdout.readline, b""):
                                try:
                                    text = line.decode(enc, errors="replace")
                                except (LookupError, TypeError):
                                    text = line.decode("utf-8", errors="replace")
                                self.log_queue.put(text)
                        proc.wait()
                    except Exception:
                        pass
                    finally:
                        if wd_timer:
                            wd_timer.cancel()
                        elapsed = round(time.monotonic() - t_start, 2)
                        rc = proc.returncode
                        self._finalize_run(s, proc, path, rc, elapsed, killed_by_timeout)

                threading.Thread(target=_tail_nowait, daemon=True).start()
        except Exception as e:
            self.log_queue.put(f"[{now()}] {T['msg_error']} {e}\n")
            self.after(0, lambda _e=e: self._set_status(f"✘ {T['msg_error']} {_e}"))

    def _finalize_run(self, s: dict, proc: subprocess.Popen, path: str,
                      rc: int, elapsed: float, killed_by_timeout: threading.Event) -> None:
        """Wspólna logika po zakończeniu procesu — stats, historia, status, notify, dependents."""
        T = TRANSLATIONS[self.lang]
        name = s.get("name", "")
        now = lambda: datetime.now().strftime("%H:%M:%S")

        # ── Per-script statistics ──
        s["run_count"] = s.get("run_count", 0) + 1
        run_times = s.get("run_times", [])
        run_times.append(elapsed)
        s["run_times"] = run_times[-50:]
        s["last_rc"] = rc
        self.after(0, self._refresh_tree)

        # Use unambiguous format so _classify_log_line can detect rc value
        _done_icon = "✔" if rc == 0 else "✘"
        self.log_queue.put(
            f"[{now()}] {_done_icon}  {T['msg_done']} {rc}) [{elapsed}s]\n")

        # ── Clear active proc reference ──
        if self._active_proc is proc:
            self._active_proc   = None
            self._active_script = None
        with self._running_lock:
            if self._running_procs.get(path) is proc:
                del self._running_procs[path]

        # ── History & status ──
        self._last_run_info = {"name": name, "code": rc, "elapsed": elapsed}
        self._run_history.append({
            "name":    name,
            "path":    path,
            "time":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code":    rc,
            "elapsed": elapsed,
        })
        # Limit history to 200 entries to prevent memory bloat (v1.7)
        if len(self._run_history) > 200:
            self._run_history = self._run_history[-200:]
        self._schedule_save()
        info = dict(self._last_run_info)
        self.after(0, lambda info=info: self._set_status(
            T["status_last_run"].format(**info), autoclear=0))
        
        # v1.8: notification on script finish/failure
        if rc == 0:
            self._show_notification(
                T.get("notifications_title", "psLauncher"),
                f"{T.get('notifications_script_finished', 'Script finished:')} {name}"
            )
        else:
            self._show_notification(
                T.get("notifications_title", "psLauncher"),
                f"{T.get('notifications_script_failed', 'Script failed:')} {name} (rc={rc})"
            )

        # ── Desktop notification ──
        notify_min = int(s.get("notify_min_sec", 0))
        if s.get("notify_on_finish") and elapsed >= notify_min:
            self._send_notification(
                title=T.get("notify_title", "psLauncher"),
                message=(f"{name} — "
                         f"{T.get('notify_done','Finished')}  "
                         f"{T.get('notify_code','RC')}={rc}  [{elapsed}s]"))

        # ── Dependency chain ──
        if rc == 0 and not killed_by_timeout.is_set():
            self._fire_dependents(name)

    # ── STOP / RESTART ──────────────────────
    def _stop_selected(self):
        T = TRANSLATIONS[self.lang]
        # v1.6: prefer stopping the process matching the currently selected
        # row (so Stop works correctly even if another script started later)
        proc = None
        name = ""
        sel = self.tree.selection()
        if sel:
            idx = int(sel[0])
            sel_path = self.scripts[idx].get("path", "")
            cand = self._running_procs.get(sel_path)
            if cand is not None and cand.poll() is None:
                proc = cand
                name = self.scripts[idx].get("name", "")
        if proc is None:
            proc = self._active_proc
            name = self._active_script.get("name", "") if self._active_script else ""
        if proc is None or proc.poll() is not None:
            self._set_status(T.get("msg_no_running", "No running process."))
            return
        try:
            proc.kill()
            self.log_queue.put(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                f"{T.get('msg_process_killed','Stopped:')} {name}\n")
            self._set_status(f"⏹ {T.get('msg_process_killed','Stopped:')} {name}")
            # v1.6: resolve stop_path BEFORE clearing _active_script, so the
            # fallback (no tree selection, stopping the globally-tracked
            # process) can still find the right watchdog to silence
            stop_path = ""
            if sel:
                stop_path = self.scripts[int(sel[0])].get("path", "")
            elif self._active_script:
                stop_path = self._active_script.get("path", "")
            if self._active_proc is proc:
                self._active_proc   = None
                self._active_script = None
            wd_evt = self._watchdog_stop.get(stop_path) if stop_path else None
            if wd_evt:
                wd_evt.set()
                self._watchdog_stop.pop(stop_path, None)
        except Exception as e:
            self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}\n")

    def _restart_selected(self):
        T = TRANSLATIONS[self.lang]
        script = self._active_script
        proc   = self._active_proc
        self._stop_selected()
        if script:
            self.log_queue.put(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"{T.get('msg_process_restarted','Restarting:')} {script.get('name','')}\n")
            def _wait_and_restart(proc=proc, script=script):
                # Give the old process up to 2s to actually exit before starting a new one
                if proc is not None:
                    try:
                        proc.wait(timeout=2)
                    except Exception:
                        pass
                threading.Thread(
                    target=self._run_script, args=(script,), daemon=True).start()
            threading.Thread(target=_wait_and_restart, daemon=True).start()
        else:
            # fall back to tree selection
            self._run_selected()

    # ── WATCHDOG ────────────────────────────
    def _watchdog_loop(self, s: dict, interval: int, stop_evt: threading.Event):
        """Ping process every `interval` seconds; restart if it died
        unexpectedly. Uses the per-path process registry (v1.6) instead of
        the single-slot _active_proc, so it works correctly even when other
        scripts are running concurrently, and skips restart if the script
        was stopped on purpose via _stop_selected (stop_evt is set there)."""
        T = TRANSLATIONS[self.lang]
        name = s.get("name", "")
        path = s.get("path", "")
        while not stop_evt.is_set():
            stop_evt.wait(timeout=interval)
            if stop_evt.is_set():
                break
            with self._running_lock:
                proc = self._running_procs.get(path)
            if proc is None or proc.poll() is not None:
                # Process died on its own (not via intentional stop, which
                # would have set stop_evt above) — restart it.
                self.log_queue.put(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"🐾 {T.get('watchdog_restarting','Watchdog → restarting:')} {name}\n")
                threading.Thread(
                    target=self._run_script, args=(s,), daemon=True).start()
                # Give the new proc a moment to register before next ping
                stop_evt.wait(timeout=min(interval, 5))

    # ── SYSTEM NOTIFICATION ─────────────────
    def _send_notification(self, title: str, message: str):
        """Send OS desktop notification.
        Priority:
          1. Windows  – PowerShell WinForms BalloonTip
          2. macOS    – osascript display notification
          3. plyer    – cross-platform (if installed)
          4. notify-send – Linux native (if available, no extra deps)
        Never raises; notifications are always optional."""
        try:
            system = platform.system()
            if system == "Windows":
                try:
                    # Sanitise strings for inline PowerShell to prevent injection
                    _t = title.replace("'", "\\'")
                    _m = message.replace("'", "\\'")
                    subprocess.Popen(
                        ["powershell", "-WindowStyle", "Hidden", "-Command",
                         f"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null;"
                         f"$n = New-Object System.Windows.Forms.NotifyIcon;"
                         f"$n.Icon = [System.Drawing.SystemIcons]::Information;"
                         f"$n.Visible = $true;"
                         f"$n.ShowBalloonTip(4000, '{_t}', '{_m}', [System.Windows.Forms.ToolTipIcon]::Info);"
                         f"Start-Sleep -Milliseconds 4500;"
                         f"$n.Dispose()"],
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    return
                except Exception:
                    pass
            elif system == "Darwin":
                try:
                    _t = title.replace('"', '\\"')
                    _m = message.replace('"', '\\"')
                    subprocess.Popen(
                        ["osascript", "-e",
                         f'display notification "{_m}" with title "{_t}"'])
                    return
                except Exception:
                    pass
            # plyer (cross-platform, optional install)
            if _PLYER_AVAILABLE:
                try:
                    _plyer_notif.notify(title=title, message=message,
                                        app_name="psLauncher", timeout=5)
                    return
                except Exception:
                    pass
            # notify-send fallback — Linux, no extra Python deps
            if _NOTIFY_SEND_AVAILABLE:
                try:
                    subprocess.Popen(
                        ["notify-send", "-a", "psLauncher", "-t", "5000",
                         "--", title, message],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
        except Exception:
            pass  # notifications are optional; never crash the main thread

    # ── DRY RUN ─────────────────────────────
    def _dry_run_selected(self):
        """Build the launch command exactly as _run_script would, but show it
        in a dialog instead of executing it. Useful for debugging interpreters,
        argument quoting and environment variables."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("", T["msg_no_selection"])
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        path = s.get("path", "")
        ext  = Path(path).suffix.lower()

        interp      = s.get("interpreter", DEFAULT_INTERPRETERS.get(ext, ""))
        args        = s.get("args", "")
        workdir     = s.get("workdir", "") or os.path.dirname(path) or "."
        timeout_sec = int(s.get("timeout", 0))
        ps_policy   = s.get("ps_exec_policy", "Bypass")
        is_windows  = (platform.system() == "Windows")
        is_ps1      = (ext == ".ps1")

        # Apply active profile overrides (same logic as _run_script)
        active_profile_name = s.get("active_profile", "")
        active_profile = None
        if active_profile_name:
            for p in s.get("profiles", []):
                if p["name"] == active_profile_name:
                    active_profile = p
                    break
        if active_profile:
            if active_profile.get("args"):        args = active_profile["args"]
            if active_profile.get("workdir"):     workdir = active_profile["workdir"]
            if active_profile.get("interpreter"): interp = active_profile["interpreter"]
            if active_profile.get("timeout") not in (None, "", 0):
                try:    timeout_sec = int(active_profile["timeout"])
                except (TypeError, ValueError): pass

        env_vars_str = s.get("env_vars", "").strip()
        if active_profile and active_profile.get("env_vars"):
            env_vars_str = active_profile["env_vars"].strip()

        # Resolve interpreter / build cmd (mirrors _run_script logic)
        def find_tool(*candidates):
            return self._find_tool(*candidates)

        cmd = None
        if ext in (".bat", ".cmd"):
            cmd = ([find_tool("cmd.exe", "cmd") or "cmd.exe", "/c", path]
                   if is_windows else [find_tool("bash", "sh") or "bash", path])
        elif ext == ".vbs":
            cmd = [find_tool("cscript.exe", "cscript") or "cscript.exe", "//Nologo", path] if is_windows else None
        elif is_ps1:
            ps_exe = find_tool(interp, "pwsh", "powershell.exe", "powershell") or interp or "pwsh"
            cmd = [ps_exe, "-ExecutionPolicy", ps_policy, "-File", path]
        elif ext == ".go":
            cmd = [find_tool(interp, "go") or interp or "go", "run", path]
        elif ext == ".awk":
            cmd = [find_tool(interp, "awk", "gawk", "mawk") or interp or "awk", "-f", path]
        elif ext == ".sed":
            cmd = [find_tool(interp, "sed", "gsed") or interp or "sed", "-f", path]
        elif ext == ".swift":
            cmd = [find_tool(interp, "swift") or interp or "swift", path]
        elif ext == ".ts":
            cmd = [find_tool(interp, "ts-node", "tsx") or interp or "ts-node", path]
        elif interp:
            cmd = [find_tool(interp) or interp, path]
        else:
            cmd = [path]

        if cmd and args:
            cmd += shlex.split(args, posix=(not is_windows))

        if not os.path.isdir(workdir):
            workdir = os.path.dirname(path) or "."

        # Compute env diff (only keys added/changed vs os.environ)
        env_diff: dict[str, str] = {}
        if env_vars_str:
            for token in shlex.split(env_vars_str, posix=(not is_windows)):
                if "=" in token:
                    k, v = token.split("=", 1)
                    if os.environ.get(k) != v:
                        env_diff[k] = v

        # Build display text
        cmd_str = subprocess.list2cmdline(cmd) if cmd else "(nie można ustalić / cannot determine)"
        env_str = (
            "\n".join(f"  {k}={v}" for k, v in env_diff.items())
            if env_diff else T.get("dry_run_no_env", "(no changes)")
        )
        timeout_str = f"  timeout: {timeout_sec}s" if timeout_sec else ""
        admin_str   = "  ⚠ run_as_admin=True" if s.get("run_as_admin") else ""
        profile_str = f"  profile: {active_profile_name}" if active_profile_name else ""

        # ── Dialog ──
        dlg = tk.Toplevel(self)
        dlg.title(T.get("dry_run_title", "Dry Run – command preview"))
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.resizable(True, False)

        lbl_cfg  = {"bg": C["bg_main"], "fg": C["fg_dim"],  "font": ("Consolas", 8), "anchor": "w"}
        val_cfg  = {"bg": C["bg_log"],  "fg": C["fg_main"], "font": ("Consolas", 9), "relief": "flat",
                    "state": "normal", "wrap": "word"}
        pad = {"padx": 12, "pady": (6, 2)}

        def _section(label_key, default, value, height=2):
            tk.Label(dlg, text=T.get(label_key, default), **lbl_cfg).pack(fill="x", **pad)
            txt = tk.Text(dlg, height=height, **val_cfg)
            txt.insert("1.0", value)
            txt.config(state="disabled")
            txt.pack(fill="x", padx=12, pady=(0, 4))

        _section("dry_run_cmd", "Command:", cmd_str, height=3)
        _section("dry_run_cwd", "Working directory:", workdir, height=1)
        _section("dry_run_env_diff", "Added env vars:", env_str,
                 height=max(1, len(env_diff)))

        if timeout_str or admin_str or profile_str:
            extras = "\n".join(x for x in [timeout_str, admin_str, profile_str] if x)
            _section("", "Extras:", extras.strip(), height=extras.count("\n") + 1)

        # Buttons
        frm = tk.Frame(dlg, bg=C["bg_main"])
        frm.pack(pady=10)
        btn_cfg = {"relief": "flat", "font": ("Consolas", 9), "padx": 12,
                   "pady": 4, "cursor": "hand2"}

        def _copy_cmd():
            self.clipboard_clear()
            self.clipboard_append(cmd_str)
            self._set_status(f"✔ {T.get('dry_run_copied', 'Copied to clipboard.')}")
            dlg.destroy()

        tk.Button(frm, text=T.get("dry_run_copy", "📋  Copy command"),
                  bg=C["bg_btn"], fg=C["fg_main"], command=_copy_cmd, **btn_cfg).pack(side="left", padx=4)
        tk.Button(frm, text=T["btn_ok"],
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  command=dlg.destroy, **btn_cfg).pack(side="left", padx=4)

        dlg.update_idletasks()
        _, h = dlg.winfo_width(), dlg.winfo_height()
        dlg.minsize(520, h)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        dlg.geometry(f"560x{h}+{(sw-560)//2}+{(sh-h)//2}")

    # ── DEPENDENCY CHAIN ────────────────────
    def _fire_dependents(self, finished_name: str):
        """Launch every script whose run_after matches finished_name.
        Supports multiple dependencies (comma-separated)."""
        T = TRANSLATIONS[self.lang]
        for s in self.scripts:
            trigger = s.get("run_after", "").strip()
            if trigger:
                # Support comma-separated dependencies
                dependencies = [dep.strip() for dep in trigger.split(",") if dep.strip()]
                if finished_name in dependencies:
                    path = s.get("path", "")
                    if os.path.exists(path):
                        self.log_queue.put(
                            f"[{datetime.now().strftime('%H:%M:%S')}] "
                            f"🔗 {T.get('dep_chain_fired','Dependency → launched:')} "
                            f"{s.get('name','')}\n")
                        threading.Thread(
                            target=self._run_script, args=(s,), daemon=True).start()

    # ── LOG TAG SETUP ───────────────────────
    def _apply_log_tags(self):
        """Configure Text widget tags for log syntax colouring.
        Called once at build time and again on theme change."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        tag_cfg = {
            "log_header":  {"foreground": C["log_header"],  "font": ("Consolas", 9, "bold")},
            "log_success": {"foreground": C["log_success"], "font": ("Consolas", 9, "bold")},
            "log_error":   {"foreground": C["log_error"],   "font": ("Consolas", 9, "bold")},
            "log_warning": {"foreground": C["log_warning"], "font": ("Consolas", 9, "italic")},
            "log_stdout":  {"foreground": C["log_stdout"],  "font": ("Consolas", 9)},
            "log_meta":    {"foreground": C["log_meta"],    "font": ("Consolas", 9, "italic")},
            "log_restart": {"foreground": C["log_restart"], "font": ("Consolas", 9, "bold")},
            "log_sched":   {"foreground": C["log_sched"],   "font": ("Consolas", 9, "italic")},
        }
        self.log_text.config(state="normal")
        for tag, cfg in tag_cfg.items():
            self.log_text.tag_configure(tag, **cfg)
        self.log_text.config(state="disabled")

    @staticmethod
    def _classify_log_line(line: str) -> str:
        """Return the tag name for a single log line."""
        stripped = line.strip()
        # separator line (─ / ═)
        if stripped and all(c in "─═━─ " for c in stripped):
            return "log_meta"
        # header: "▶  Running:" / "Uruchamianie:"
        if any(k in line for k in ("▶ ", "Uruchamianie:", "Running:")):
            return "log_header"
        # success / failure — lines with ✔ or ✘ icon (from _finalize_run)
        if "✔ " in line or "✘ " in line:
            return "log_success" if "✔ " in line else "log_error"
        # fallback: detect finish lines by RC pattern "code: N)" or "(N) ["
        if any(k in line for k in ("Zakończono", "Finished", "kod:", "code:")):
            m = re.search(r"\((\d+)\)", line)
            if m:
                rc_val = int(m.group(1))
                return "log_success" if rc_val == 0 else "log_error"
            return "log_stdout"
        # explicit error markers
        if any(k in line for k in ("Błąd:", "Error:", "✘", "❌", "msg_not_found",
                                    "not found", "nie istnieje", "PermissionError",
                                    "Traceback", "Exception", "FAILED")):
            return "log_error"
        # warnings
        if any(k in line for k in ("⚠", "Warning", "Ostrzeżenie", "Already running",
                                    "Już działa", "Timeout", "timeout")):
            return "log_warning"
        # restart / watchdog
        if any(k in line for k in ("🔄", "Restart", "restart", "Watchdog",
                                    "watchdog", "Auto-restart", "🐾")):
            return "log_restart"
        # scheduler
        if any(k in line for k in ("Harmonogram", "Scheduler", "sched_fired",
                                    "⏱", "dep_chain")):
            return "log_sched"
        # metadata / housekeeping (launched no-wait, admin, config warnings)
        if any(k in line for k in ("no-wait", "Launched", "admin", "✔",
                                    "Backup", "backup", "CSV", "⚙")):
            return "log_meta"
        return "log_stdout"

    def _strip_ansi_codes(self, text: str) -> str:
        """Remove ANSI escape sequences from text"""
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    def _colorize_log_line(self, line: str) -> str:
        """Apply ANSI colors to log line based on content type (for file export)."""
        if not self._ansi_enabled or not self._ansi_engine:
            return line
        
        # Detect line type and apply appropriate color
        if "✘" in line or "ERROR" in line.upper() or "Błąd" in line or "msg_error" in line:
            return self._ansi_engine.color(line, Color.BRIGHT_RED)
        elif "✔" in line or "SUCCESS" in line.upper() or "Sukces" in line or "msg_done" in line:
            return self._ansi_engine.color(line, Color.BRIGHT_GREEN)
        elif "⚠" in line or "WARNING" in line.upper() or "Ostrzeżenie" in line or "msg_timeout" in line:
            return self._ansi_engine.color(line, Color.BRIGHT_YELLOW)
        elif "▶" in line or "RUNNING" in line.upper() or "Uruchomiono" in line or "msg_running" in line:
            return self._ansi_engine.color(line, Color.BRIGHT_CYAN)
        elif "ℹ" in line or "INFO" in line.upper() or "Informacja" in line:
            return self._ansi_engine.color(line, Color.BRIGHT_BLUE)
        elif "🔄" in line or "RESTART" in line.upper() or "msg_auto_restart" in line:
            return self._ansi_engine.color(line, Color.BRIGHT_MAGENTA)
        elif "─" * 10 in line:  # Separator lines
            return self._ansi_engine.color(line, Color.BRIGHT_BLACK)
        else:
            # Regular output - keep default color
            return line

    def _process_log_queue(self):
        try:
            # Process up to 50 messages at once to reduce UI updates (v1.7)
            batch = []
            for _ in range(50):
                try:
                    batch.append(self.log_queue.get_nowait())
                except queue.Empty:
                    break
            
            if not batch:
                # No messages, but still schedule next check
                self.after(100, self._process_log_queue)
                return
            
            # Use appropriate widget based on dock state
            target_widget = self._undocked_log_text if not self._log_docked and hasattr(self, '_undocked_log_text') and self._undocked_log_text else self.log_text
            
            # Check if widget still exists before configuring
            try:
                target_widget.config(state="normal")
            except tk.TclError:
                # Widget has been destroyed, skip this batch
                self.after(100, self._process_log_queue)
                return
            
            # Process all messages in batch
            for msg in batch:
                # Strip ANSI codes for Tkinter display (it doesn't support them natively)
                msg = self._strip_ansi_codes(msg)
                
                # Insert and colour line by line so each gets its own tag
                for line in msg.splitlines(keepends=True):
                    tag = self._classify_log_line(line)
                    insert_pos = target_widget.index("end")
                    target_widget.insert("end", line)
                    end_pos = target_widget.index("end")
                    target_widget.tag_add(tag, insert_pos, end_pos)
            
            # Trim log using app_settings log_max_lines (0 = unlimited, fallback 5000)
            max_lines = int(self.app_settings.get("log_max_lines", 0))
            if max_lines <= 0:
                max_lines = 5000
            line_count = int(target_widget.index("end-1c").split(".")[0])
            if line_count > max_lines:
                keep = max(1, max_lines - 1000)
                target_widget.delete("1.0", f"{line_count - keep}.0")
                target_widget.see("end")
                target_widget.config(state="disabled")
        except queue.Empty:
            pass
        except tk.TclError:
            # Widget destroyed during processing, skip
            pass
        self.after(100, self._process_log_queue)

    def _clear_log(self):
        target_widget = self._undocked_log_text if not self._log_docked and hasattr(self, '_undocked_log_text') and self._undocked_log_text else self.log_text
        try:
            target_widget.config(state="normal")
            target_widget.delete("1.0", "end")
            target_widget.config(state="disabled")
        except tk.TclError:
            # Widget has been destroyed, ignore
            pass

    def _export_log(self):
        """Export log content to a file with timestamp."""
        T = TRANSLATIONS[self.lang]
        target_widget = self._undocked_log_text if not self._log_docked and hasattr(self, '_undocked_log_text') and self._undocked_log_text else self.log_text
        
        content = target_widget.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showinfo("", T.get("log_empty", "Log is empty."))
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"pslauncher_log_{timestamp}.txt"
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*")
            ],
            title=T.get("menu_export_log", "Export log to file…")
        )
        
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"psLauncher Log Export\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    # Apply ANSI colorization if enabled for file export
                    if self._ansi_enabled and self._ansi_engine:
                        colorized_lines = []
                        for line in content.splitlines(keepends=True):
                            colorized_lines.append(self._colorize_log_line(line))
                        f.write(''.join(colorized_lines))
                    else:
                        f.write(content)
                        
                self._set_status(f"✔ Log exported to: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("", str(e))

    def _copy_log(self):
        """Copy entire log content to clipboard."""
        content = self.log_text.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            T = TRANSLATIONS[self.lang]
            self._set_status(f"📋 {T.get('log_copied', 'Log copied to clipboard.')}")

    def _edit_global_env_vars(self):
        """Edit global environment variables applied to all scripts."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        dlg = tk.Toplevel(self)
        dlg.title(T.get("global_env_vars", "Global environment variables"))
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("600x500")
        
        pad = {"padx": 10, "pady": 5}
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        
        # Info label
        tk.Label(dlg, text=T.get("global_env_vars_hint", "Applied to all scripts"),
                bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 9, "italic")).pack(pady=5)
        
        # Use existing _EnvVarEditorDialog
        var_env = tk.StringVar(value=self._global_env_vars)
        
        # Simple entry with editor button
        entry_frame = tk.Frame(dlg, bg=C["bg_main"])
        entry_frame.pack(fill="x", padx=10, pady=5)
        
        entry_cfg = {"bg": C["bg_entry"], "fg": C["fg_main"], "insertbackground": C["insert_fg"],
                     "relief": "flat", "font": ("Consolas", 9)}
        tk.Entry(entry_frame, textvariable=var_env, width=50, **entry_cfg).pack(side="left", fill="x", expand=True)
        
        def _open_editor():
            editor_dlg = _EnvVarEditorDialog(dlg, var_env.get(), self.lang, theme=C)
            dlg.wait_window(editor_dlg)
            if editor_dlg.result:
                var_env.set(editor_dlg.result)
        
        tk.Button(entry_frame, text="…", bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 8), width=3,
                  command=_open_editor).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = tk.Frame(dlg, bg=C["bg_main"])
        btn_frame.pack(side="bottom", pady=10)
        
        def _save():
            self._global_env_vars = var_env.get()
            self._schedule_save()
            self._set_status("✔ Global environment variables updated")
            dlg.destroy()
        
        tk.Button(btn_frame, text=T["btn_ok"], command=_save,
                 bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                 font=("Consolas", 9, "bold"), padx=12, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frame, text=T["btn_cancel"], command=dlg.destroy,
                 bg=C["btn_cancel_bg"], fg=C["btn_cancel_fg"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)
        
        _center_dialog(dlg)

    def _check_git_available(self):
        """Check if git is available in the system."""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _git_init(self):
        """Initialize git repository in the config directory."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            subprocess.run(["git", "init"], cwd=config_dir, check=True, capture_output=True)
            T = TRANSLATIONS[self.lang]
            self._set_status(f"✔ {T.get('git_init_success', 'Repository initialized')}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git init failed: {e}")

    def _git_status(self):
        """Show git status."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            result = subprocess.run(["git", "status"], cwd=config_dir, check=True, capture_output=True, text=True)
            self._show_git_output("Git Status", result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git status failed: {e}")

    def _git_add(self):
        """Add files to git index."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            subprocess.run(["git", "add", "."], cwd=config_dir, check=True, capture_output=True)
            T = TRANSLATIONS[self.lang]
            self._set_status(f"✔ {T.get('git_add_success', 'Added to index')}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git add failed: {e}")

    def _git_commit(self):
        """Commit changes with a message."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        T = TRANSLATIONS[self.lang]
        msg = simpledialog.askstring("Git Commit", T.get("git_commit_msg", "Commit message:"))
        if not msg:
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            subprocess.run(["git", "commit", "-m", msg], cwd=config_dir, check=True, capture_output=True)
            self._set_status(f"✔ {T.get('git_commit_success', 'Changes committed')}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git commit failed: {e}")

    def _git_log(self):
        """Show git commit history."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            result = subprocess.run(["git", "log", "--oneline", "-10"], cwd=config_dir, check=True, capture_output=True, text=True)
            self._show_git_output("Git Log", result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git log failed: {e}")

    def _git_diff(self):
        """Show git diff."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            result = subprocess.run(["git", "diff"], cwd=config_dir, check=True, capture_output=True, text=True)
            self._show_git_output("Git Diff", result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git diff failed: {e}")

    def _git_checkout(self):
        """Checkout a specific commit or branch."""
        if not self._check_git_available():
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", T.get("git_not_available", "Git is not available in the system"))
            return
        
        T = TRANSLATIONS[self.lang]
        ref = simpledialog.askstring("Git Checkout", "Commit hash or branch:")
        if not ref:
            return
        
        config_dir = os.path.dirname(self.CONFIG_FILE)
        try:
            subprocess.run(["git", "checkout", ref], cwd=config_dir, check=True, capture_output=True)
            self._set_status(f"✔ Checked out: {ref}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("", f"Git checkout failed: {e}")

    def _show_git_output(self, title, output):
        """Show git command output in a dialog."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.configure(bg=C["bg_main"])
        dlg.geometry("600x400")
        
        text = tk.Text(dlg, bg=C["bg_entry"], fg=C["fg_main"], 
                      font=("Consolas", 9), relief="flat", wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", output)
        text.config(state="disabled")
        
        scrollbar = ttk.Scrollbar(dlg, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.config(yscrollcommand=scrollbar.set)
        
        tk.Button(dlg, text=T["btn_close"], command=dlg.destroy,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(pady=10)

    def _load_plugin(self):
        """Load a plugin from a Python file."""
        T = TRANSLATIONS[self.lang]
        path = filedialog.askopenfilename(
            title=T.get("plugins_load", "Load plugin"),
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if not path:
            return
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("plugin", path)
            if spec is None or spec.loader is None:
                raise ImportError("Cannot load plugin spec")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            plugin_name = getattr(module, "PLUGIN_NAME", os.path.basename(path))
            plugin_version = getattr(module, "PLUGIN_VERSION", "1.0")
            plugin_hooks = {}
            
            for attr_name in dir(module):
                if attr_name.startswith("on_"):
                    plugin_hooks[attr_name] = getattr(module, attr_name)
            
            plugin = {
                "name": plugin_name,
                "version": plugin_version,
                "module": module,
                "hooks": plugin_hooks,
                "path": path
            }
            
            self._plugins.append(plugin)
            self._set_status(f"✔ Plugin loaded: {plugin_name} v{plugin_version}")
            
        except Exception as e:
            T = TRANSLATIONS[self.lang]
            messagebox.showerror("", f"{T.get('plugins_error', 'Plugin loading error:')}: {e}")

    def _show_plugins(self):
        """Show list of loaded plugins."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        dlg = tk.Toplevel(self)
        dlg.title(T.get("plugins_list", "Plugin list"))
        dlg.configure(bg=C["bg_main"])
        dlg.geometry("500x400")
        
        if not self._plugins:
            tk.Label(dlg, text=T.get("plugins_none", "No plugins loaded"),
                    bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 10)).pack(pady=20)
        else:
            for p in self._plugins:
                frame = tk.Frame(dlg, bg=C["bg_main"])
                frame.pack(fill="x", padx=10, pady=5)
                
                info = f"{p['name']} v{p['version']}"
                tk.Label(frame, text=info, bg=C["bg_main"], fg=C["fg_main"],
                        font=("Consolas", 10, "bold")).pack(anchor="w")
                
                hooks = ", ".join(p['hooks'].keys()) if p['hooks'] else "No hooks"
                tk.Label(frame, text=f"Hooks: {hooks}", bg=C["bg_main"], fg=C["fg_main"],
                        font=("Consolas", 9)).pack(anchor="w")
        
        tk.Button(dlg, text=T["btn_close"], command=dlg.destroy,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(pady=10)

    def _open_plugins_folder(self):
        """Open the plugins folder in file explorer."""
        import subprocess
        import platform
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(self._plugins_dir)])
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(self._plugins_dir)])
            else:
                subprocess.run(["xdg-open", str(self._plugins_dir)])
        except Exception as e:
            messagebox.showerror("", f"Failed to open plugins folder: {e}")

    def _call_plugin_hooks(self, hook_name, *args, **kwargs):
        """Call a specific hook in all loaded plugins."""
        for plugin in self._plugins:
            if hook_name in plugin['hooks']:
                try:
                    plugin['hooks'][hook_name](*args, **kwargs)
                except Exception as e:
                    T = TRANSLATIONS[self.lang]
                    self.log_queue.put(f"[Plugin error] {plugin['name']}.{hook_name}: {e}\n")

    def _show_history(self):
        """Show run history dialog with rerun option."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        dlg = tk.Toplevel(self)
        dlg.title(T.get("history_title", "Run History"))
        dlg.configure(bg=C["bg_main"])
        dlg.geometry("800x500")
        
        # Treeview for history
        columns = ("date", "script", "status", "duration")
        tree = ttk.Treeview(dlg, columns=columns, show="headings", height=15)
        tree.heading("date", text=T.get("history_date", "Date"))
        tree.heading("script", text=T.get("history_script", "Script"))
        tree.heading("status", text=T.get("history_status", "Status"))
        tree.heading("duration", text=T.get("history_duration", "Duration"))
        
        tree.column("date", width=150)
        tree.column("script", width=300)
        tree.column("status", width=100)
        tree.column("duration", width=100)
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Populate history
        for entry in reversed(self._run_history):
            date_str = entry.get("timestamp", "")
            script_name = entry.get("name", "Unknown")
            status = "✔ Success" if entry.get("code", 0) == 0 else "✗ Failed"
            duration = f"{entry.get('elapsed', 0):.2f}s"
            tree.insert("", "end", values=(date_str, script_name, status, duration))
        
        # Button frame
        btn_frame = tk.Frame(dlg, bg=C["bg_main"])
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        def _rerun():
            sel = tree.selection()
            if not sel:
                return
            idx = int(tree.index(sel[0]))
            history_idx = len(self._run_history) - 1 - idx
            entry = self._run_history[history_idx]
            script_path = entry.get("path")
            if script_path:
                for i, s in enumerate(self.scripts):
                    if s.get("path") == script_path:
                        self.tree.selection_set(str(i))
                        self.tree.focus(str(i))
                        self._run_selected()
                        dlg.destroy()
                        break
        
        def _clear():
            if messagebox.askyesno("", T.get("history_clear", "Clear history")):
                self._run_history.clear()
                self._schedule_save()
                tree.delete(*tree.get_children())
        
        tk.Button(btn_frame, text=T.get("history_rerun", "Rerun"), command=_rerun,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text=T.get("history_clear", "Clear history"), command=_clear,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text=T["btn_close"], command=dlg.destroy,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="right", padx=5)

    def _clear_history(self):
        """Clear run history."""
        T = TRANSLATIONS[self.lang]
        if messagebox.askyesno("", T.get("history_clear", "Clear history")):
            self._run_history.clear()
            self._schedule_save()
            self._set_status("✔ History cleared")

    def _export_config(self):
        """Export full configuration to JSON file."""
        T = TRANSLATIONS[self.lang]
        path = filedialog.asksaveasfilename(
            title=T.get("config_export", "Export configuration…"),
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        
        try:
            config = {
                "scripts": self.scripts,
                "lang": self.lang,
                "theme": self.theme_name,
                "groups": self._groups,
                "run_history": self._run_history,
                "schedules": self._schedules,
                "app_settings": self.app_settings,
                "global_env_vars": getattr(self, "_global_env_vars", ""),
                "export_timestamp": datetime.datetime.now().isoformat()
            }
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self._set_status(f"✔ {T.get('config_export_success', 'Configuration saved:')} {path}")
            
        except Exception as e:
            messagebox.showerror("", f"Export failed: {e}")

    def _import_config(self):
        """Import full configuration from JSON file."""
        T = TRANSLATIONS[self.lang]
        path = filedialog.askopenfilename(
            title=T.get("config_import", "Import configuration…"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        
        if not messagebox.askyesno("", T.get("config_import_confirm", "Are you sure you want to import configuration? Current configuration will be replaced.")):
            return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Validate and apply configuration
            self.scripts = config.get("scripts", [])
            self.lang = config.get("lang", "en")
            self.theme_name = config.get("theme", "light")
            self._groups = config.get("groups", [])
            self._run_history = config.get("run_history", [])
            self._schedules = config.get("schedules", [])
            self.app_settings = config.get("app_settings", self._default_app_settings())
            self._global_env_vars = config.get("global_env_vars", "")
            self._notifications_enabled = self.app_settings.get("notifications_enabled", False)
            
            # Apply theme and language
            self._apply_theme()
            self._apply_lang()
            
            # Refresh UI
            self._refresh_tree()
            self._rebuild_group_bar()
            self._rebuild_tag_filter()
            
            # Save configuration
            self._schedule_save()
            
            self._set_status(f"✔ {T.get('config_import_success', 'Configuration loaded:')} {path}")
            
        except Exception as e:
            messagebox.showerror("", f"Import failed: {e}")

    def _toggle_notifications(self):
        """Toggle system notifications on/off."""
        self._notifications_enabled = self.var_notifications_enabled.get()
        self.app_settings["notifications_enabled"] = self._notifications_enabled
        self._schedule_save()
        status = "✔ Notifications enabled" if self._notifications_enabled else "✗ Notifications disabled"
        self._set_status(status)

    def _toggle_ansi_colors(self):
        """Toggle ANSI colors on/off."""
        self._ansi_enabled = self.var_ansi_colors_enabled.get()
        self.app_settings["ansi_colors_enabled"] = self._ansi_enabled
        self._schedule_save()
        status = "✔ ANSI colors enabled" if self._ansi_enabled else "✗ ANSI colors disabled"
        self._set_status(status)

    # v1.8: Structured logging integration
    def _log_structured(self, level: str, message: str, **context):
        """Log message using structured logger if available."""
        if self._structured_logger:
            try:
                getattr(self._structured_logger, level.lower())(message, **context)
            except Exception:
                pass  # Fallback silently if structured logging fails

    def _log_performance(self, operation_name: str, message: Optional[str] = None):
        """Log performance metrics using structured logger."""
        if self._structured_logger:
            try:
                self._structured_logger.log_performance(operation_name, message)
            except Exception:
                pass

    # v1.8: Sandbox integration
    def _open_sandbox(self):
        """Open sandbox window for isolated script execution."""
        if not _SANDBOX_AVAILABLE:
            messagebox.showwarning("", "Sandbox module not available")
            return
        
        try:
            sandbox_window = SandboxWindow(self)
            self._log_structured("info", "Sandbox window opened")
        except Exception as e:
            messagebox.showerror("", f"Failed to open sandbox: {e}")
            self._log_structured("error", f"Failed to open sandbox: {e}")

    # v1.8: Debugger integration
    def _toggle_debugger(self):
        """Toggle debugger on/off."""
        if not _DEBUGGER_AVAILABLE:
            messagebox.showwarning("", "Debugger module not available")
            return
        
        self._debugger_enabled = not self._debugger_enabled
        self.app_settings["debugger_enabled"] = self._debugger_enabled
        self._schedule_save()
        
        if self._debugger_enabled:
            self._execution_controller = ExecutionController(self._debugger_config)
            self._state_inspector = StateInspector(self._execution_controller)
            self._profiler = Profiler()
            self._log_structured("info", "Debugger enabled")
        else:
            self._execution_controller = None
            self._state_inspector = None
            self._profiler = None
            self._log_structured("info", "Debugger disabled")
        
        status = "✔ Debugger enabled" if self._debugger_enabled else "✗ Debugger disabled"
        self._set_status(status)

    # v1.8: Dependencies check integration
    def _check_dependencies(self):
        """Check and display all optional dependencies."""
        deps_status = []
        
        # Check tkinterdnd2
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            deps_status.append(("tkinterdnd2", "OK", "optional"))
        except ImportError:
            deps_status.append(("tkinterdnd2", "MISSING", "optional"))
        
        # Check plyer
        try:
            from plyer import notification
            deps_status.append(("plyer", "OK", "optional"))
        except ImportError:
            deps_status.append(("plyer", "MISSING", "optional"))
        
        # Check keyboard
        try:
            import keyboard
            deps_status.append(("keyboard", "OK", "optional"))
        except ImportError:
            deps_status.append(("keyboard", "MISSING", "optional"))
        
        # Check sandbox
        try:
            import sandbox
            deps_status.append(("sandbox", "OK", "optional"))
        except ImportError:
            deps_status.append(("sandbox", "MISSING", "optional"))
        
        # Check logger
        try:
            import logger
            deps_status.append(("logger", "OK", "optional"))
        except ImportError:
            deps_status.append(("logger", "MISSING", "optional"))
        
        # Check debugger
        try:
            import debugger
            deps_status.append(("debugger", "OK", "optional"))
        except ImportError:
            deps_status.append(("debugger", "MISSING", "optional"))
        
        # Check ansi
        try:
            import ansi
            deps_status.append(("ansi", "OK", "optional"))
        except ImportError:
            deps_status.append(("ansi", "MISSING", "optional"))
        
        # Check script_runner
        try:
            import script_runner
            deps_status.append(("script_runner", "OK", "optional"))
        except ImportError:
            deps_status.append(("script_runner", "MISSING", "optional"))
        
        # Display results
        result_window = tk.Toplevel(self)
        result_window.title("Dependencies Check")
        result_window.geometry("500x400")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(result_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", "=== Dependencies Status ===\n\n")
        for name, status, dep_type in deps_status:
            icon = "✓" if status == "OK" else "✗"
            text_widget.insert("end", f"{icon} {name}: {status} ({dep_type})\n")
        
        text_widget.insert("end", "\n=== Summary ===\n")
        ok_count = sum(1 for _, status, _ in deps_status if status == "OK")
        total_count = len(deps_status)
        text_widget.insert("end", f"Available: {ok_count}/{total_count}\n")
        
        text_widget.config(state="disabled")
        self._log_structured("info", f"Dependencies check: {ok_count}/{total_count} available")

    # v1.8: Script templates integration
    def _show_script_templates(self):
        """Show script templates dialog"""
        if not _SCRIPT_RUNNER_AVAILABLE or not self._script_runner:
            messagebox.showwarning("", "Script runner module not available")
            return
        
        template_window = tk.Toplevel(self)
        template_window.title("Script Templates")
        template_window.geometry("800x600")
        
        # Template list
        list_frame = ttk.Frame(template_window)
        list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="Available Templates", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        template_listbox = tk.Listbox(list_frame, font=("Segoe UI", 9))
        template_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=template_listbox.yview)
        template_listbox.configure(yscrollcommand=template_scrollbar.set)
        
        template_listbox.pack(side="left", fill="both", expand=True)
        template_scrollbar.pack(side="right", fill="y")
        
        # Load templates
        templates = self._script_runner.get_template_manager().list_templates()
        for template in templates:
            template_listbox.insert("end", f"{template.name} ({template.script_type.value})")
        
        # Template details
        details_frame = ttk.Frame(template_window)
        details_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(details_frame, text="Template Details", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=("Consolas", 9), height=20)
        details_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=details_scrollbar.set)
        
        details_text.pack(side="left", fill="both", expand=True)
        details_scrollbar.pack(side="right", fill="y")
        
        def show_template_details(event):
            selection = template_listbox.curselection()
            if selection:
                idx = selection[0]
                template = templates[idx]
                details_text.config(state="normal")
                details_text.delete("1.0", "end")
                details_text.insert("1.0", f"Name: {template.name}\n")
                details_text.insert("end", f"Type: {template.script_type.value}\n")
                details_text.insert("end", f"Description: {template.description}\n")
                details_text.insert("end", f"Tags: {', '.join(template.tags)}\n")
                details_text.insert("end", f"\n--- Content ---\n\n")
                details_text.insert("end", template.content)
                details_text.config(state="disabled")
        
        template_listbox.bind("<<ListboxSelect>>", show_template_details)
        
        # Buttons
        button_frame = ttk.Frame(template_window)
        button_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        def create_from_template():
            selection = template_listbox.curselection()
            if not selection:
                return
            
            idx = selection[0]
            template = templates[idx]
            
            output_path = filedialog.asksaveasfilename(
                title="Save Script",
                defaultextension=template.script_type.value,
                filetypes=[(f"{template.script_type.value} files", f"*.{template.script_type.value}")]
            )
            
            if output_path:
                success = self._script_runner.get_template_manager().create_script_from_template(
                    template.id, output_path
                )
                if success:
                    messagebox.showinfo("", "Script created successfully")
                    self._log_structured("info", f"Script created from template: {template.name}")
                else:
                    messagebox.showerror("", "Failed to create script")
        
        ttk.Button(button_frame, text="Create from Template", command=create_from_template).pack(side="left")
        ttk.Button(button_frame, text="Close", command=lambda: template_window.destroy()).pack(side="right")

    def _show_execution_history(self):
        """Show execution history dialog"""
        if not _SCRIPT_RUNNER_AVAILABLE or not self._script_runner:
            messagebox.showwarning("", "Script runner module not available")
            return
        
        history_window = tk.Toplevel(self)
        history_window.title("Execution History")
        history_window.geometry("1000x600")
        
        # History list
        list_frame = ttk.Frame(history_window)
        list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="Execution History", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        history_tree = ttk.Treeview(list_frame, columns=("name", "type", "status", "duration", "time"), show="headings")
        history_tree.heading("name", text="Script")
        history_tree.heading("type", text="Type")
        history_tree.heading("status", text="Status")
        history_tree.heading("duration", text="Duration")
        history_tree.heading("time", text="Time")
        
        history_tree.column("name", width=200)
        history_tree.column("type", width=80)
        history_tree.column("status", width=80)
        history_tree.column("duration", width=80)
        history_tree.column("time", width=150)
        
        history_tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=history_tree_scroll.set)
        
        history_tree.pack(side="left", fill="both", expand=True)
        history_tree_scroll.pack(side="right", fill="y")
        
        # Load history
        records = self._script_runner.get_execution_history().get_records(limit=100)
        for record in reversed(records):
            status_icon = "✔" if record.status.value == "completed" else "✗"
            duration = f"{record.duration_ms:.0f}ms" if record.duration_ms else "N/A"
            time_str = datetime.fromtimestamp(record.start_time).strftime("%Y-%m-%d %H:%M:%S")
            history_tree.insert("", "end", values=(
                record.script_name,
                record.script_type.value,
                f"{status_icon} {record.status.value}",
                duration,
                time_str
            ))
        
        # Stats panel
        stats_frame = ttk.Frame(history_window)
        stats_frame.pack(side="right", fill="both", padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Statistics", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        stats_text = tk.Text(stats_frame, wrap=tk.WORD, font=("Consolas", 9), width=30)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=stats_text.yview)
        stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_text.pack(side="left", fill="both", expand=True)
        stats_scrollbar.pack(side="right", fill="y")
        
        # Load stats
        all_stats = self._script_runner.get_execution_history().get_all_stats()
        stats_text.insert("1.0", "=== Script Statistics ===\n\n")
        
        for script_path, stats in list(all_stats.items())[:20]:
            script_name = Path(script_path).name
            success_rate = (stats.successful_runs / stats.total_runs * 100) if stats.total_runs > 0 else 0
            stats_text.insert("end", f"{script_name}\n")
            stats_text.insert("end", f"  Runs: {stats.total_runs}\n")
            stats_text.insert("end", f"  Success: {stats.successful_runs}\n")
            stats_text.insert("end", f"  Failed: {stats.failed_runs}\n")
            stats_text.insert("end", f"  Success Rate: {success_rate:.1f}%\n")
            stats_text.insert("end", f"  Avg Duration: {stats.avg_duration_ms:.0f}ms\n")
            stats_text.insert("end", "\n")
        
        stats_text.config(state="disabled")
        
        # Buttons
        button_frame = ttk.Frame(history_window)
        button_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        def clear_history():
            if messagebox.askyesno("", "Clear all execution history?"):
                self._script_runner.get_execution_history().clear_history()
                history_window.destroy()
                self._show_execution_history()
        
        ttk.Button(button_frame, text="Clear History", command=clear_history).pack(side="left")
        ttk.Button(button_frame, text="Close", command=lambda: history_window.destroy()).pack(side="right")

    def _show_interpreters_info(self):
        """Show available interpreters information"""
        if not _SCRIPT_RUNNER_AVAILABLE or not self._script_runner:
            messagebox.showwarning("", "Script runner module not available")
            return
        
        info_window = tk.Toplevel(self)
        info_window.title("Available Interpreters")
        info_window.geometry("600x400")
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(info_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", "=== Available Interpreters ===\n\n")
        
        env_manager = self._script_runner.get_environment_manager()
        for script_type, interpreters in env_manager.interpreters.items():
            text_widget.insert("end", f"{script_type.value.upper()}:\n")
            for interp in interpreters:
                text_widget.insert("end", f"  - {interp}\n")
            text_widget.insert("end", "\n")
        
        text_widget.config(state="disabled")

    def _show_script_validator(self):
        """Show script validation dialog"""
        if not _SCRIPT_RUNNER_AVAILABLE or not self._script_runner:
            messagebox.showwarning("", "Script runner module not available")
            return
        
        validator_window = tk.Toplevel(self)
        validator_window.title("Script Validator")
        validator_window.geometry("600x400")
        
        # Script selection
        top_frame = ttk.Frame(validator_window)
        top_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(top_frame, text="Script Path:").pack(side="left")
        script_path_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=script_path_var, width=50).pack(side="left", padx=5)
        
        def browse_script():
            path = filedialog.askopenfilename(
                title="Select Script",
                filetypes=[
                    ("Python scripts", "*.py"),
                    ("Batch files", "*.bat;*.cmd"),
                    ("PowerShell scripts", "*.ps1"),
                    ("Shell scripts", "*.sh"),
                    ("All files", "*.*")
                ]
            )
            if path:
                script_path_var.set(path)
        
        ttk.Button(top_frame, text="Browse", command=browse_script).pack(side="left")
        
        # Validate button
        def validate_script():
            script_path = script_path_var.get()
            if not script_path:
                messagebox.showwarning("", "Please select a script")
                return
            
            result = self._script_runner.validate_script(script_path)
            
            result_text.config(state="normal")
            result_text.delete("1.0", "end")
            
            if result.is_valid:
                result_text.insert("1.0", "✓ Script is VALID\n\n")
            else:
                result_text.insert("1.0", "✗ Script is INVALID\n\n")
            
            result_text.insert("end", f"Syntax OK: {'Yes' if result.syntax_ok else 'No'}\n")
            result_text.insert("end", f"Dependencies OK: {'Yes' if result.dependencies_ok else 'No'}\n\n")
            
            if result.errors:
                result_text.insert("end", "=== Errors ===\n")
                for error in result.errors:
                    result_text.insert("end", f"  - {error}\n")
                result_text.insert("end", "\n")
            
            if result.warnings:
                result_text.insert("end", "=== Warnings ===\n")
                for warning in result.warnings:
                    result_text.insert("end", f"  - {warning}\n")
            
            result_text.config(state="disabled")
            
            self._log_structured("info", f"Script validation: {script_path} - {'Valid' if result.is_valid else 'Invalid'}")
        
        ttk.Button(top_frame, text="Validate", command=validate_script).pack(side="left", padx=5)
        
        # Results
        result_frame = ttk.Frame(validator_window)
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(result_frame, text="Validation Results", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        result_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 9))
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
        result_text.configure(yscrollcommand=result_scrollbar.set)
        
        result_text.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")
        result_text.config(state="disabled")

    def _show_backup_manager(self):
        """Show backup manager dialog"""
        if not _SCRIPT_RUNNER_AVAILABLE or not self._script_runner:
            messagebox.showwarning("", "Script runner module not available")
            return
        
        backup_window = tk.Toplevel(self)
        backup_window.title("Backup Manager")
        backup_window.geometry("800x600")
        
        # Script selection
        top_frame = ttk.Frame(backup_window)
        top_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(top_frame, text="Script Path:").pack(side="left")
        script_path_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=script_path_var, width=50).pack(side="left", padx=5)
        
        def browse_script():
            path = filedialog.askopenfilename(
                title="Select Script",
                filetypes=[
                    ("Python scripts", "*.py"),
                    ("Batch files", "*.bat;*.cmd"),
                    ("PowerShell scripts", "*.ps1"),
                    ("Shell scripts", "*.sh"),
                    ("All files", "*.*")
                ]
            )
            if path:
                script_path_var.set(path)
                load_backups()
        
        ttk.Button(top_frame, text="Browse", command=browse_script).pack(side="left")
        
        def create_backup():
            script_path = script_path_var.get()
            if not script_path:
                messagebox.showwarning("", "Please select a script")
                return
            
            backup_info = self._script_runner.create_backup(script_path)
            if backup_info:
                messagebox.showinfo("", "Backup created successfully")
                self._log_structured("info", f"Backup created: {script_path}")
                load_backups()
            else:
                messagebox.showerror("", "Failed to create backup")
        
        ttk.Button(top_frame, text="Create Backup", command=create_backup).pack(side="left", padx=5)
        
        def cleanup_old_backups():
            if messagebox.askyesno("", "Delete backups older than 30 days?"):
                self._script_runner.get_backup_manager().cleanup_old_backups(30)
                messagebox.showinfo("", "Old backups cleaned up")
                load_backups()
        
        ttk.Button(top_frame, text="Cleanup Old Backups", command=cleanup_old_backups).pack(side="right")
        
        # Backups list
        list_frame = ttk.Frame(backup_window)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="Available Backups", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        backup_tree = ttk.Treeview(list_frame, columns=("path", "created", "size"), show="headings")
        backup_tree.heading("path", text="Backup Path")
        backup_tree.heading("created", text="Created")
        backup_tree.heading("size", text="Size")
        
        backup_tree.column("path", width=300)
        backup_tree.column("created", width=150)
        backup_tree.column("size", width=100)
        
        backup_tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=backup_tree.yview)
        backup_tree.configure(yscrollcommand=backup_tree_scroll.set)
        
        backup_tree.pack(side="left", fill="both", expand=True)
        backup_tree_scroll.pack(side="right", fill="y")
        
        def load_backups():
            script_path = script_path_var.get()
            if not script_path:
                return
            
            # Clear existing items
            for item in backup_tree.get_children():
                backup_tree.delete(item)
            
            # Load backups
            backups = self._script_runner.get_backups(script_path)
            for backup in backups:
                created_str = datetime.fromtimestamp(backup.created_at).strftime("%Y-%m-%d %H:%M:%S")
                size_str = f"{backup.size} bytes"
                backup_tree.insert("", "end", values=(backup.backup_path, created_str, size_str))
        
        def restore_backup():
            selection = backup_tree.selection()
            if not selection:
                messagebox.showwarning("", "Please select a backup")
                return
            
            script_path = script_path_var.get()
            if not script_path:
                messagebox.showwarning("", "Please select a script")
                return
            
            backups = self._script_runner.get_backups(script_path)
            idx = backup_tree.index(selection[0])
            if idx < len(backups):
                backup_info = backups[idx]
                if self._script_runner.restore_backup(backup_info):
                    messagebox.showinfo("", "Backup restored successfully")
                    self._log_structured("info", f"Backup restored: {script_path}")
                else:
                    messagebox.showerror("", "Failed to restore backup")
        
        def delete_backup():
            selection = backup_tree.selection()
            if not selection:
                messagebox.showwarning("", "Please select a backup")
                return
            
            script_path = script_path_var.get()
            if not script_path:
                messagebox.showwarning("", "Please select a script")
                return
            
            if not messagebox.askyesno("", "Delete selected backup?"):
                return
            
            backups = self._script_runner.get_backups(script_path)
            idx = backup_tree.index(selection[0])
            if idx < len(backups):
                backup_info = backups[idx]
                backups[idx] = self._script_runner.get_backup_manager().delete_backup(backup_info)
                messagebox.showinfo("", "Backup deleted")
                load_backups()
        
        # Buttons
        button_frame = ttk.Frame(backup_window)
        button_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Restore Backup", command=restore_backup).pack(side="left")
        ttk.Button(button_frame, text="Delete Backup", command=delete_backup).pack(side="left")
        ttk.Button(button_frame, text="Close", command=lambda: backup_window.destroy()).pack(side="right")

    def _show_task_scheduler(self):
        """Show task scheduler dialog"""
        if not _SCRIPT_RUNNER_AVAILABLE or not self._script_runner:
            messagebox.showwarning("", "Script runner module not available")
            return
        
        scheduler_window = tk.Toplevel(self)
        scheduler_window.title("Task Scheduler")
        scheduler_window.geometry("900x600")
        
        # Task list
        list_frame = ttk.Frame(scheduler_window)
        list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="Scheduled Tasks", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        task_tree = ttk.Treeview(list_frame, columns=("script", "type", "value", "enabled", "next_run"), show="headings")
        task_tree.heading("script", text="Script")
        task_tree.heading("type", text="Type")
        task_tree.heading("value", text="Schedule")
        task_tree.heading("enabled", text="Enabled")
        task_tree.heading("next_run", text="Next Run")
        
        task_tree.column("script", width=200)
        task_tree.column("type", width=80)
        task_tree.column("value", width=100)
        task_tree.column("enabled", width=60)
        task_tree.column("next_run", width=150)
        
        task_tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=task_tree.yview)
        task_tree.configure(yscrollcommand=task_tree_scroll.set)
        
        task_tree.pack(side="left", fill="both", expand=True)
        task_tree_scroll.pack(side="right", fill="y")
        
        def load_tasks():
            # Clear existing items
            for item in task_tree.get_children():
                task_tree.delete(item)
            
            # Load tasks
            tasks = self._script_runner.list_scheduled_tasks()
            for task in tasks:
                script_name = Path(task.script_path).name
                enabled_str = "Yes" if task.enabled else "No"
                next_run_str = datetime.fromtimestamp(task.next_run).strftime("%Y-%m-%d %H:%M:%S") if task.next_run else "N/A"
                task_tree.insert("", "end", values=(script_name, task.schedule_type, task.schedule_value, enabled_str, next_run_str))
        
        load_tasks()
        
        # Task editor
        editor_frame = ttk.Frame(scheduler_window)
        editor_frame.pack(side="right", fill="both", padx=5, pady=5)
        
        ttk.Label(editor_frame, text="Add/Edit Task", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        # Script path
        ttk.Label(editor_frame, text="Script Path:").pack(anchor="w")
        script_path_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=script_path_var, width=40).pack(fill="x", pady=2)
        
        def browse_script():
            path = filedialog.askopenfilename(
                title="Select Script",
                filetypes=[
                    ("Python scripts", "*.py"),
                    ("Batch files", "*.bat;*.cmd"),
                    ("PowerShell scripts", "*.ps1"),
                    ("Shell scripts", "*.sh"),
                    ("All files", "*.*")
                ]
            )
            if path:
                script_path_var.set(path)
        
        ttk.Button(editor_frame, text="Browse", command=browse_script).pack(anchor="w", pady=2)
        
        # Schedule type
        ttk.Label(editor_frame, text="Schedule Type:").pack(anchor="w", pady=(10, 0))
        schedule_type_var = tk.StringVar(value="interval")
        schedule_type_combo = ttk.Combobox(editor_frame, textvariable=schedule_type_var, 
                                          values=["interval", "daily", "weekly"], state="readonly")
        schedule_type_combo.pack(fill="x", pady=2)
        
        # Schedule value
        ttk.Label(editor_frame, text="Schedule Value:").pack(anchor="w", pady=(10, 0))
        schedule_value_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=schedule_value_var, width=40).pack(fill="x", pady=2)
        
        ttk.Label(editor_frame, text="Examples: '5m' (5 min), '1h' (1 hour), '14:30' (daily), 'monday 14:30' (weekly)", 
                  font=("Segoe UI", 8)).pack(anchor="w")
        
        # Enabled
        enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(editor_frame, text="Enabled", variable=enabled_var).pack(anchor="w", pady=(10, 0))
        
        # Buttons
        def add_task():
            script_path = script_path_var.get()
            if not script_path:
                messagebox.showwarning("", "Please select a script")
                return
            
            schedule_type = schedule_type_var.get()
            schedule_value = schedule_value_var.get()
            if not schedule_value:
                messagebox.showwarning("", "Please enter schedule value")
                return
            
            task_id = hashlib.md5(f"{script_path}{time.time()}".encode()).hexdigest()
            task = ScheduledTask(
                id=task_id,
                script_path=script_path,
                schedule_type=schedule_type,
                schedule_value=schedule_value,
                enabled=enabled_var.get()
            )
            
            self._script_runner.add_scheduled_task(task)
            messagebox.showinfo("", "Task added successfully")
            self._log_structured("info", f"Scheduled task added: {script_path}")
            load_tasks()
        
        def delete_task():
            selection = task_tree.selection()
            if not selection:
                messagebox.showwarning("", "Please select a task")
                return
            
            tasks = self._script_runner.list_scheduled_tasks()
            idx = task_tree.index(selection[0])
            if idx < len(tasks):
                task = tasks[idx]
                if self._script_runner.remove_scheduled_task(task.id):
                    messagebox.showinfo("", "Task deleted successfully")
                    load_tasks()
        
        def toggle_task():
            selection = task_tree.selection()
            if not selection:
                messagebox.showwarning("", "Please select a task")
                return
            
            tasks = self._script_runner.list_scheduled_tasks()
            idx = task_tree.index(selection[0])
            if idx < len(tasks):
                task = tasks[idx]
                if task.enabled:
                    self._script_runner.get_task_scheduler().disable_task(task.id)
                else:
                    self._script_runner.get_task_scheduler().enable_task(task.id)
                load_tasks()
        
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(button_frame, text="Add Task", command=add_task).pack(side="left", fill="x", expand=True)
        ttk.Button(button_frame, text="Delete Task", command=delete_task).pack(side="left", fill="x", expand=True)
        ttk.Button(button_frame, text="Toggle Enable", command=toggle_task).pack(side="left", fill="x", expand=True)
        
        # Scheduler control
        control_frame = ttk.Frame(scheduler_window)
        control_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        def start_scheduler():
            self._script_runner.start_scheduler()
            messagebox.showinfo("", "Scheduler started")
            self._log_structured("info", "Task scheduler started")
        
        def stop_scheduler():
            self._script_runner.stop_scheduler()
            messagebox.showinfo("", "Scheduler stopped")
            self._log_structured("info", "Task scheduler stopped")
        
        ttk.Button(control_frame, text="Start Scheduler", command=start_scheduler).pack(side="left")
        ttk.Button(control_frame, text="Stop Scheduler", command=stop_scheduler).pack(side="left")
        ttk.Button(control_frame, text="Close", command=lambda: scheduler_window.destroy()).pack(side="right")

    def _show_advanced_search(self):
        """Show advanced search dialog"""
        search_window = tk.Toplevel(self)
        search_window.title("Advanced Search")
        search_window.geometry("600x500")
        
        # Search options
        options_frame = ttk.Frame(search_window)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(options_frame, text="Search Text:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        search_text_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=search_text_var, width=40).grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(options_frame, text="Script Type:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        type_var = tk.StringVar(value="all")
        type_combo = ttk.Combobox(options_frame, textvariable=type_var, 
                                 values=["all", "python", "batch", "powershell", "shell", "node", "lua"], 
                                 state="readonly")
        type_combo.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(options_frame, text="Group:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        group_var = tk.StringVar(value="all")
        groups = ["all", "__ungrouped__"] + list(set(s.get("group", "") for s in self.scripts if s.get("group")))
        group_combo = ttk.Combobox(options_frame, textvariable=group_var, values=groups, state="readonly")
        group_combo.grid(row=2, column=1, sticky="ew", pady=5)
        
        ttk.Label(options_frame, text="Tag:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        tag_var = tk.StringVar(value="all")
        all_tags = set()
        for s in self.scripts:
            for tag in s.get("tags", "").split(","):
                if tag.strip():
                    all_tags.add(tag.strip())
        tag_combo = ttk.Combobox(options_frame, textvariable=tag_var, values=["all"] + sorted(all_tags), state="readonly")
        tag_combo.grid(row=3, column=1, sticky="ew", pady=5)
        
        ttk.Label(options_frame, text="Last Status:", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(options_frame, textvariable=status_var, 
                                   values=["all", "success", "failed", "never"], state="readonly")
        status_combo.grid(row=4, column=1, sticky="ew", pady=5)
        
        # Favorites only
        favorites_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Favorites Only", variable=favorites_var).grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Search button
        def perform_search():
            search_parts = []
            
            if search_text_var.get():
                search_parts.append(search_text_var.get())
            
            if type_var.get() != "all":
                search_parts.append(f"type:{type_var.get()}")
            
            if group_var.get() != "all":
                if group_var.get() == "__ungrouped__":
                    search_parts.append("group:__ungrouped__")
                else:
                    search_parts.append(f"group:{group_var.get()}")
            
            if tag_var.get() != "all":
                search_parts.append(f"tag:{tag_var.get()}")
            
            if status_var.get() != "all":
                search_parts.append(f"status:{status_var.get()}")
            
            if favorites_var.get():
                self._favorites_filter = True
                self.btn_favorites.config(bg=C["btn_active_bg"] if C.get("btn_active_bg") else "#4CAF50")
            else:
                self._favorites_filter = False
                self.btn_favorites.config(bg=C["btn_bg"] if C.get("btn_bg") else "#f0f0f0")
            
            search_query = " ".join(search_parts)
            self.var_search.set(search_query)
            self._refresh_tree()
            
            # Show results count
            result_count = len(self.tree.get_children())
            messagebox.showinfo("", f"Found {result_count} scripts")
            
            self._log_structured("info", f"Advanced search: '{search_query}' - {result_count} results")
        
        button_frame = ttk.Frame(search_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Search", command=perform_search).pack(side="left")
        ttk.Button(button_frame, text="Clear", command=lambda: (self.var_search.set(""), self._refresh_tree(), search_window.destroy())).pack(side="left")
        ttk.Button(button_frame, text="Close", command=search_window.destroy).pack(side="right")

    def _show_tag_manager(self):
        """Show tag manager dialog"""
        tag_window = tk.Toplevel(self)
        tag_window.title("Tag Manager")
        tag_window.geometry("700x500")
        
        # Left panel - all tags
        left_frame = ttk.Frame(tag_window)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="All Tags", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        # Collect all tags
        all_tags = set()
        for s in self.scripts:
            for tag in s.get("tags", "").split(","):
                if tag.strip():
                    all_tags.add(tag.strip())
        
        tag_listbox = tk.Listbox(left_frame, font=("Segoe UI", 9))
        tag_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tag_listbox.yview)
        tag_listbox.configure(yscrollcommand=tag_scrollbar.set)
        
        for tag in sorted(all_tags):
            tag_listbox.insert("end", tag)
        
        tag_listbox.pack(side="left", fill="both", expand=True)
        tag_scrollbar.pack(side="right", fill="y")
        
        # Right panel - edit selected script tags
        right_frame = ttk.Frame(tag_window)
        right_frame.pack(side="right", fill="both", padx=5, pady=5)
        
        ttk.Label(right_frame, text="Edit Script Tags", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        # Script selection
        ttk.Label(right_frame, text="Select Script:").pack(anchor="w", pady=5)
        script_var = tk.StringVar()
        script_combo = ttk.Combobox(right_frame, textvariable=script_var, 
                                   values=[s.get("name", "") for s in self.scripts], state="readonly")
        script_combo.pack(fill="x", pady=5)
        
        # Current tags
        ttk.Label(right_frame, text="Current Tags (comma-separated):").pack(anchor="w", pady=5)
        current_tags_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=current_tags_var, width=30).pack(fill="x", pady=5)
        
        def load_script_tags():
            script_name = script_var.get()
            if script_name:
                for s in self.scripts:
                    if s.get("name") == script_name:
                        current_tags_var.set(s.get("tags", ""))
                        break
        
        def save_script_tags():
            script_name = script_var.get()
            if script_name:
                for s in self.scripts:
                    if s.get("name") == script_name:
                        s["tags"] = current_tags_var.get()
                        self._save_config()
                        self._refresh_tree()
                        messagebox.showinfo("", "Tags saved successfully")
                        self._log_structured("info", f"Tags updated for script: {script_name}")
                        break
        
        def add_tag_to_script():
            selection = tag_listbox.curselection()
            if selection:
                tag = tag_listbox.get(selection[0])
                current_tags = current_tags_var.get().split(",")
                current_tags = [t.strip() for t in current_tags if t.strip()]
                if tag not in current_tags:
                    current_tags.append(tag)
                    current_tags_var.set(", ".join(current_tags))
        
        script_combo.bind("<<ComboboxSelected>>", lambda e: load_script_tags())
        
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Add Selected Tag", command=add_tag_to_script).pack(side="left", fill="x", expand=True)
        ttk.Button(button_frame, text="Save Tags", command=save_script_tags).pack(side="left", fill="x", expand=True)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(tag_window)
        bottom_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        def create_new_tag():
            new_tag = simpledialog.askstring("New Tag", "Enter new tag name:")
            if new_tag:
                new_tag = new_tag.strip()
                if new_tag and new_tag not in all_tags:
                    tag_listbox.insert("end", new_tag)
                    all_tags.add(new_tag)
        
        ttk.Button(bottom_frame, text="Create New Tag", command=create_new_tag).pack(side="left")
        ttk.Button(bottom_frame, text="Close", command=tag_window.destroy).pack(side="right")

    def _setup_quick_actions_toolbar(self):
        """Setup quick actions toolbar"""
        if hasattr(self, '_quick_toolbar'):
            return
        
        C = THEMES.get(self.theme_name, THEMES["light"])
        self._quick_toolbar = tk.Frame(self, bg=C["bg_panel"] if C.get("bg_panel") else "#f0f0f0", height=40)
        self._quick_toolbar.pack(side="top", fill="x", padx=5, pady=5)
        self._quick_toolbar.pack_propagate(False)
        
        ttk.Label(self._quick_toolbar, text="Quick Actions:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        
        # Quick action buttons
        def quick_run():
            self._run_selected()
        
        def quick_add():
            self._add_script()
        
        def quick_scan():
            self._scan_directory()
        
        def quick_validate():
            selection = self.tree.selection()
            if selection:
                idx = self.tree.index(selection[0])
                if idx < len(self.scripts):
                    script = self.scripts[idx]
                    if _SCRIPT_RUNNER_AVAILABLE:
                        result = self._script_runner.validate_script(script.get("path", ""))
                        messagebox.showinfo("Validation Result", 
                                          f"Valid: {result.is_valid}\nErrors: {len(result.errors)}\nWarnings: {len(result.warnings)}")
        
        def quick_backup():
            selection = self.tree.selection()
            if selection:
                idx = self.tree.index(selection[0])
                if idx < len(self.scripts):
                    script = self.scripts[idx]
                    if _SCRIPT_RUNNER_AVAILABLE:
                        backup = self._script_runner.create_backup(script.get("path", ""))
                        if backup:
                            messagebox.showinfo("Backup", "Backup created successfully")
                        else:
                            messagebox.showerror("Backup", "Failed to create backup")
        
        def quick_search():
            self._show_advanced_search()
        
        ttk.Button(self._quick_toolbar, text="▶ Run", command=quick_run, width=8).pack(side="left", padx=2)
        ttk.Button(self._quick_toolbar, text="+ Add", command=quick_add, width=8).pack(side="left", padx=2)
        ttk.Button(self._quick_toolbar, text="🔍 Scan", command=quick_scan, width=8).pack(side="left", padx=2)
        ttk.Button(self._quick_toolbar, text="✓ Validate", command=quick_validate, width=10).pack(side="left", padx=2)
        ttk.Button(self._quick_toolbar, text="💾 Backup", command=quick_backup, width=10).pack(side="left", padx=2)
        ttk.Button(self._quick_toolbar, text="🔎 Search", command=quick_search, width=10).pack(side="left", padx=2)
        
        # Separator
        ttk.Separator(self._quick_toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Quick filters
        ttk.Label(self._quick_toolbar, text="Filter:").pack(side="left", padx=2)
        
        def filter_favorites():
            self._favorites_filter = not self._favorites_filter
            self.btn_favorites.config(bg=C["btn_active_bg"] if self._favorites_filter and C.get("btn_active_bg") else "#4CAF50" if self._favorites_filter else C["btn_bg"] if C.get("btn_bg") else "#f0f0f0")
            self._refresh_tree()
        
        def filter_pinned():
            # Toggle pinned filter
            if not hasattr(self, '_pinned_filter'):
                self._pinned_filter = False
            self._pinned_filter = not self._pinned_filter
            self._refresh_tree()
        
        ttk.Button(self._quick_toolbar, text="★ Favorites", command=filter_favorites, width=12).pack(side="left", padx=2)
        ttk.Button(self._quick_toolbar, text="📌 Pinned", command=filter_pinned, width=12).pack(side="left", padx=2)

    def _setup_system_notifications(self):
        """Setup system notifications integration"""
        if not hasattr(self, '_notification_enabled'):
            self._notification_enabled = True
        
        if _SCRIPT_RUNNER_AVAILABLE:
            # Register notification callback
            def notification_callback(script_name: str, message: str, status):
                if not self._notification_enabled:
                    return
                
                # Show system notification using plyer if available
                try:
                    from plyer import notification
                    icon_path = str(APP_DIR / "icons" / "psl-ico.ico") if (APP_DIR / "icons" / "psl-ico.ico").exists() else None
                    
                    if status.value == "completed":
                        notification.notify(
                            title=f"✓ {script_name}",
                            message=message,
                            app_name="psLauncher",
                            app_icon=icon_path
                        )
                    elif status.value == "failed":
                        notification.notify(
                            title=f"✗ {script_name}",
                            message=message,
                            app_name="psLauncher",
                            app_icon=icon_path
                        )
                    elif status.value == "timeout":
                        notification.notify(
                            title=f"⏱ {script_name}",
                            message=message,
                            app_name="psLauncher",
                            app_icon=icon_path
                        )
                except Exception:
                    # Fallback to status bar message
                    self._set_status(f"{script_name}: {message}")
            
            self._script_runner.get_notification_manager().register_callback(notification_callback)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Run selected script: Ctrl+R
        self.bind("<Control-r>", lambda e: self._run_selected())
        
        # Add script: Ctrl+N
        self.bind("<Control-n>", lambda e: self._add_script())
        
        # Scan directory: Ctrl+S
        self.bind("<Control-s>", lambda e: self._scan_directory())
        
        # Search: Ctrl+F
        self.bind("<Control-f>", lambda e: (self.entry_search.focus(), self._show_advanced_search()))
        
        # Quick validate: Ctrl+V
        self.bind("<Control-v>", lambda e: self._show_script_validator())
        
        # Tag manager: Ctrl+T
        self.bind("<Control-t>", lambda e: self._show_tag_manager())
        
        # Backup manager: Ctrl+B
        self.bind("<Control-b>", lambda e: self._show_backup_manager())
        
        # Task scheduler: Ctrl+Shift+S
        self.bind("<Control-Shift-S>", lambda e: self._show_task_scheduler())
        
        # Execution history: Ctrl+H
        self.bind("<Control-h>", lambda e: self._show_execution_history())
        
        # Script templates: Ctrl+Shift+T
        self.bind("<Control-Shift-T>", lambda e: self._show_script_templates())
        
        # Toggle favorites: Ctrl+F (already used for search, use Ctrl+Shift+F)
        self.bind("<Control-Shift-F>", lambda e: self._toggle_favorites())
        
        # Delete selected: Delete key
        self.bind("<Delete>", lambda e: self._remove_selected())
        
        # Edit selected: Ctrl+E
        self.bind("<Control-e>", lambda e: self._edit_selected())
        
        # Refresh: F5
        self.bind("<F5>", lambda e: self._refresh_tree())
        
        # Close window: Ctrl+Q
        self.bind("<Control-q>", lambda e: self.quit())
        
        # Open sandbox: Ctrl+Shift+O
        self.bind("<Control-Shift-O>", lambda e: self._open_sandbox())
        
        # Toggle debugger: Ctrl+Shift+D
        self.bind("<Control-Shift-D>", lambda e: self._toggle_debugger())

    def _toggle_favorites(self):
        """Toggle favorites filter"""
        self._favorites_filter = not self._favorites_filter
        self.btn_favorites.config(bg=C["btn_active_bg"] if self._favorites_filter and C.get("btn_active_bg") else "#4CAF50" if self._favorites_filter else C["btn_bg"] if C.get("btn_bg") else "#f0f0f0")
        self._refresh_tree()

    def _start_profiling(self):
        """Start CPU profiling."""
        if not _DEBUGGER_AVAILABLE or not self._debugger_enabled or not self._profiler:
            messagebox.showwarning("", "Debugger not enabled or available")
            return
        
        try:
            self._profiler.start_cpu_profiling()
            self._log_structured("info", "CPU profiling started")
            self._set_status("✔ CPU profiling started")
        except Exception as e:
            messagebox.showerror("", f"Failed to start profiling: {e}")
            self._log_structured("error", f"Failed to start profiling: {e}")

    def _stop_profiling(self):
        """Stop CPU profiling and show results."""
        if not _DEBUGGER_AVAILABLE or not self._debugger_enabled or not self._profiler:
            messagebox.showwarning("", "Debugger not enabled or available")
            return
        
        try:
            results = self._profiler.stop_cpu_profiling()
            self._log_structured("info", "CPU profiling stopped")
            self._set_status("✔ CPU profiling stopped")
            
            # Show results in a dialog
            report = self._profiler.get_cpu_profiling_report()
            self._show_profiling_results(report)
        except Exception as e:
            messagebox.showerror("", f"Failed to stop profiling: {e}")
            self._log_structured("error", f"Failed to stop profiling: {e}")

    def _show_profiling_results(self, report: str):
        """Show profiling results in a dialog."""
        result_window = tk.Toplevel(self)
        result_window.title("Profiling Results")
        result_window.geometry("800x600")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = tk.Scrollbar(result_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", report)
        text_widget.config(state="disabled")

    def _show_notification(self, title: str, message: str):
        """Show system notification if enabled."""
        if not self._notifications_enabled:
            return
        self._send_notification(title, message)

    def _toggle_log_window(self):
        """Toggle between docked and undocked log window."""
        if self._log_docked:
            # Undock - create separate window
            self._undock_log()
        else:
            # Dock - return to main window
            self._dock_log()

    def _undock_log(self):
        """Undock log into a separate floating window."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        T = TRANSLATIONS[self.lang]
        
        # Create new toplevel window
        self._log_window = tk.Toplevel(self)
        self._log_window.title(f"psLauncher - {T.get('log_title', 'Execution log')}")
        self._log_window.geometry("800x500")
        self._log_window.configure(bg=C["bg_main"])
        
        # Handle window close button - dock instead of destroy
        self._log_window.protocol("WM_DELETE_WINDOW", self._dock_log)
        
        # Header frame
        hdr = tk.Frame(self._log_window, bg=C["bg_panel"])
        hdr.pack(fill="x", padx=8, pady=8)
        
        tk.Label(hdr, text=T.get('log_title', 'Execution log'),
                bg=C["bg_panel"], fg=C["fg_accent"],
                font=("Consolas", 9, "bold")).pack(side="left")
        
        # Dock button
        tk.Button(hdr, text="🔒",
                 bg=C["bg_panel"], fg=C["fg_dim"],
                 relief="flat", font=("Segoe UI Emoji", 9),
                 padx=4, pady=2, cursor="hand2", borderwidth=0,
                 command=self._dock_log).pack(side="right")
        
        # Copy button
        tk.Button(hdr, text="📋",
                 bg=C["bg_panel"], fg=C["fg_dim"],
                 relief="flat", font=("Segoe UI Emoji", 9),
                 padx=4, pady=2, cursor="hand2", borderwidth=0,
                 command=self._copy_log).pack(side="right")
        
        # Export button
        tk.Button(hdr, text="💾",
                 bg=C["bg_panel"], fg=C["fg_dim"],
                 relief="flat", font=("Segoe UI Emoji", 9),
                 padx=4, pady=2, cursor="hand2", borderwidth=0,
                 command=self._export_log).pack(side="right")
        
        # Log frame
        log_frame = tk.Frame(self._log_window, bg=C["bg_log"])
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Create new text widget for undocked window
        self._undocked_log_text = tk.Text(
            log_frame,
            bg=C["bg_log"], fg=C["log_stdout"],
            font=("Consolas", 9),
            relief="flat", state="disabled",
            wrap="none",
            padx=6, pady=4,
            cursor="xterm",
            selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
        )
        
        # Scrollbars
        log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self._undocked_log_text.yview, style="Vertical.TScrollbar")
        log_hsb = ttk.Scrollbar(log_frame, orient="horizontal", command=self._undocked_log_text.xview, style="Horizontal.TScrollbar")
        self._undocked_log_text.configure(yscrollcommand=log_vsb.set, xscrollcommand=log_hsb.set)
        
        self._undocked_log_text.pack(side="left", fill="both", expand=True)
        log_vsb.pack(side="right", fill="y")
        log_hsb.pack(side="bottom", fill="x")
        
        # Copy content from original log
        original_content = self.log_text.get("1.0", "end-1c")
        self._undocked_log_text.config(state="normal")
        self._undocked_log_text.insert("1.0", original_content)
        self._undocked_log_text.config(state="disabled")
        
        # Apply tags
        self._apply_log_tags_to_widget(self._undocked_log_text)
        
        # Hide original log frame
        self.log_text.master.pack_forget()
        
        # Update state
        self._log_docked = False
        self.btn_log_undock.config(text="🔒")
        self._set_status("🔓 Log undocked")

    def _dock_log(self):
        """Dock log back to main window."""
        if self._log_window:
            self._log_window.destroy()
            self._log_window = None
        
        # Move the undocked text widget back to the original frame
        if hasattr(self, '_undocked_log_text') and self._undocked_log_text:
            try:
                # Get the original log frame
                C = THEMES.get(self.theme_name, THEMES["light"])
                log_frame = tk.Frame(self.frm_right, bg=C["bg_log"])
                log_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
                
                # Move the widget back
                self._undocked_log_text.pack(in_=log_frame, side="left", fill="both", expand=True)
                
                # Restore it as the main log_text
                self.log_text = self._undocked_log_text
                self._undocked_log_text = None
                
                # Recreate scrollbars if needed
                log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview, style="Vertical.TScrollbar")
                log_hsb = ttk.Scrollbar(log_frame, orient="horizontal", command=self.log_text.xview, style="Horizontal.TScrollbar")
                self.log_text.configure(yscrollcommand=log_vsb.set, xscrollcommand=log_hsb.set)
                
                log_vsb.pack(side="right", fill="y")
                log_hsb.pack(side="bottom", fill="x")
            except tk.TclError:
                # If moving fails, recreate the widget
                C = THEMES.get(self.theme_name, THEMES["light"])
                log_frame = tk.Frame(self.frm_right, bg=C["bg_log"])
                log_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
                
                self.log_text = tk.Text(
                    log_frame,
                    bg=C["bg_log"], fg=C["log_stdout"],
                    font=("Consolas", 9),
                    relief="flat", state="disabled",
                    wrap="none",
                    height=10,
                    padx=6, pady=4,
                    cursor="xterm",
                    selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
                )
                
                log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview, style="Vertical.TScrollbar")
                log_hsb = ttk.Scrollbar(log_frame, orient="horizontal", command=self.log_text.xview, style="Horizontal.TScrollbar")
                self.log_text.configure(yscrollcommand=log_vsb.set, xscrollcommand=log_hsb.set)
                
                self.log_text.pack(side="left", fill="both", expand=True)
                log_vsb.pack(side="right", fill="y")
                log_hsb.pack(side="bottom", fill="x")
                
                self._apply_log_tags()
                self._undocked_log_text = None
        
        # Update state
        self._log_docked = True
        self.btn_log_undock.config(text="🔓")
        self._set_status("🔒 Log docked")

    def _apply_log_tags_to_widget(self, widget):
        """Apply log coloring tags to a specific text widget."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        widget.tag_config("log_stdout", foreground=C["log_stdout"])
        widget.tag_config("log_error", foreground=C["log_error"])
        widget.tag_config("log_warning", foreground=C["log_warning"])
        widget.tag_config("log_success", foreground=C["log_success"])
        widget.tag_config("log_meta", foreground=C["log_meta"])
        widget.tag_config("log_restart", foreground=C["log_restart"])
        widget.tag_config("log_sched", foreground=C["log_sched"])

    # ── REQUIREMENTS INSTALL ────────────────────────
    def _install_requirements(self):
        """Otwiera dialog wyboru pliku requirements.txt i instaluje biblioteki przez pip."""
        T = TRANSLATIONS[self.lang]

        # Sprawdź dostępność pip
        pip_cmd = [sys.executable, "-m", "pip"]
        try:
            subprocess.run(pip_cmd + ["--version"], capture_output=True, timeout=10, check=True)
        except Exception:
            self._log(T.get("req_pip_missing", "❌  pip nie jest dostępny w tym środowisku."), "error")
            return

        path_str = filedialog.askopenfilename(
            title=T.get("req_select_title", "Wybierz plik requirements"),
            filetypes=[("requirements.txt", "*.txt"), ("Wszystkie pliki", "*.*")],
        )
        if not path_str:
            return

        req_path = Path(path_str)

        # Okno dialogowe z logiem instalacji
        dlg = tk.Toplevel(self)
        dlg.title(T.get("req_dlg_title", "Instalacja bibliotek"))
        dlg.geometry("700x420")
        dlg.resizable(True, True)
        C = THEMES[self.theme]
        dlg.configure(bg=C["bg"])
        dlg.grab_set()

        hdr_text = T.get("req_installing", "Instalowanie z:") + " " + req_path.name
        hdr = tk.Label(dlg, text=hdr_text,
                       bg=C["bg"], fg=C["fg_header"], font=("Consolas", 10, "bold"), anchor="w")
        hdr.pack(fill="x", padx=10, pady=(10, 4))

        txt = tk.Text(dlg, bg=C["log_bg"], fg=C["log_fg"], font=("Consolas", 9),
                      state="disabled", wrap="none", relief="flat", borderwidth=0)
        sb_y = ttk.Scrollbar(dlg, command=txt.yview, style="Vertical.TScrollbar")
        txt.configure(yscrollcommand=sb_y.set)
        sb_y.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True, padx=(10, 0), pady=4)

        btn_close = tk.Button(dlg, text="✖  Zamknij", state="disabled",
                              bg=C.get("btn_bg", C["bg"]), fg=C["fg"],
                              relief="flat", cursor="hand2",
                              command=dlg.destroy)
        btn_close.pack(pady=(4, 10))

        def _append(line: str) -> None:
            txt.config(state="normal")
            txt.insert("end", line + "\n")
            txt.see("end")
            txt.config(state="disabled")

        def _run_install() -> None:
            cmd = pip_cmd + ["install", "-r", str(req_path)]
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                for line in proc.stdout:
                    self.after(0, lambda l=line.rstrip(): _append(l))
                proc.wait()
                rc = proc.returncode
                if rc == 0:
                    msg = T.get("req_done_ok", "✅  Instalacja zakończona pomyślnie.")
                else:
                    msg = T.get("req_done_err", "❌  pip zakończył się kodem:") + " " + str(rc)
                self.after(0, lambda m=msg: _append(m))
            except Exception as exc:
                self.after(0, lambda e=exc: _append(f"❌  {e}"))
            finally:
                self.after(0, lambda: btn_close.config(state="normal"))

        threading.Thread(target=_run_install, daemon=True).start()

    # ── PANEL TOGGLE ────────────────────────
    def _toggle_panel(self):
        T = TRANSLATIONS[self.lang]
        if self.panel_visible:
            self.paned.forget(self.frm_right)
            self.panel_visible = False
            self.btn_toggle_panel.config(text=T["btn_show_panel"])
        else:
            self.paned.add(self.frm_right, minsize=200, after=self.frm_left)
            self.panel_visible = True
            self.btn_toggle_panel.config(text=T["btn_hide_panel"])

    # ── SANDBOX ─────────────────────────────
    def _make_sandbox_theme(self) -> dict:
        """Mapuje klucze motywu psLauncher na format oczekiwany przez SandboxWindow."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        return {
            "DARK":    C.get("bg_main",   "#eff1f5"),
            "PANEL":   C.get("bg_panel",  "#e6e9ef"),
            "CARD":    C.get("bg_btn",    "#ccd0da"),
            "TEXT":    C.get("fg_main",   "#4c4f69"),
            "DIM":     C.get("fg_dim",    "#8c8fa1"),
            "ACCENT":  C.get("fg_accent", "#7287fd"),
            "ACCENT2": C.get("fg_link",   "#209fb5"),
            "RED":     C.get("btn_del_bg","#d20f39"),
            "YELLOW":  "#df8e1d",
            "BG":      C.get("bg_main",   "#eff1f5"),
        }

    def _open_sandbox(self):
        """Otwiera okno Sandbox."""
        if not _SANDBOX_AVAILABLE:
            T = TRANSLATIONS[self.lang]
            messagebox.showwarning(
                T.get("menu_sandbox", "Sandbox"),
                "Moduł sandbox.py nie jest dostępny.\n"
                "Upewnij się, że sandbox.py znajduje się w tym samym katalogu co psLauncher.py."
            )
            return
        theme = self._make_sandbox_theme()
        _sandbox_mod.open_sandbox(self, theme)

    def _sandbox_show_runners(self):
        """Otwiera Sandbox i wpisuje komendę 'runners'."""
        if not _SANDBOX_AVAILABLE:
            self._open_sandbox()  # pokaże ostrzeżenie
            return
        theme = self._make_sandbox_theme()
        win = _sandbox_mod.open_sandbox(self, theme)
        # Po utworzeniu okna wyślij polecenie runners
        def _send_runners():
            win._input_var.set("runners")
            win._run_command()
        win.after(150, _send_runners)

    def _open_sandbox_with_file(self, path: str):
        """Otwiera Sandbox i uruchamia w nim dowolny plik podany z zewnatrz
        (np. z menu kontekstowego Eksploratora Windows: 'Uruchom w Sandbox').
        W odroznieniu od _run_in_sandbox nie wymaga, by plik byl juz dodany
        do biblioteki self.scripts — interpreter jest zgadywany na podstawie
        rozszerzenia (DEFAULT_INTERPRETERS)."""
        T = TRANSLATIONS[self.lang]
        if not _SANDBOX_AVAILABLE:
            messagebox.showwarning(
                T.get("menu_sandbox", "Sandbox"),
                "Modul sandbox.py nie jest dostepny.\n"
                "Upewnij sie, ze sandbox.py znajduje sie w tym samym katalogu co psLauncher.py."
            )
            return
        if not path or not os.path.isfile(path):
            messagebox.showwarning("", T["msg_not_found"] + str(path))
            return

        ext        = Path(path).suffix.lower()
        is_windows = platform.system() == "Windows"
        is_ps1     = ext == ".ps1"
        interp     = DEFAULT_INTERPRETERS.get(ext, "")
        ps_policy  = "Bypass"

        cmd = None
        if ext in (".bat", ".cmd"):
            cmd = (["cmd.exe", "/c", path] if is_windows
                   else [self._find_tool("bash", "sh") or "bash", path])
        elif ext == ".vbs":
            cmd = (["cscript.exe", "//Nologo", path] if is_windows else None)
        elif is_ps1:
            ps_exe = self._find_tool(interp, "pwsh", "powershell.exe", "powershell") or interp or "pwsh"
            cmd = [ps_exe, "-ExecutionPolicy", ps_policy, "-File", path]
        elif ext == ".go":
            cmd = [self._find_tool(interp, "go") or interp or "go", "run", path]
        elif ext == ".awk":
            cmd = [self._find_tool(interp, "awk", "gawk", "mawk") or interp or "awk", "-f", path]
        elif ext == ".sed":
            cmd = [self._find_tool(interp, "sed", "gsed") or interp or "sed", "-f", path]
        elif ext == ".swift":
            cmd = [self._find_tool(interp, "swift") or interp or "swift", path]
        elif ext == ".ts":
            cmd = [self._find_tool(interp, "ts-node", "tsx") or interp or "ts-node", path]
        elif interp:
            cmd = [self._find_tool(interp) or interp, path]
        else:
            cmd = [path]

        if not cmd:
            messagebox.showwarning("", T["msg_error"] + " — nie mozna ustalic komendy dla tego typu pliku.")
            return

        cmd_str = subprocess.list2cmdline(cmd)

        # Bring main window to front, then open sandbox and inject the command
        self.deiconify()
        self.lift()
        self.focus_force()
        theme = self._make_sandbox_theme()
        win = _sandbox_mod.open_sandbox(self, theme)

        def _send_cmd():
            win._input_var.set(cmd_str)
            win._run_command()
        win.after(150, _send_cmd)

    def _run_in_sandbox(self):
        """Otwiera Sandbox i uruchamia w nim zaznaczony skrypt."""
        T = TRANSLATIONS[self.lang]
        if not _SANDBOX_AVAILABLE:
            messagebox.showwarning(
                T.get("menu_sandbox", "Sandbox"),
                "Moduł sandbox.py nie jest dostępny.\n"
                "Upewnij się, że sandbox.py znajduje się w tym samym katalogu co psLauncher.py."
            )
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("", T["msg_no_selection"])
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        path = s.get("path", "")
        if not path or not os.path.isfile(path):
            messagebox.showwarning("", T["msg_not_found"] + path)
            return

        ext        = Path(path).suffix.lower()
        is_windows = platform.system() == "Windows"
        is_ps1     = ext == ".ps1"
        interp     = s.get("interpreter", DEFAULT_INTERPRETERS.get(ext, ""))
        args       = s.get("args", "")
        ps_policy  = s.get("ps_exec_policy", "Bypass")

        # Apply active profile overrides
        active_profile_name = s.get("active_profile", "")
        if active_profile_name:
            for p in s.get("profiles", []):
                if p["name"] == active_profile_name:
                    if p.get("args"):        args   = p["args"]
                    if p.get("interpreter"): interp = p["interpreter"]
                    break

        # Build command list (mirrors _run_script / _dry_run_selected logic)
        cmd = None
        if ext in (".bat", ".cmd"):
            cmd = (["cmd.exe", "/c", path] if is_windows
                   else [self._find_tool("bash", "sh") or "bash", path])
        elif ext == ".vbs":
            cmd = (["cscript.exe", "//Nologo", path] if is_windows else None)
        elif is_ps1:
            ps_exe = self._find_tool(interp, "pwsh", "powershell.exe", "powershell") or interp or "pwsh"
            cmd = [ps_exe, "-ExecutionPolicy", ps_policy, "-File", path]
        elif ext == ".go":
            cmd = [self._find_tool(interp, "go") or interp or "go", "run", path]
        elif ext == ".awk":
            cmd = [self._find_tool(interp, "awk", "gawk", "mawk") or interp or "awk", "-f", path]
        elif ext == ".sed":
            cmd = [self._find_tool(interp, "sed", "gsed") or interp or "sed", "-f", path]
        elif ext == ".swift":
            cmd = [self._find_tool(interp, "swift") or interp or "swift", path]
        elif ext == ".ts":
            cmd = [self._find_tool(interp, "ts-node", "tsx") or interp or "ts-node", path]
        elif interp:
            cmd = [self._find_tool(interp) or interp, path]
        else:
            cmd = [path]

        if cmd and args:
            cmd += shlex.split(args, posix=(not is_windows))

        if not cmd:
            messagebox.showwarning("", T["msg_error"] + " — nie można ustalić komendy dla tego typu pliku.")
            return

        cmd_str = subprocess.list2cmdline(cmd)

        # Open sandbox and inject the command
        theme = self._make_sandbox_theme()
        win = _sandbox_mod.open_sandbox(self, theme)

        def _send_cmd():
            win._input_var.set(cmd_str)
            win._run_command()
        win.after(150, _send_cmd)

    # ── SETTINGS DIALOG ─────────────────────
    def _show_settings(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        S = self.app_settings          # shorthand

        dlg = tk.Toplevel(self)
        dlg.title(T.get("settings_title", "Settings – psLauncher"))
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.resizable(False, False)

        # ── Notebook (tabs) ──────────────────────────────
        nb_style = ttk.Style(dlg)
        nb_style.configure("Settings.TNotebook",       background=C["bg_main"])
        nb_style.configure("Settings.TNotebook.Tab",   background=C["bg_panel"],
                           foreground=C["fg_main"], padding=[10, 4])
        nb_style.map("Settings.TNotebook.Tab",
                     background=[("selected", C["bg_btn"])],
                     foreground=[("selected", C["fg_main"])])

        nb = ttk.Notebook(dlg, style="Settings.TNotebook")
        nb.pack(fill="both", expand=True, padx=12, pady=(10, 4))

        fg  = C["fg_main"]
        bg  = C["bg_main"]
        bpb = C["bg_panel"]
        fnt = ("Consolas", 9)
        fnt_b = ("Consolas", 9, "bold")

        def _frame(parent):
            f = tk.Frame(parent, bg=bg, padx=16, pady=12)
            f.pack(fill="both", expand=True)
            return f

        def _lbl(parent, text, bold=False, row=None, col=0, pady=3):
            l = tk.Label(parent, text=text, bg=bg, fg=fg,
                         font=fnt_b if bold else fnt, anchor="w")
            if row is not None:
                l.grid(row=row, column=col, sticky="w", pady=pady, padx=(0,8))
            else:
                l.pack(anchor="w", pady=2)
            return l

        def _sep(parent):
            tk.Frame(parent, bg=C.get("border","#555"), height=1).pack(
                fill="x", pady=8)

        # ─────────────────────────────────────
        # TAB 1 – OGÓLNE
        # ─────────────────────────────────────
        tab_gen = tk.Frame(nb, bg=bg)
        nb.add(tab_gen, text=T.get("settings_tab_general", "General"))
        fg_gen = _frame(tab_gen)
        fg_gen.columnconfigure(1, weight=1)

        # Język
        _lbl(fg_gen, T.get("settings_lang", "Language:"), row=0)
        var_lang = tk.StringVar(value=self.lang)
        frm_lang = tk.Frame(fg_gen, bg=bg)
        frm_lang.grid(row=0, column=1, sticky="w", pady=3)
        tk.Radiobutton(frm_lang, text="Polski", variable=var_lang, value="pl",
                       bg=bg, fg=fg, selectcolor=bpb, font=fnt,
                       activebackground=bg).pack(side="left", padx=(0,10))
        tk.Radiobutton(frm_lang, text="English", variable=var_lang, value="en",
                       bg=bg, fg=fg, selectcolor=bpb, font=fnt,
                       activebackground=bg).pack(side="left")

        # Potwierdzenie usunięcia
        var_confirm_del = tk.BooleanVar(value=S.get("confirm_delete", True))
        tk.Checkbutton(fg_gen, text=T.get("settings_confirm_delete","Confirm before removing"),
                       variable=var_confirm_del, bg=bg, fg=fg, selectcolor=bpb,
                       activebackground=bg, font=fnt).grid(
                       row=2, column=0, columnspan=2, sticky="w", pady=3)

        # Zapis przy zamknięciu
        var_save_exit = tk.BooleanVar(value=S.get("save_on_exit", True))
        tk.Checkbutton(fg_gen, text=T.get("settings_save_on_exit","Save config on exit"),
                       variable=var_save_exit, bg=bg, fg=fg, selectcolor=bpb,
                       activebackground=bg, font=fnt).grid(
                       row=3, column=0, columnspan=2, sticky="w", pady=3)

        # Autostart (Windows only)
        var_autostart = tk.BooleanVar(value=S.get("autostart", False))
        cb_autostart = tk.Checkbutton(
            fg_gen, text=T.get("settings_autostart","Launch with Windows startup"),
            variable=var_autostart, bg=bg, fg=fg, selectcolor=bpb,
            activebackground=bg, font=fnt,
            state="normal" if platform.system() == "Windows" else "disabled")
        cb_autostart.grid(row=4, column=0, columnspan=2, sticky="w", pady=3)

        # ─────────────────────────────────────
        # TAB 2 – ŚCIEŻKI
        # ─────────────────────────────────────
        tab_paths = tk.Frame(nb, bg=bg)
        nb.add(tab_paths, text=T.get("settings_tab_paths", "Paths"))
        fp = _frame(tab_paths)

        _lbl(fp, T.get("settings_work_dir", "Working directory:"), bold=True)
        var_work_dir = tk.StringVar(value=S.get("work_dir", str(APP_DIR)))
        frm_wd = tk.Frame(fp, bg=bg)
        frm_wd.pack(fill="x", pady=(2,0))
        ent_wd = tk.Entry(frm_wd, textvariable=var_work_dir, font=fnt,
                          bg=bpb, fg=fg, insertbackground=fg,
                          relief="flat", bd=4, width=44)
        ent_wd.pack(side="left", fill="x", expand=True)

        def _browse_wd():
            d = filedialog.askdirectory(initialdir=var_work_dir.get() or str(APP_DIR))
            if d:
                var_work_dir.set(d)
        tk.Button(frm_wd, text=T.get("settings_work_dir_browse","Change…"),
                  bg=C["bg_btn"], fg=fg, font=fnt, relief="flat",
                  cursor="hand2", padx=8, command=_browse_wd).pack(side="left", padx=(6,0))

        tk.Label(fp, text=T.get("settings_work_dir_hint",
                 "(requires restart; existing files will be copied)"),
                 bg=bg, fg=C.get("fg_dim", "#888"), font=("Consolas",8)).pack(anchor="w", pady=(2,6))

        var_migrate = tk.BooleanVar(value=True)
        tk.Checkbutton(fp, text=T.get("settings_work_dir_migrate","Copy existing files to new directory"),
                       variable=var_migrate, bg=bg, fg=fg, selectcolor=bpb,
                       activebackground=bg, font=fnt).pack(anchor="w", pady=2)

        _sep(fp)
        _lbl(fp, "Config: " + self.CONFIG_FILE, bold=False)
        _lbl(fp, "APP_DIR: " + str(APP_DIR), bold=False)

        # ─────────────────────────────────────
        # TAB 3 – URUCHAMIANIE
        # ─────────────────────────────────────
        tab_run = tk.Frame(nb, bg=bg)
        nb.add(tab_run, text=T.get("settings_tab_run","Execution"))
        fr = _frame(tab_run)
        fr.columnconfigure(1, weight=1)

        _lbl(fr, T.get("settings_default_timeout","Default timeout [s] (0=none):"), row=0)
        var_timeout = tk.IntVar(value=S.get("default_timeout", 0))
        tk.Spinbox(fr, from_=0, to=86400, textvariable=var_timeout, width=8,
                   bg=bpb, fg=fg, insertbackground=fg, font=fnt,
                   buttonbackground=bpb, relief="flat").grid(
                   row=0, column=1, sticky="w", pady=3)

        _lbl(fr, T.get("settings_default_retries","Default auto-restart retries:"), row=1)
        var_retries = tk.IntVar(value=S.get("default_retries", 3))
        tk.Spinbox(fr, from_=0, to=99, textvariable=var_retries, width=8,
                   bg=bpb, fg=fg, insertbackground=fg, font=fnt,
                   buttonbackground=bpb, relief="flat").grid(
                   row=1, column=1, sticky="w", pady=3)

        var_def_restart = tk.BooleanVar(value=S.get("default_restart", False))
        tk.Checkbutton(fr, text=T.get("settings_default_restart","Enable auto-restart by default"),
                       variable=var_def_restart, bg=bg, fg=fg, selectcolor=bpb,
                       activebackground=bg, font=fnt).grid(
                       row=2, column=0, columnspan=2, sticky="w", pady=3)

        _lbl(fr, T.get("settings_default_encoding","Default output encoding:"), row=3)
        var_enc = tk.StringVar(value=S.get("default_encoding","utf-8"))
        enc_cb = ttk.Combobox(fr, textvariable=var_enc, width=14, font=fnt,
                              values=["utf-8","cp1250","cp1252","latin-1","ascii","utf-16"],
                              state="readonly")
        enc_cb.grid(row=3, column=1, sticky="w", pady=3)

        # ─────────────────────────────────────
        # TAB 4 – POWIADOMIENIA
        # ─────────────────────────────────────
        tab_notif = tk.Frame(nb, bg=bg)
        nb.add(tab_notif, text=T.get("settings_tab_notifications","Notifications"))
        fn = _frame(tab_notif)
        fn.columnconfigure(1, weight=1)

        var_notify = tk.BooleanVar(value=S.get("notify_global", True))
        tk.Checkbutton(fn, text=T.get("settings_notify_global","Enable system notifications"),
                       variable=var_notify, bg=bg, fg=fg, selectcolor=bpb,
                       activebackground=bg, font=fnt).grid(
                       row=0, column=0, columnspan=2, sticky="w", pady=3)

        _lbl(fn, T.get("settings_notify_min_sec","Notify only when longer than [s]:"), row=1)
        var_notify_min = tk.IntVar(value=S.get("notify_min_sec", 0))
        tk.Spinbox(fn, from_=0, to=3600, textvariable=var_notify_min, width=8,
                   bg=bpb, fg=fg, insertbackground=fg, font=fnt,
                   buttonbackground=bpb, relief="flat").grid(
                   row=1, column=1, sticky="w", pady=3)

        # ─────────────────────────────────────
        # TAB 5 – INTERFEJS
        # ─────────────────────────────────────
        tab_ui = tk.Frame(nb, bg=bg)
        nb.add(tab_ui, text=T.get("settings_tab_ui","Interface"))
        fu = _frame(tab_ui)
        fu.columnconfigure(1, weight=1)

        var_log_max = tk.IntVar(value=S.get("log_max_lines", 0))
        _lbl(fu, T.get("settings_log_max_lines","Max log lines (0=unlimited):"), row=0)
        tk.Spinbox(fu, from_=0, to=99999, textvariable=var_log_max, width=8,
                   bg=bpb, fg=fg, insertbackground=fg, font=fnt,
                   buttonbackground=bpb, relief="flat").grid(
                   row=0, column=1, sticky="w", pady=3)

        var_panel_start = tk.BooleanVar(value=S.get("panel_on_start", True))
        tk.Checkbutton(fu, text=T.get("settings_panel_on_start","Show side panel on startup"),
                       variable=var_panel_start, bg=bg, fg=fg, selectcolor=bpb,
                       activebackground=bg, font=fnt).grid(
                       row=1, column=0, columnspan=2, sticky="w", pady=3)

        var_row_h = tk.IntVar(value=S.get("tree_row_height", 22))
        _lbl(fu, T.get("settings_tree_row_height","Row height [px]:"), row=2)
        tk.Spinbox(fu, from_=16, to=48, textvariable=var_row_h, width=8,
                   bg=bpb, fg=fg, insertbackground=fg, font=fnt,
                   buttonbackground=bpb, relief="flat").grid(
                   row=2, column=1, sticky="w", pady=3)

        # ── info label at bottom ──────────────────────────────
        lbl_info = tk.Label(dlg, text="", bg=bg, fg=C.get("fg_dim","#888"),
                            font=("Consolas",8))
        lbl_info.pack(fill="x", padx=14, pady=(0,2))

        # ── Buttons ──────────────────────────────────────────
        frm_btn = tk.Frame(dlg, bg=bg)
        frm_btn.pack(fill="x", padx=12, pady=(4,10))

        def _apply(close=False):
            new_lang  = var_lang.get()
            new_theme = var_theme.get()
            new_wd    = var_work_dir.get().strip()

            # Validate work_dir
            if new_wd and new_wd != S.get("work_dir",""):
                # Try to create the directory
                try:
                    Path(new_wd).mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    messagebox.showerror("", f"{T.get('settings_work_dir','Dir')}: {exc}")
                    return

                # Optionally migrate files
                if var_migrate.get():
                    old_dir = Path(S.get("work_dir", str(APP_DIR)))
                    new_dir = Path(new_wd)
                    migrated = []
                    err = None
                    for f in old_dir.glob("pslauncher_config*"):
                        try:
                            shutil.copy2(f, new_dir / f.name)
                            migrated.append(f.name)
                        except Exception as exc:
                            err = exc
                    if err:
                        lbl_info.config(text=T.get("settings_migrate_err","Copy error:") + f" {err}",
                                        fg="#f38ba8")
                    elif migrated:
                        lbl_info.config(text=T.get("settings_migrate_done","Files copied to:") + f" {new_wd}",
                                        fg="#a6e3a1")
                S["work_dir"] = new_wd
                lbl_info.config(text=T.get("settings_restart_needed","Restart required for path change."),
                                fg="#f9e2af")

            # General
            S["confirm_delete"]   = var_confirm_del.get()
            S["save_on_exit"]     = var_save_exit.get()
            S["autostart"]        = var_autostart.get()
            # Execution
            S["default_timeout"]  = var_timeout.get()
            S["default_retries"]  = var_retries.get()
            S["default_restart"]  = var_def_restart.get()
            S["default_encoding"] = var_enc.get()
            # Notifications
            S["notify_global"]    = var_notify.get()
            S["notify_min_sec"]   = var_notify_min.get()
            # UI
            S["log_max_lines"]    = var_log_max.get()
            S["panel_on_start"]   = var_panel_start.get()
            S["tree_row_height"]  = var_row_h.get()

            # Apply autostart (Windows registry)
            if platform.system() == "Windows":
                self._set_autostart(S["autostart"])

            # Apply row height immediately
            try:
                style = ttk.Style()
                style.configure("Treeview", rowheight=S["tree_row_height"])
            except Exception:
                pass

            # Apply lang/theme if changed
            if new_lang != self.lang:
                self._set_lang(new_lang)
            if new_theme != self.theme_name:
                self._apply_theme(new_theme)
                self._set_theme(new_theme)

            # Auto-backup before config changes (v1.7)
            self._create_backup()

            self._schedule_save()
            self._set_status(f"✔ {T.get('settings_title','Settings')} — OK")

            if close:
                dlg.destroy()

        tk.Button(frm_btn, text=T.get("settings_btn_apply","Apply"),
                  bg=C["bg_btn"], fg=fg, font=fnt, relief="flat",
                  cursor="hand2", padx=12, pady=3,
                  command=lambda: _apply(False)).pack(side="left", padx=(0,6))
        tk.Button(frm_btn, text=T.get("settings_btn_ok","OK"),
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], font=fnt_b,
                  relief="flat", cursor="hand2", padx=12, pady=3,
                  command=lambda: _apply(True)).pack(side="left", padx=(0,6))
        tk.Button(frm_btn, text=T.get("settings_btn_cancel","Cancel"),
                  bg=C["bg_btn"], fg=fg, font=fnt, relief="flat",
                  cursor="hand2", padx=12, pady=3,
                  command=dlg.destroy).pack(side="left")

        _center_dialog(dlg)

    def _set_autostart(self, enable: bool):
        """Add/remove psLauncher from Windows startup registry."""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_path = os.path.abspath(sys.argv[0])
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                                0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, "psLauncher", 0, winreg.REG_SZ,
                                      f'"{sys.executable}" "{app_path}"')
                else:
                    try:
                        winreg.DeleteValue(key, "psLauncher")
                    except FileNotFoundError:
                        pass
        except Exception as exc:
            T = TRANSLATIONS[self.lang]
            self._set_status(T.get("settings_autostart_err","Autostart error:") + f" {exc}")

    # ── PS POLICY ───────────────────────────
    def _show_ps_policy(self):
        T = TRANSLATIONS[self.lang]
        current = "N/A"
        if platform.system() == "Windows":
            try:
                r = subprocess.run(
                    ["powershell.exe", "-Command",
                     "Get-ExecutionPolicy -Scope CurrentUser"],
                    capture_output=True, text=True, timeout=5)
                current = r.stdout.strip() or "N/A"
            except Exception:
                pass
        msg = T["msg_ps_policy_info"] + "\n  " + current
        messagebox.showinfo(T["menu_ps_policy"], msg)

    # ── ABOUT / HELP ────────────────────────
    def _show_about(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        dlg = tk.Toplevel(self)
        dlg.title(T["about_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="psLauncher", bg=C["bg_main"], fg=C["fg_accent"],
                 font=("Consolas", 18, "bold")).pack(pady=(18, 2))
        tk.Label(dlg, text=f"v{__version__}", bg=C["bg_main"], fg=C["fg_dim"],
                 font=("Consolas", 9)).pack()
        lic_text = "Licencja: Freeware" if self.lang == "pl" else "License: Freeware"
        tk.Label(dlg, text=lic_text, bg=C["bg_main"], fg=C["fg_dim"],
                 font=("Consolas", 9, "italic")).pack(pady=(2, 0))

        tk.Frame(dlg, bg=C["bg_sep"], height=1).pack(fill="x", padx=20, pady=10)

        info_lbl = tk.Label(dlg, text=T["about_text"],
                            bg=C["bg_main"], fg=C["fg_main"],
                            font=("Consolas", 9), justify="center")
        info_lbl.pack(padx=24, pady=4)

        tk.Frame(dlg, bg=C["bg_sep"], height=1).pack(fill="x", padx=20, pady=10)

        frm_btns = tk.Frame(dlg, bg=C["bg_main"])
        frm_btns.pack(pady=(0, 14))
        tk.Button(frm_btns, text="GitHub",
                  bg=C["bg_btn"], fg=C["fg_accent"],
                  relief="flat", font=("Consolas", 9), padx=10, pady=4,
                  cursor="hand2",
                  command=lambda: webbrowser.open(__github__)).pack(side="left", padx=4)
        tk.Button(frm_btns, text=T["btn_ok"],
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=14, pady=4,
                  cursor="hand2", command=dlg.destroy).pack(side="left", padx=4)

        dlg.bind("<Escape>", lambda e: dlg.destroy())
        _center_dialog(dlg)

    def _show_text_dialog(self, title: str, text: str, geometry: str = "600x500"):
        """Generic themed scrollable text dialog — shared by Help, Shortcuts,
        Features and Description so each only needs its own title/text."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        T = TRANSLATIONS[self.lang]
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry(geometry)

        txt = scrolledtext.ScrolledText(dlg, bg=C["bg_log"], fg=C["fg_main"],
                                         font=("Consolas", 9), relief="flat",
                                         wrap="word", state="normal")
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert("end", text)
        txt.config(state="disabled")

        tk.Button(dlg, text=T["btn_ok"],
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=14, pady=4,
                  cursor="hand2", command=dlg.destroy).pack(pady=(0, 10))

        dlg.bind("<Escape>", lambda e: dlg.destroy())
        _center_dialog(dlg)

    def _show_help(self):
        T = TRANSLATIONS[self.lang]
        self._show_text_dialog(T["help_title"], T["help_text"])

    def _show_shortcuts(self):
        T = TRANSLATIONS[self.lang]
        self._show_text_dialog(T.get("shortcuts_title", "Keyboard shortcuts"),
                               T.get("shortcuts_text", ""))

    def _show_features(self):
        T = TRANSLATIONS[self.lang]
        self._show_text_dialog(T.get("features_title", "Features"),
                               T.get("features_text", ""))

    def _show_description(self):
        T = TRANSLATIONS[self.lang]
        self._show_text_dialog(T.get("desc_title", "Description"),
                               T.get("desc_text", ""), geometry="600x420")

    # ── KEYBOARD SHORTCUTS ──────────────────
    def _bind_keys(self):
        # ── Uruchamianie ────────────────────────────────────────────────────
        self.bind("<F5>",            lambda e: self._run_selected())
        self.bind("<Return>",        lambda e: self._run_selected())
        self.bind("<F6>",            lambda e: self._stop_selected())
        self.bind("<F7>",            lambda e: self._restart_selected())
        self.bind("<Control-Return>", lambda e: self._edit_options())
        # ── Lista skryptów ──────────────────────────────────────────────────
        self.bind("<Control-o>",     lambda e: self._add_script())
        self.bind("<Control-s>",     lambda e: self._open_scan_dialog())
        self.bind("<Delete>",        lambda e: self._remove_selected())
        self.bind("<Control-d>",     lambda e: self._duplicate_selected())
        self.bind("<Control-p>",     lambda e: self._pin_selected_toggle())
        self.bind("<F2>",            lambda e: self._rename_selected())
        # ── Nawigacja / widok ───────────────────────────────────────────────
        self.bind("<Control-f>",     lambda e: self.entry_search.focus_set())
        self.bind("<Escape>",        lambda e: self._search_clear())
        self.bind("<Control-b>",     lambda e: self._toggle_panel())
        self.bind("<Control-l>",     lambda e: self._clear_log())
        self.bind("<F11>",           lambda e: self._toggle_fullscreen())
        # ── Narzędzia / dialogi ─────────────────────────────────────────────
        self.bind("<Control-h>",     lambda e: self._show_history())
        self.bind("<Control-q>",     lambda e: self._show_queue_dialog())
        self.bind("<Control-t>",     lambda e: self._show_scheduler_dialog())
        self.bind("<Control-k>",     lambda e: self._enter_kiosk())
        self.bind("<Control-e>",     lambda e: self._export_log())
        self.bind("<Control-comma>", lambda e: self._show_settings())
        # ── Eksport / import ────────────────────────────────────────────────
        self.bind("<Control-Shift-e>", lambda e: self._export_list())
        self.bind("<Control-Shift-i>", lambda e: self._import_list())
        # ── Pomoc ───────────────────────────────────────────────────────────
        self.bind("<F1>",            lambda e: self._show_help())
        self.bind("<Control-F1>",    lambda e: self._show_about())
        # ── Zamknięcie ──────────────────────────────────────────────────────
        self.bind("<Control-w>",     lambda e: self._on_close())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── SHORTCUT HELPERS ────────────────────────────────────────────────────
    def _pin_selected_toggle(self):
        """Ctrl+P — przełącz pin zaznaczonego skryptu."""
        sel = self.tree.selection()
        if sel:
            self._toggle_pin(int(sel[0]))

    def _search_clear(self):
        """Escape — wyczyść wyszukiwarkę i oddaj focus drzewu."""
        T = TRANSLATIONS[self.lang]
        q = self.var_search.get()
        ph = T["search_placeholder"]
        if q and q != ph:
            self.var_search.set("")
            self._search_focus_out(None)
            self._refresh_tree()
        self.tree.focus_set()

    def _toggle_fullscreen(self):
        """F11 — przełącz tryb pełnoekranowy."""
        current = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current)

    # ── DRAG & DROP ─────────────────────────
    def _setup_dnd(self):
        if not _DND_AVAILABLE:
            return
        # Register drop target on the treeview and the window
        for widget in (self, self.tree):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_dnd_drop)

    def _on_dnd_drop(self, event):
        """Handle files dragged onto the window."""
        raw = event.data
        # tkinterdnd2 wraps paths with spaces in braces on Windows
        import re as _re
        paths = _re.findall(r'\{([^}]+)\}|(\S+)', raw)
        flat = [p[0] or p[1] for p in paths]
        added = 0
        for p in flat:
            p = p.strip()
            if os.path.isfile(p) and Path(p).suffix.lower() in SCRIPT_TYPES:
                self._add_script_entry(p)
                added += 1
        if added:
            self._refresh_tree()
            self._schedule_save()
            T = TRANSLATIONS[self.lang]
            self._set_status(f"✔ +{added} {T['btn_add']}")

    def _on_close(self):
        self._hotkey_mgr.unregister_all()
        # Cancel any pending debounced save and flush synchronously —
        # self.destroy() below would otherwise kill the Tk event loop
        # before a self.after()-scheduled _flush_save() ever fires,
        # silently dropping the last few seconds of changes.
        if self._save_timer_id is not None:
            self.after_cancel(self._save_timer_id)
            self._save_timer_id = None
        if self.app_settings.get("save_on_exit", True):
            self._save_config()
        self.destroy()

    # ── KIOSK ───────────────────────────────
    def _enter_kiosk(self):
        if self._kiosk_win and self._kiosk_win.winfo_exists():
            self._kiosk_win.lift()
            return
        self.withdraw()
        self._kiosk_win = KioskWindow(self)

    # ── HOTKEYS ─────────────────────────────
    def _hotkey_triggered(self, s: dict):
        """Called from keyboard lib thread — schedule run on main thread."""
        self.after(0, lambda: self._run_script_by_entry(s))

    def _run_script_by_entry(self, s: dict):
        path = s.get("path", "")
        if not os.path.exists(path):
            return
        if path in self._running_procs and self._running_procs[path].poll() is None:
            self._set_status(
                f"⚠ {TRANSLATIONS[self.lang].get('msg_already_running', 'Already running:')} "
                f"{s.get('name', '')}")
            return
        threading.Thread(target=self._run_script, args=(s,), daemon=True).start()
        self._set_status(f"⌨ {s.get('name','')} [{s.get('hotkey','')}]")

    # ══════════════════════════════════════════
    #  v1.2  NEW FEATURES
    # ══════════════════════════════════════════

    # ── GROUP BAR ───────────────────────────
    def _rebuild_group_bar(self):
        """Rebuild the horizontal group-filter button row."""
        C = THEMES.get(self.theme_name, THEMES["light"])
        T = TRANSLATIONS[self.lang]
        for w in self._frm_groups.winfo_children():
            w.destroy()
        self._group_btns = []

        all_groups = [("", T["group_all"])] + \
                     [(g, g) for g in self._groups] + \
                     [("__ungrouped__", T["group_ungrouped"])]

        for key, label in all_groups:
            active = (self._active_group == key)
            btn = tk.Button(
                self._frm_groups,
                text=label,
                relief="flat",
                font=("Consolas", 8, "bold" if active else "normal"),
                padx=8, pady=2, cursor="hand2",
                bg=C["fg_accent"] if active else C["bg_btn"],
                fg=C["bg_main"] if active else C["fg_main"],
                command=lambda k=key: self._set_active_group(k),
            )
            btn.pack(side="left", padx=2, pady=2)
            self._group_btns.append(btn)

    def _set_active_group(self, key: str):
        self._active_group = key
        self._rebuild_group_bar()
        self._refresh_tree()

    # ── RENAME ──────────────────────────────
    def _rename_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        s = self.scripts[idx]
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T["dlg_rename_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text=T["dlg_rename_label"],
                 bg=C["bg_main"], fg=C["fg_main"],
                 font=("Consolas", 9)).pack(padx=16, pady=(12, 4), anchor="w")
        var = tk.StringVar(value=s.get("name", ""))
        e = tk.Entry(dlg, textvariable=var, width=36,
                     bg=C["bg_entry"], fg=C["fg_main"],
                     insertbackground=C["insert_fg"],
                     relief="flat", font=("Consolas", 9))
        e.pack(padx=16, pady=4)
        e.select_range(0, "end")
        e.focus_set()

        def _ok():
            new = var.get().strip()
            if new:
                self.scripts[idx]["name"] = new
                self._refresh_tree()
                self._schedule_save()
            dlg.destroy()

        frm = tk.Frame(dlg, bg=C["bg_main"])
        frm.pack(pady=(8, 12))
        tk.Button(frm, text=T["btn_ok"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"),
                  padx=12, pady=3, cursor="hand2", command=_ok).pack(side="left", padx=4)
        tk.Button(frm, text=T["btn_cancel"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9),
                  padx=12, pady=3, cursor="hand2", command=dlg.destroy).pack(side="left", padx=4)
        dlg.bind("<Return>", lambda e: _ok())
        _center_dialog(dlg)

    # ── DUPLICATE ───────────────────────────
    def _duplicate_selected(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        import copy
        orig = self.scripts[idx]
        proposed = orig.get("name", "") + " (kopia)"

        # Small inline dialog for the copy name
        dlg = tk.Toplevel(self)
        dlg.title(T.get("dlg_dup_title", "Duplikuj skrypt"))
        dlg.configure(bg=C["bg_main"])
        dlg.resizable(False, False)
        dlg.grab_set()
        lbl_cfg = {"bg": C["bg_main"], "fg": C["fg_main"], "font": ("Consolas", 9)}
        tk.Label(dlg, text=T.get("dlg_dup_label", "Nazwa kopii:"), **lbl_cfg).grid(
            row=0, column=0, sticky="w", padx=10, pady=(12, 4))
        var_name = tk.StringVar(value=proposed)
        ent = tk.Entry(dlg, textvariable=var_name, width=36,
                       bg=C["bg_entry"], fg=C["fg_main"],
                       insertbackground=C["insert_fg"], relief="flat",
                       font=("Consolas", 9))
        ent.grid(row=0, column=1, padx=(0, 10), pady=(12, 4))
        ent.select_range(0, "end")
        ent.focus_set()

        result = {}

        def _ok(event=None):
            result["name"] = var_name.get().strip() or proposed
            dlg.destroy()

        def _cancel():
            dlg.destroy()

        btn_frm = tk.Frame(dlg, bg=C["bg_main"])
        btn_frm.grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(btn_frm, text=T["btn_ok"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=12, pady=3,
                  cursor="hand2", command=_ok).pack(side="left", padx=4)
        tk.Button(btn_frm, text=T["btn_cancel"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9), padx=12, pady=3,
                  cursor="hand2", command=_cancel).pack(side="left", padx=4)
        ent.bind("<Return>", _ok)
        dlg.bind("<Escape>", lambda e: _cancel())

        _center_dialog(dlg)
        self.wait_window(dlg)

        if not result:
            return
        dup = copy.deepcopy(orig)
        dup["name"]   = result["name"]
        dup["pinned"] = False
        # Reset runtime stats for the copy
        dup["run_count"] = 0
        dup["run_times"] = []
        dup["last_rc"]   = None
        self.scripts.insert(idx + 1, dup)
        self._refresh_tree()
        self._schedule_save()
        self._set_status(f"✔ {T['msg_duplicate_done']} {dup['name']}")

    # ── PIN / UNPIN ─────────────────────────
    def _toggle_pin(self, idx: int):
        T = TRANSLATIONS[self.lang]
        s = self.scripts[idx]
        s["pinned"] = not s.get("pinned", False)
        self._refresh_tree()
        self._schedule_save()
        key = "msg_pinned" if s["pinned"] else "msg_unpinned"
        self._set_status(f"✔ {T[key]} {s.get('name', '')}")

    # ── FAVORITE / UNFAVORITE (v1.7) ───────────
    def _toggle_favorite(self, idx: int):
        T = TRANSLATIONS[self.lang]
        s = self.scripts[idx]
        s["favorite"] = not s.get("favorite", False)
        self._refresh_tree()
        self._schedule_save()
        key = "favorite_add" if s["favorite"] else "favorite_remove"
        self._set_status(f"✔ {T[key]} {s.get('name', '')}")

    # ── FAVORITES FILTER (v1.7) ─────────────────
    def _toggle_favorites_filter(self):
        self._favorites_filter = not self._favorites_filter
        C = THEMES.get(self.theme_name, THEMES["light"])
        if self._favorites_filter:
            self.btn_favorites.config(bg=C["btn_ok_bg"], fg=C["btn_ok_fg"])
        else:
            self.btn_favorites.config(bg=C["bg_btn"], fg=C["fg_main"])
        self._refresh_tree()

    # ── AUTO BACKUP (v1.7) ─────────────────────
    def _create_backup(self):
        """Create a backup of the config file before making changes."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.CONFIG_FILE + f".bak_{timestamp}"
                shutil.copy2(self.CONFIG_FILE, backup_file)
                # Keep only last 5 backups
                backup_dir = os.path.dirname(self.CONFIG_FILE)
                backups = sorted([f for f in os.listdir(backup_dir) if f.startswith(os.path.basename(self.CONFIG_FILE) + ".bak_")])
                while len(backups) > 5:
                    old_backup = os.path.join(backup_dir, backups.pop(0))
                    try:
                        os.remove(old_backup)
                    except Exception:
                        pass
        except Exception:
            pass  # Silently fail on backup errors

    # ── MOVE TO GROUP ───────────────────────
    def _move_to_group(self, idx: int, group: str):
        self.scripts[idx]["group"] = group
        self._refresh_tree()
        self._schedule_save()

    # ── GROUPS MANAGEMENT ───────────────────
    def _new_group(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T["dlg_new_group_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text=T["dlg_new_group_label"],
                 bg=C["bg_main"], fg=C["fg_main"],
                 font=("Consolas", 9)).pack(padx=16, pady=(12, 4), anchor="w")
        var = tk.StringVar()
        e = tk.Entry(dlg, textvariable=var, width=30,
                     bg=C["bg_entry"], fg=C["fg_main"],
                     insertbackground=C["insert_fg"],
                     relief="flat", font=("Consolas", 9))
        e.pack(padx=16, pady=4)
        e.focus_set()

        def _ok():
            name = var.get().strip()
            if name and name not in self._groups:
                self._groups.append(name)
                self._rebuild_group_bar()
                self._schedule_save()
            dlg.destroy()

        frm = tk.Frame(dlg, bg=C["bg_main"])
        frm.pack(pady=(8, 12))
        tk.Button(frm, text=T["btn_ok"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"),
                  padx=12, pady=3, cursor="hand2", command=_ok).pack(side="left", padx=4)
        tk.Button(frm, text=T["btn_cancel"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9),
                  padx=12, pady=3, cursor="hand2", command=dlg.destroy).pack(side="left", padx=4)
        dlg.bind("<Return>", lambda e: _ok())
        _center_dialog(dlg)

    def _manage_groups(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T["dlg_manage_groups_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("320x340")

        lb = tk.Listbox(dlg, bg=C["bg_entry"], fg=C["fg_main"],
                        selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
                        font=("Consolas", 9), relief="flat", borderwidth=0)
        lb.pack(fill="both", expand=True, padx=8, pady=8)
        for g in self._groups:
            lb.insert("end", g)

        def _delete():
            sel = lb.curselection()
            if sel:
                g = lb.get(sel[0])
                # unassign scripts in this group
                for s in self.scripts:
                    if s.get("group") == g:
                        s["group"] = ""
                self._groups.remove(g)
                lb.delete(sel[0])
                self._rebuild_group_bar()
                self._refresh_tree()
                self._schedule_save()

        frm = tk.Frame(dlg, bg=C["bg_main"])
        frm.pack(pady=(0, 10))
        tk.Button(frm, text="➕ " + T["menu_group_new"], bg=C["bg_btn"], fg=C["fg_main"],
                  relief="flat", font=("Consolas", 9), padx=8, pady=3, cursor="hand2",
                  command=lambda: [dlg.destroy(), self._new_group()]).pack(side="left", padx=4)
        tk.Button(frm, text="🗑 " + T["ctx_remove"], bg=C["btn_del_bg"], fg=C["btn_del_fg"],
                  relief="flat", font=("Consolas", 9), padx=8, pady=3, cursor="hand2",
                  command=_delete).pack(side="left", padx=4)
        tk.Button(frm, text=T["btn_ok"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=8, pady=3, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=4)

        _center_dialog(dlg)

    # ── RUN GROUP (sequential) ──────────────
    def _run_active_group(self):
        """Run all visible scripts in the active group sequentially."""
        visible_iids = self.tree.get_children()
        if not visible_iids:
            return
        scripts = []
        for iid in visible_iids:
            idx = int(iid)
            s = self.scripts[idx]
            if os.path.exists(s.get("path", "")):
                scripts.append(s)

        def _run_seq(script_list):
            for s in script_list:
                self._run_script(s)

        threading.Thread(target=_run_seq, args=(scripts,), daemon=True).start()

    # ══════════════════════════════════════════
    #  v1.3  NEW FEATURES
    # ══════════════════════════════════════════

    # ── RUN QUEUE DIALOG ────────────────────
    def _show_queue_dialog(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T.get("dlg_queue_title", "Run queue"))
        dlg.configure(bg=C["bg_main"])
        dlg.geometry("500x380")

        cols = ("name", "status")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse", height=12)
        tree.heading("name",   text=T.get("queue_col_script", "Script"))
        tree.heading("status", text=T.get("queue_col_status", "Status"))
        tree.column("name",   width=320)
        tree.column("status", width=120, anchor="center")
        vsb = ttk.Scrollbar(dlg, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Populate from queue
        status_map: dict[str, tk.StringVar] = {}
        for entry in self._run_queue:
            iid = tree.insert("", "end", values=(
                entry.get("name", ""),
                entry.get("_status", T.get("queue_status_pending", "Pending"))))
            status_map[entry["path"]] = iid

        def _refresh_tree_q():
            for child in tree.get_children():
                tree.delete(child)
            for entry in self._run_queue:
                tree.insert("", "end", values=(
                    entry.get("name", ""),
                    entry.get("_status", T.get("queue_status_pending", "Pending"))))

        def _add_selected():
            sel = self.tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            s = self.scripts[idx].copy()
            s["_status"] = T.get("queue_status_pending", "Pending")
            self._run_queue.append(s)
            _refresh_tree_q()

        def _clear_q():
            self._run_queue.clear()
            _refresh_tree_q()

        def _run_queue_seq():
            T2 = TRANSLATIONS[self.lang]
            for i, entry in enumerate(list(self._run_queue)):
                entry["_status"] = T2.get("queue_status_running", "Running")
                self.after(0, _refresh_tree_q)
                self._run_script(entry)
                rc = self._last_run_info.get("code", 0) if self._last_run_info else 0
                entry["_status"] = (T2.get("queue_status_done", "Done") if rc == 0
                                    else T2.get("queue_status_error", "Error") + f" ({rc})")
                self.after(0, _refresh_tree_q)

        frm = tk.Frame(dlg, bg=C["bg_main"])
        frm.pack(side="bottom", pady=8, fill="x", padx=8)

        def _run_q_thread():
            threading.Thread(target=_run_queue_seq, daemon=True).start()

        btn_cfg = dict(relief="flat", font=("Consolas", 9), padx=10, pady=3, cursor="hand2")
        tk.Button(frm, text=T.get("queue_btn_add", "Add selected"),
                  bg=C["bg_btn"], fg=C["fg_main"], **btn_cfg,
                  command=_add_selected).pack(side="left", padx=4)
        tk.Button(frm, text=T.get("queue_btn_run", "▶  Run queue"),
                  bg=C["btn_run_bg"], fg=C["btn_run_fg"], **btn_cfg,
                  command=_run_q_thread).pack(side="left", padx=4)
        tk.Button(frm, text=T.get("queue_btn_clear", "Clear"),
                  bg=C["btn_del_bg"], fg=C["btn_del_fg"], **btn_cfg,
                  command=_clear_q).pack(side="left", padx=4)
        tk.Button(frm, text=T["btn_ok"],
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=10, pady=3,
                  cursor="hand2", command=dlg.destroy).pack(side="right", padx=4)

        _center_dialog(dlg)

    # ── SCHEDULER DIALOG ────────────────────
    def _show_scheduler_dialog(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T.get("dlg_sched_title", "Scheduler"))
        dlg.configure(bg=C["bg_main"])
        dlg.geometry("620x420")

        cols = ("script", "trigger", "next", "status")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse", height=10)
        tree.heading("script",  text=T.get("sched_col_script", "Script"))
        tree.heading("trigger", text=T.get("sched_col_trigger", "Trigger"))
        tree.heading("next",    text=T.get("sched_col_next", "Next run"))
        tree.heading("status",  text=T.get("sched_col_status", "Status"))
        tree.column("script",  width=200)
        tree.column("trigger", width=140)
        tree.column("next",    width=130)
        tree.column("status",  width=90, anchor="center")
        vsb = ttk.Scrollbar(dlg, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        def _refresh_sched_tree():
            for ch in tree.get_children():
                tree.delete(ch)
            for e in self._schedules:
                nxt = datetime.fromtimestamp(e["next_ts"]).strftime("%Y-%m-%d %H:%M") \
                      if e.get("next_ts") else "—"
                status = (T.get("sched_status_active", "Active") if e.get("active")
                          else T.get("sched_status_inactive", "Inactive"))
                tree.insert("", "end", values=(
                    e.get("name", ""),
                    e.get("trigger_label", ""),
                    nxt,
                    status,
                ))

        _refresh_sched_tree()

        # Add-schedule panel
        frm_add = tk.Frame(dlg, bg=C["bg_panel"])
        frm_add.pack(side="bottom", fill="x", padx=8, pady=4)

        lbl_cfg  = dict(bg=C["bg_panel"], fg=C["fg_main"], font=("Consolas", 9))
        ent_cfg  = dict(bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                        relief="flat", font=("Consolas", 9))

        # Script selector (combo from self.scripts)
        tk.Label(frm_add, text=T.get("sched_col_script", "Script") + ":",
                 **lbl_cfg).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        script_names = [s.get("name", "") for s in self.scripts]
        var_script = tk.StringVar()
        cb_script = ttk.Combobox(frm_add, textvariable=var_script,
                                 values=script_names, width=22, state="readonly")
        cb_script.grid(row=0, column=1, sticky="w", padx=4, pady=2)

        # Trigger type
        tk.Label(frm_add, text=T.get("sched_col_trigger", "Trigger") + ":",
                 **lbl_cfg).grid(row=0, column=2, sticky="w", padx=4, pady=2)
        var_type = tk.StringVar(value="time")
        types = [("time",     T.get("sched_type_time", "At time")),
                 ("interval", T.get("sched_type_interval", "Every N sec"))]
        cb_type = ttk.Combobox(frm_add, textvariable=var_type,
                               values=[v for _, v in types], width=14, state="readonly")
        cb_type.set(types[0][1])
        cb_type.grid(row=0, column=3, sticky="w", padx=4, pady=2)

        # Value (time or interval)
        var_value = tk.StringVar(value="08:00")
        tk.Label(frm_add, text="Value:", **lbl_cfg).grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ent_val = tk.Entry(frm_add, textvariable=var_value, width=12, **ent_cfg)
        ent_val.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        def _type_changed(*_):
            type_idx = [k for k, _ in types].index(
                "interval" if "N sec" in cb_type.get() or "interwał" in cb_type.get().lower()
                else "time")
            if type_idx == 1:
                var_value.set("60")
            else:
                var_value.set("08:00")
        cb_type.bind("<<ComboboxSelected>>", _type_changed)

        def _add_sched():
            name = var_script.get().strip()
            if not name:
                return
            # Find script entry
            script = next((s for s in self.scripts if s.get("name") == name), None)
            if not script:
                return
            raw = var_value.get().strip()
            type_key = "interval" if cb_type.get() in (
                T.get("sched_type_interval"), "Every N sec", "Co N sekund") else "time"
            try:
                if type_key == "time":
                    h, m = map(int, raw.split(":"))
                    now_dt = datetime.now()
                    next_dt = now_dt.replace(hour=h, minute=m, second=0, microsecond=0)
                    if next_dt <= now_dt:
                        next_dt = next_dt.replace(day=next_dt.day + 1)
                    next_ts = next_dt.timestamp()
                    trigger_label = f"@ {raw}"
                else:
                    interval = int(raw)
                    next_ts = time.time() + interval
                    trigger_label = f"every {interval}s"
            except Exception:
                return
            self._schedules.append({
                "name": name, "script": script,
                "type": type_key, "value": raw,
                "next_ts": next_ts,
                "trigger_label": trigger_label,
                "active": True,
            })
            _refresh_sched_tree()

        def _remove_sched():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if 0 <= idx < len(self._schedules):
                del self._schedules[idx]
            _refresh_sched_tree()

        btn_cfg = dict(relief="flat", font=("Consolas", 9), padx=8, pady=3, cursor="hand2")
        tk.Button(frm_add, text=T.get("sched_btn_add", "Add schedule"),
                  bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], **btn_cfg,
                  command=_add_sched).grid(row=1, column=2, padx=4, pady=2)
        tk.Button(frm_add, text=T.get("sched_btn_remove", "Remove"),
                  bg=C["btn_del_bg"], fg=C["btn_del_fg"], **btn_cfg,
                  command=_remove_sched).grid(row=1, column=3, padx=4, pady=2)
        tk.Button(frm_add, text=T.get("sched_btn_close", "Close"),
                  bg=C["bg_btn"], fg=C["fg_main"], **btn_cfg,
                  command=dlg.destroy).grid(row=1, column=4, padx=8, pady=2)

        _center_dialog(dlg)

    # ── SCHEDULER TICK ──────────────────────
    def _scheduler_tick(self):
        """Check schedules every 10 s and fire due entries."""
        now_ts = time.time()
        T = TRANSLATIONS[self.lang]
        for entry in self._schedules:
            if not entry.get("active"):
                continue
            if now_ts >= entry.get("next_ts", float("inf")):
                script = entry.get("script")
                if script and os.path.exists(script.get("path", "")):
                    self.log_queue.put(
                        f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                        f"⏰ {T.get('sched_fired','Scheduler → launched:')} "
                        f"{entry.get('name','')}\n")
                    threading.Thread(
                        target=self._run_script, args=(script,), daemon=True).start()
                # Advance next_ts
                if entry["type"] == "interval":
                    try:
                        interval = int(entry["value"])
                    except ValueError:
                        interval = 60
                    entry["next_ts"] = now_ts + interval
                else:
                    # Daily repeat
                    entry["next_ts"] = entry["next_ts"] + 86400
        self._sched_timer_id = self.after(10_000, self._scheduler_tick)

    # ── EXPORT / IMPORT LIST ────────────────
    # CSV column set: minimal portable fields (no binary/list fields)
    _CSV_FIELDS = [
        "name", "path", "interpreter", "args", "workdir", "encoding",
        "group", "tags", "note", "run_as_admin", "hidden_window", "wait",
        "ps_exec_policy", "auto_restart", "max_retries", "timeout",
        "watchdog_interval", "notify_on_finish", "notify_min_sec", "run_after",
        "hotkey", "kiosk_visible",
    ]

    def _export_list(self):
        T = TRANSLATIONS[self.lang]
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("CSV", "*.csv"), ("All files", "*.*")],
            title=T["menu_export"],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                self._export_csv(path)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"scripts": self.scripts, "groups": self._groups}, f,
                              ensure_ascii=False, indent=2)
                self._set_status(f"✔ {T['export_saved']} {path}")
        except Exception as e:
            messagebox.showerror("", str(e))

    def _export_csv(self, path: str):
        T = TRANSLATIONS[self.lang]
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self._CSV_FIELDS, extrasaction="ignore")
                writer.writeheader()
                for s in self.scripts:
                    writer.writerow({k: s.get(k, "") for k in self._CSV_FIELDS})
            os.replace(tmp_path, path)
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise
        self._set_status(f"✔ {T.get('csv_saved','CSV saved:')} {path}")

    def _import_list(self):
        T = TRANSLATIONS[self.lang]
        path = filedialog.askopenfilename(
            filetypes=[("JSON/CSV", "*.json *.csv"), ("JSON", "*.json"),
                       ("CSV", "*.csv"), ("All files", "*.*")],
            title=T["menu_import"],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                self._import_csv(path)
            else:
                self._import_json(path)
        except Exception as e:
            messagebox.showerror("", str(e))

    def _import_json(self, path: str):
        T = TRANSLATIONS[self.lang]
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        imported = data.get("scripts", [])
        new_groups = data.get("groups", [])
        added = self._merge_scripts(imported)
        for g in new_groups:
            if g not in self._groups:
                self._groups.append(g)
        self._rebuild_group_bar()
        self._refresh_tree()
        self._schedule_save()
        self._hotkey_mgr.reload(self.scripts)
        self._set_status(f"✔ {T['import_loaded']} {added}")

    def _import_csv(self, path: str):
        T = TRANSLATIONS[self.lang]
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Normalise booleans that CSV stores as strings
        bool_fields = {"run_as_admin", "hidden_window", "wait",
                       "auto_restart", "notify_on_finish", "kiosk_visible"}
        int_fields  = {"max_retries", "timeout", "watchdog_interval", "notify_min_sec"}
        imported = []
        for row in rows:
            s = {k: row.get(k, "") for k in self._CSV_FIELDS}
            for bf in bool_fields:
                s[bf] = str(s.get(bf, "")).strip().lower() in ("1", "true", "yes")
            for inf in int_fields:
                try:
                    s[inf] = int(s.get(inf, 0))
                except (ValueError, TypeError):
                    s[inf] = 0
            imported.append(s)
        added = self._merge_scripts(imported)
        self._refresh_tree()
        self._schedule_save()
        self._set_status(f"✔ {T.get('csv_loaded','Loaded from CSV:')} {added}")

    def _merge_scripts(self, incoming: list) -> int:
        """Add incoming script entries, skipping duplicates by path. Returns count added."""
        added = 0
        defaults = {
            "group": "", "pinned": False, "env_vars": "",
            "auto_restart": False, "max_retries": 3, "timeout": 0,
            "tags": "", "note": "", "profiles": [], "active_profile": "",
            "run_count": 0, "run_times": [], "last_rc": None,
            "watchdog_interval": 0, "notify_on_finish": False,
            "notify_min_sec": 0, "run_after": "",
            "hotkey": "", "kiosk_visible": True,
        }
        for s in incoming:
            if not any(x.get("path") == s.get("path") for x in self.scripts):
                for k, v in defaults.items():
                    s.setdefault(k, v)
                self.scripts.append(s)
                added += 1
        return added

    def _export_list_format(self, fmt: str):
        T = TRANSLATIONS[self.lang]
        if fmt == "csv":
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
                title=T.get("menu_export_csv", "Export as CSV"),
            )
            if path:
                try:
                    self._export_csv(path)
                except Exception as e:
                    messagebox.showerror("", str(e))

    def _import_list_format(self, fmt: str):
        T = TRANSLATIONS[self.lang]
        if fmt == "csv":
            path = filedialog.askopenfilename(
                filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
                title=T.get("menu_import_csv", "Import from CSV"),
            )
            if path:
                try:
                    self._import_csv(path)
                except Exception as e:
                    messagebox.showerror("", str(e))

    # ── VALIDATE ALL ─────────────────────────
    def _validate_all_scripts(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        problems = []
        for s in self.scripts:
            path = s.get("path", "")
            name = s.get("name", path)
            if not os.path.exists(path):
                problems.append((name, T["validate_missing_file"], path))
                continue
            ext = Path(path).suffix.lower()
            interp = s.get("interpreter", DEFAULT_INTERPRETERS.get(ext, ""))
            is_windows = (platform.system() == "Windows")
            ok = True
            if ext in (".bat", ".cmd"):
                ok = is_windows or self._find_tool("bash", "sh") is not None
            elif ext == ".vbs":
                ok = is_windows
            elif ext == ".ps1":
                ok = self._find_tool(interp, "pwsh", "powershell.exe", "powershell") is not None
            elif interp:
                ok = self._find_tool(interp) is not None
            if not ok:
                problems.append((name, T["validate_missing_interp"], interp or ext))

        if not problems:
            messagebox.showinfo(T["validate_title"],
                                 T["validate_ok"].format(total=len(self.scripts)))
            return

        dlg = tk.Toplevel(self)
        dlg.title(T["validate_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("520x320")

        cols = ("name", "issue", "detail")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
        tree.heading("name",   text=T["col_name"])
        tree.heading("issue",  text="?")
        tree.heading("detail", text=T["col_path"])
        tree.column("name", width=150)
        tree.column("issue", width=160)
        tree.column("detail", width=190)
        vsb = ttk.Scrollbar(dlg, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        for name, issue, detail in problems:
            tree.insert("", "end", values=(name, issue, detail))

        tk.Button(dlg, text=T["btn_ok"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=12, pady=3,
                  cursor="hand2", command=dlg.destroy).pack(side="bottom", pady=10)

        _center_dialog(dlg)

    # ── ADVANCED SEARCH (v1.7) ─────────────────
    def _show_advanced_search(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T["search_dlg_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("400x300")

        # Search filters
        frm = tk.Frame(dlg, bg=C["bg_main"])
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        row = 0
        def _lbl(text, r):
            tk.Label(frm, text=text, bg=C["bg_main"], fg=C["fg_main"],
                    font=("Consolas", 9)).grid(row=r, column=0, sticky="w", pady=2)

        def _entry(r, default=""):
            var = tk.StringVar(value=default)
            entry = tk.Entry(frm, textvariable=var, bg=C["bg_entry"], fg=C["fg_main"],
                           insertbackground=C["insert_fg"], relief="flat", font=("Consolas", 9))
            entry.grid(row=r, column=1, sticky="ew", pady=2)
            return var

        # Name filter
        _lbl(T["search_dlg_name"], row)
        var_name = _entry(row)
        row += 1

        # Type filter
        _lbl(T["search_dlg_type"], row)
        var_type = tk.StringVar(value="")
        type_cb = ttk.Combobox(frm, textvariable=var_type, values=[""] + list(SCRIPT_TYPES.keys()),
                               state="readonly", font=("Consolas", 9))
        type_cb.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # Group filter
        _lbl(T["search_dlg_group"], row)
        groups = [""] + sorted(set(s.get("group", "") for s in self.scripts if s.get("group")))
        var_group = tk.StringVar(value="")
        group_cb = ttk.Combobox(frm, textvariable=var_group, values=groups,
                                state="readonly", font=("Consolas", 9))
        group_cb.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # Tag filter
        _lbl(T["search_dlg_tag"], row)
        var_tag = _entry(row)
        row += 1

        # Status filter
        _lbl(T["search_dlg_status"], row)
        var_status = tk.StringVar(value=T["search_dlg_status_all"])
        status_cb = ttk.Combobox(frm, textvariable=var_status,
                                 values=[T["search_dlg_status_all"],
                                        T["search_dlg_status_success"],
                                        T["search_dlg_status_failed"],
                                        T["search_dlg_status_never"]],
                                 state="readonly", font=("Consolas", 9))
        status_cb.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        frm.columnconfigure(1, weight=1)

        # Buttons
        btn_frm = tk.Frame(dlg, bg=C["bg_main"])
        btn_frm.pack(side="bottom", pady=10)

        def _apply():
            # Apply filters to search
            name_q = var_name.get().lower()
            type_q = var_type.get()
            group_q = var_group.get()
            tag_q = var_tag.get().lower()
            status_q = var_status.get()

            # Build search query
            search_parts = []
            if name_q:
                search_parts.append(name_q)
            if type_q:
                search_parts.append(f"type:{type_q}")
            if group_q:
                search_parts.append(f"group:{group_q}")
            if tag_q:
                search_parts.append(f"tag:{tag_q}")
            if status_q != T["search_dlg_status_all"]:
                if status_q == T["search_dlg_status_success"]:
                    search_parts.append("status:success")
                elif status_q == T["search_dlg_status_failed"]:
                    search_parts.append("status:failed")
                elif status_q == T["search_dlg_status_never"]:
                    search_parts.append("status:never")

            self.var_search.set(" ".join(search_parts))
            self._refresh_tree()
            dlg.destroy()

        def _reset():
            var_name.set("")
            var_type.set("")
            var_group.set("")
            var_tag.set("")
            var_status.set(T["search_dlg_status_all"])

        tk.Button(btn_frm, text=T["search_dlg_apply"], command=_apply,
                 bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                 font=("Consolas", 9, "bold"), padx=12, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frm, text=T["search_dlg_reset"], command=_reset,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frm, text=T["btn_close"], command=dlg.destroy,
                 bg=C["btn_cancel_bg"], fg=C["btn_cancel_fg"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)

        _center_dialog(dlg)

    # ── RUN HISTORY ─────────────────────────
    def _show_history(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        dlg = tk.Toplevel(self)
        dlg.title(T["dlg_history_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("640x380")

        cols = ("name", "time", "code", "elapsed")
        col_labels = {
            "name":    T["history_col_name"],
            "time":    T["history_col_time"],
            "code":    T["history_col_code"],
            "elapsed": T["history_col_elapsed"],
        }
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
        tree.heading("name",    text=col_labels["name"])
        tree.heading("time",    text=col_labels["time"])
        tree.heading("code",    text=col_labels["code"])
        tree.heading("elapsed", text=col_labels["elapsed"])
        tree.column("name",    width=200)
        tree.column("time",    width=150)
        tree.column("code",    width=60,  anchor="center")
        tree.column("elapsed", width=80,  anchor="center")

        vsb = ttk.Scrollbar(dlg, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0,8), pady=8)

        # Store history entries for context menu (v1.7)
        history_entries = []
        for entry in reversed(self._run_history):
            tree.insert("", "end", values=(
                entry.get("name", ""),
                entry.get("time", ""),
                entry.get("code", ""),
                entry.get("elapsed", ""),
            ))
            history_entries.append(entry)

        # Context menu for re-run (v1.7)
        def _show_history_menu(event):
            row_id = tree.identify_row(event.y)
            if not row_id:
                return
            idx = tree.index(row_id)
            if idx >= len(history_entries):
                return
            entry = history_entries[idx]
            
            menu = tk.Menu(dlg, tearoff=0, bg=C["menubar_bg"], fg=C["menubar_fg"],
                          activebackground=C["menu_abg"], activeforeground=C["menu_afg"],
                          relief="flat", borderwidth=1)
            menu.add_command(label=T["ctx_rerun"], 
                           command=lambda e=entry: self._rerun_from_history(e))
            menu.tk_popup(event.x_root, event.y_root)

        tree.bind("<Button-3>", _show_history_menu)

        tk.Button(dlg, text=T["btn_close"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=12, pady=3,
                  cursor="hand2", command=dlg.destroy).pack(side="bottom", pady=10)
        _center_dialog(dlg)

    # ── RE-RUN FROM HISTORY (v1.7) ─────────────
    def _rerun_from_history(self, entry: dict):
        """Re-run a script from history entry."""
        script_name = entry.get("name", "")
        # Find script by name in current scripts list
        for i, s in enumerate(self.scripts):
            if s.get("name", "") == script_name:
                # Select and run
                self.tree.selection_set(str(i))
                self.tree.focus(str(i))
                self._run_selected()
                return
        self._set_status(f"✘ Script not found: {script_name}")

    # ── BATCH RUN (v1.7) ───────────────────────
    def _show_batch_run_dialog(self):
        """Show dialog to run multiple scripts at once."""
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])
        
        # Get selected scripts
        sel = self.tree.selection()
        selected_indices = [int(i) for i in sel]
        
        if not selected_indices:
            messagebox.showinfo("", T.get("batch_run_no_selection", "Select scripts first"))
            return
        
        # Create dialog
        dlg = tk.Toplevel(self)
        dlg.title(T["batch_dlg_title"])
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("500x400")
        
        # Info label
        info_lbl = tk.Label(dlg, text=f"{T['batch_dlg_info']} ({len(selected_indices)} scripts)",
                           bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 9))
        info_lbl.pack(pady=10)
        
        # Script list
        list_frame = tk.Frame(dlg, bg=C["bg_main"])
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        script_list = tk.Listbox(list_frame, bg=C["bg_entry"], fg=C["fg_main"],
                                font=("Consolas", 9), relief="flat")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=script_list.yview)
        script_list.configure(yscrollcommand=scrollbar.set)
        
        for idx in selected_indices:
            s = self.scripts[idx]
            script_list.insert("end", s.get("name", ""))
        
        script_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Options
        opts_frame = tk.Frame(dlg, bg=C["bg_main"])
        opts_frame.pack(fill="x", padx=10, pady=5)
        
        var_concurrent = tk.BooleanVar(value=False)
        var_stop_on_error = tk.BooleanVar(value=True)
        var_max_threads = tk.IntVar(value=4)
        
        tk.Checkbutton(opts_frame, text=T["batch_dlg_concurrent"], variable=var_concurrent,
                      bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 9),
                      command=lambda: self._toggle_thread_limit(opts_frame, var_concurrent, var_max_threads, C, T)).pack(anchor="w")
        
        self.thread_limit_frame = tk.Frame(opts_frame, bg=C["bg_main"])
        tk.Label(self.thread_limit_frame, text="Max concurrent threads:", 
                bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 9)).pack(side="left")
        tk.Spinbox(self.thread_limit_frame, from_=1, to=16, textvariable=var_max_threads, width=5,
                  bg=C["bg_entry"], fg=C["fg_main"], insertbackground=C["insert_fg"],
                  buttonbackground=C["bg_btn"], relief="flat", font=("Consolas", 9)).pack(side="left", padx=5)
        
        tk.Checkbutton(opts_frame, text=T["batch_dlg_stop_on_error"], variable=var_stop_on_error,
                      bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 9),
                      selectcolor=C["bg_entry"], activebackground=C["bg_main"]).pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(dlg, bg=C["bg_main"])
        btn_frame.pack(side="bottom", pady=10)
        
        def _run():
            concurrent = var_concurrent.get()
            stop_on_error = var_stop_on_error.get()
            max_threads = var_max_threads.get()
            dlg.destroy()
            self._run_batch(selected_indices, concurrent, stop_on_error, max_threads)
        
        tk.Button(btn_frame, text=T["batch_run_selected"], command=_run,
                 bg=C["btn_ok_bg"], fg=C["btn_ok_fg"], relief="flat",
                 font=("Consolas", 9, "bold"), padx=12, pady=3).pack(side="left", padx=5)
        tk.Button(btn_frame, text=T["btn_close"], command=dlg.destroy,
                 bg=C["bg_btn"], fg=C["fg_main"], relief="flat",
                 font=("Consolas", 9), padx=12, pady=3).pack(side="left", padx=5)
        
        _center_dialog(dlg)
        
        # Initially hide thread limit frame
        self.thread_limit_frame.pack_forget()
    
    def _toggle_thread_limit(self, parent, var_concurrent, var_max_threads, C, T):
        """Toggle visibility of thread limit frame based on concurrent checkbox."""
        if var_concurrent.get():
            self.thread_limit_frame.pack(anchor="w", pady=2)
        else:
            self.thread_limit_frame.pack_forget()
    
    def _run_batch(self, indices: list, concurrent: bool, stop_on_error: bool, max_threads: int = 4):
        """Run multiple scripts with optional thread pool for concurrent execution."""
        T = TRANSLATIONS[self.lang]
        
        if concurrent:
            # Run with thread pool to limit concurrent threads
            import queue
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def run_single(idx):
                self.tree.selection_set(str(idx))
                self.tree.focus(str(idx))
                self._run_selected()
                # Wait for completion
                while self._active_proc is not None and self._active_proc.poll() is None:
                    time.sleep(0.1)
                return idx, self._last_run_info.get("code", 0) if self._last_run_info else 0
            
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = {executor.submit(run_single, idx): idx for idx in indices}
                
                for future in as_completed(futures):
                    idx, return_code = future.result()
                    if stop_on_error and return_code != 0:
                        self.log_queue.put(f"[Batch run stopped due to error in script {self.scripts[idx].get('name', '')}]\n")
                        # Cancel remaining futures
                        for f in futures:
                            f.cancel()
                        break
            
            self._set_status(f"✔ {T['batch_run_title']}: {len(indices)} scripts completed (max {max_threads} concurrent)")
        else:
            # Run sequentially
            for idx in indices:
                self.tree.selection_set(str(idx))
                self.tree.focus(str(idx))
                self._run_selected()
                # Wait for completion
                while self._active_proc is not None and self._active_proc.poll() is None:
                    time.sleep(0.1)
                # Check if we should stop on error
                if stop_on_error and self._last_run_info and self._last_run_info.get("code", 0) != 0:
                    self.log_queue.put(f"[Batch run stopped due to error]\n")
                    break
    
    def _run_script_by_index(self, idx: int):
        """Run script by index (for batch concurrent runs)."""
        self.tree.selection_set(str(idx))
        self.tree.focus(str(idx))
        self._run_selected()

    def _open_debugger(self):
        """Open debugger dialog for selected script"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("", "Please select a script to debug")
            return
        
        idx = int(sel[0])
        script = self.scripts[idx]
        path = script.get("path", "")
        
        DebuggerDialog(self, path, script.get("name", ""), self.lang,
                      theme=THEMES.get(self.theme_name, THEMES["light"]))

    # ── STATISTICS DASHBOARD ─────────────────
    def _show_dashboard(self):
        T = TRANSLATIONS[self.lang]
        C = THEMES.get(self.theme_name, THEMES["light"])

        # success/failure counts per script name, derived from run_history
        per_name_runs = {}
        per_name_ok = {}
        per_name_times = {}
        for entry in self._run_history:
            nm = entry.get("name", "")
            per_name_runs[nm] = per_name_runs.get(nm, 0) + 1
            if entry.get("code", 1) == 0:
                per_name_ok[nm] = per_name_ok.get(nm, 0) + 1
            if "elapsed" in entry:
                per_name_times.setdefault(nm, []).append(entry["elapsed"])

        rows = []
        for s in self.scripts:
            name = s.get("name", "")
            run_count = s.get("run_count", 0)
            run_times = s.get("run_times", [])
            avg_time = round(sum(run_times) / len(run_times), 2) if run_times else 0.0
            last_time = round(run_times[-1], 2) if run_times else 0.0
            last_rc = s.get("last_rc")
            hist_runs = per_name_runs.get(name, 0)
            hist_ok = per_name_ok.get(name, 0)
            success_pct = round(100 * hist_ok / hist_runs, 1) if hist_runs else None
            # Additional metrics
            hist_times = per_name_times.get(name, [])
            hist_avg = round(sum(hist_times) / len(hist_times), 2) if hist_times else 0.0
            min_time = round(min(hist_times), 2) if hist_times else 0.0
            max_time = round(max(hist_times), 2) if hist_times else 0.0
            rows.append({
                "name": name, "runs": run_count, "avg": avg_time,
                "last": last_time, "last_rc": last_rc,
                "success": success_pct, "hist_avg": hist_avg,
                "min_time": min_time, "max_time": max_time,
            })

        total_runs = len(self._run_history)
        total_ok = sum(1 for e in self._run_history if e.get("code", 1) == 0)
        overall_success = round(100 * total_ok / total_runs, 1) if total_runs else 0.0
        
        # Calculate total execution time
        total_exec_time = sum(e.get("elapsed", 0) for e in self._run_history)
        avg_exec_time = round(total_exec_time / total_runs, 2) if total_runs else 0.0

        dlg = tk.Toplevel(self)
        dlg.title(T.get("dashboard_title", "Statistics dashboard"))
        dlg.configure(bg=C["bg_main"])
        dlg.grab_set()
        dlg.geometry("850x500")

        # Enhanced summary with more metrics
        summary_text = (
            f"{T.get('dashboard_summary', 'Total scripts: {total}  •  Total runs: {runs}  •  Avg success rate: {success}%').format(total=len(self.scripts), runs=total_runs, success=overall_success)}\n"
            f"Total execution time: {total_exec_time:.1f}s  •  Avg execution time: {avg_exec_time:.2f}s"
        )
        lbl_summary = tk.Label(
            dlg,
            text=summary_text,
            bg=C["bg_main"], fg=C["fg_main"], font=("Consolas", 9, "bold"))
        lbl_summary.pack(side="top", anchor="w", padx=10, pady=(8, 4))

        if not rows:
            tk.Label(dlg, text=T.get("dashboard_no_data",
                                      "No data yet — run some scripts to see statistics."),
                     bg=C["bg_main"], fg=C["fg_main"],
                     font=("Consolas", 9)).pack(padx=10, pady=20)
        else:
            cols = ("name", "runs", "success", "avg", "min", "max", "last", "lastrc")
            col_labels = {
                "name":   T.get("dashboard_col_name", "Script"),
                "runs":   T.get("dashboard_col_runs", "Runs"),
                "success":T.get("dashboard_col_success", "Success %"),
                "avg":    T.get("dashboard_col_avg", "Avg time [s]"),
                "min":    "Min [s]",
                "max":    "Max [s]",
                "last":   T.get("dashboard_col_last", "Last time [s]"),
                "lastrc": T.get("dashboard_col_lastrc", "Last code"),
            }
            tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
            widths = {"name": 200, "runs": 60, "success": 80, "avg": 80, "min": 70, "max": 70, "last": 80, "lastrc": 70}
            for c in cols:
                tree.heading(c, text=col_labels[c],
                              command=lambda c=c: _sort(c))
                anchor = "w" if c == "name" else "center"
                tree.column(c, width=widths[c], anchor=anchor)

            vsb = ttk.Scrollbar(dlg, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="top", fill="both", expand=True, padx=(10, 0), pady=4)
            vsb.pack(side="right", fill="y", padx=(0, 10), pady=4)

            def _fill(sort_key=None, reverse=False):
                tree.delete(*tree.get_children())
                data = list(rows)
                if sort_key:
                    data.sort(key=lambda r: (r.get(sort_key) is None,
                                              r.get(sort_key) or 0), reverse=reverse)
                for r in data:
                    success_disp = "—" if r["success"] is None else f"{r['success']}"
                    last_rc_disp = "—" if r["last_rc"] is None else str(r["last_rc"])
                    min_disp = "—" if r["min_time"] == 0 else f"{r['min_time']}"
                    max_disp = "—" if r["max_time"] == 0 else f"{r['max_time']}"
                    tree.insert("", "end", values=(
                        r["name"], r["runs"], success_disp, r["avg"], 
                        min_disp, max_disp, r["last"], last_rc_disp))

            _sort_state = {"key": None, "rev": False}

            def _sort(key):
                if _sort_state["key"] == key:
                    _sort_state["rev"] = not _sort_state["rev"]
                else:
                    _sort_state["key"] = key
                    _sort_state["rev"] = False
                _fill(_sort_state["key"], _sort_state["rev"])

            _fill()

            # ── Top-5 slowest scripts ──
            slowest = sorted([r for r in rows if r["avg"] > 0],
                              key=lambda r: r["avg"], reverse=True)[:5]
            if slowest:
                frm_top = tk.Frame(dlg, bg=C["bg_main"])
                frm_top.pack(side="bottom", fill="x", padx=10, pady=(4, 0))
                tk.Label(frm_top, text=T.get("dashboard_top_slowest", "Slowest scripts (avg)") + ":",
                         bg=C["bg_main"], fg=C["fg_main"],
                         font=("Consolas", 9, "bold")).pack(anchor="w")
                for r in slowest:
                    tk.Label(frm_top, text=f"  {r['name']} — {r['avg']}s",
                             bg=C["bg_main"], fg=C["fg_main"],
                             font=("Consolas", 9)).pack(anchor="w")

        tk.Button(dlg, text=T["btn_ok"], bg=C["btn_ok_bg"], fg=C["btn_ok_fg"],
                  relief="flat", font=("Consolas", 9, "bold"), padx=12, pady=3,
                  cursor="hand2", command=dlg.destroy).pack(side="bottom", pady=10)

        _center_dialog(dlg)

    # ── EXPORT LOG ──────────────────────────
    def _export_log(self):
        T = TRANSLATIONS[self.lang]
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")],
            title=T.get("log_export", "Export log"),
        )
        if not path:
            return
        tmp_path = path + ".tmp"
        try:
            content = self.log_text.get("1.0", "end")
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, path)
            self._set_status(f"✔ {T.get('log_exported', 'Log saved:')} {path}")
        except Exception as e:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            messagebox.showerror("", str(e))

    # ── FULL CONFIG BACKUP / RESTORE ────────
    def _export_full_config(self):
        """Export the entire app state (scripts, groups, schedules, history,
        language, theme) to a single JSON backup file."""
        T = TRANSLATIONS[self.lang]
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            title=T.get("menu_export_full", "Export full backup…"),
            initialfile="pslauncher_backup.json",
        )
        if not path:
            return
        try:
            cfg = {
                "scripts": self.scripts,
                "lang": self.lang,
                "theme": self.theme_name,
                "groups": self._groups,
                "run_history": self._run_history,
                "schedules": self._schedules,
                "app_version": __version__,
                "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            self._set_status(f"✔ {T.get('full_backup_saved','Backup saved:')} {path}")
        except Exception as e:
            messagebox.showerror("", str(e))

    def _import_full_config(self):
        """Restore the entire app state from a full backup JSON file.
        Replaces scripts/groups/schedules/history/lang/theme."""
        T = TRANSLATIONS[self.lang]
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            title=T.get("menu_import_full", "Import full backup…"),
        )
        if not path:
            return

        try:
            cfg = self._read_config_file(path)
        except Exception as e:
            messagebox.showerror("", str(e))
            return

        if not messagebox.askyesno(
                T.get("full_backup_confirm_title", "Import full backup"),
                T.get("full_backup_confirm_msg",
                      "This will replace all current data. Continue?")):
            return

        # Stop any running watchdogs / hotkeys tied to the old script list
        for stop_evt in self._watchdog_stop.values():
            stop_evt.set()
        self._watchdog_stop.clear()

        self.scripts      = cfg.get("scripts", [])
        self._groups      = cfg.get("groups", [])
        self._run_history = cfg.get("run_history", [])
        self._schedules   = cfg.get("schedules", [])
        self.lang         = cfg.get("lang", self.lang)
        self.theme_name   = cfg.get("theme", self.theme_name)

        # migrate / fill in defaults for imported scripts
        defaults = {
            "group": "", "pinned": False, "env_vars": "", "auto_restart": False,
            "max_retries": 3, "timeout": 0, "tags": "", "note": "",
            "profiles": [], "active_profile": "",
            "run_count": 0, "run_times": [], "last_rc": None,
            "watchdog_interval": 0, "notify_on_finish": False,
            "notify_min_sec": 0, "run_after": "",
            "hotkey": "", "kiosk_visible": True,
        }
        for s in self.scripts:
            for k, v in defaults.items():
                s.setdefault(k, v)

        self._apply_lang()
        self._apply_theme(self.theme_name)
        self._rebuild_group_bar()
        self._refresh_tree()
        self._hotkey_mgr.reload(self.scripts)
        self._schedule_save()

        T = TRANSLATIONS[self.lang]
        self._set_status(f"✔ {T.get('full_backup_loaded','Backup loaded.')}")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    try:
        app = PSLauncher()
        # CLI: psLauncher.exe "<path_to_script>"  -> open Sandbox with that file
        # (used by the Windows Explorer "Run in Sandbox" context-menu entry)
        if len(sys.argv) > 1:
            cli_path = sys.argv[1]
            if cli_path and os.path.isfile(cli_path):
                app.after(200, lambda p=cli_path: app._open_sandbox_with_file(p))
        app.mainloop()
    except Exception as e:
        error_msg = f"Fatal error: {e}\n\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        try:
            messagebox.showerror("psLauncher - Fatal Error", error_msg)
        except:
            pass
        sys.exit(1)

