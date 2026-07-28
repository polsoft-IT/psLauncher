"""
script_runner.py - Advanced script execution module for psLauncher

Provides:
- Script template system with predefined templates
- Advanced execution history and analytics
- Intelligent environment management
- Performance tracking and optimization
- Script validation and syntax checking
- Dependency management
"""

from __future__ import annotations

import os
import sys
import json
import time
import shutil
import subprocess
import threading
import concurrent.futures
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from collections import defaultdict
import hashlib
import copy


class ScriptType(Enum):
    """Supported script types"""
    PYTHON = "python"
    BATCH = "batch"
    POWERSHELL = "powershell"
    SHELL = "shell"
    NODE = "node"
    LUA = "lua"
    RUBY = "ruby"
    PERL = "perl"
    PHP = "php"
    R = "r"
    TCL = "tcl"
    VBSCRIPT = "vbs"
    GO = "go"
    JAVA = "java"
    TYPESCRIPT = "typescript"
    COFFEESCRIPT = "coffeescript"
    ELIXIR = "elixir"


class ExecutionStatus(Enum):
    """Execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ScriptTemplate:
    """Script template definition"""
    id: str
    name: str
    description: str
    script_type: ScriptType
    content: str
    variables: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)


@dataclass
class ExecutionRecord:
    """Single execution record"""
    id: str
    script_path: str
    script_name: str
    script_type: ScriptType
    status: ExecutionStatus
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    exit_code: Optional[int] = None
    output: str = ""
    error: str = ""
    environment: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStats:
    """Execution statistics for a script"""
    script_path: str
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    last_run: Optional[float] = None
    last_status: Optional[ExecutionStatus] = None


@dataclass
class ScheduledTask:
    """Scheduled task definition"""
    id: str
    script_path: str
    schedule_type: str  # "once", "interval", "daily", "weekly", "monthly"
    schedule_value: str  # e.g., "5m", "14:30", "monday", "1"
    enabled: bool = True
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    run_count: int = 0
    environment: Dict[str, str] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Script validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    syntax_ok: bool = True
    dependencies_ok: bool = True


@dataclass
class BackupInfo:
    """Script backup information"""
    script_path: str
    backup_path: str
    created_at: float
    size: int
    checksum: str


class ScriptTemplateManager:
    """Manages script templates"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = Path(templates_dir) if templates_dir else Path.cwd() / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, ScriptTemplate] = {}
        self._load_templates()
        self._create_default_templates()
    
    def _load_templates(self):
        """Load templates from directory"""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = ScriptTemplate(**data)
                    self.templates[template.id] = template
            except Exception:
                continue
    
    def _create_default_templates(self):
        """Create default templates if they don't exist"""
        default_templates = [
            ScriptTemplate(
                id="python_basic",
                name="Basic Python Script",
                description="Simple Python script template",
                script_type=ScriptType.PYTHON,
                content='''#!/usr/bin/env python3
"""
Basic Python Script Template
"""

def main():
    print("Hello from Python!")
    # Add your code here

if __name__ == "__main__":
    main()
''',
                variables=["main"],
                tags=["basic", "python"]
            ),
            ScriptTemplate(
                id="batch_basic",
                name="Basic Batch Script",
                description="Simple Windows batch script template",
                script_type=ScriptType.BATCH,
                content='''@echo off
REM Basic Batch Script Template
echo Hello from Batch!
REM Add your commands here
''',
                variables=[],
                tags=["basic", "windows", "batch"]
            ),
            ScriptTemplate(
                id="powershell_basic",
                name="Basic PowerShell Script",
                description="Simple PowerShell script template",
                script_type=ScriptType.POWERSHELL,
                content='''# Basic PowerShell Script Template
Write-Host "Hello from PowerShell!"
# Add your commands here
''',
                variables=[],
                tags=["basic", "windows", "powershell"]
            ),
            ScriptTemplate(
                id="python_with_args",
                name="Python with Arguments",
                description="Python script with command-line arguments",
                script_type=ScriptType.PYTHON,
                content='''#!/usr/bin/env python3
"""
Python Script with Arguments
"""
import sys

def main():
    if len(sys.argv) > 1:
        print(f"Arguments: {sys.argv[1:]}")
    else:
        print("No arguments provided")
    
    # Add your code here

if __name__ == "__main__":
    main()
''',
                variables=["sys.argv"],
                tags=["advanced", "python", "arguments"]
            ),
        ]
        
        for template in default_templates:
            if template.id not in self.templates:
                self.templates[template.id] = template
                self._save_template(template)
    
    def _save_template(self, template: ScriptTemplate):
        """Save template to file"""
        template_file = self.templates_dir / f"{template.id}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(template), f, indent=2, default=str)
    
    def add_template(self, template: ScriptTemplate):
        """Add a new template"""
        self.templates[template.id] = template
        self._save_template(template)
    
    def get_template(self, template_id: str) -> Optional[ScriptTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, script_type: Optional[ScriptType] = None) -> List[ScriptTemplate]:
        """List all templates, optionally filtered by type"""
        templates = list(self.templates.values())
        if script_type:
            templates = [t for t in templates if t.script_type == script_type]
        return templates
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        if template_id in self.templates:
            del self.templates[template_id]
            template_file = self.templates_dir / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
            return True
        return False
    
    def create_script_from_template(self, template_id: str, output_path: str, 
                                     variables: Optional[Dict[str, str]] = None) -> bool:
        """Create a script from template"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        content = template.content
        if variables:
            for var_name, var_value in variables.items():
                content = content.replace(f"{{{var_name}}}", var_value)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True


class ExecutionHistory:
    """Manages execution history and analytics"""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = Path(history_file) if history_file else Path.cwd() / "execution_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[ExecutionRecord] = []
        self.stats: Dict[str, ExecutionStats] = {}
        self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [ExecutionRecord(**r) for r in data.get('records', [])]
                    stats_data = data.get('stats', {})
                    self.stats = {k: ExecutionStats(**v) for k, v in stats_data.items()}
            except Exception:
                self.records = []
                self.stats = {}
    
    def _save_history(self):
        """Save history to file"""
        data = {
            'records': [asdict(r) for r in self.records],
            'stats': {k: asdict(v) for k, v in self.stats.items()}
        }
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_record(self, record: ExecutionRecord):
        """Add execution record"""
        self.records.append(record)
        
        # Update stats
        script_path = record.script_path
        if script_path not in self.stats:
            self.stats[script_path] = ExecutionStats(script_path=script_path)
        
        stats = self.stats[script_path]
        stats.total_runs += 1
        stats.last_run = record.start_time
        stats.last_status = record.status
        
        if record.status == ExecutionStatus.COMPLETED:
            stats.successful_runs += 1
        else:
            stats.failed_runs += 1
        
        if record.duration_ms:
            stats.total_duration_ms += record.duration_ms
            stats.avg_duration_ms = stats.total_duration_ms / stats.total_runs
            stats.min_duration_ms = min(stats.min_duration_ms, record.duration_ms)
            stats.max_duration_ms = max(stats.max_duration_ms, record.duration_ms)
        
        self._save_history()
    
    def get_records(self, script_path: Optional[str] = None, 
                    limit: int = 100) -> List[ExecutionRecord]:
        """Get execution records, optionally filtered by script"""
        records = self.records
        if script_path:
            records = [r for r in records if r.script_path == script_path]
        return records[-limit:]
    
    def get_stats(self, script_path: str) -> Optional[ExecutionStats]:
        """Get statistics for a script"""
        return self.stats.get(script_path)
    
    def get_all_stats(self) -> Dict[str, ExecutionStats]:
        """Get statistics for all scripts"""
        return self.stats
    
    def clear_history(self, script_path: Optional[str] = None):
        """Clear history, optionally for a specific script"""
        if script_path:
            self.records = [r for r in self.records if r.script_path != script_path]
            if script_path in self.stats:
                del self.stats[script_path]
        else:
            self.records = []
            self.stats = {}
        self._save_history()
    
    def get_success_rate(self, script_path: str) -> float:
        """Get success rate for a script (0.0 to 1.0)"""
        stats = self.get_stats(script_path)
        if not stats or stats.total_runs == 0:
            return 0.0
        return stats.successful_runs / stats.total_runs


class EnvironmentManager:
    """Manages script execution environments"""
    
    def __init__(self):
        self.interpreters: Dict[ScriptType, List[str]] = {}
        self._detect_interpreters()
    
    def _detect_interpreters(self):
        """Detect available interpreters"""
        # Python
        python_paths = [sys.executable, shutil.which("python"), shutil.which("python3")]
        self.interpreters[ScriptType.PYTHON] = [p for p in python_paths if p]
        
        # Batch (Windows only)
        if sys.platform == "win32":
            self.interpreters[ScriptType.BATCH] = [shutil.which("cmd.exe") or "cmd.exe"]
            self.interpreters[ScriptType.POWERSHELL] = [shutil.which("powershell") or "powershell.exe"]
            self.interpreters[ScriptType.VBSCRIPT] = [shutil.which("cscript") or "cscript.exe"]
        
        # Shell (Unix only)
        if sys.platform != "win32":
            self.interpreters[ScriptType.SHELL] = [shutil.which("bash") or shutil.which("sh") or "sh"]
        
        # Other interpreters
        self.interpreters[ScriptType.NODE] = [shutil.which("node") or shutil.which("nodejs")]
        self.interpreters[ScriptType.LUA] = [shutil.which("lua")]
        self.interpreters[ScriptType.RUBY] = [shutil.which("ruby")]
        self.interpreters[ScriptType.PERL] = [shutil.which("perl")]
        self.interpreters[ScriptType.PHP] = [shutil.which("php")]
        self.interpreters[ScriptType.R] = [shutil.which("Rscript")]
        self.interpreters[ScriptType.TCL] = [shutil.which("tclsh")]
        self.interpreters[ScriptType.GO] = [shutil.which("go")]
        self.interpreters[ScriptType.JAVA] = [shutil.which("java")]
        self.interpreters[ScriptType.TYPESCRIPT] = [shutil.which("ts-node"), shutil.which("deno")]
        self.interpreters[ScriptType.COFFEESCRIPT] = [shutil.which("coffee")]
        self.interpreters[ScriptType.ELIXIR] = [shutil.which("elixir")]
        
        # Remove None values
        for script_type in list(self.interpreters.keys()):
            self.interpreters[script_type] = [p for p in self.interpreters[script_type] if p]
            if not self.interpreters[script_type]:
                del self.interpreters[script_type]
    
    def get_interpreter(self, script_type: ScriptType) -> Optional[str]:
        """Get the best available interpreter for a script type"""
        interpreters = self.interpreters.get(script_type, [])
        return interpreters[0] if interpreters else None
    
    def get_all_interpreters(self, script_type: ScriptType) -> List[str]:
        """Get all available interpreters for a script type"""
        return self.interpreters.get(script_type, [])
    
    def is_available(self, script_type: ScriptType) -> bool:
        """Check if an interpreter is available for a script type"""
        return script_type in self.interpreters
    
    def detect_script_type(self, script_path: str) -> Optional[ScriptType]:
        """Detect script type from file extension"""
        path = Path(script_path)
        ext_map = {
            '.py': ScriptType.PYTHON,
            '.bat': ScriptType.BATCH,
            '.cmd': ScriptType.BATCH,
            '.ps1': ScriptType.POWERSHELL,
            '.sh': ScriptType.SHELL,
            '.js': ScriptType.NODE,
            '.lua': ScriptType.LUA,
            '.rb': ScriptType.RUBY,
            '.pl': ScriptType.PERL,
            '.php': ScriptType.PHP,
            '.r': ScriptType.R,
            '.R': ScriptType.R,
            '.tcl': ScriptType.TCL,
            '.vbs': ScriptType.VBSCRIPT,
            '.go': ScriptType.GO,
            '.java': ScriptType.JAVA,
            '.ts': ScriptType.TYPESCRIPT,
            '.coffee': ScriptType.COFFEESCRIPT,
            '.exs': ScriptType.ELIXIR,
        }
        return ext_map.get(path.suffix.lower())


class ParallelExecutor:
    """Executes multiple scripts in parallel"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def run_scripts(self, script_configs: List[Tuple[str, Optional[str], Optional[Dict[str, str]], Optional[int]]]) -> List[ExecutionRecord]:
        """
        Run multiple scripts in parallel
        script_configs: list of (script_path, working_dir, environment, timeout)
        """
        futures = []
        for script_path, working_dir, environment, timeout in script_configs:
            future = self.executor.submit(
                self._run_single_script,
                script_path,
                working_dir,
                environment,
                timeout
            )
            futures.append(future)
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Create a failed record
                result = ExecutionRecord(
                    id=hashlib.md5(f"error{time.time()}".encode()).hexdigest(),
                    script_path="unknown",
                    script_name="error",
                    script_type=ScriptType.PYTHON,
                    status=ExecutionStatus.FAILED,
                    start_time=time.time(),
                    end_time=time.time(),
                    duration_ms=0,
                    error=str(e)
                )
                results.append(result)
        
        return results
    
    def _run_single_script(self, script_path: str, working_dir: Optional[str] = None,
                           environment: Optional[Dict[str, str]] = None,
                           timeout: Optional[int] = None) -> ExecutionRecord:
        """Run a single script"""
        script_path = str(Path(script_path).absolute())
        env_manager = EnvironmentManager()
        script_type = env_manager.detect_script_type(script_path)
        
        if not script_type:
            return ExecutionRecord(
                id=hashlib.md5(f"{script_path}{time.time()}".encode()).hexdigest(),
                script_path=script_path,
                script_name=Path(script_path).name,
                script_type=ScriptType.PYTHON,
                status=ExecutionStatus.FAILED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error="Unsupported script type"
            )
        
        interpreter = env_manager.get_interpreter(script_type)
        if not interpreter:
            return ExecutionRecord(
                id=hashlib.md5(f"{script_path}{time.time()}".encode()).hexdigest(),
                script_path=script_path,
                script_name=Path(script_path).name,
                script_type=script_type,
                status=ExecutionStatus.FAILED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error=f"No interpreter available for {script_type.value}"
            )
        
        record = ExecutionRecord(
            id=hashlib.md5(f"{script_path}{time.time()}".encode()).hexdigest(),
            script_path=script_path,
            script_name=Path(script_path).name,
            script_type=script_type,
            status=ExecutionStatus.RUNNING,
            start_time=time.time(),
            environment=environment or {}
        )
        
        try:
            cmd = self._build_command(interpreter, script_path, script_type)
            process = subprocess.run(
                cmd,
                cwd=working_dir or str(Path(script_path).parent),
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            record.end_time = time.time()
            record.duration_ms = (record.end_time - record.start_time) * 1000
            record.exit_code = process.returncode
            record.output = process.stdout
            record.error = process.stderr
            
            if process.returncode == 0:
                record.status = ExecutionStatus.COMPLETED
            else:
                record.status = ExecutionStatus.FAILED
            
        except subprocess.TimeoutExpired:
            record.end_time = time.time()
            record.duration_ms = (record.end_time - record.start_time) * 1000
            record.status = ExecutionStatus.TIMEOUT
            record.error = "Script execution timed out"
        
        except Exception as e:
            record.end_time = time.time()
            record.duration_ms = (record.end_time - record.start_time) * 1000
            record.status = ExecutionStatus.FAILED
            record.error = str(e)
        
        return record
    
    def _build_command(self, interpreter: str, script_path: str, script_type: ScriptType) -> List[str]:
        """Build command for script execution"""
        if script_type == ScriptType.PYTHON:
            return [interpreter, script_path]
        elif script_type == ScriptType.BATCH:
            return [interpreter, "/C", script_path]
        elif script_type == ScriptType.POWERSHELL:
            return [interpreter, "-ExecutionPolicy", "Bypass", "-File", script_path]
        elif script_type == ScriptType.SHELL:
            return [interpreter, script_path]
        elif script_type == ScriptType.NODE:
            return [interpreter, script_path]
        elif script_type == ScriptType.GO:
            return [interpreter, "run", script_path]
        elif script_type == ScriptType.JAVA:
            return [interpreter, script_path]
        elif script_type == ScriptType.TYPESCRIPT:
            return [interpreter, script_path]
        else:
            return [interpreter, script_path]


class TaskScheduler:
    """Schedules and manages recurring script execution"""
    
    def __init__(self, scheduler_file: Optional[str] = None):
        self.scheduler_file = Path(scheduler_file) if scheduler_file else Path.cwd() / "scheduler.json"
        self.scheduler_file.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, ScheduledTask] = {}
        self._scheduler_thread = None
        self._running = False
        self._load_tasks()
    
    def _load_tasks(self):
        """Load scheduled tasks from file"""
        if self.scheduler_file.exists():
            try:
                with open(self.scheduler_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {k: ScheduledTask(**v) for k, v in data.items()}
            except Exception:
                self.tasks = {}
    
    def _save_tasks(self):
        """Save scheduled tasks to file"""
        data = {k: asdict(v) for k, v in self.tasks.items()}
        with open(self.scheduler_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_task(self, task: ScheduledTask):
        """Add a scheduled task"""
        self.tasks[task.id] = task
        self._save_tasks()
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[ScheduledTask]:
        """List all tasks"""
        return list(self.tasks.values())
    
    def enable_task(self, task_id: str):
        """Enable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self._save_tasks()
    
    def disable_task(self, task_id: str):
        """Disable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            self._save_tasks()
    
    def start_scheduler(self, script_runner: ScriptRunner):
        """Start the scheduler thread"""
        if self._running:
            return
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, args=(script_runner,))
        self._scheduler_thread.daemon = True
        self._scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the scheduler thread"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self, script_runner: ScriptRunner):
        """Main scheduler loop"""
        while self._running:
            current_time = time.time()
            
            for task in self.tasks.values():
                if not task.enabled:
                    continue
                
                if task.next_run and current_time >= task.next_run:
                    # Run the task
                    try:
                        script_runner.run_script(
                            task.script_path,
                            environment=task.environment
                        )
                        task.last_run = current_time
                        task.run_count += 1
                        self._update_next_run(task)
                    except Exception:
                        pass
            
            time.sleep(1)  # Check every second
    
    def _update_next_run(self, task: ScheduledTask):
        """Update the next run time for a task"""
        if task.schedule_type == "interval":
            # Parse interval (e.g., "5m" = 5 minutes, "1h" = 1 hour)
            value = task.schedule_value
            if value.endswith('s'):
                seconds = int(value[:-1])
            elif value.endswith('m'):
                seconds = int(value[:-1]) * 60
            elif value.endswith('h'):
                seconds = int(value[:-1]) * 3600
            else:
                seconds = int(value)
            
            task.next_run = time.time() + seconds
        
        elif task.schedule_type == "daily":
            # Parse time (e.g., "14:30")
            hour, minute = map(int, task.schedule_value.split(':'))
            now = datetime.now()
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            task.next_run = next_run.timestamp()
        
        elif task.schedule_type == "weekly":
            # Parse day and time (e.g., "monday 14:30")
            parts = task.schedule_value.split()
            day_name = parts[0].lower()
            time_str = parts[1] if len(parts) > 1 else "00:00"
            
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_day = days.index(day_name)
            
            hour, minute = map(int, time_str.split(':'))
            now = datetime.now()
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            while next_run.weekday() != target_day:
                next_run += timedelta(days=1)
            
            task.next_run = next_run.timestamp()
        
        self._save_tasks()


class ScriptValidator:
    """Validates scripts before execution"""
    
    def __init__(self):
        self.env_manager = EnvironmentManager()
    
    def validate(self, script_path: str) -> ValidationResult:
        """Validate a script"""
        result = ValidationResult(is_valid=True)
        script_path = str(Path(script_path).absolute())
        
        # Check if file exists
        if not Path(script_path).exists():
            result.is_valid = False
            result.errors.append("Script file does not exist")
            return result
        
        # Check if file is readable
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Cannot read script file: {e}")
            return result
        
        # Check script type
        script_type = self.env_manager.detect_script_type(script_path)
        if not script_type:
            result.warnings.append("Unknown script type")
        
        # Check if interpreter is available
        if script_type and not self.env_manager.is_available(script_type):
            result.is_valid = False
            result.errors.append(f"No interpreter available for {script_type.value}")
            result.dependencies_ok = False
        
        # Syntax check based on script type
        syntax_ok = self._check_syntax(script_path, script_type, content)
        if not syntax_ok:
            result.syntax_ok = False
            result.is_valid = False
            result.errors.append("Syntax check failed")
        
        # Check for common issues
        self._check_common_issues(script_path, script_type, content, result)
        
        return result
    
    def _check_syntax(self, script_path: str, script_type: Optional[ScriptType], content: str) -> bool:
        """Check script syntax"""
        if script_type == ScriptType.PYTHON:
            try:
                import py_compile
                py_compile.compile(script_path, doraise=True)
                return True
            except Exception:
                return False
        
        elif script_type == ScriptType.POWERSHELL:
            try:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", f"Test-Path -Path '{script_path}'"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except Exception:
                return True  # Skip syntax check if PowerShell is not available
        
        elif script_type == ScriptType.BATCH:
            # Basic check for batch files
            return True
        
        return True
    
    def _check_common_issues(self, script_path: str, script_type: Optional[ScriptType], 
                            content: str, result: ValidationResult):
        """Check for common script issues"""
        # Check for empty file
        if not content.strip():
            result.warnings.append("Script file is empty")
        
        # Check for very large files
        if len(content) > 1000000:  # 1MB
            result.warnings.append("Script file is very large (>1MB)")
        
        # Check for potential infinite loops (basic check)
        if script_type == ScriptType.PYTHON:
            if "while True:" in content and "break" not in content:
                result.warnings.append("Potential infinite loop detected (while True without break)")
        
        # Check for dangerous operations
        dangerous_patterns = ["rm -rf", "del /f", "format c:", "shutdown"]
        for pattern in dangerous_patterns:
            if pattern.lower() in content.lower():
                result.warnings.append(f"Potentially dangerous pattern detected: {pattern}")


class ScriptBackupManager:
    """Manages script backups"""
    
    def __init__(self, backup_dir: Optional[str] = None):
        self.backup_dir = Path(backup_dir) if backup_dir else Path.cwd() / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backups: Dict[str, List[BackupInfo]] = {}
        self._load_backups()
    
    def _load_backups(self):
        """Load backup information"""
        backup_info_file = self.backup_dir / "backup_info.json"
        if backup_info_file.exists():
            try:
                with open(backup_info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for script_path, backups in data.items():
                        self.backups[script_path] = [BackupInfo(**b) for b in backups]
            except Exception:
                self.backups = {}
    
    def _save_backups(self):
        """Save backup information"""
        backup_info_file = self.backup_dir / "backup_info.json"
        data = {
            k: [asdict(b) for b in v]
            for k, v in self.backups.items()
        }
        with open(backup_info_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_backup(self, script_path: str) -> Optional[BackupInfo]:
        """Create a backup of a script"""
        script_path = str(Path(script_path).absolute())
        
        if not Path(script_path).exists():
            return None
        
        # Generate backup filename
        script_name = Path(script_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{script_name}_{timestamp}"
        backup_path = self.backup_dir / backup_filename
        
        # Copy file
        try:
            shutil.copy2(script_path, backup_path)
            
            # Calculate checksum
            with open(script_path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            
            # Create backup info
            backup_info = BackupInfo(
                script_path=script_path,
                backup_path=str(backup_path),
                created_at=time.time(),
                size=backup_path.stat().st_size,
                checksum=checksum
            )
            
            # Store backup info
            if script_path not in self.backups:
                self.backups[script_path] = []
            self.backups[script_path].append(backup_info)
            
            # Keep only last 10 backups per script
            if len(self.backups[script_path]) > 10:
                self.backups[script_path] = self.backups[script_path][-10:]
            
            self._save_backups()
            return backup_info
        
        except Exception:
            return None
    
    def restore_backup(self, backup_info: BackupInfo) -> bool:
        """Restore a script from backup"""
        try:
            backup_path = Path(backup_info.backup_path)
            script_path = Path(backup_info.script_path)
            
            if not backup_path.exists():
                return False
            
            # Create backup of current file before restoring
            if script_path.exists():
                self.create_backup(str(script_path))
            
            # Restore from backup
            shutil.copy2(backup_path, script_path)
            return True
        
        except Exception:
            return False
    
    def get_backups(self, script_path: str) -> List[BackupInfo]:
        """Get all backups for a script"""
        script_path = str(Path(script_path).absolute())
        return self.backups.get(script_path, [])
    
    def delete_backup(self, backup_info: BackupInfo) -> bool:
        """Delete a backup"""
        try:
            backup_path = Path(backup_info.backup_path)
            if backup_path.exists():
                backup_path.unlink()
            
            # Remove from backup info
            script_path = backup_info.script_path
            if script_path in self.backups:
                self.backups[script_path] = [
                    b for b in self.backups[script_path]
                    if b.backup_path != backup_info.backup_path
                ]
                if not self.backups[script_path]:
                    del self.backups[script_path]
            
            self._save_backups()
            return True
        
        except Exception:
            return False
    
    def cleanup_old_backups(self, days: int = 30):
        """Delete backups older than specified days"""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        for script_path in list(self.backups.keys()):
            self.backups[script_path] = [
                b for b in self.backups[script_path]
                if b.created_at > cutoff_time
            ]
            
            # Delete actual files
            for backup in self.backups[script_path]:
                backup_path = Path(backup.backup_path)
                if backup_path.exists():
                    backup_path.unlink()
            
            if not self.backups[script_path]:
                del self.backups[script_path]
        
        self._save_backups()


class NotificationManager:
    """Manages notifications for script execution results"""
    
    def __init__(self):
        self._notification_callbacks: List[Callable[[str, str, ExecutionStatus], None]] = []
        self._enabled = True
    
    def register_callback(self, callback: Callable[[str, str, ExecutionStatus], None]):
        """Register a notification callback"""
        self._notification_callbacks.append(callback)
    
    def notify(self, script_name: str, message: str, status: ExecutionStatus):
        """Send notification"""
        if not self._enabled:
            return
        
        for callback in self._notification_callbacks:
            try:
                callback(script_name, message, status)
            except Exception:
                pass
    
    def notify_success(self, script_name: str, duration_ms: float):
        """Notify about successful execution"""
        message = f"Script completed successfully in {duration_ms:.0f}ms"
        self.notify(script_name, message, ExecutionStatus.COMPLETED)
    
    def notify_failure(self, script_name: str, error: str):
        """Notify about failed execution"""
        message = f"Script failed: {error}"
        self.notify(script_name, message, ExecutionStatus.FAILED)
    
    def notify_timeout(self, script_name: str):
        """Notify about timeout"""
        message = "Script execution timed out"
        self.notify(script_name, message, ExecutionStatus.TIMEOUT)
    
    def enable(self):
        """Enable notifications"""
        self._enabled = True
    
    def disable(self):
        """Disable notifications"""
        self._enabled = False


class ScriptRunner:
    """Advanced script runner with history, templates, and environment management"""
    
    def __init__(self, templates_dir: Optional[str] = None, history_file: Optional[str] = None,
                 scheduler_file: Optional[str] = None, backup_dir: Optional[str] = None):
        self.template_manager = ScriptTemplateManager(templates_dir)
        self.execution_history = ExecutionHistory(history_file)
        self.environment_manager = EnvironmentManager()
        self.parallel_executor = ParallelExecutor(max_workers=4)
        self.task_scheduler = TaskScheduler(scheduler_file)
        self.script_validator = ScriptValidator()
        self.backup_manager = ScriptBackupManager(backup_dir)
        self.notification_manager = NotificationManager()
        self._running_scripts: Dict[str, str] = {}  # execution_id -> script_path
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_complete': [],
            'on_error': [],
            'on_output': [],
        }
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for an event"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, *args, **kwargs):
        """Trigger all callbacks for an event"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass
    
    def run_script(self, script_path: str, working_dir: Optional[str] = None,
                   environment: Optional[Dict[str, str]] = None,
                   timeout: Optional[int] = None) -> ExecutionRecord:
        """Run a script and record execution"""
        script_path = str(Path(script_path).absolute())
        script_type = self.environment_manager.detect_script_type(script_path)
        
        if not script_type:
            raise ValueError(f"Unsupported script type: {Path(script_path).suffix}")
        
        interpreter = self.environment_manager.get_interpreter(script_type)
        if not interpreter:
            raise ValueError(f"No interpreter available for {script_type.value}")
        
        execution_id = hashlib.md5(f"{script_path}{time.time()}".encode()).hexdigest()
        self._running_scripts[execution_id] = script_path
        
        record = ExecutionRecord(
            id=execution_id,
            script_path=script_path,
            script_name=Path(script_path).name,
            script_type=script_type,
            status=ExecutionStatus.RUNNING,
            start_time=time.time(),
            environment=environment or {}
        )
        
        self._trigger_callback('on_start', record)
        
        try:
            # Build command
            cmd = self._build_command(interpreter, script_path, script_type)
            
            # Run script
            process = subprocess.run(
                cmd,
                cwd=working_dir or str(Path(script_path).parent),
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            record.end_time = time.time()
            record.duration_ms = (record.end_time - record.start_time) * 1000
            record.exit_code = process.returncode
            record.output = process.stdout
            record.error = process.stderr
            
            if process.returncode == 0:
                record.status = ExecutionStatus.COMPLETED
                self._trigger_callback('on_complete', record)
            else:
                record.status = ExecutionStatus.FAILED
                self._trigger_callback('on_error', record)
            
        except subprocess.TimeoutExpired:
            record.end_time = time.time()
            record.duration_ms = (record.end_time - record.start_time) * 1000
            record.status = ExecutionStatus.TIMEOUT
            record.error = "Script execution timed out"
            self._trigger_callback('on_error', record)
        
        except Exception as e:
            record.end_time = time.time()
            record.duration_ms = (record.end_time - record.start_time) * 1000
            record.status = ExecutionStatus.FAILED
            record.error = str(e)
            self._trigger_callback('on_error', record)
        
        finally:
            if execution_id in self._running_scripts:
                del self._running_scripts[execution_id]
            self.execution_history.add_record(record)
        
        return record
    
    def _build_command(self, interpreter: str, script_path: str, 
                      script_type: ScriptType) -> List[str]:
        """Build command for script execution"""
        if script_type == ScriptType.PYTHON:
            return [interpreter, script_path]
        elif script_type == ScriptType.BATCH:
            return [interpreter, "/C", script_path]
        elif script_type == ScriptType.POWERSHELL:
            return [interpreter, "-ExecutionPolicy", "Bypass", "-File", script_path]
        elif script_type == ScriptType.SHELL:
            return [interpreter, script_path]
        elif script_type == ScriptType.NODE:
            return [interpreter, script_path]
        elif script_type == ScriptType.GO:
            return [interpreter, "run", script_path]
        elif script_type == ScriptType.JAVA:
            return [interpreter, script_path]
        elif script_type == ScriptType.TYPESCRIPT:
            return [interpreter, script_path]
        else:
            return [interpreter, script_path]
    
    def get_template_manager(self) -> ScriptTemplateManager:
        """Get the template manager"""
        return self.template_manager
    
    def get_execution_history(self) -> ExecutionHistory:
        """Get the execution history"""
        return self.execution_history
    
    def get_environment_manager(self) -> EnvironmentManager:
        """Get the environment manager"""
        return self.environment_manager
    
    def get_parallel_executor(self) -> ParallelExecutor:
        """Get the parallel executor"""
        return self.parallel_executor
    
    def get_task_scheduler(self) -> TaskScheduler:
        """Get the task scheduler"""
        return self.task_scheduler
    
    def get_script_validator(self) -> ScriptValidator:
        """Get the script validator"""
        return self.script_validator
    
    def get_backup_manager(self) -> ScriptBackupManager:
        """Get the backup manager"""
        return self.backup_manager
    
    def get_notification_manager(self) -> NotificationManager:
        """Get the notification manager"""
        return self.notification_manager
    
    def run_scripts_parallel(self, script_configs: List[Tuple[str, Optional[str], Optional[Dict[str, str]], Optional[int]]]) -> List[ExecutionRecord]:
        """Run multiple scripts in parallel"""
        return self.parallel_executor.run_scripts(script_configs)
    
    def validate_script(self, script_path: str) -> ValidationResult:
        """Validate a script before execution"""
        return self.script_validator.validate(script_path)
    
    def create_backup(self, script_path: str) -> Optional[BackupInfo]:
        """Create a backup of a script"""
        return self.backup_manager.create_backup(script_path)
    
    def restore_backup(self, backup_info: BackupInfo) -> bool:
        """Restore a script from backup"""
        return self.backup_manager.restore_backup(backup_info)
    
    def get_backups(self, script_path: str) -> List[BackupInfo]:
        """Get all backups for a script"""
        return self.backup_manager.get_backups(script_path)
    
    def start_scheduler(self):
        """Start the task scheduler"""
        self.task_scheduler.start_scheduler(self)
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.task_scheduler.stop_scheduler()
    
    def add_scheduled_task(self, task: ScheduledTask):
        """Add a scheduled task"""
        self.task_scheduler.add_task(task)
    
    def remove_scheduled_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        return self.task_scheduler.remove_task(task_id)
    
    def list_scheduled_tasks(self) -> List[ScheduledTask]:
        """List all scheduled tasks"""
        return self.task_scheduler.list_tasks()
    
    def run_script_with_validation(self, script_path: str, working_dir: Optional[str] = None,
                                   environment: Optional[Dict[str, str]] = None,
                                   timeout: Optional[int] = None,
                                   create_backup_before: bool = False) -> ExecutionRecord:
        """Run a script with validation and optional backup"""
        # Validate first
        validation = self.validate_script(script_path)
        if not validation.is_valid:
            return ExecutionRecord(
                id=hashlib.md5(f"{script_path}{time.time()}".encode()).hexdigest(),
                script_path=script_path,
                script_name=Path(script_path).name,
                script_type=self.environment_manager.detect_script_type(script_path) or ScriptType.PYTHON,
                status=ExecutionStatus.FAILED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error="Validation failed: " + "; ".join(validation.errors)
            )
        
        # Create backup if requested
        if create_backup_before:
            self.create_backup(script_path)
        
        # Run the script
        record = self.run_script(script_path, working_dir, environment, timeout)
        
        # Send notification
        if record.status == ExecutionStatus.COMPLETED:
            self.notification_manager.notify_success(record.script_name, record.duration_ms or 0)
        elif record.status == ExecutionStatus.FAILED:
            self.notification_manager.notify_failure(record.script_name, record.error)
        elif record.status == ExecutionStatus.TIMEOUT:
            self.notification_manager.notify_timeout(record.script_name)
        
        return record


# Convenience functions
def create_runner(templates_dir: Optional[str] = None, 
                  history_file: Optional[str] = None) -> ScriptRunner:
    """Create a new ScriptRunner instance"""
    return ScriptRunner(templates_dir, history_file)


if __name__ == "__main__":
    # Test the script runner
    runner = create_runner()
    
    print("=== Available Interpreters ===")
    for script_type, interpreters in runner.environment_manager.interpreters.items():
        print(f"{script_type.value}: {interpreters}")
    
    print("\n=== Available Templates ===")
    for template in runner.template_manager.list_templates():
        print(f"{template.name} ({template.script_type.value}): {template.description}")
