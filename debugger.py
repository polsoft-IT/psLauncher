from __future__ import annotations

"""
debugger.py – wysokopoziomowy moduł debuggera dla skryptów Python.

UWAGA:
Ten moduł implementuje architekturę, interfejsy i stuby funkcji.
Realna integracja z profilerami, zdalnym debugowaniem, AI itd.
wymaga dodatkowych komponentów i środowiska.
"""

__version__ = "1.0.0"
__author__ = "Sebastian Januchowski"
__company__ = "polsoft.ITS™ Group"
__github__ = "https://github.com/polsoft-IT"
__email__ = "polsoft.its@mail.com"
__description__ = "Wysokopoziomowy moduł debuggera dla skryptów Python z obsługą breakpoints, inspekcji stanu, live editing, profiling, AI-assisted debugging, time-travel debugging, chaos engineering, security auditing i collaborative debugging."

import sys
import os
import time
import json
import threading
import traceback
import inspect
import copy
import importlib
import cProfile
import pstats
import tracemalloc
import asyncio
import random
import ctypes
import ast
import code
import io
import contextlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Protocol,
)

# Import structured logger
try:
    from logger import get_logger
    _logger = get_logger()
except ImportError:
    _logger = None

# Optional dependencies - will be imported when needed
try:
    import psutil
except ImportError:
    psutil = None

try:
    import websockets
except ImportError:
    websockets = None

try:
    import httpx
except ImportError:
    httpx = None


# ============================================================
# 1. Konfiguracja debuggera
# ============================================================

@dataclass
class Breakpoint:
    file: str
    line: int
    condition: Optional[str] = None
    log_message: Optional[str] = None
    hit_count: int = 0
    hit_limit: Optional[int] = None
    exception_breakpoint: bool = False
    temporary: bool = False  # One-shot breakpoint
    hit_operator: Optional[str] = None  # '==', '>', '<', '%', etc.


@dataclass
class DebuggerConfig:
    enable_ai_assistance: bool = True
    enable_time_travel: bool = True
    enable_remote_debugging: bool = False
    enable_chaos_engineering: bool = False
    enable_security_auditing: bool = True
    enable_collaboration: bool = False
    # Sandbox configuration
    enable_os_isolation: bool = False
    enable_security_sandbox: bool = False
    enable_filesystem_sandbox: bool = False
    enable_hard_sandbox: bool = False
    enable_execution_limits: bool = True
    enable_python_sandbox: bool = True


# ============================================================
# 2. Kontrola przepływu programu (Execution Control)
# ============================================================

class ExecutionController:
    """
    Kontrola przepływu: breakpoints, step, pause/resume.
    """

    def __init__(self, config: DebuggerConfig):
        self.config = config
        self.breakpoints: List[Breakpoint] = []
        self.paused = False
        self._pause_lock = threading.Lock()
        self._pause_cond = threading.Condition(self._pause_lock)
        self.current_frame: Optional[inspect.FrameInfo] = None
        self._step_mode: Optional[str] = None  # 'over', 'into', 'out'
        self._step_depth: int = 0
        self._step_start_frame: Optional[Any] = None
        self._stop_at_next_line: bool = False

    def add_breakpoint(
        self,
        file: str,
        line: int,
        condition: Optional[str] = None,
        log_message: Optional[str] = None,
        hit_limit: Optional[int] = None,
        exception_breakpoint: bool = False,
        temporary: bool = False,
        hit_operator: Optional[str] = None,
    ) -> None:
        bp = Breakpoint(
            file=file,
            line=line,
            condition=condition,
            log_message=log_message,
            hit_limit=hit_limit,
            exception_breakpoint=exception_breakpoint,
            temporary=temporary,
            hit_operator=hit_operator,
        )
        self.breakpoints.append(bp)

    def _match_breakpoint(self, frame: inspect.FrameInfo) -> Optional[Breakpoint]:
        filename = frame.filename
        lineno = frame.lineno
        for bp in self.breakpoints:
            if os.path.abspath(bp.file) == os.path.abspath(filename) and bp.line == lineno:
                return bp
        return None

    def check_breakpoint(self, frame: inspect.FrameInfo) -> None:
        bp = self._match_breakpoint(frame)
        if not bp:
            return
        bp.hit_count += 1
        if bp.log_message:
            if _logger:
                _logger.info(f"LOGPOINT: {bp.log_message}", context={"hit_count": bp.hit_count})
            else:
                print(f"[LOGPOINT] {bp.log_message} (hit={bp.hit_count})")
        
        # Handle hit-count operators
        if bp.hit_operator:
            should_pause = False
            if bp.hit_operator == '==' and bp.hit_limit is not None:
                should_pause = bp.hit_count == bp.hit_limit
            elif bp.hit_operator == '>' and bp.hit_limit is not None:
                should_pause = bp.hit_count > bp.hit_limit
            elif bp.hit_operator == '<' and bp.hit_limit is not None:
                should_pause = bp.hit_count < bp.hit_limit
            elif bp.hit_operator == '%' and bp.hit_limit is not None and bp.hit_limit > 0:
                should_pause = bp.hit_count % bp.hit_limit == 0
            if not should_pause:
                return
        elif bp.hit_limit is not None and bp.hit_count < bp.hit_limit:
            return
        
        if bp.condition:
            try:
                if not eval(bp.condition, frame.frame.f_globals, frame.frame.f_locals):
                    return
            except Exception:
                return
        self.pause(frame)
        
        # Remove temporary breakpoint after hit
        if bp.temporary:
            self.breakpoints.remove(bp)

    def pause(self, frame: inspect.FrameInfo) -> None:
        self.current_frame = frame
        with self._pause_lock:
            self.paused = True
            while self.paused:
                self._pause_cond.wait()

    def resume(self) -> None:
        with self._pause_lock:
            self.paused = False
            self._pause_cond.notify_all()

    def step_over(self) -> None:
        """Step over: execute next line in current frame"""
        self._step_mode = 'over'
        self._step_start_frame = self.current_frame.frame if self.current_frame else None
        self._step_depth = len(inspect.stack())
        self.resume()

    def step_into(self) -> None:
        """Step into: enter next function call"""
        self._step_mode = 'into'
        self._step_depth = len(inspect.stack())
        self.resume()

    def step_out(self) -> None:
        """Step out: exit current function"""
        self._step_mode = 'out'
        self._step_depth = len(inspect.stack())
        self.resume()

    def _should_stop_at_frame(self, frame: Any) -> bool:
        """Check if execution should stop at current frame based on step mode"""
        if not self._step_mode:
            return False
        
        current_depth = len(inspect.stack())
        
        if self._step_mode == 'over':
            # Stop when we return to same or higher depth
            return current_depth <= self._step_depth
        elif self._step_mode == 'into':
            # Stop at any new line
            return True
        elif self._step_mode == 'out':
            # Stop when we go up one level
            return current_depth < self._step_depth
        
        return False

    def reset_step_mode(self) -> None:
        """Reset step mode after stopping"""
        self._step_mode = None
        self._step_depth = 0
        self._step_start_frame = None

    def run_to_cursor(self, file: str, line: int) -> None:
        self.add_breakpoint(file, line)
        self.resume()

    def handle_exception(self, exc_type, exc_value, exc_tb) -> None:
        frame = inspect.getframeinfo(exc_tb.tb_frame)
        for bp in self.breakpoints:
            if bp.exception_breakpoint:
                self.pause(frame)
                break


# ============================================================
# 3. Podgląd i inspekcja stanu (State Inspection)
# ============================================================

class StateInspector:
    """
    Drzewo zmiennych, watch expressions, call stack, hover inspection.
    """

    def __init__(self, controller: ExecutionController):
        self.controller = controller
        self.watch_expressions: List[str] = []

    def get_variables_view(self) -> Dict[str, Any]:
        frame_info = self.controller.current_frame
        if not frame_info:
            return {}
        frame = frame_info.frame
        return {
            "locals": dict(frame.f_locals),
            "globals": dict(frame.f_globals),
        }

    def add_watch_expression(self, expr: str) -> None:
        self.watch_expressions.append(expr)

    def evaluate_watch_expressions(self) -> Dict[str, Any]:
        frame_info = self.controller.current_frame
        if not frame_info:
            return {}
        frame = frame_info.frame
        results = {}
        for expr in self.watch_expressions:
            try:
                results[expr] = eval(expr, frame.f_globals, frame.f_locals)
            except Exception as e:
                results[expr] = f"ERROR: {e}"
        return results

    def get_call_stack(self) -> List[Dict[str, Any]]:
        stack = []
        for frame_info in inspect.stack():
            stack.append(
                {
                    "file": frame_info.filename,
                    "line": frame_info.lineno,
                    "function": frame_info.function,
                }
            )
        return stack

    def select_stack_frame(self, index: int) -> None:
        try:
            frame_info = inspect.stack()[index]
            self.controller.current_frame = frame_info
        except IndexError:
            pass

    def hover_inspect(self, var_name: str) -> Any:
        frame_info = self.controller.current_frame
        if not frame_info:
            return None
        frame = frame_info.frame
        return frame.f_locals.get(var_name, frame.f_globals.get(var_name))


# ============================================================
# 4. Modyfikacja na żywo (Live Editing & Manipulation)
# ============================================================

class LiveEditor:
    """
    Edycja wartości zmiennych, hot reload, set next statement.
    """

    def __init__(self, controller: ExecutionController):
        self.controller = controller
        self._reloaded_modules: Dict[str, Any] = {}
        self._py_frame_locals_to_fast = None
        self._init_ctypes_api()

    def _init_ctypes_api(self) -> None:
        """Initialize ctypes API for frame manipulation"""
        try:
            pythonapi = ctypes.pythonapi
            self._py_frame_locals_to_fast = pythonapi.PyFrame_LocalsToFast
            self._py_frame_locals_to_fast.argtypes = [ctypes.py_object, ctypes.c_int]
            self._py_frame_locals_to_fast.restype = ctypes.c_int
        except Exception as e:
            if _logger:
                _logger.error(f"LIVE EDITOR: Failed to initialize ctypes API: {e}")
            else:
                print(f"[LIVE EDITOR] Failed to initialize ctypes API: {e}")

    def set_variable(self, name: str, value: Any) -> None:
        frame_info = self.controller.current_frame
        if not frame_info:
            return
        frame = frame_info.frame
        
        if name in frame.f_locals:
            frame.f_locals[name] = value
            # Use PyFrame_LocalsToFast to sync locals to fast locals
            self._sync_frame_locals(frame)
        elif name in frame.f_globals:
            frame.f_globals[name] = value

    def _sync_frame_locals(self, frame: Any) -> bool:
        """Sync frame.f_locals to fast locals using PyFrame_LocalsToFast"""
        if self._py_frame_locals_to_fast is None:
            return False
        
        try:
            # PyFrame_LocalsToFast(frame, clear)
            # clear=0 means keep existing fast locals, clear=1 means clear them
            result = self._py_frame_locals_to_fast(frame, 0)
            return result == 0  # 0 means success
        except Exception as e:
            if _logger:
                _logger.error(f"LIVE EDITOR: Failed to sync frame locals: {e}")
            else:
                print(f"[LIVE EDITOR] Failed to sync frame locals: {e}")
            return False

    def hot_reload_code(self, module_name: str) -> None:
        """Reload a module and update existing instances"""
        if module_name not in sys.modules:
            raise ImportError(f"Module {module_name} not found")
        
        old_module = sys.modules[module_name]
        
        # Store old module references for instance updates
        self._reloaded_modules[module_name] = old_module
        
        try:
            # Reload the module
            new_module = importlib.reload(old_module)
            
            # Update class instances in current frame
            frame_info = self.controller.current_frame
            if frame_info:
                frame = frame_info.frame
                self._update_instances(frame.f_locals, old_module, new_module)
                self._update_instances(frame.f_globals, old_module, new_module)
            
            if _logger:
                _logger.info(f"HOT RELOAD: Module {module_name} reloaded successfully")
            else:
                print(f"[HOT RELOAD] Module {module_name} reloaded successfully")
        except Exception as e:
            if _logger:
                _logger.error(f"HOT RELOAD ERROR: Failed to reload {module_name}: {e}")
            else:
                print(f"[HOT RELOAD ERROR] Failed to reload {module_name}: {e}")

    def _update_instances(self, namespace: Dict[str, Any], old_module: Any, new_module: Any) -> None:
        """Update instances of classes from the old module to use new class definitions"""
        for name, obj in list(namespace.items()):
            if isinstance(obj, type) and obj.__module__ == old_module.__name__:
                # Update class reference
                if hasattr(new_module, name):
                    namespace[name] = getattr(new_module, name)
            elif hasattr(obj, '__class__') and obj.__class__.__module__ == old_module.__name__:
                # Update instance's class
                class_name = obj.__class__.__name__
                if hasattr(new_module, class_name):
                    obj.__class__ = getattr(new_module, class_name)

    def set_next_statement(self, file: str, line: int) -> None:
        """Set the next statement to execute at the specified line"""
        frame_info = self.controller.current_frame
        if not frame_info:
            raise RuntimeError("No active frame to set next statement")
        
        frame = frame_info.frame
        
        # Check if the file matches
        if os.path.abspath(frame.f_code.co_filename) != os.path.abspath(file):
            raise RuntimeError(f"Cannot jump to different file: {file}")
        
        # Check if line is within valid range
        if not (1 <= line <= frame.f_code.co_lnotab[-1] if hasattr(frame.f_code, 'co_lnotab') else True):
            raise RuntimeError(f"Invalid line number: {line}")
        
        try:
            # Set the next line to execute
            frame.f_lineno = line
            if _logger:
                _logger.info(f"SET NEXT STATEMENT: Jumping to line {line} in {file}")
            else:
                print(f"[SET NEXT STATEMENT] Jumping to line {line} in {file}")
        except AttributeError:
            raise RuntimeError("f_lineno modification not supported in this Python implementation")
        except Exception as e:
            raise RuntimeError(f"Failed to set next statement: {e}")


# ============================================================
# 5. Safe Code Evaluation (AST Sandbox)
# ============================================================

class SafeEvaluator:
    """
    Safe code evaluation using AST sandboxing to prevent dangerous operations.
    """

    # Dangerous nodes that should not be allowed
    DANGEROUS_NODES = {
        ast.Import, ast.ImportFrom,  # Module imports
        ast.Delete,  # del statement
    }

    # Dangerous function calls
    DANGEROUS_CALLS = {
        'eval', 'exec', 'compile', 'open', 'file',
        '__import__', 'reload',
        'exit', 'quit',
        'input', 'raw_input',
    }

    # Dangerous attributes
    DANGEROUS_ATTRIBUTES = {
        '__globals__', '__code__', '__closure__',
        'func_code', 'func_globals', 'func_closure',
        'im_class', 'im_func', 'im_self',
        'f_locals', 'f_globals', 'f_code',
    }

    def __init__(self):
        self._allowed_builtins = {
            'len', 'str', 'int', 'float', 'list', 'dict', 'tuple', 'set',
            'bool', 'type', 'isinstance', 'issubclass', 'range', 'enumerate',
            'zip', 'map', 'filter', 'sorted', 'reversed', 'slice',
            'abs', 'min', 'max', 'sum', 'any', 'all',
            'print', 'repr', 'hex', 'oct', 'bin',
        }

    def is_safe_expression(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check if an expression is safe to evaluate"""
        try:
            tree = ast.parse(code, mode='eval')
            return self._check_ast(tree)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

    def is_safe_statement(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check if a statement is safe to execute"""
        try:
            tree = ast.parse(code, mode='exec')
            return self._check_ast(tree)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

    def _check_ast(self, tree: ast.AST) -> Tuple[bool, Optional[str]]:
        """Recursively check AST for dangerous operations"""
        for node in ast.walk(tree):
            # Check for dangerous node types
            if type(node) in self.DANGEROUS_NODES:
                return False, f"Dangerous node type: {type(node).__name__}"

            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_CALLS:
                        return False, f"Dangerous function call: {node.func.id}"

            # Check for dangerous attribute access
            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    return False, f"Dangerous attribute access: {node.attr}"

            # Check for subscript with dangerous operations
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Slice):
                    # Slices are generally safe
                    pass

        return True, None

    def safe_eval(self, code: str, globals_dict: Optional[Dict[str, Any]] = None, 
                  locals_dict: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[str]]:
        """Safely evaluate an expression"""
        is_safe, error = self.is_safe_expression(code)
        if not is_safe:
            return False, None, error

        try:
            # Create restricted globals
            safe_globals = self._create_safe_globals(globals_dict or {})
            result = eval(code, safe_globals, locals_dict or {})
            return True, result, None
        except Exception as e:
            return False, None, str(e)

    def safe_exec(self, code: str, globals_dict: Optional[Dict[str, Any]] = None,
                  locals_dict: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """Safely execute a statement"""
        is_safe, error = self.is_safe_statement(code)
        if not is_safe:
            return False, error

        try:
            # Create restricted globals
            safe_globals = self._create_safe_globals(globals_dict or {})
            exec(code, safe_globals, locals_dict or {})
            return True, None
        except Exception as e:
            return False, str(e)

    def _create_safe_globals(self, original_globals: Dict[str, Any]) -> Dict[str, Any]:
        """Create a safe globals dictionary with restricted builtins"""
        safe_globals = {
            '__builtins__': {name: __builtins__[name] for name in self._allowed_builtins if name in __builtins__},
        }
        # Add safe user-provided globals
        for key, value in original_globals.items():
            if not key.startswith('__'):
                safe_globals[key] = value
        return safe_globals


# ============================================================
# 6. Diagnostyka i logowanie (Logging & Diagnostics)
# ============================================================

class LogEntry:
    level: str
    message: str
    timestamp: float
    source_file: Optional[str]
    source_line: Optional[int]


class LoggerDiagnostics:
    """
    Interaktywna konsola debuggera, strukturalne logi, source mapping.
    """

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log(self, level: str, message: str, file: Optional[str] = None, line: Optional[int] = None) -> None:
        entry = {
            "level": level,
            "message": message,
            "timestamp": time.time(),
            "file": file,
            "line": line,
        }
        self.logs.append(entry)
        if _logger:
            _logger.log(level, message, file=file, line=line)
        else:
            print(f"[{level}] {message}")

    def filter_logs(self, level: str) -> List[Dict[str, Any]]:
        return [l for l in self.logs if l["level"] == level]

    def clear_logs(self) -> None:
        self.logs.clear()

    def source_map(self, entry: Dict[str, Any]) -> Tuple[Optional[str], Optional[int]]:
        return entry.get("file"), entry.get("line")

    def repl_eval(self, code: str, frame: Optional[inspect.FrameInfo]) -> Any:
        if not frame:
            return None
        f = frame.frame
        try:
            return eval(code, f.f_globals, f.f_locals)
        except Exception:
            try:
                exec(code, f.f_globals, f.f_locals)
                return None
            except Exception as e:
                self.log("Error", f"REPL error: {e}")
                return None


# ============================================================
# 6. Profiling & Diagnostics (CPU, Memory, Async)
# ============================================================

class Profiler:
    """
    CPU profiler, memory profiler, async stack traces.
    """

    def __init__(self):
        self.cpu_data: Dict[str, float] = {}
        self.memory_snapshots: List[Dict[str, Any]] = []
        self._cpu_profiler: Optional[cProfile.Profile] = None
        self._tracemalloc_enabled: bool = False
        self._baseline_snapshot: Optional[Dict[str, Any]] = None

    def start_cpu_profiling(self) -> None:
        """Start CPU profiling using cProfile"""
        self._cpu_profiler = cProfile.Profile()
        self._cpu_profiler.enable()
        if _logger:
            _logger.info("CPU PROFILER: Started")
        else:
            print("[CPU PROFILER] Started")

    def stop_cpu_profiling(self) -> Dict[str, float]:
        """Stop CPU profiling and return results"""
        if not self._cpu_profiler:
            return {}
        
        self._cpu_profiler.disable()
        
        # Get statistics
        stats = pstats.Stats(self._cpu_profiler)
        
        # Convert to dict format
        self.cpu_data = {}
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            func_name = f"{func[0]}:{func[2]}" if len(func) > 2 else str(func)
            self.cpu_data[func_name] = {
                "call_count": cc,
                "total_time": tt,
                "cumulative_time": ct,
            }
        
        if _logger:
            _logger.info(f"CPU PROFILER: Stopped. Collected {len(self.cpu_data)} function stats")
        else:
            print(f"[CPU PROFILER] Stopped. Collected {len(self.cpu_data)} function stats")
        return self.cpu_data

    def get_cpu_profiling_report(self, sort_by: str = "cumulative") -> str:
        """Get a formatted CPU profiling report"""
        if not self._cpu_profiler:
            return "No CPU profiling data available"
        
        stats = pstats.Stats(self._cpu_profiler)
        stats.sort_stats(sort_by)
        
        import io
        output = io.StringIO()
        stats.stream = output
        stats.print_stats()
        return output.getvalue()

    def start_memory_profiling(self) -> None:
        """Start memory profiling using tracemalloc"""
        if not self._tracemalloc_enabled:
            tracemalloc.start()
            self._tracemalloc_enabled = True
            self._baseline_snapshot = self._take_tracemalloc_snapshot()
            if _logger:
                _logger.info("MEMORY PROFILER: Started")
            else:
                print("[MEMORY PROFILER] Started")

    def stop_memory_profiling(self) -> None:
        """Stop memory profiling"""
        if self._tracemalloc_enabled:
            tracemalloc.stop()
            self._tracemalloc_enabled = False
            if _logger:
                _logger.info("MEMORY PROFILER: Stopped")
            else:
                print("[MEMORY PROFILER] Stopped")

    def _take_tracemalloc_snapshot(self) -> Optional[Dict[str, Any]]:
        """Take a tracemalloc snapshot if enabled"""
        if not self._tracemalloc_enabled:
            return None
        
        snapshot = tracemalloc.take_snapshot()
        return {
            "timestamp": time.time(),
            "snapshot": snapshot,
            "stats": snapshot.statistics('lineno'),
        }

    def take_memory_snapshot(self) -> None:
        """Take a memory snapshot"""
        if self._tracemalloc_enabled:
            snapshot_data = self._take_tracemalloc_snapshot()
            if snapshot_data:
                self.memory_snapshots.append(snapshot_data)
                if _logger:
                    _logger.info(f"MEMORY SNAPSHOT: Taken. Total snapshots: {len(self.memory_snapshots)}")
                else:
                    print(f"[MEMORY SNAPSHOT] Taken. Total snapshots: {len(self.memory_snapshots)}")
        else:
            # Fallback to basic info if tracemalloc not enabled
            import sys
            snapshot = {
                "timestamp": time.time(),
                "info": {
                    "rss": sys.getsizeof({}),  # Basic memory info
                    "tracemalloc_disabled": True,
                },
            }
            self.memory_snapshots.append(snapshot)

    def detect_memory_leaks(self) -> List[Dict[str, Any]]:
        """Detect memory leaks by comparing snapshots"""
        if len(self.memory_snapshots) < 2:
            return []
        
        leaks = []
        for i in range(1, len(self.memory_snapshots)):
            prev = self.memory_snapshots[i - 1]
            curr = self.memory_snapshots[i]
            
            if "snapshot" in prev and "snapshot" in curr:
                # Compare tracemalloc snapshots
                diff = curr["snapshot"].compare_to(prev["snapshot"], 'lineno')
                
                for stat in diff:
                    if stat.size_diff > 0:
                        leaks.append({
                            "file": stat.traceback[0].filename if stat.traceback else "unknown",
                            "line": stat.traceback[0].lineno if stat.traceback else 0,
                            "size_diff": stat.size_diff,
                            "count_diff": stat.count_diff,
                        })
        
        return leaks

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        if not self._tracemalloc_enabled:
            return {"status": "not_enabled"}
        
        current = tracemalloc.get_traced_memory()
        return {
            "current": current[0],
            "peak": current[1],
        }

    def async_stack_traces(self) -> List[Dict[str, Any]]:
        """Get async stack traces from all running tasks"""
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                return []
            
            # Get all tasks
            tasks = asyncio.all_tasks(loop)
            
            traces = []
            for task in tasks:
                try:
                    stack = task.get_stack()
                    frames = []
                    for frame in stack:
                        frames.append({
                            "file": frame.f_code.co_filename,
                            "line": frame.f_lineno,
                            "function": frame.f_code.co_name,
                        })
                    
                    traces.append({
                        "task_id": id(task),
                        "task_name": task.get_name(),
                        "coroutine": str(task.get_coro()),
                        "stack": frames,
                        "done": task.done(),
                    })
                except Exception:
                    continue
            
            return traces
        except RuntimeError:
            # No event loop running
            return []
        except Exception as e:
            return [{"error": str(e)}]


# ============================================================
# 7. Architektura i integracja (System & Architecture)
# ============================================================

class RemoteDebugger:
    """
    Remote debugging, multi-thread/process, source maps, plugin API.
    """

    def __init__(self, config: DebuggerConfig):
        self.config = config
        self.connected = False
        self._websocket_server: Optional[Any] = None
        self._source_maps: Dict[str, str] = {}  # compiled_file -> original_file
        self._plugins: Dict[str, Callable] = {}
        self._dap_handlers: Dict[str, Callable] = {}

    async def connect(self, host: str, port: int) -> None:
        """Connect to remote debugger via WebSocket"""
        if not self.config.enable_remote_debugging:
            raise RuntimeError("Remote debugging disabled")
        
        if websockets is None:
            if _logger:
                _logger.warning("REMOTE DEBUGGER: websockets library not installed, using stub mode")
            else:
                print("[REMOTE DEBUGGER] websockets library not installed, using stub mode")
            self.connected = True
            return
        
        try:
            self._websocket_server = await websockets.serve(
                self._handle_websocket_message, host, port
            )
            self.connected = True
            if _logger:
                _logger.info(f"REMOTE DEBUGGER: WebSocket server started on {host}:{port}")
            else:
                print(f"[REMOTE DEBUGGER] WebSocket server started on {host}:{port}")
        except Exception as e:
            if _logger:
                _logger.error(f"REMOTE DEBUGGER ERROR: Failed to start WebSocket server: {e}")
            else:
                print(f"[REMOTE DEBUGGER ERROR] Failed to start WebSocket server: {e}")
            self.connected = True  # Fallback to stub mode

    async def _handle_websocket_message(self, websocket: Any, path: str) -> None:
        """Handle incoming WebSocket messages"""
        async for message in websocket:
            try:
                data = json.loads(message)
                response = await self._process_dap_request(data)
                await websocket.send(json.dumps(response))
            except Exception as e:
                error_response = {"error": str(e)}
                await websocket.send(json.dumps(error_response))

    async def _process_dap_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process Debug Adapter Protocol (DAP) requests"""
        command = request.get("command")
        seq = request.get("seq", 0)
        
        if command in self._dap_handlers:
            return await self._dap_handlers[command](request)
        
        # Default DAP responses
        if command == "initialize":
            return self._dap_response(seq, True, {
                "supportsConfigurationDoneRequest": True,
                "supportsStepBack": True,
                "supportsStepInTargetsRequest": True,
                "supportsEvaluateForHovers": True,
                "supportsSetVariable": True,
                "supportsConditionalBreakpoints": True,
                "supportsHitConditionalBreakpoints": True,
                "supportsLogPoints": True,
            })
        elif command == "setBreakpoints":
            return await self._dap_set_breakpoints(request)
        elif command == "setExceptionBreakpoints":
            return self._dap_response(seq, True, {})
        elif command == "configurationDone":
            return self._dap_response(seq, True, {})
        elif command == "threads":
            return await self._dap_threads(request)
        elif command == "stackTrace":
            return await self._dap_stack_trace(request)
        elif command == "scopes":
            return await self._dap_scopes(request)
        elif command == "variables":
            return await self._dap_variables(request)
        elif command == "evaluate":
            return await self._dap_evaluate(request)
        elif command == "setVariable":
            return await self._dap_set_variable(request)
        elif command == "continue":
            return await self._dap_continue(request)
        elif command == "next":
            return await self._dap_next(request)
        elif command == "stepIn":
            return await self._dap_step_in(request)
        elif command == "stepOut":
            return await self._dap_step_out(request)
        elif command == "pause":
            return await self._dap_pause(request)
        elif command == "disconnect":
            return await self._dap_disconnect(request)
        
        return self._dap_error_response(seq, f"Unknown command: {command}")

    def _dap_response(self, seq: int, success: bool, body: Dict[str, Any]) -> Dict[str, Any]:
        """Create a DAP response"""
        return {
            "seq": seq,
            "type": "response",
            "request_seq": seq,
            "success": success,
            "body": body,
        }

    def _dap_error_response(self, seq: int, message: str) -> Dict[str, Any]:
        """Create a DAP error response"""
        return {
            "seq": seq,
            "type": "response",
            "request_seq": seq,
            "success": False,
            "message": message,
        }

    async def _dap_set_breakpoints(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle setBreakpoints DAP request"""
        seq = request.get("seq", 0)
        breakpoints = request.get("arguments", {}).get("breakpoints", [])
        source = request.get("arguments", {}).get("source", {})
        path = source.get("path")
        
        response_breakpoints = []
        for bp in breakpoints:
            bp_response = {
                "line": bp.get("line"),
                "verified": True,
            }
            response_breakpoints.append(bp_response)
        
        return self._dap_response(seq, True, {"breakpoints": response_breakpoints})

    async def _dap_threads(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle threads DAP request"""
        seq = request.get("seq", 0)
        threads = []
        for i, thread in enumerate(threading.enumerate()):
            threads.append({
                "id": thread.ident or i,
                "name": thread.name,
            })
        
        return self._dap_response(seq, True, {"threads": threads})

    async def _dap_stack_trace(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stackTrace DAP request"""
        seq = request.get("seq", 0)
        stack_frames = []
        
        for i, frame_info in enumerate(inspect.stack()):
            stack_frames.append({
                "id": i,
                "name": frame_info.function,
                "line": frame_info.lineno,
                "column": 0,
                "source": {
                    "path": frame_info.filename,
                },
            })
        
        return self._dap_response(seq, True, {
            "stackFrames": stack_frames,
            "totalFrames": len(stack_frames),
        })

    async def _dap_scopes(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scopes DAP request"""
        seq = request.get("seq", 0)
        frame_id = request.get("arguments", {}).get("frameId", 0)
        
        scopes = [
            {
                "name": "Locals",
                "variablesReference": frame_id * 1000 + 1,
                "expensive": False,
            },
            {
                "name": "Globals",
                "variablesReference": frame_id * 1000 + 2,
                "expensive": False,
            },
        ]
        
        return self._dap_response(seq, True, {"scopes": scopes})

    async def _dap_variables(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle variables DAP request"""
        seq = request.get("seq", 0)
        variables_reference = request.get("arguments", {}).get("variablesReference", 0)
        
        # Extract frame ID from variables reference
        frame_id = variables_reference // 1000
        scope_type = variables_reference % 1000  # 1 = locals, 2 = globals
        
        variables = []
        try:
            stack = inspect.stack()
            if 0 <= frame_id < len(stack):
                frame = stack[frame_id].frame
                
                if scope_type == 1:  # Locals
                    for name, value in frame.f_locals.items():
                        variables.append({
                            "name": name,
                            "value": repr(value)[:1000],
                            "type": type(value).__name__,
                            "variablesReference": 0,
                        })
                elif scope_type == 2:  # Globals
                    for name, value in frame.f_globals.items():
                        if not name.startswith("__"):
                            variables.append({
                                "name": name,
                                "value": repr(value)[:1000],
                                "type": type(value).__name__,
                                "variablesReference": 0,
                            })
        except Exception as e:
            pass
        
        return self._dap_response(seq, True, {"variables": variables})

    async def _dap_evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle evaluate DAP request"""
        seq = request.get("seq", 0)
        expression = request.get("arguments", {}).get("expression", "")
        frame_id = request.get("arguments", {}).get("frameId", 0)
        
        try:
            stack = inspect.stack()
            if 0 <= frame_id < len(stack):
                frame = stack[frame_id].frame
                result = eval(expression, frame.f_globals, frame.f_locals)
                return self._dap_response(seq, True, {
                    "result": repr(result),
                    "variablesReference": 0,
                })
        except Exception as e:
            return self._dap_error_response(seq, str(e))
        
        return self._dap_error_response(seq, "Invalid frame")

    async def _dap_set_variable(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle setVariable DAP request"""
        seq = request.get("seq", 0)
        name = request.get("arguments", {}).get("name", "")
        value = request.get("arguments", {}).get("value", "")
        frame_id = request.get("arguments", {}).get("frameId", 0)
        
        try:
            stack = inspect.stack()
            if 0 <= frame_id < len(stack):
                frame = stack[frame_id].frame
                evaluated_value = eval(value, frame.f_globals, frame.f_locals)
                frame.f_locals[name] = evaluated_value
                return self._dap_response(seq, True, {
                    "value": repr(evaluated_value),
                })
        except Exception as e:
            return self._dap_error_response(seq, str(e))
        
        return self._dap_error_response(seq, "Invalid frame")

    async def _dap_continue(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle continue DAP request"""
        seq = request.get("seq", 0)
        # Resume execution
        return self._dap_response(seq, True, {})

    async def _dap_next(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle next (step over) DAP request"""
        seq = request.get("seq", 0)
        # Step over
        return self._dap_response(seq, True, {})

    async def _dap_step_in(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stepIn DAP request"""
        seq = request.get("seq", 0)
        # Step into
        return self._dap_response(seq, True, {})

    async def _dap_step_out(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stepOut DAP request"""
        seq = request.get("seq", 0)
        # Step out
        return self._dap_response(seq, True, {})

    async def _dap_pause(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pause DAP request"""
        seq = request.get("seq", 0)
        # Pause execution
        return self._dap_response(seq, True, {})

    async def _dap_disconnect(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle disconnect DAP request"""
        seq = request.get("seq", 0)
        self.disconnect()
        return self._dap_response(seq, True, {})

    def register_dap_handler(self, command: str, handler: Callable) -> None:
        """Register a custom DAP command handler"""
        self._dap_handlers[command] = handler

    def disconnect(self) -> None:
        self.connected = False
        if self._websocket_server:
            self._websocket_server.close()
            self._websocket_server = None
        if _logger:
            _logger.info("REMOTE DEBUGGER: Disconnected")
        else:
            print("[REMOTE DEBUGGER] Disconnected")

    def list_threads(self) -> List[int]:
        return [t.ident for t in threading.enumerate() if t.ident is not None]

    def list_child_processes(self) -> List[int]:
        """List child processes using psutil"""
        if psutil is None:
            if _logger:
                _logger.warning("REMOTE DEBUGGER: psutil not installed, returning empty list")
            else:
                print("[REMOTE DEBUGGER] psutil not installed, returning empty list")
            return []
        
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            return [child.pid for child in children]
        except Exception as e:
            if _logger:
                _logger.error(f"REMOTE DEBUGGER ERROR: Failed to list child processes: {e}")
            else:
                print(f"[REMOTE DEBUGGER ERROR] Failed to list child processes: {e}")
            return []

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a process"""
        if psutil is None:
            return None
        
        try:
            proc = psutil.Process(pid)
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(),
                "memory_info": proc.memory_info()._asdict(),
            }
        except Exception:
            return None

    def apply_source_maps(self, compiled_file: str, original_file: str) -> None:
        """Register a source map for a compiled file"""
        self._source_maps[os.path.abspath(compiled_file)] = os.path.abspath(original_file)
        if _logger:
            _logger.info(f"SOURCE MAPS: Mapped {compiled_file} -> {original_file}")
        else:
            print(f"[SOURCE MAPS] Mapped {compiled_file} -> {original_file}")

    def get_original_file(self, compiled_file: str) -> Optional[str]:
        """Get the original file path for a compiled file"""
        return self._source_maps.get(os.path.abspath(compiled_file))

    def register_plugin(self, name: str, handler: Callable) -> None:
        """Register a plugin handler"""
        self._plugins[name] = handler
        if _logger:
            _logger.info(f"PLUGIN API: Registered plugin: {name}")
        else:
            print(f"[PLUGIN API] Registered plugin: {name}")

    def plugin_api_call(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered plugin"""
        if name not in self._plugins:
            return {"error": f"Plugin not found: {name}"}
        
        try:
            result = self._plugins[name](payload)
            return {"plugin": name, "status": "ok", "result": result}
        except Exception as e:
            return {"plugin": name, "status": "error", "error": str(e)}

    def list_plugins(self) -> List[str]:
        """List all registered plugins"""
        return list(self._plugins.keys())


# ============================================================
# 8. AI-Assisted Debugging
# ============================================================

class AIEngine(Protocol):
    def analyze_root_cause(self, error: str, stack: str) -> str:
        ...

    def predict_errors(self, code: str) -> List[str]:
        ...

    def natural_language_query(self, query: str, context: Dict[str, Any]) -> Any:
        ...

    def generate_fix(self, error: str, code: str) -> str:
        ...


class DummyAIEngine:
    """
    Prosty stub AI.
    """

    def analyze_root_cause(self, error: str, stack: str) -> str:
        return f"Root cause (stub): {error}"

    def predict_errors(self, code: str) -> List[str]:
        return ["Potential deadlock (stub)", "Possible memory leak (stub)"]

    def natural_language_query(self, query: str, context: Dict[str, Any]) -> Any:
        return {"query": query, "result": "stub response"}

    def generate_fix(self, error: str, code: str) -> str:
        return "# Stub fix: Check error handling"


class LLMEngine:
    """
    Real LLM integration for AI-assisted debugging.
    Supports OpenAI, Anthropic, and local Ollama.
    """

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = provider
        self.api_key = api_key or os.environ.get(f"{provider.upper()}_API_KEY")
        self.model = model or self._get_default_model()
        self.base_url = base_url
        self._client: Optional[Any] = None

    def _get_default_model(self) -> str:
        if self.provider == "openai":
            return "gpt-4"
        elif self.provider == "anthropic":
            return "claude-3-opus-20240229"
        elif self.provider == "ollama":
            return "llama2"
        return "gpt-4"

    def _get_client(self) -> Any:
        """Get or create the API client"""
        if self._client is not None:
            return self._client

        if self.provider == "openai":
            if httpx is None:
                raise ImportError("httpx is required for OpenAI integration")
            self._client = OpenAIClient(self.api_key, self.model)
        elif self.provider == "anthropic":
            if httpx is None:
                raise ImportError("httpx is required for Anthropic integration")
            self._client = AnthropicClient(self.api_key, self.model)
        elif self.provider == "ollama":
            if httpx is None:
                raise ImportError("httpx is required for Ollama integration")
            self._client = OllamaClient(self.base_url or "http://localhost:11434", self.model)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        return self._client

    def analyze_root_cause(self, error: str, stack: str) -> str:
        """Analyze the root cause of an error using LLM"""
        client = self._get_client()
        prompt = f"""Analyze the following error and provide a root cause analysis:

Error: {error}

Stack Trace:
{stack}

Provide a concise explanation of the root cause."""
        return client.chat(prompt)

    def predict_errors(self, code: str) -> List[str]:
        """Predict potential errors in code using LLM"""
        client = self._get_client()
        prompt = f"""Analyze the following code and predict potential errors, bugs, or issues:

{code}

List each potential error on a separate line."""
        response = client.chat(prompt)
        return [line.strip() for line in response.split("\n") if line.strip()]

    def natural_language_query(self, query: str, context: Dict[str, Any]) -> Any:
        """Answer natural language queries about code context"""
        client = self._get_client()
        context_str = json.dumps(context, indent=2)
        prompt = f"""Answer the following question about the code context:

Question: {query}

Context:
{context_str}"""
        return client.chat(prompt)

    def generate_fix(self, error: str, code: str) -> str:
        """Generate a code fix for the given error"""
        client = self._get_client()
        prompt = f"""Generate a fix for the following error in the code:

Error: {error}

Code:
{code}

Provide the corrected code only, without explanation."""
        return client.chat(prompt)


class OpenAIClient:
    """OpenAI API client"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    def chat(self, prompt: str) -> str:
        if httpx is None:
            raise ImportError("httpx is required")
        
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class AnthropicClient:
    """Anthropic API client"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    def chat(self, prompt: str) -> str:
        if httpx is None:
            raise ImportError("httpx is required")
        
        response = httpx.post(
            f"{self.base_url}/messages",
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]


class OllamaClient:
    """Ollama (local LLM) client with streaming support"""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        self._token_count = 0
        self._cost_tracking = False

    def chat(self, prompt: str, stream: bool = False) -> Union[str, Any]:
        if httpx is None:
            raise ImportError("httpx is required")
        
        if stream:
            return self._chat_streaming(prompt)
        
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        self._token_count += len(data.get("response", "")) // 4  # Approximate token count
        return data["response"]

    def _chat_streaming(self, prompt: str) -> Any:
        """Streaming chat response"""
        if httpx is None:
            raise ImportError("httpx is required")
        
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
            },
        )
        
        def token_generator():
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        self._token_count += 1
                        yield data["response"]
        
        return token_generator()

    def get_token_count(self) -> int:
        return self._token_count

    def enable_cost_tracking(self) -> None:
        self._cost_tracking = True

    def get_estimated_cost(self) -> float:
        """Estimate cost based on token count"""
        # Ollama is free (local), but we can estimate compute cost
        return self._token_count * 0.0001  # Placeholder


class AIAssistant:
    """
    AI-assisted debugging: RCA, predictive errors, GenAI REPL, auto-fix.
    """

    def __init__(self, engine: Optional[AIEngine] = None):
        self.engine = engine or DummyAIEngine()
        self.safe_evaluator = SafeEvaluator()

    def root_cause_analysis(self, exc: BaseException) -> str:
        stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return self.engine.analyze_root_cause(str(exc), stack)

    def predictive_error_detection(self, code: str) -> List[str]:
        return self.engine.predict_errors(code)

    def genai_repl(self, query: str, context: Dict[str, Any]) -> Any:
        return self.engine.natural_language_query(query, context)

    def auto_fix(self, exc: BaseException, code: str) -> str:
        """Generate an automatic fix for the given error"""
        return self.engine.generate_fix(str(exc), code)

    def safe_auto_fix(self, exc: BaseException, code: str, test_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate and safely test an automatic fix in a sandbox.
        Returns a dict with the fix code, test result, and any errors.
        """
        fix_code = self.auto_fix(exc, code)
        
        result = {
            "fix_code": fix_code,
            "tested": False,
            "test_passed": False,
            "error": None,
        }
        
        # Check if the fix is safe
        is_safe, error = self.safe_evaluator.is_safe_statement(fix_code)
        if not is_safe:
            result["error"] = f"Generated fix is not safe: {error}"
            return result
        
        # Test the fix if test code is provided
        if test_code:
            try:
                # Create a sandbox environment
                sandbox_globals = {}
                sandbox_locals = {}
                
                # Execute the fix
                success, exec_error = self.safe_evaluator.safe_exec(fix_code, sandbox_globals, sandbox_locals)
                if not success:
                    result["error"] = f"Failed to execute fix: {exec_error}"
                    return result
                
                # Execute the test
                success, test_error = self.safe_evaluator.safe_exec(test_code, sandbox_globals, sandbox_locals)
                result["tested"] = True
                result["test_passed"] = success
                if not success:
                    result["error"] = f"Test failed: {test_error}"
            except Exception as e:
                result["error"] = f"Sandbox test error: {str(e)}"
        
        return result


# ============================================================
# 9. Time-Travel / Replay Debugging
# ============================================================

@dataclass
class TimeTravelSnapshot:
    timestamp: float
    state: Dict[str, Any]
    frame_info: Optional[Dict[str, Any]] = None
    call_stack: Optional[List[Dict[str, Any]]] = None
    delta: Optional[Dict[str, Any]] = None  # Delta from previous snapshot
    is_delta: bool = False  # Whether this is a delta snapshot


class TimeTravelDebugger:
    """
    Cofanie wykonania, deterministyczny replay with delta snapshots.
    """

    def __init__(self):
        self.snapshots: List[TimeTravelSnapshot] = []
        self._current_index: int = -1
        self._max_snapshots: int = 1000  # Limit memory usage
        self._use_delta_snapshots: bool = True  # Enable delta snapshots by default
        self._previous_state: Optional[Dict[str, Any]] = None

    def record_state(self, frame: Optional[inspect.FrameInfo]) -> None:
        if not frame:
            return
        if hasattr(frame, 'frame'):
            f = frame.frame
        else:
            return
        
        # Record frame info
        frame_info = {
            "filename": f.f_code.co_filename,
            "lineno": f.f_lineno,
            "function": f.f_code.co_name,
        }
        
        # Record call stack
        call_stack = []
        for stack_frame in inspect.stack():
            call_stack.append({
                "file": stack_frame.filename,
                "line": stack_frame.lineno,
                "function": stack_frame.function,
            })
        
        # Use delta snapshots if enabled
        if self._use_delta_snapshots and self._previous_state is not None:
            delta = self._compute_delta(self._previous_state, f.f_locals, f.f_globals)
            snapshot = TimeTravelSnapshot(
                timestamp=time.time(),
                state={},  # Empty for delta snapshots
                frame_info=frame_info,
                call_stack=call_stack,
                delta=delta,
                is_delta=True,
            )
        else:
            # Full snapshot
            try:
                state = {
                    "locals": copy.deepcopy(dict(f.f_locals)),
                    "globals": copy.deepcopy(dict(f.f_globals)),
                }
            except Exception as e:
                # Fallback to shallow copy if deep copy fails
                state = {
                    "locals": dict(f.f_locals),
                    "globals": dict(f.f_globals),
                }
            
            snapshot = TimeTravelSnapshot(
                timestamp=time.time(),
                state=state,
                frame_info=frame_info,
                call_stack=call_stack,
                delta=None,
                is_delta=False,
            )
            self._previous_state = state
        
        self.snapshots.append(snapshot)
        self._current_index = len(self.snapshots) - 1
        
        # Limit memory usage
        if len(self.snapshots) > self._max_snapshots:
            removed = self.snapshots.pop(0)
            # Update previous state if we removed a full snapshot
            if not removed.is_delta and self.snapshots:
                self._previous_state = self._get_full_state(0)
            self._current_index -= 1

    def _compute_delta(self, previous_state: Dict[str, Any], current_locals: Dict[str, Any], 
                       current_globals: Dict[str, Any]) -> Dict[str, Any]:
        """Compute delta between previous and current state"""
        delta = {
            "locals": {},
            "globals": {},
        }
        
        # Compute locals delta
        prev_locals = previous_state.get("locals", {})
        for key, value in current_locals.items():
            if key not in prev_locals or prev_locals[key] != value:
                delta["locals"][key] = copy.deepcopy(value)
        
        # Track deleted locals
        for key in prev_locals:
            if key not in current_locals:
                delta["locals"][f"__deleted__{key}"] = None
        
        # Compute globals delta (only for non-__ keys)
        prev_globals = previous_state.get("globals", {})
        for key, value in current_globals.items():
            if not key.startswith("__"):
                if key not in prev_globals or prev_globals[key] != value:
                    delta["globals"][key] = copy.deepcopy(value)
        
        return delta

    def _get_full_state(self, index: int) -> Optional[Dict[str, Any]]:
        """Reconstruct full state from snapshots up to index"""
        if index < 0 or index >= len(self.snapshots):
            return None
        
        state = {"locals": {}, "globals": {}}
        
        for i in range(index + 1):
            snapshot = self.snapshots[i]
            if snapshot.is_delta and snapshot.delta:
                # Apply delta
                for key, value in snapshot.delta["locals"].items():
                    if key.startswith("__deleted__"):
                        del state["locals"][key[11:]]
                    else:
                        state["locals"][key] = value
                for key, value in snapshot.delta["globals"].items():
                    state["globals"][key] = value
            elif not snapshot.is_delta:
                # Full snapshot
                state = copy.deepcopy(snapshot.state)
        
        return state

    def enable_delta_snapshots(self) -> None:
        """Enable delta snapshots for memory efficiency"""
        self._use_delta_snapshots = True
        if _logger:
            _logger.info("TIME TRAVEL: Delta snapshots enabled")
        else:
            print("[TIME TRAVEL] Delta snapshots enabled")

    def disable_delta_snapshots(self) -> None:
        """Disable delta snapshots (use full snapshots)"""
        self._use_delta_snapshots = False
        if _logger:
            _logger.info("TIME TRAVEL: Delta snapshots disabled")
        else:
            print("[TIME TRAVEL] Delta snapshots disabled")

    def step_back(self) -> Optional[TimeTravelSnapshot]:
        """Step back to the previous snapshot"""
        if self._current_index <= 0:
            return None
        self._current_index -= 1
        return self.snapshots[self._current_index]

    def step_forward(self) -> Optional[TimeTravelSnapshot]:
        """Step forward to the next snapshot"""
        if self._current_index >= len(self.snapshots) - 1:
            return None
        self._current_index += 1
        return self.snapshots[self._current_index]

    def restore_state(self, frame: Optional[inspect.FrameInfo]) -> bool:
        """Restore state to current frame from current snapshot"""
        if self._current_index < 0 or self._current_index >= len(self.snapshots):
            return False
        
        snapshot = self.snapshots[self._current_index]
        if not frame or not hasattr(frame, 'frame'):
            return False
        
        f = frame.frame
        
        try:
            # Restore locals
            for key, value in snapshot.state["locals"].items():
                f.f_locals[key] = copy.deepcopy(value)
            
            # Restore globals (carefully - may have side effects)
            for key, value in snapshot.state["globals"].items():
                if key not in f.f_locals:  # Don't override locals
                    f.f_globals[key] = copy.deepcopy(value)
            
            if _logger:
                _logger.info(f"TIME TRAVEL: Restored state to snapshot {self._current_index} (timestamp: {snapshot.timestamp})")
            else:
                print(f"[TIME TRAVEL] Restored state to snapshot {self._current_index} (timestamp: {snapshot.timestamp})")
            return True
        except Exception as e:
            if _logger:
                _logger.error(f"TIME TRAVEL ERROR: Failed to restore state: {e}")
            else:
                print(f"[TIME TRAVEL ERROR] Failed to restore state: {e}")
            return False

    def jump_to_snapshot(self, index: int) -> Optional[TimeTravelSnapshot]:
        """Jump to a specific snapshot index"""
        if 0 <= index < len(self.snapshots):
            self._current_index = index
            return self.snapshots[index]
        return None

    def get_current_snapshot(self) -> Optional[TimeTravelSnapshot]:
        """Get the current snapshot"""
        if 0 <= self._current_index < len(self.snapshots):
            return self.snapshots[self._current_index]
        return None

    def save_session(self, path: str) -> None:
        """Save all snapshots to a file"""
        data = []
        for s in self.snapshots:
            # Convert snapshot to serializable format
            snapshot_data = {
                "timestamp": s.timestamp,
                "state": s.state,
                "frame_info": s.frame_info,
                "call_stack": s.call_stack,
            }
            data.append(snapshot_data)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if _logger:
            _logger.info(f"TIME TRAVEL: Saved {len(data)} snapshots to {path}")
        else:
            print(f"[TIME TRAVEL] Saved {len(data)} snapshots to {path}")

    def load_session(self, path: str) -> None:
        """Load snapshots from a file"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.snapshots = []
        for d in data:
            snapshot = TimeTravelSnapshot(
                timestamp=d["timestamp"],
                state=d["state"],
                frame_info=d.get("frame_info"),
                call_stack=d.get("call_stack"),
            )
            self.snapshots.append(snapshot)
        
        self._current_index = len(self.snapshots) - 1
        if _logger:
            _logger.info(f"TIME TRAVEL: Loaded {len(self.snapshots)} snapshots from {path}")
        else:
            print(f"[TIME TRAVEL] Loaded {len(self.snapshots)} snapshots from {path}")

    def get_snapshot_count(self) -> int:
        """Get the total number of snapshots"""
        return len(self.snapshots)

    def clear_snapshots(self) -> None:
        """Clear all snapshots"""
        self.snapshots.clear()
        self._current_index = -1


# ============================================================
# 10. Chaos Engineering – Fault Injection & Network Simulation
# ============================================================

class ChaosEngine:
    """
    Wstrzykiwanie błędów, symulacja sieci.
    """

    def __init__(self):
        self.enabled = False
        self._network_latency_ms: int = 0
        self._network_drop_rate: float = 0.0
        self._network_jitter_ms: int = 0
        self._original_socket = None

    def inject_fault(self, kind: str) -> None:
        if not self.enabled:
            return
        if kind == "io_error":
            raise IOError("Injected I/O error (chaos)")
        elif kind == "out_of_memory":
            raise MemoryError("Injected OOM (chaos)")
        elif kind == "disk_full":
            raise OSError("Injected disk full (chaos)")
        elif kind == "timeout":
            raise TimeoutError("Injected timeout (chaos)")
        elif kind == "connection_refused":
            raise ConnectionRefusedError("Injected connection refused (chaos)")

    def simulate_network(self, latency_ms: int = 0, drop_rate: float = 0.0, jitter_ms: int = 0) -> None:
        """Simulate network conditions (latency, packet loss, jitter)"""
        if not self.enabled:
            print("[CHAOS] Network simulation disabled")
            return
        
        self._network_latency_ms = latency_ms
        self._network_drop_rate = max(0.0, min(1.0, drop_rate))
        self._network_jitter_ms = jitter_ms
        
        print(f"[CHAOS] Network simulation enabled: latency={latency_ms}ms, drop_rate={drop_rate*100}%, jitter={jitter_ms}ms")
        
        # Note: Real network simulation requires system-level tools (tc, netem) or proxy
        # This is a simplified implementation that adds delays to socket operations
        self._patch_socket_module()

    def _patch_socket_module(self) -> None:
        """Patch socket module to add chaos effects"""
        import socket as socket_module
        
        if self._original_socket is None:
            self._original_socket = socket_module.socket
        
        def chaos_socket(*args, **kwargs):
            original_socket = self._original_socket(*args, **kwargs)
            
            # Wrap send/recv methods
            original_send = original_socket.send
            original_recv = original_socket.recv
            
            def chaos_send(data):
                # Apply packet drop
                if random.random() < self._network_drop_rate:
                    raise ConnectionError("Packet dropped (chaos)")
                
                # Apply latency
                if self._network_latency_ms > 0:
                    jitter = random.randint(-self._network_jitter_ms, self._network_jitter_ms)
                    time.sleep(max(0, (self._network_latency_ms + jitter) / 1000.0))
                
                return original_send(data)
            
            def chaos_recv(bufsize):
                # Apply packet drop
                if random.random() < self._network_drop_rate:
                    raise ConnectionError("Packet dropped (chaos)")
                
                # Apply latency
                if self._network_latency_ms > 0:
                    jitter = random.randint(-self._network_jitter_ms, self._network_jitter_ms)
                    time.sleep(max(0, (self._network_latency_ms + jitter) / 1000.0))
                
                return original_recv(bufsize)
            
            original_socket.send = chaos_send
            original_socket.recv = chaos_recv
            
            return original_socket
        
        socket_module.socket = chaos_socket

    def reset_network(self) -> None:
        """Reset network simulation to normal"""
        if self._original_socket:
            import socket as socket_module
            socket_module.socket = self._original_socket
        self._network_latency_ms = 0
        self._network_drop_rate = 0.0
        self._network_jitter_ms = 0
        print("[CHAOS] Network simulation reset")


# ============================================================
# 11. Security Auditing – Syscall Tracking & Sandbox Debugging
# ============================================================

class SecurityAuditor:
    """
    Audyt wywołań systemowych, sandbox debugging using sys.addaudithook().
    """

    def __init__(self):
        self.syscalls: List[Dict[str, Any]] = []
        self._audit_hook_enabled: bool = False
        self._original_audit_hook = None

    def track_syscall(self, event: str, args: Tuple[Any, ...]) -> None:
        """Track a syscall using Python's audit hook"""
        self.syscalls.append({
            "event": event,
            "args": str(args),
            "timestamp": time.time(),
        })

    def _audit_hook(self, event: str, args: Tuple[Any, ...]) -> None:
        """Internal audit hook callback"""
        # Track specific security-relevant events
        security_events = [
            "open", "compile", "exec", "import", "load_dynamic",
            "socket.connect", "socket.bind", "subprocess.Popen",
            "os.system", "os.exec", "os.spawn",
        ]
        
        if any(event.startswith(se) for se in security_events):
            self.track_syscall(event, args)

    def enable_audit_hook(self) -> None:
        """Enable Python's audit hook for system event tracking"""
        if self._audit_hook_enabled:
            return
        
        if sys.version_info < (3, 8):
            print("[SECURITY] sys.addaudithook requires Python 3.8+")
            return
        
        try:
            sys.addaudithook(self._audit_hook)
            self._audit_hook_enabled = True
            print("[SECURITY] Audit hook enabled")
        except Exception as e:
            print(f"[SECURITY ERROR] Failed to enable audit hook: {e}")

    def disable_audit_hook(self) -> None:
        """Disable audit hook (note: audit hooks cannot be removed in Python)"""
        # Python doesn't support removing audit hooks once added
        # We can only disable tracking
        self._audit_hook_enabled = False
        print("[SECURITY] Audit tracking disabled (hook remains in place)")

    def get_syscall_log(self) -> List[Dict[str, Any]]:
        return self.syscalls

    def filter_syscalls(self, event: str) -> List[Dict[str, Any]]:
        """Filter syscalls by event name"""
        return [s for s in self.syscalls if s["event"] == event]

    def clear_syscall_log(self) -> None:
        self.syscalls.clear()

    def sandbox_debugging(self, container_name: Optional[str] = None) -> None:
        """Run code in a sandboxed environment (Docker/gVisor)"""
        if psutil is None:
            print("[SECURITY] psutil not installed, sandbox debugging unavailable")
            return
        
        try:
            # Check if Docker is available
            import subprocess
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[SECURITY] Docker detected: {result.stdout.strip()}")
                if container_name:
                    print(f"[SECURITY] Would use container: {container_name}")
                else:
                    print("[SECURITY] Sandbox debugging requires container name")
            else:
                print("[SECURITY] Docker not available, sandbox debugging limited")
        except FileNotFoundError:
            print("[SECURITY] Docker not found, sandbox debugging unavailable")
        except Exception as e:
            print(f"[SECURITY ERROR] Sandbox debugging failed: {e}")

    def analyze_security_risks(self) -> List[Dict[str, Any]]:
        """Analyze syscall log for potential security risks"""
        risks = []
        
        for syscall in self.syscalls:
            event = syscall["event"]
            
            if event == "open" and "w" in syscall["args"]:
                risks.append({
                    "type": "file_write",
                    "severity": "medium",
                    "syscall": syscall,
                })
            elif event in ("exec", "compile", "os.exec", "os.spawn"):
                risks.append({
                    "type": "code_execution",
                    "severity": "high",
                    "syscall": syscall,
                })
            elif event.startswith("socket"):
                risks.append({
                    "type": "network_access",
                    "severity": "medium",
                    "syscall": syscall,
                })
        
        return risks


# ============================================================
# 12. OS Isolation (Linux Namespaces & Cgroups v2)
# ============================================================

@dataclass
class NamespaceConfig:
    pid: bool = True
    net: bool = True
    mnt: bool = True
    ipc: bool = True
    uts: bool = True
    user: bool = True


@dataclass
class CgroupConfig:
    memory_limit_mb: Optional[int] = None
    cpu_quota_us: Optional[int] = None
    cpu_period_us: Optional[int] = None
    io_read_bps: Optional[int] = None
    io_write_bps: Optional[int] = None
    pids_max: Optional[int] = None


class OSIsolation:
    """
    OS-level isolation using Linux Namespaces and Cgroups v2.
    Provides PID, NET, MNT, IPC, UTS, and USER namespace isolation.
    """

    def __init__(self):
        self._linux_available = self._check_linux()
        self._cgroup_v2_available = self._check_cgroup_v2()
        self._namespace_config = NamespaceConfig()
        self._cgroup_config = CgroupConfig()
        self._cgroup_path: Optional[str] = None
        self._original_namespace_fds: Dict[str, int] = {}

    def _check_linux(self) -> bool:
        """Check if running on Linux"""
        return sys.platform == "linux"

    def _check_cgroup_v2(self) -> bool:
        """Check if Cgroups v2 is available"""
        if not self._linux_available:
            return False
        try:
            return os.path.exists("/sys/fs/cgroup/cgroup.controllers")
        except Exception:
            return False

    def configure_namespaces(self, config: NamespaceConfig) -> None:
        """Configure which namespaces to isolate"""
        self._namespace_config = config
        print("[OS ISOLATION] Namespace configuration updated")

    def configure_cgroups(self, config: CgroupConfig) -> None:
        """Configure Cgroups v2 resource limits"""
        if not self._cgroup_v2_available:
            print("[OS ISOLATION] Cgroups v2 not available")
            return
        self._cgroup_config = config
        print("[OS ISOLATION] Cgroup configuration updated")

    def create_cgroup(self, name: str = "debugger_sandbox") -> bool:
        """Create a new Cgroup v2 for the sandbox"""
        if not self._cgroup_v2_available:
            print("[OS ISOLATION] Cgroups v2 not available")
            return False

        try:
            cgroup_root = "/sys/fs/cgroup"
            self._cgroup_path = os.path.join(cgroup_root, name)
            
            if not os.path.exists(self._cgroup_path):
                os.mkdir(self._cgroup_path)
                print(f"[OS ISOLATION] Created cgroup: {self._cgroup_path}")
            
            # Apply resource limits
            self._apply_cgroup_limits()
            return True
        except PermissionError:
            print("[OS ISOLATION] Permission denied - requires root")
            return False
        except Exception as e:
            print(f"[OS ISOLATION ERROR] Failed to create cgroup: {e}")
            return False

    def _apply_cgroup_limits(self) -> None:
        """Apply configured resource limits to the cgroup"""
        if not self._cgroup_path:
            return

        limits = [
            ("memory.max", str(self._cgroup_config.memory_limit_mb * 1024 * 1024) if self._cgroup_config.memory_limit_mb else None),
            ("cpu.max", f"{self._cgroup_config.cpu_quota_us if self._cgroup_config.cpu_quota_us else 'max'} {self._cgroup_config.cpu_period_us if self._cgroup_config.cpu_period_us else 100000}"),
            ("pids.max", str(self._cgroup_config.pids_max) if self._cgroup_config.pids_max else "max"),
        ]

        for limit_file, value in limits:
            if value and self._cgroup_path:
                try:
                    with open(os.path.join(self._cgroup_path, limit_file), "w") as f:
                        f.write(value)
                    print(f"[OS ISOLATION] Applied limit: {limit_file} = {value}")
                except Exception as e:
                    print(f"[OS ISOLATION ERROR] Failed to set {limit_file}: {e}")

    def unshare_namespaces(self) -> bool:
        """Unshare configured namespaces (requires root privileges)"""
        if not self._linux_available:
            print("[OS ISOLATION] Namespaces only available on Linux")
            return False

        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")

            namespace_flags = 0
            if self._namespace_config.pid:
                namespace_flags |= 0x20000000  # CLONE_NEWPID
            if self._namespace_config.net:
                namespace_flags |= 0x40000000  # CLONE_NEWNET
            if self._namespace_config.mnt:
                namespace_flags |= 0x00020000  # CLONE_NEWNS
            if self._namespace_config.ipc:
                namespace_flags |= 0x08000000  # CLONE_NEWIPC
            if self._namespace_config.uts:
                namespace_flags |= 0x04000000  # CLONE_NEWUTS
            if self._namespace_config.user:
                namespace_flags |= 0x10000000  # CLONE_NEWUSER

            if namespace_flags:
                result = libc.unshare(namespace_flags)
                if result == 0:
                    print("[OS ISOLATION] Successfully unshared namespaces")
                    return True
                else:
                    print(f"[OS ISOLATION ERROR] Failed to unshare namespaces: {result}")
                    return False
        except Exception as e:
            print(f"[OS ISOLATION ERROR] Namespace unshare failed: {e}")
            return False

    def set_hostname(self, hostname: str) -> bool:
        """Set hostname in UTS namespace"""
        if not self._linux_available:
            return False

        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            result = libc.sethostname(hostname.encode(), len(hostname))
            if result == 0:
                print(f"[OS ISOLATION] Hostname set to: {hostname}")
                return True
        except Exception as e:
            print(f"[OS ISOLATION ERROR] Failed to set hostname: {e}")
        return False

    def get_cgroup_stats(self) -> Dict[str, Any]:
        """Get current cgroup statistics"""
        if not self._cgroup_path or not os.path.exists(self._cgroup_path):
            return {}

        stats = {}
        try:
            # Memory stats
            with open(os.path.join(self._cgroup_path, "memory.current"), "r") as f:
                stats["memory_current"] = int(f.read().strip())
            with open(os.path.join(self._cgroup_path, "memory.max"), "r") as f:
                stats["memory_max"] = f.read().strip()

            # CPU stats
            with open(os.path.join(self._cgroup_path, "cpu.stat"), "r") as f:
                cpu_stats = {}
                for line in f:
                    if "usage_usec" in line:
                        cpu_stats["usage_usec"] = int(line.split()[1])
                stats["cpu"] = cpu_stats

            # PIDs
            with open(os.path.join(self._cgroup_path, "pids.current"), "r") as f:
                stats["pids_current"] = int(f.read().strip())
        except Exception as e:
            print(f"[OS ISOLATION ERROR] Failed to get cgroup stats: {e}")

        return stats

    def cleanup_cgroup(self) -> None:
        """Remove the cgroup"""
        if self._cgroup_path and os.path.exists(self._cgroup_path):
            try:
                os.rmdir(self._cgroup_path)
                print(f"[OS ISOLATION] Removed cgroup: {self._cgroup_path}")
                self._cgroup_path = None
            except Exception as e:
                print(f"[OS ISOLATION ERROR] Failed to remove cgroup: {e}")

    def is_available(self) -> bool:
        """Check if OS isolation features are available"""
        return self._linux_available


# ============================================================
# 13. Security & Syscalls (Seccomp, Capabilities, AppArmor/SELinux)
# ============================================================

@dataclass
class SeccompConfig:
    allowed_syscalls: List[str] = field(default_factory=lambda: [
        "read", "write", "exit", "exit_group", "rt_sigreturn",
        "fstat", "mmap", "mprotect", "munmap", "brk",
        "arch_prctl", "getpid", "gettid", "futex",
    ])
    blocked_syscalls: List[str] = field(default_factory=lambda: [
        "execve", "ptrace", "socket", "connect", "bind",
        "listen", "accept", "clone", "fork", "vfork",
    ])


@dataclass
class CapabilityConfig:
    drop_all: bool = True
    keep_capabilities: List[str] = field(default_factory=list)


class SecuritySandbox:
    """
    System call filtering and capability management using Seccomp-BPF
    and Linux capabilities.
    """

    def __init__(self):
        self._linux_available = sys.platform == "linux"
        self._seccomp_available = self._check_seccomp()
        self._seccomp_config = SeccompConfig()
        self._capability_config = CapabilityConfig()
        self._seccomp_filter_loaded = False

    def _check_seccomp(self) -> bool:
        """Check if Seccomp is available"""
        if not self._linux_available:
            return False
        try:
            with open("/proc/sys/kernel/seccomp", "r") as f:
                return f.read().strip() != "0"
        except Exception:
            return False

    def configure_seccomp(self, config: SeccompConfig) -> None:
        """Configure Seccomp syscall filtering"""
        self._seccomp_config = config
        print("[SECURITY SANDBOX] Seccomp configuration updated")

    def configure_capabilities(self, config: CapabilityConfig) -> None:
        """Configure Linux capabilities"""
        self._capability_config = config
        print("[SECURITY SANDBOX] Capability configuration updated")

    def load_seccomp_filter(self) -> bool:
        """Load Seccomp-BPF filter (requires libseccomp or ctypes)"""
        if not self._seccomp_available:
            print("[SECURITY SANDBOX] Seccomp not available")
            return False

        try:
            # This is a simplified implementation
            # In production, use libseccomp Python bindings or proper BPF generation
            import ctypes
            libc = ctypes.CDLL("libc.so.6")

            # Set SECCOMP_MODE_STRICT (mode 1)
            # This only allows read, write, exit, and sigreturn
            # For more complex filtering, use SECCOMP_MODE_FILTER (mode 2) with BPF
            result = libc.prctl(22, 1, 0, 0, 0)  # PR_SET_SECCOMP, SECCOMP_MODE_STRICT
            if result == 0:
                self._seccomp_filter_loaded = True
                print("[SECURITY SANDBOX] Seccomp strict mode enabled")
                return True
        except Exception as e:
            print(f"[SECURITY SANDBOX ERROR] Failed to load seccomp filter: {e}")
        return False

    def drop_capabilities(self) -> bool:
        """Drop Linux capabilities"""
        if not self._linux_available:
            print("[SECURITY SANDBOX] Capabilities only available on Linux")
            return False

        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")

            if self._capability_config.drop_all:
                # Drop all capabilities except those in keep list
                # CAP_SYS_ADMIN = 21, CAP_NET_ADMIN = 12, CAP_SYS_PTRACE = 19
                caps_to_drop = [
                    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                    16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34
                ]
                
                for cap in caps_to_drop:
                    if cap not in [self._cap_to_num(c) for c in self._capability_config.keep_capabilities]:
                        libc.prctl(24, cap, 0, 0, 0)  # PR_CAPBSET_DROP
                
                print("[SECURITY SANDBOX] Dropped all capabilities")
                return True
        except Exception as e:
            print(f"[SECURITY SANDBOX ERROR] Failed to drop capabilities: {e}")
        return False

    def _cap_to_num(self, cap_name: str) -> int:
        """Convert capability name to number"""
        cap_map = {
            "CAP_CHOWN": 0, "CAP_DAC_OVERRIDE": 1, "CAP_DAC_READ_SEARCH": 2,
            "CAP_FOWNER": 3, "CAP_FSETID": 4, "CAP_KILL": 5, "CAP_SETGID": 6,
            "CAP_SETUID": 7, "CAP_SETPCAP": 8, "CAP_LINUX_IMMUTABLE": 9,
            "CAP_NET_BIND_SERVICE": 10, "CAP_NET_BROADCAST": 11, "CAP_NET_ADMIN": 12,
            "CAP_NET_RAW": 13, "CAP_IPC_LOCK": 14, "CAP_IPC_OWNER": 15,
            "CAP_SYS_MODULE": 16, "CAP_SYS_RAWIO": 17, "CAP_SYS_CHROOT": 18,
            "CAP_SYS_PTRACE": 19, "CAP_SYS_PACCT": 20, "CAP_SYS_ADMIN": 21,
            "CAP_SYS_BOOT": 22, "CAP_SYS_NICE": 23, "CAP_SYS_RESOURCE": 24,
            "CAP_SYS_TIME": 25, "CAP_SYS_TTY_CONFIG": 26, "CAP_MKNOD": 27,
            "CAP_LEASE": 28, "CAP_AUDIT_WRITE": 29, "CAP_AUDIT_CONTROL": 30,
            "CAP_SETFCAP": 31, "CAP_MAC_OVERRIDE": 32, "CAP_MAC_ADMIN": 33,
            "CAP_SYSLOG": 34, "CAP_WAKE_ALARM": 35, "CAP_BLOCK_SUSPEND": 36,
        }
        return cap_map.get(cap_name, -1)

    def check_apparmor(self) -> bool:
        """Check if AppArmor is available"""
        if not self._linux_available:
            return False
        try:
            return os.path.exists("/sys/kernel/security/apparmor")
        except Exception:
            return False

    def check_selinux(self) -> bool:
        """Check if SELinux is available"""
        if not self._linux_available:
            return False
        try:
            return os.path.exists("/sys/fs/selinux")
        except Exception:
            return False

    def get_security_status(self) -> Dict[str, Any]:
        """Get security module status"""
        return {
            "linux_available": self._linux_available,
            "seccomp_available": self._seccomp_available,
            "seccomp_filter_loaded": self._seccomp_filter_loaded,
            "apparmor_available": self.check_apparmor(),
            "selinux_available": self.check_selinux(),
        }


# ============================================================
# 14. File System Sandboxing (Chroot, tmpfs, Read-Only Mounts)
# ============================================================

@dataclass
class FilesystemConfig:
    chroot_path: Optional[str] = None
    use_tmpfs: bool = True
    read_only_paths: List[str] = field(default_factory=list)
    bind_mounts: Dict[str, str] = field(default_factory=dict)  # source -> target


class FilesystemSandbox:
    """
    File system isolation using chroot, tmpfs, and read-only mounts.
    """

    def __init__(self):
        self._linux_available = sys.platform == "linux"
        self._config = FilesystemConfig()
        self._original_root: Optional[str] = None
        self._tmpfs_mounts: List[str] = []

    def configure(self, config: FilesystemConfig) -> None:
        """Configure filesystem sandbox"""
        self._config = config
        print("[FILESYSTEM SANDBOX] Configuration updated")

    def setup_chroot(self, path: str) -> bool:
        """Setup chroot environment (requires root)"""
        if not self._linux_available:
            print("[FILESYSTEM SANDBOX] Chroot only available on Linux")
            return False

        if not os.path.exists(path):
            print(f"[FILESYSTEM SANDBOX] Path does not exist: {path}")
            return False

        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")

            # Save original root
            self._original_root = os.getcwd()

            # Change root
            result = libc.chroot(path.encode())
            if result == 0:
                # Change to root directory
                os.chdir("/")
                self._config.chroot_path = path
                print(f"[FILESYSTEM SANDBOX] Chroot set to: {path}")
                return True
            else:
                print(f"[FILESYSTEM SANDBOX ERROR] Failed to chroot: {result}")
                return False
        except Exception as e:
            print(f"[FILESYSTEM SANDBOX ERROR] Chroot failed: {e}")
            return False

    def mount_tmpfs(self, mount_point: str, size_mb: int = 100) -> bool:
        """Mount tmpfs at specified path"""
        if not self._linux_available:
            print("[FILESYSTEM SANDBOX] tmpfs only available on Linux")
            return False

        try:
            if not os.path.exists(mount_point):
                os.makedirs(mount_point)

            import subprocess
            result = subprocess.run(
                ["mount", "-t", "tmpfs", "-o", f"size={size_mb}M", "tmpfs", mount_point],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._tmpfs_mounts.append(mount_point)
                print(f"[FILESYSTEM SANDBOX] Mounted tmpfs at: {mount_point} ({size_mb}MB)")
                return True
            else:
                print(f"[FILESYSTEM SANDBOX ERROR] Failed to mount tmpfs: {result.stderr}")
                return False
        except Exception as e:
            print(f"[FILESYSTEM SANDBOX ERROR] tmpfs mount failed: {e}")
            return False

    def mount_read_only(self, path: str) -> bool:
        """Mount path as read-only"""
        if not self._linux_available:
            print("[FILESYSTEM SANDBOX] Read-only mounts only available on Linux")
            return False

        try:
            import subprocess
            result = subprocess.run(
                ["mount", "-o", "remount,ro", path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._config.read_only_paths.append(path)
                print(f"[FILESYSTEM SANDBOX] Mounted read-only: {path}")
                return True
            else:
                print(f"[FILESYSTEM SANDBOX ERROR] Failed to mount read-only: {result.stderr}")
                return False
        except Exception as e:
            print(f"[FILESYSTEM SANDBOX ERROR] Read-only mount failed: {e}")
            return False

    def create_bind_mount(self, source: str, target: str) -> bool:
        """Create a bind mount"""
        if not self._linux_available:
            print("[FILESYSTEM SANDBOX] Bind mounts only available on Linux")
            return False

        try:
            if not os.path.exists(target):
                os.makedirs(target)

            import subprocess
            result = subprocess.run(
                ["mount", "--bind", source, target],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._config.bind_mounts[source] = target
                print(f"[FILESYSTEM SANDBOX] Bind mount: {source} -> {target}")
                return True
            else:
                print(f"[FILESYSTEM SANDBOX ERROR] Failed bind mount: {result.stderr}")
                return False
        except Exception as e:
            print(f"[FILESYSTEM SANDBOX ERROR] Bind mount failed: {e}")
            return False

    def cleanup(self) -> None:
        """Cleanup filesystem sandbox"""
        # Unmount tmpfs
        for mount_point in self._tmpfs_mounts:
            try:
                import subprocess
                subprocess.run(["umount", mount_point], capture_output=True)
                print(f"[FILESYSTEM SANDBOX] Unmounted: {mount_point}")
            except Exception as e:
                print(f"[FILESYSTEM SANDBOX ERROR] Failed to unmount {mount_point}: {e}")

        self._tmpfs_mounts.clear()

        # Note: chroot cannot be easily undone without proper process management
        # In production, use pivot_root or run in separate namespace


# ============================================================
# 15. Hard Sandboxing (MicroVMs, WebAssembly)
# ============================================================

@dataclass
class MicroVMConfig:
    backend: str = "firecracker"  # firecracker, gvisor, kata
    cpu_count: int = 1
    memory_mb: int = 512
    enable_network: bool = False


@dataclass
class WasmConfig:
    runtime: str = "wasmtime"  # wasmtime, wasmer, wasm3
    enable_wasi: bool = True
    memory_limit_mb: int = 256


class HardSandbox:
    """
    Hard sandboxing using MicroVMs (Firecracker, gVisor, Kata) and WebAssembly.
    """

    def __init__(self):
        self._microvm_config = MicroVMConfig()
        self._wasm_config = WasmConfig()
        self._firecracker_available = self._check_firecracker()
        self._gvisor_available = self._check_gvisor()
        self._wasm_available = self._check_wasm()
        self._microvm_process: Optional[int] = None

    def _check_firecracker(self) -> bool:
        """Check if Firecracker is available"""
        try:
            import subprocess
            result = subprocess.run(["firecracker-vmlinux", "--version"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def _check_gvisor(self) -> bool:
        """Check if gVisor runsc is available"""
        try:
            import subprocess
            result = subprocess.run(["runsc", "--version"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def _check_wasm(self) -> bool:
        """Check if WebAssembly runtime is available"""
        try:
            import subprocess
            result = subprocess.run(["wasmtime", "--version"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def configure_microvm(self, config: MicroVMConfig) -> None:
        """Configure MicroVM settings"""
        self._microvm_config = config
        print("[HARD SANDBOX] MicroVM configuration updated")

    def configure_wasm(self, config: WasmConfig) -> None:
        """Configure WebAssembly settings"""
        self._wasm_config = config
        print("[HARD SANDBOX] WebAssembly configuration updated")

    def start_firecracker_vm(self, kernel_path: str, rootfs_path: str) -> bool:
        """Start a Firecracker MicroVM"""
        if not self._firecracker_available:
            print("[HARD SANDBOX] Firecracker not available")
            return False

        try:
            import subprocess
            import shutil
            
            # Check if firecracker is available
            if not shutil.which("firecracker"):
                print("[HARD SANDBOX ERROR] firecracker not found in PATH")
                return False
            
            # Start Firecracker in background
            process = subprocess.Popen(
                ["firecracker", "--api-sock", "/tmp/firecracker.sock"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Check if process started successfully
            if process.poll() is not None:
                print("[HARD SANDBOX ERROR] firecracker process failed to start")
                return False
            
            self._microvm_process = process.pid
            print(f"[HARD SANDBOX] Firecracker VM started (PID: {process.pid})")
            
            # Configure VM via API (simplified)
            # In production, use proper API calls to configure kernel, rootfs, etc.
            return True
        except Exception as e:
            print(f"[HARD SANDBOX ERROR] Failed to start Firecracker: {e}")
            return False

    def stop_microvm(self) -> None:
        """Stop the MicroVM"""
        if self._microvm_process:
            try:
                import subprocess
                subprocess.run(["kill", str(self._microvm_process)], capture_output=True)
                print(f"[HARD SANDBOX] MicroVM stopped (PID: {self._microvm_process})")
                self._microvm_process = None
            except Exception as e:
                print(f"[HARD SANDBOX ERROR] Failed to stop MicroVM: {e}")

    def run_in_wasm(self, wasm_file: str) -> Optional[str]:
        """Run a WebAssembly file"""
        if not self._wasm_available:
            print("[HARD SANDBOX] WebAssembly runtime not available")
            return None

        try:
            import subprocess
            runtime = self._wasm_config.runtime
            args = [runtime]
            
            if self._wasm_config.enable_wasi:
                args.extend(["--dir", "."])
            
            args.append(wasm_file)
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"[HARD SANDBOX] WebAssembly execution successful")
                return result.stdout
            else:
                print(f"[HARD SANDBOX ERROR] WebAssembly execution failed: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print("[HARD SANDBOX ERROR] WebAssembly execution timeout")
            return None
        except Exception as e:
            print(f"[HARD SANDBOX ERROR] Failed to run WebAssembly: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get hard sandbox status"""
        return {
            "firecracker_available": self._firecracker_available,
            "gvisor_available": self._gvisor_available,
            "wasm_available": self._wasm_available,
            "microvm_running": self._microvm_process is not None,
            "microvm_pid": self._microvm_process,
        }


# ============================================================
# 16. Execution Limits (Timeouts, Resource Limits)
# ============================================================

@dataclass
class ExecutionLimits:
    timeout_seconds: float = 5.0
    max_memory_mb: int = 512
    max_output_size: int = 1024 * 1024  # 1MB
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    wall_time_limit: float = 10.0


class ExecutionLimiter:
    """
    Execution limits and resource constraints for sandboxed code.
    """

    def __init__(self):
        self._config = ExecutionLimits()
        self._start_time: Optional[float] = None
        self._output_buffer: io.StringIO = io.StringIO()
        self._output_size = 0

    def configure(self, config: ExecutionLimits) -> None:
        """Configure execution limits"""
        self._config = config
        print("[EXECUTION LIMITS] Configuration updated")

    def set_timeout(self, timeout_seconds: float) -> None:
        """Set execution timeout"""
        self._config.timeout_seconds = timeout_seconds

    def set_memory_limit(self, max_memory_mb: int) -> None:
        """Set memory limit"""
        self._config.max_memory_mb = max_memory_mb

    def set_output_limit(self, max_output_size: int) -> None:
        """Set output buffer size limit"""
        self._config.max_output_size = max_output_size

    def start_timer(self) -> None:
        """Start execution timer"""
        self._start_time = time.time()

    def check_timeout(self) -> bool:
        """Check if execution has exceeded timeout"""
        if self._start_time is None:
            return False
        
        elapsed = time.time() - self._start_time
        if elapsed > self._config.timeout_seconds:
            print(f"[EXECUTION LIMITS] Timeout exceeded: {elapsed:.2f}s > {self._config.timeout_seconds}s")
            return True
        return False

    def check_wall_time(self) -> bool:
        """Check if wall time limit exceeded"""
        if self._start_time is None:
            return False
        
        elapsed = time.time() - self._start_time
        if elapsed > self._config.wall_time_limit:
            print(f"[EXECUTION LIMITS] Wall time exceeded: {elapsed:.2f}s > {self._config.wall_time_limit}s")
            return True
        return False

    def capture_output(self, data: str) -> bool:
        """Capture output with size limit"""
        if self._output_size + len(data) > self._config.max_output_size:
            print(f"[EXECUTION LIMITS] Output size limit exceeded")
            return False
        
        self._output_buffer.write(data)
        self._output_size += len(data)
        return True

    def get_output(self) -> str:
        """Get captured output"""
        return self._output_buffer.getvalue()

    def clear_output(self) -> None:
        """Clear output buffer"""
        self._output_buffer = io.StringIO()
        self._output_size = 0

    def get_elapsed_time(self) -> float:
        """Get elapsed execution time"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def apply_rlimits(self) -> bool:
        """Apply resource limits using setrlimit (Unix only)"""
        if sys.platform == "win32":
            print("[EXECUTION LIMITS] setrlimit not available on Windows")
            return False

        try:
            import resource
            
            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (int(self._config.timeout_seconds), int(self._config.timeout_seconds)))
            
            # Set memory limit (address space)
            resource.setrlimit(resource.RLIMIT_AS, (self._config.max_memory_mb * 1024 * 1024, self._config.max_memory_mb * 1024 * 1024))
            
            # Set file size limit
            resource.setrlimit(resource.RLIMIT_FSIZE, (self._config.max_file_size, self._config.max_file_size))
            
            print("[EXECUTION LIMITS] Resource limits applied")
            return True
        except Exception as e:
            print(f"[EXECUTION LIMITS ERROR] Failed to apply rlimits: {e}")
            return False


# ============================================================
# 17. Python-Specific Sandboxing (Audit Hooks, Builtins,Env)
# ============================================================

class PythonSandbox:
    """
    Python-specific sandboxing using audit hooks, builtins filtering,
    and environment cleansing.
    """

    def __init__(self):
        self._audit_hook_enabled = False
        self._original_builtins: Dict[str, Any] = {}
        self._blocked_builtins: set = {
            'eval', 'exec', 'compile', 'open', 'file',
            '__import__', 'reload', 'exit', 'quit',
            'input', 'raw_input',
        }
        self._safe_builtins: Dict[str, Any] = {}
        self._original_environment: Dict[str, str] = {}
        self._audit_events: List[Dict[str, Any]] = []

    def enable_audit_hook(self) -> None:
        """Enable Python audit hook for security monitoring"""
        if sys.version_info < (3, 8):
            print("[PYTHON SANDBOX] Audit hooks require Python 3.8+")
            return

        if self._audit_hook_enabled:
            return

        try:
            sys.addaudithook(self._audit_callback)
            self._audit_hook_enabled = True
            print("[PYTHON SANDBOX] Audit hook enabled")
        except Exception as e:
            print(f"[PYTHON SANDBOX ERROR] Failed to enable audit hook: {e}")

    def _audit_callback(self, event: str, args: Tuple[Any, ...]) -> None:
        """Audit hook callback"""
        self._audit_events.append({
            "event": event,
            "args": str(args),
            "timestamp": time.time(),
        })

        # Block dangerous operations
        dangerous_events = [
            "compile", "exec", "eval", "open",
            "os.system", "os.exec", "os.spawn",
            "subprocess.Popen", "subprocess.run",
            "socket.connect", "socket.bind",
        ]

        if any(event.startswith(de) for de in dangerous_events):
            print(f"[PYTHON SANDBOX] Blocked dangerous operation: {event}")
            raise SecurityError(f"Blocked operation: {event}")

    def disable_audit_hook(self) -> None:
        """Disable audit hook (note: cannot be removed in Python)"""
        self._audit_hook_enabled = False
        print("[PYTHON SANDBOX] Audit tracking disabled")

    def filter_builtins(self) -> None:
        """Filter dangerous built-in functions"""
        # Save original builtins
        self._original_builtins = dict(__builtins__.__dict__) if hasattr(__builtins__, '__dict__') else dict(__builtins__)

        # Create safe builtins dict
        self._safe_builtins = {
            name: func for name, func in self._original_builtins.items()
            if name not in self._blocked_builtins and not name.startswith('_')
        }

        # Replace builtins
        import builtins
        for name in self._blocked_builtins:
            if name in builtins.__dict__:
                setattr(builtins, name, self._blocked_builtin_wrapper)

        print("[PYTHON SANDBOX] Builtins filtered")

    def _blocked_builtin_wrapper(self, *args, **kwargs):
        """Wrapper for blocked builtins"""
        raise SecurityError(f"Blocked built-in function: {self._blocked_builtin_wrapper.__name__}")

    def restore_builtins(self) -> None:
        """Restore original builtins"""
        import builtins
        for name, value in self._original_builtins.items():
            setattr(builtins, name, value)
        print("[PYTHON SANDBOX] Builtins restored")

    def cleanse_environment(self) -> None:
        """Cleanse environment variables"""
        # Save original environment
        self._original_environment = dict(os.environ)

        # Remove sensitive environment variables
        sensitive_keys = [
            'API_KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'PRIVATE_KEY',
            'AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'GOOGLE_CREDENTIALS',
            'DATABASE_URL', 'REDIS_URL', 'MONGO_URL',
        ]

        for key in list(os.environ.keys()):
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                del os.environ[key]

        print("[PYTHON SANDBOX] Environment cleansed")

    def restore_environment(self) -> None:
        """Restore original environment"""
        os.environ.clear()
        os.environ.update(self._original_environment)
        print("[PYTHON SANDBOX] Environment restored")

    def get_audit_events(self) -> List[Dict[str, Any]]:
        """Get audit event log"""
        return self._audit_events.copy()

    def clear_audit_events(self) -> None:
        """Clear audit event log"""
        self._audit_events.clear()


class SecurityError(Exception):
    """Security violation in sandbox"""
    pass


# ============================================================
# 18. Collaborative Debugging
# ============================================================

class CollaborativeDebugger:
    """
    Live sharing, post-mortem dump, integracja z APM.
    """

    def __init__(self, config: DebuggerConfig):
        self.config = config
        self.session_active = False
        self._participants: List[str] = []
        self._websocket_server: Optional[Any] = None
        self._apm_providers: Dict[str, Any] = {}
        self._shared_state: Dict[str, Any] = {}
        self._client_connections: List[Any] = []
        self._session_id: str = str(time.time())

    def start_live_session(self, host: str = "localhost", port: int = 8765) -> None:
        if not self.config.enable_collaboration:
            raise RuntimeError("Collaboration disabled")
        
        if websockets is None:
            print("[COLLAB] websockets not installed, using stub mode")
            self.session_active = True
            return
        
        async def run_server():
            self._websocket_server = await websockets.serve(
                self._handle_collaboration_message, host, port
            )
            print(f"[COLLAB] Live session started on {host}:{port} (Session ID: {self._session_id})")
            await self._websocket_server.wait_closed()
        
        # Start server in background
        import asyncio
        asyncio.create_task(run_server())
        self.session_active = True

    async def _handle_collaboration_message(self, websocket: Any, path: str) -> None:
        """Handle collaboration messages with session synchronization"""
        self._client_connections.append(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "join":
                        participant = data.get("participant", "anonymous")
                        self._participants.append(participant)
                        await self._broadcast_to_all({
                            "type": "joined",
                            "participant": participant,
                            "participants": self._participants,
                            "session_id": self._session_id,
                        })
                    elif msg_type == "leave":
                        participant = data.get("participant")
                        if participant in self._participants:
                            self._participants.remove(participant)
                        await self._broadcast_to_all({
                            "type": "left",
                            "participant": participant,
                            "participants": self._participants,
                        })
                    elif msg_type == "sync_state":
                        # Update shared state and broadcast to all
                        state_key = data.get("key")
                        state_value = data.get("value")
                        if state_key:
                            self._shared_state[state_key] = state_value
                            await self._broadcast_to_all({
                                "type": "state_update",
                                "key": state_key,
                                "value": state_value,
                                "participant": data.get("participant"),
                            })
                    elif msg_type == "request_state":
                        # Send current shared state to requester
                        await websocket.send(json.dumps({
                            "type": "state_sync",
                            "state": self._shared_state,
                        }))
                    elif msg_type == "chat":
                        # Broadcast chat message
                        await self._broadcast_to_all({
                            "type": "chat",
                            "message": data.get("message"),
                            "participant": data.get("participant"),
                            "timestamp": time.time(),
                        })
                    elif msg_type == "cursor_move":
                        # Broadcast cursor position
                        await self._broadcast_to_all({
                            "type": "cursor_update",
                            "file": data.get("file"),
                            "line": data.get("line"),
                            "participant": data.get("participant"),
                        }, exclude=websocket)
                except Exception as e:
                    print(f"[COLLAB ERROR] Failed to handle message: {e}")
        finally:
            if websocket in self._client_connections:
                self._client_connections.remove(websocket)

    async def _broadcast_to_all(self, message: Dict[str, Any], exclude: Optional[Any] = None) -> None:
        """Broadcast message to all connected clients"""
        for client in self._client_connections:
            if client != exclude:
                try:
                    await client.send(json.dumps(message))
                except Exception as e:
                    print(f"[COLLAB ERROR] Failed to send to client: {e}")

    def update_shared_state(self, key: str, value: Any) -> None:
        """Update shared state (can be called from debugger)"""
        self._shared_state[key] = value

    def get_shared_state(self, key: Optional[str] = None) -> Any:
        """Get shared state or entire state dict"""
        if key:
            return self._shared_state.get(key)
        return self._shared_state.copy()

    def stop_live_session(self) -> None:
        self.session_active = False
        if self._websocket_server:
            self._websocket_server.close()
            self._websocket_server = None
        self._participants.clear()
        self._client_connections.clear()
        self._shared_state.clear()
        print("[COLLAB] Live session stopped")

    def get_participants(self) -> List[str]:
        return self._participants.copy()

    def get_session_id(self) -> str:
        return self._session_id

    def generate_post_mortem_dump(
        self,
        exc: BaseException,
        logs: List[Dict[str, Any]],
        env: Dict[str, Any],
        path: str,
    ) -> None:
        report = {
            "exception": str(exc),
            "traceback": "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            ),
            "logs": logs,
            "environment": env,
            "timestamp": time.time(),
            "session_id": self._session_id,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[COLLAB] Post-mortem dump saved to {path}")

    def register_apm_provider(self, name: str, api_key: str, provider_type: str = "sentry") -> None:
        """Register an APM provider (Sentry, Datadog, OpenTelemetry)"""
        self._apm_providers[name] = {
            "api_key": api_key,
            "type": provider_type,
        }
        print(f"[COLLAB] Registered APM provider: {name} ({provider_type})")

    def integrate_apm(self, event: Dict[str, Any], provider: Optional[str] = None) -> None:
        """Send event to APM provider"""
        if not self._apm_providers:
            print("[COLLAB] No APM providers registered")
            return
        
        target_provider = provider or list(self._apm_providers.keys())[0]
        if target_provider not in self._apm_providers:
            print(f"[COLLAB] APM provider not found: {target_provider}")
            return
        
        provider_config = self._apm_providers[target_provider]
        
        if httpx is None:
            print("[COLLAB] httpx not installed, APM integration unavailable")
            return
        
        try:
            if provider_config["type"] == "sentry":
                self._send_to_sentry(event, provider_config["api_key"])
            elif provider_config["type"] == "datadog":
                self._send_to_datadog(event, provider_config["api_key"])
            else:
                print(f"[COLLAB] Unsupported APM provider type: {provider_config['type']}")
        except Exception as e:
            print(f"[COLLAB ERROR] Failed to send to APM: {e}")

    def _send_to_sentry(self, event: Dict[str, Any], api_key: str) -> None:
        """Send event to Sentry"""
        if httpx is None:
            return
        
        url = f"https://sentry.io/api/{api_key}/store/"
        response = httpx.post(url, json=event)
        response.raise_for_status()
        print("[COLLAB] Event sent to Sentry")

    def _send_to_datadog(self, event: Dict[str, Any], api_key: str) -> None:
        """Send event to Datadog"""
        if httpx is None:
            return
        
        url = "https://api.datadoghq.com/api/v1/events"
        response = httpx.post(
            url,
            headers={"DD-API-KEY": api_key},
            json=event,
        )
        response.raise_for_status()
        print("[COLLAB] Event sent to Datadog")


# ============================================================
# 13. Multi-Threading Debugging Support
# ============================================================

class MultiThreadDebugger:
    """
    Multi-threading debugging: thread freezing, context switching, thread-specific breakpoints.
    """

    def __init__(self, controller: ExecutionController):
        self.controller = controller
        self._frozen_threads: Dict[int, threading.Event] = {}
        self._thread_breakpoints: Dict[int, List[Breakpoint]] = defaultdict(list)
        self._active_thread_id: Optional[int] = None
        self._thread_contexts: Dict[int, Dict[str, Any]] = {}

    def freeze_thread(self, thread_id: int) -> bool:
        """Freeze a specific thread"""
        if thread_id not in threading._active():
            return False
        
        freeze_event = threading.Event()
        self._frozen_threads[thread_id] = freeze_event
        print(f"[MULTI-THREAD] Thread {thread_id} frozen")
        return True

    def unfreeze_thread(self, thread_id: int) -> bool:
        """Unfreeze a specific thread"""
        if thread_id in self._frozen_threads:
            self._frozen_threads[thread_id].set()
            del self._frozen_threads[thread_id]
            print(f"[MULTI-THREAD] Thread {thread_id} unfrozen")
            return True
        return False

    def unfreeze_all_threads(self) -> None:
        """Unfreeze all frozen threads"""
        for thread_id in list(self._frozen_threads.keys()):
            self.unfreeze_thread(thread_id)

    def switch_thread_context(self, thread_id: int) -> bool:
        """Switch debugging context to a specific thread"""
        if thread_id not in threading._active():
            return False
        
        self._active_thread_id = thread_id
        print(f"[MULTI-THREAD] Switched to thread {thread_id}")
        return True

    def get_active_thread_id(self) -> Optional[int]:
        """Get the currently active thread ID"""
        return self._active_thread_id

    def add_thread_breakpoint(self, thread_id: int, file: str, line: int, **kwargs) -> None:
        """Add a breakpoint specific to a thread"""
        bp = Breakpoint(file=file, line=line, **kwargs)
        self._thread_breakpoints[thread_id].append(bp)
        print(f"[MULTI-THREAD] Thread-specific breakpoint added for thread {thread_id}")

    def get_thread_breakpoints(self, thread_id: int) -> List[Breakpoint]:
        """Get breakpoints for a specific thread"""
        return self._thread_breakpoints.get(thread_id, [])

    def save_thread_context(self, thread_id: int, context: Dict[str, Any]) -> None:
        """Save the context of a thread"""
        self._thread_contexts[thread_id] = context

    def get_thread_context(self, thread_id: int) -> Optional[Dict[str, Any]]:
        """Get the saved context of a thread"""
        return self._thread_contexts.get(thread_id)

    def list_all_threads(self) -> List[Dict[str, Any]]:
        """List all threads with their status"""
        threads = []
        for thread in threading.enumerate():
            thread_id = thread.ident or 0
            threads.append({
                "id": thread_id,
                "name": thread.name,
                "alive": thread.is_alive(),
                "frozen": thread_id in self._frozen_threads,
                "active": thread_id == self._active_thread_id,
            })
        return threads


# ============================================================
# 15. CLI/TUI Interface (Debug Console)
# ============================================================

class DebugConsole:
    """
    Interactive CLI/TUI debugger console similar to pdb/ipdb.
    """

    def __init__(self, debugger: 'Debugger'):
        self.debugger = debugger
        self._safe_evaluator = SafeEvaluator()
        self._running = False
        self._commands = {
            'h': self._help,
            'help': self._help,
            'q': self._quit,
            'quit': self._quit,
            'exit': self._quit,
            'n': self._next,
            'next': self._next,
            's': self._step,
            'step': self._step,
            'c': self._continue,
            'continue': self._continue,
            'r': self._return,
            'return': self._return,
            'b': self._breakpoint,
            'break': self._breakpoint,
            'cl': self._clear_breakpoint,
            'clear': self._clear_breakpoint,
            'p': self._print,
            'print': self._print,
            'pp': self._pretty_print,
            'l': self._list,
            'list': self._list,
            'w': self._where,
            'where': self._where,
            'u': self._up,
            'up': self._up,
            'd': self._down,
            'down': self._down,
            'vars': self._variables,
            'locals': self._locals,
            'globals': self._globals,
            'ai': self._ai_help,
            'time': self._time_travel,
            'threads': self._list_threads,
            'collab': self._collab_status,
        }

    def start(self) -> None:
        """Start the interactive console"""
        self._running = True
        print("[DEBUG CONSOLE] Starting interactive debugger console")
        print("Type 'help' for available commands")
        
        try:
            while self._running:
                try:
                    line = input("(debugger) ").strip()
                    if not line:
                        continue
                    self._execute_command(line)
                except EOFError:
                    print("\nUse 'quit' to exit")
                except KeyboardInterrupt:
                    print("\nInterrupted. Type 'quit' to exit")
        finally:
            print("[DEBUG CONSOLE] Console closed")

    def _execute_command(self, line: str) -> None:
        """Execute a console command"""
        parts = line.split()
        if not parts:
            return  # Empty command, do nothing
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self._commands:
            try:
                self._commands[cmd](*args)
            except Exception as e:
                print(f"Error: {e}")
        else:
            # Try to evaluate as Python expression
            self._evaluate_expression(line)

    def _help(self, *args) -> None:
        """Show help"""
        print("""Available commands:
  h, help          - Show this help
  q, quit, exit    - Exit the debugger
  n, next          - Step over (next line)
  s, step          - Step into (enter function)
  c, continue      - Continue execution
  r, return        - Step out (return from function)
  b, break [file] [line] - Set breakpoint
  cl, clear [num]   - Clear breakpoint
  p, print <expr>  - Print expression
  pp <expr>        - Pretty print expression
  l, list [file]    - List source code
  w, where          - Show current position
  u, up            - Move up in stack
  d, down          - Move down in stack
  vars             - Show all variables
  locals           - Show local variables
  globals          - Show global variables
  ai <query>        - Ask AI for help
  time             - Time-travel commands
  threads          - List threads
  collab           - Collaboration status
""")

    def _quit(self, *args) -> None:
        """Quit the debugger"""
        self._running = False
        print("Exiting debugger...")

    def _next(self, *args) -> None:
        """Step over"""
        self.debugger.controller.step_over()
        print("Step over")

    def _step(self, *args) -> None:
        """Step into"""
        self.debugger.controller.step_into()
        print("Step into")

    def _continue(self, *args) -> None:
        """Continue execution"""
        print("Continuing execution...")

    def _return(self, *args) -> None:
        """Step out"""
        self.debugger.controller.step_out()
        print("Step out")

    def _breakpoint(self, *args) -> None:
        """Set breakpoint"""
        if len(args) >= 2:
            file, line = args[0], int(args[1])
            self.debugger.controller.add_breakpoint(file, line)
            print(f"Breakpoint set at {file}:{line}")
        else:
            print("Usage: break <file> <line>")

    def _clear_breakpoint(self, *args) -> None:
        """Clear breakpoint"""
        if args:
            index = int(args[0])
            if 0 <= index < len(self.debugger.controller.breakpoints):
                bp = self.debugger.controller.breakpoints.pop(index)
                print(f"Cleared breakpoint at {bp.file}:{bp.line}")
        else:
            print("Usage: clear <index>")

    def _print(self, *args) -> None:
        """Print expression"""
        if args:
            expr = ' '.join(args)
            self._evaluate_expression(expr)

    def _pretty_print(self, *args) -> None:
        """Pretty print expression"""
        if args:
            expr = ' '.join(args)
            result = self._evaluate_expression(expr, pretty=True)

    def _list(self, *args) -> None:
        """List source code"""
        print("Listing source code (not implemented in stub)")

    def _where(self, *args) -> None:
        """Show current position"""
        frame_info = self.debugger.controller.current_frame
        if frame_info:
            print(f"Current: {frame_info.filename}:{frame_info.lineno}")
        else:
            print("No current frame")

    def _up(self, *args) -> None:
        """Move up in stack"""
        print("Moving up in stack (not implemented in stub)")

    def _down(self, *args) -> None:
        """Move down in stack"""
        print("Moving down in stack (not implemented in stub)")

    def _variables(self, *args) -> None:
        """Show all variables"""
        self._locals()
        print("---")
        self._globals()

    def _locals(self, *args) -> None:
        """Show local variables"""
        frame_info = self.debugger.controller.current_frame
        if frame_info and hasattr(frame_info, 'frame'):
            print("Local variables:")
            for name, value in frame_info.frame.f_locals.items():
                print(f"  {name} = {repr(value)[:100]}")

    def _globals(self, *args) -> None:
        """Show global variables"""
        frame_info = self.debugger.controller.current_frame
        if frame_info and hasattr(frame_info, 'frame'):
            print("Global variables:")
            for name, value in frame_info.frame.f_globals.items():
                if not name.startswith('__'):
                    print(f"  {name} = {repr(value)[:100]}")

    def _ai_help(self, *args) -> None:
        """Ask AI for help"""
        if self.debugger.ai:
            query = ' '.join(args)
            if query:
                context = self._get_current_context()
                response = self.debugger.ai.genai_repl(query, context)
                print(f"AI: {response}")
        else:
            print("AI assistance not enabled")

    def _time_travel(self, *args) -> None:
        """Time-travel commands"""
        if self.debugger.time_travel:
            print(f"Snapshots: {self.debugger.time_travel.get_snapshot_count()}")
            print("Commands: back, forward, jump <index>, save <path>, load <path>")
        else:
            print("Time-travel not enabled")

    def _list_threads(self, *args) -> None:
        """List threads"""
        threads = self.debugger.multi_thread.list_all_threads()
        print("Threads:")
        for t in threads:
            status = "[frozen]" if t["frozen"] else "[active]" if t["active"] else ""
            print(f"  {t['id']}: {t['name']} {status}")

    def _collab_status(self, *args) -> None:
        """Collaboration status"""
        print(f"Session ID: {self.debugger.collab.get_session_id()}")
        print(f"Participants: {self.debugger.collab.get_participants()}")
        print(f"Session active: {self.debugger.collab.session_active}")

    def _evaluate_expression(self, expr: str, pretty: bool = False) -> None:
        """Safely evaluate an expression"""
        frame_info = self.debugger.controller.current_frame
        globals_dict = frame_info.frame.f_globals if frame_info else {}
        locals_dict = frame_info.frame.f_locals if frame_info else {}
        
        success, result, error = self._safe_evaluator.safe_eval(expr, globals_dict, locals_dict)
        if success:
            if pretty:
                import pprint
                pprint.pprint(result)
            else:
                print(repr(result))
        else:
            print(f"Error: {error}")

    def _get_current_context(self) -> Dict[str, Any]:
        """Get current execution context"""
        frame_info = self.debugger.controller.current_frame
        if frame_info and hasattr(frame_info, 'frame'):
            return {
                "locals": dict(frame_info.frame.f_locals),
                "globals": {k: v for k, v in frame_info.frame.f_globals.items() if not k.startswith('__')},
            }
        return {}


# ============================================================
# 17. Framework-Specific Handlers
# ============================================================

class FrameworkHandler:
    """Base class for framework-specific debugging handlers"""

    def inspect_object(self, obj: Any) -> Dict[str, Any]:
        """Inspect a framework-specific object"""
        return {"type": type(obj).__name__, "repr": repr(obj)}


class DjangoHandler(FrameworkHandler):
    """Handler for Django framework objects"""

    def inspect_object(self, obj: Any) -> Dict[str, Any]:
        result = super().inspect_object(obj)
        
        # Check for Django models
        try:
            from django.db import models
            if isinstance(obj, models.Model):
                result["django_model"] = True
                result["class"] = obj.__class__.__name__
                result["pk"] = obj.pk
                result["fields"] = {
                    field.name: getattr(obj, field.name)
                    for field in obj._meta.fields
                }
        except ImportError:
            pass
        
        # Check for QuerySet
        try:
            from django.db.models.query import QuerySet
            if isinstance(obj, QuerySet):
                result["django_queryset"] = True
                result["model"] = obj.model.__name__
                result["count"] = obj.count()
        except ImportError:
            pass
        
        return result


class FastAPIHandler(FrameworkHandler):
    """Handler for FastAPI framework objects"""

    def inspect_object(self, obj: Any) -> Dict[str, Any]:
        result = super().inspect_object(obj)
        
        # Check for Pydantic models
        try:
            from pydantic import BaseModel
            if isinstance(obj, BaseModel):
                result["pydantic_model"] = True
                result["fields"] = obj.model_dump()
        except ImportError:
            pass
        
        return result


class SQLAlchemyHandler(FrameworkHandler):
    """Handler for SQLAlchemy objects"""

    def inspect_object(self, obj: Any) -> Dict[str, Any]:
        result = super().inspect_object(obj)
        
        # Check for SQLAlchemy models
        try:
            from sqlalchemy.orm import declarative_base
            if hasattr(obj, '_sa_instance_state'):
                result["sqlalchemy_model"] = True
                result["class"] = obj.__class__.__name__
                result["columns"] = {
                    col.name: getattr(obj, col.name, None)
                    for col in obj.__table__.columns
                }
        except ImportError:
            pass
        
        return result


class PyTorchHandler(FrameworkHandler):
    """Handler for PyTorch objects"""

    def inspect_object(self, obj: Any) -> Dict[str, Any]:
        result = super().inspect_object(obj)
        
        # Check for PyTorch tensors
        try:
            import torch
            if isinstance(obj, torch.Tensor):
                result["pytorch_tensor"] = True
                result["shape"] = list(obj.shape)
                result["dtype"] = str(obj.dtype)
                result["device"] = str(obj.device)
                result["requires_grad"] = obj.requires_grad
        except ImportError:
            pass
        
        # Check for PyTorch models
        try:
            import torch.nn as nn
            if isinstance(obj, nn.Module):
                result["pytorch_model"] = True
                result["parameters"] = sum(p.numel() for p in obj.parameters())
        except ImportError:
            pass
        
        return result


class PandasHandler(FrameworkHandler):
    """Handler for Pandas objects"""

    def inspect_object(self, obj: Any) -> Dict[str, Any]:
        result = super().inspect_object(obj)
        
        # Check for DataFrame
        try:
            import pandas as pd
            if isinstance(obj, pd.DataFrame):
                result["pandas_dataframe"] = True
                result["shape"] = obj.shape
                result["columns"] = list(obj.columns)
                result["dtypes"] = obj.dtypes.to_dict()
                result["head"] = obj.head(5).to_dict()
        except ImportError:
            pass
        
        # Check for Series
        try:
            import pandas as pd
            if isinstance(obj, pd.Series):
                result["pandas_series"] = True
                result["length"] = len(obj)
                result["dtype"] = str(obj.dtype)
                result["head"] = obj.head(5).to_dict()
        except ImportError:
            pass
        
        return result


# ============================================================
# 18. Główny obiekt Debugger – integracja wszystkich komponentów
# ============================================================

class Debugger:
    """
    Wysokopoziomowy obiekt debuggera integrujący wszystkie funkcje.
    """

    def __init__(self, config: Optional[DebuggerConfig] = None):
        self.config = config or DebuggerConfig()
        self.controller = ExecutionController(self.config)
        self.state_inspector = StateInspector(self.controller)
        self.live_editor = LiveEditor(self.controller)
        self.logger = LoggerDiagnostics()
        self.profiler = Profiler()
        self.remote = RemoteDebugger(self.config)
        self.ai = AIAssistant() if self.config.enable_ai_assistance else None
        self.time_travel = TimeTravelDebugger() if self.config.enable_time_travel else None
        self.chaos = ChaosEngine()
        self.security = SecurityAuditor()
        self.collab = CollaborativeDebugger(self.config)
        self.multi_thread = MultiThreadDebugger(self.controller)
        self.safe_evaluator = SafeEvaluator()
        self.console = DebugConsole(self)
        self.framework_handlers: Dict[str, Any] = {}
        
        # Sandbox modules
        self.os_isolation = OSIsolation() if self.config.enable_os_isolation else None
        self.security_sandbox = SecuritySandbox() if self.config.enable_security_sandbox else None
        self.filesystem_sandbox = FilesystemSandbox() if self.config.enable_filesystem_sandbox else None
        self.hard_sandbox = HardSandbox() if self.config.enable_hard_sandbox else None
        self.execution_limiter = ExecutionLimiter() if self.config.enable_execution_limits else None
        self.python_sandbox = PythonSandbox() if self.config.enable_python_sandbox else None
        
        self._attached = False
        self._original_breakpointhook = sys.breakpointhook
        self._call_stack_depth = 0
        self._async_debugging_enabled = False
        self._thread_local = threading.local()
        self._subprocess_pids: List[int] = []

    def attach(self) -> None:
        """
        Podpięcie debuggera do bieżącego procesu.
        """
        if self._attached:
            return
        
        # Set trace function for current thread
        sys.settrace(self._trace_func)
        threading.settrace(self._trace_func)
        
        # Override sys.breakpointhook for native breakpoint() support
        sys.breakpointhook = self._breakpoint_handler
        
        self._attached = True
        print("[DEBUGGER] Attached to process")

    def detach(self) -> None:
        """
        Odpięcie debuggera.
        """
        if not self._attached:
            return
        
        sys.settrace(None)
        threading.settrace(None)
        sys.breakpointhook = self._original_breakpointhook
        
        self._attached = False
        print("[DEBUGGER] Detached from process")

    def _breakpoint_handler(self) -> None:
        """
        Handler for native Python breakpoint() calls.
        """
        frame = sys._getframe().f_back
        frame_info = inspect.getframeinfo(frame)
        self.controller.add_breakpoint(
            frame_info.filename,
            frame_info.lineno,
            temporary=True,
            log_message="Native breakpoint() call"
        )
        self.controller.pause(frame_info)

    def _trace_func(self, frame, event, arg):
        """
        Główna funkcja trace obsługująca wszystkie zdarzenia.
        """
        try:
            frame_info = inspect.getframeinfo(frame)
            
            if event == "call":
                self._call_stack_depth += 1
                # Check for async function calls
                if self._async_debugging_enabled and self._is_async_frame(frame):
                    self._handle_async_call(frame)
                    
            elif event == "line":
                # Check if we should stop based on step mode
                if self.controller._should_stop_at_frame(frame):
                    self.controller.pause(frame_info)
                    self.controller.reset_step_mode()
                
                # Check breakpoints
                self.controller.check_breakpoint(frame_info)
                
                # Record time-travel state
                if self.time_travel:
                    self.time_travel.record_state(frame_info)
                    
            elif event == "return":
                self._call_stack_depth -= 1
                if self._async_debugging_enabled and self._is_async_frame(frame):
                    self._handle_async_return(frame)
                    
            elif event == "exception":
                exc_type, exc_value, exc_tb = arg
                self.controller.handle_exception(exc_type, exc_value, exc_tb)
                
                if self.ai:
                    msg = self.ai.root_cause_analysis(exc_value)
                    self.logger.log("Error", msg, frame_info.filename, frame_info.lineno)
        except Exception as e:
            # Don't let trace errors crash the program
            self.logger.log("Error", f"Trace error: {e}")
        
        return self._trace_func

    def _is_async_frame(self, frame: Any) -> bool:
        """Check if frame is an async coroutine"""
        return frame.f_code.co_flags & 0x80  # CO_COROUTINE

    def _handle_async_call(self, frame: Any) -> None:
        """Handle async function call for debugging"""
        frame_info = inspect.getframeinfo(frame)
        self.logger.log("Debug", f"Async call: {frame.f_code.co_name} at {frame_info.filename}:{frame_info.lineno}")

    def _handle_async_return(self, frame: Any) -> None:
        """Handle async function return for debugging"""
        frame_info = inspect.getframeinfo(frame)
        self.logger.log("Debug", f"Async return: {frame.f_code.co_name} from {frame_info.filename}:{frame_info.lineno}")

    def enable_async_debugging(self) -> None:
        """Enable async/await debugging support"""
        self._async_debugging_enabled = True
        print("[DEBUGGER] Async debugging enabled")

    def disable_async_debugging(self) -> None:
        """Disable async/await debugging support"""
        self._async_debugging_enabled = False
        print("[DEBUGGER] Async debugging disabled")

    def track_subprocess(self, pid: int) -> None:
        """Track a subprocess for debugging"""
        self._subprocess_pids.append(pid)
        print(f"[DEBUGGER] Tracking subprocess PID: {pid}")

    def get_tracked_subprocesses(self) -> List[int]:
        """Get list of tracked subprocess PIDs"""
        return self._subprocess_pids.copy()

    def stop_tracking_subprocess(self, pid: int) -> bool:
        """Stop tracking a subprocess"""
        if pid in self._subprocess_pids:
            self._subprocess_pids.remove(pid)
            print(f"[DEBUGGER] Stopped tracking subprocess PID: {pid}")
            return True
        return False

    def register_framework_handler(self, name: str, handler: FrameworkHandler) -> None:
        """Register a framework-specific handler"""
        self.framework_handlers[name] = handler
        print(f"[DEBUGGER] Registered framework handler: {name}")

    def inspect_framework_object(self, obj: Any) -> Dict[str, Any]:
        """Inspect an object using registered framework handlers"""
        for handler in self.framework_handlers.values():
            result = handler.inspect_object(obj)
            if len(result) > 2:  # More than just type and repr
                return result
        
        # Fallback to basic inspection
        return {"type": type(obj).__name__, "repr": repr(obj)}

    def auto_register_framework_handlers(self) -> None:
        """Auto-register available framework handlers"""
        try:
            self.register_framework_handler("django", DjangoHandler())
        except Exception:
            pass
        
        try:
            self.register_framework_handler("fastapi", FastAPIHandler())
        except Exception:
            pass
        
        try:
            self.register_framework_handler("sqlalchemy", SQLAlchemyHandler())
        except Exception:
            pass
        
        try:
            self.register_framework_handler("pytorch", PyTorchHandler())
        except Exception:
            pass
        
        try:
            self.register_framework_handler("pandas", PandasHandler())
        except Exception:
            pass

    def run(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Uruchomienie funkcji z podpiętym debuggerem.
        """
        self.attach()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self.detach()


# ============================================================
# 14. Przykład użycia (do usunięcia w produkcji)
# ============================================================

def _example_function():
    x = 0
    for i in range(5):
        x += i
    return x


if __name__ == "__main__":
    cfg = DebuggerConfig(
        enable_ai_assistance=True,
        enable_time_travel=True,
        enable_remote_debugging=False,
        enable_chaos_engineering=False,
        enable_security_auditing=True,
        enable_collaboration=True,
    )
    dbg = Debugger(cfg)
    dbg.controller.add_breakpoint(__file__, 420, log_message="Hit example breakpoint")
    result = dbg.run(_example_function)
    print("Result:", result)
