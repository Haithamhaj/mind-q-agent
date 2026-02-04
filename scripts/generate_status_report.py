#!/usr/bin/env python3
"""
Mind-Q Agent Status Report Generator
Generates a comprehensive status report for the project.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Task definitions for each phase
TASKS = {
    "Phase 0": {
        1: ("KùzuDB Graph Interface", "mind_q_agent/graph/kuzu_graph.py", "tests/unit/test_kuzu_graph.py"),
        2: ("ChromaDB Vector Interface", "mind_q_agent/vector/chroma_vector.py", "tests/unit/test_chroma_vector.py"),
        3: ("Entity Extraction", "mind_q_agent/extraction/entity_extractor.py", "tests/unit/test_entity_extractor.py"),
        4: ("File Watcher", "mind_q_agent/watcher/file_watcher.py", "tests/unit/test_file_watcher.py"),
        5: ("Integration Test Phase 0", "tests/integration/test_phase0.py", None),
        6: ("Error Handling Layer", "mind_q_agent/utils/errors.py", "tests/unit/test_errors.py"),
        7: ("Config Manager", "mind_q_agent/config/manager.py", "tests/unit/test_config.py"),
        8: ("Logging System", "mind_q_agent/utils/logger.py", None),
        9: ("Schema Migration Script", "scripts/init_db.py", None),
        10: ("Phase 0 Documentation", "README_PHASE0.md", None),
    },
    "Phase 1": {
        11: ("Ingestion Pipeline Logic", "mind_q_agent/ingestion/pipeline.py", "tests/unit/test_ingestion_logic.py"),
        12: ("Ingestion Queue Worker", "mind_q_agent/ingestion/worker.py", "tests/unit/test_worker.py"),
        13: ("Edge Co-occurrence Logic", "mind_q_agent/ingestion/pipeline.py", None),
        14: ("Pipeline Unit Tests", "tests/unit/test_ingestion_logic.py", None),
        15: ("Search Engine (Vector)", "mind_q_agent/search/engine.py", "tests/unit/test_search_engine.py"),
        16: ("Search Result Formatting", "mind_q_agent/search/engine.py", None),
        17: ("Search Engine Unit Tests", "tests/unit/test_search_engine.py", None),
        18: ("CLI Structure", "mind_q_agent/cli.py", None),
        19: ("CLI Implementation", "main.py", None),
        20: ("Phase 1 E2E Test", "tests/e2e/test_phase1_e2e.py", None),
    },
    "Phase 2": {
        21: ("Interaction Tracking DB", "mind_q_agent/learning/tracker.py", "tests/unit/test_tracker.py"),
        22: ("Interaction Logger API", "mind_q_agent/learning/tracker.py", None),
        23: ("Hebbian Weight Formula", "mind_q_agent/learning/hebbian_math.py", "tests/unit/test_hebbian_math.py"),
        24: ("Hebbian Update Cycle", "mind_q_agent/learning/updater.py", "tests/unit/test_updater.py"),
        25: ("Temporal Decay Math", "mind_q_agent/learning/decay_math.py", "tests/unit/test_decay_math.py"),
        26: ("Decay Batch Job", "mind_q_agent/learning/decay_job.py", "tests/unit/test_decay_job.py"),
        27: ("Graph Pruning Logic", "mind_q_agent/learning/pruning.py", "tests/unit/test_pruning.py"),
        28: ("Pruning Execution Job", "mind_q_agent/learning/prune_job.py", "tests/unit/test_prune_job.py"),
        29: ("Maintenance Scheduler", "mind_q_agent/learning/scheduler.py", "tests/unit/test_scheduler.py"),
        30: ("Phase 2 Integration Test", None, None),
    },
    "Phase 3": {
        31: ("Web Scanner Fetcher", "mind_q_agent/discovery/fetcher.py", None),
        32: ("Web Content Parser", "mind_q_agent/discovery/parser.py", None),
        33: ("Discovery Loop", "mind_q_agent/discovery/engine.py", None),
        34: ("Uncertainty Schema Update", "mind_q_agent/graph/kuzu_graph.py", None),
        35: ("Confidence Score Logic", "mind_q_agent/learning/confidence.py", None),
        36: ("Hierarchy Classifier", "mind_q_agent/learning/hierarchy.py", None),
        37: ("Cluster Detection", "mind_q_agent/learning/cluster.py", None),
        38: ("Source Authority Config", "config/default.yaml", None),
        39: ("Authority Scorer", "mind_q_agent/learning/authority.py", None),
        40: ("Final System Polish", None, None),
    },
}

def check_dependencies():
    """Check if required dependencies are installed."""
    deps = {
        "kuzu": None,
        "chromadb": None,
        "pytest": None,
        "spacy": None,
        "sentence_transformers": None,
        "watchdog": None,
        "yaml": None,
        "fitz": None,  # PyMuPDF
    }
    
    for dep in deps:
        try:
            mod = importlib.import_module(dep)
            version = getattr(mod, "__version__", "installed")
            deps[dep] = version
        except ImportError:
            deps[dep] = None
    
    return deps

def count_files():
    """Count Python files in the project."""
    src_files = list((PROJECT_ROOT / "mind_q_agent").rglob("*.py"))
    test_files = list((PROJECT_ROOT / "tests").rglob("*.py"))
    
    return {
        "src": len(src_files),
        "tests": len(test_files),
        "src_list": sorted([str(f.relative_to(PROJECT_ROOT)) for f in src_files]),
        "test_list": sorted([str(f.relative_to(PROJECT_ROOT)) for f in test_files]),
    }

def run_tests():
    """Run pytest and capture results."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        output = result.stdout + result.stderr
        
        # Parse summary
        passed = failed = skipped = 0
        for line in output.split("\n"):
            if "passed" in line or "failed" in line or "skipped" in line:
                if "passed" in line:
                    try:
                        passed = int(line.split()[0])
                    except:
                        pass
                if "failed" in line:
                    try:
                        failed = int(line.split("failed")[0].split()[-1])
                    except:
                        pass
        
        # Alternative parsing
        import re
        match = re.search(r"(\d+) passed", output)
        if match:
            passed = int(match.group(1))
        match = re.search(r"(\d+) failed", output)
        if match:
            failed = int(match.group(1))
        match = re.search(r"(\d+) skipped", output)
        if match:
            skipped = int(match.group(1))
        
        return {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped,
            "output": output[-2000:] if len(output) > 2000 else output,
            "success": result.returncode == 0
        }
    except Exception as e:
        return {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "output": str(e),
            "success": False
        }

def check_task_completion():
    """Check completion status of each task."""
    results = {}
    
    for phase, tasks in TASKS.items():
        results[phase] = {}
        for task_num, (name, main_file, test_file) in tasks.items():
            file_exists = False
            test_exists = False
            
            if main_file:
                file_exists = (PROJECT_ROOT / main_file).exists()
            else:
                file_exists = True  # No file required
            
            if test_file:
                test_exists = (PROJECT_ROOT / test_file).exists()
            else:
                test_exists = True  # No test required
            
            # Consider complete if main file exists
            complete = file_exists
            
            results[phase][task_num] = {
                "name": name,
                "file_exists": file_exists,
                "test_exists": test_exists,
                "complete": complete
            }
    
    return results

def generate_progress_bar(completed, total, width=10):
    """Generate a progress bar."""
    filled = int(width * completed / total) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    return bar

def generate_report():
    """Generate the complete status report."""
    print("Generating Mind-Q Agent Status Report...")
    print("=" * 50)
    
    # Gather data
    deps = check_dependencies()
    files = count_files()
    tests = run_tests()
    tasks = check_task_completion()
    
    # Calculate phase completion
    phase_stats = {}
    for phase, task_results in tasks.items():
        completed = sum(1 for t in task_results.values() if t["complete"])
        total = len(task_results)
        phase_stats[phase] = {"completed": completed, "total": total}
    
    total_completed = sum(p["completed"] for p in phase_stats.values())
    total_tasks = sum(p["total"] for p in phase_stats.values())
    
    # Build report
    report = []
    report.append("=" * 50)
    report.append("       MIND-Q AGENT STATUS REPORT")
    report.append("=" * 50)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Dependencies
    report.append("📦 DEPENDENCIES STATUS:")
    report.append("-" * 30)
    for dep, version in deps.items():
        status = f"✅ {dep}: {version}" if version else f"❌ {dep}: NOT INSTALLED"
        report.append(status)
    report.append("")
    
    # Project structure
    report.append("📁 PROJECT STRUCTURE:")
    report.append("-" * 30)
    report.append(f"Total source files: {files['src']}")
    report.append(f"Total test files: {files['tests']}")
    report.append("")
    
    # Test results
    report.append("🧪 TEST RESULTS:")
    report.append("-" * 30)
    report.append(f"Total tests: {tests['total']}")
    report.append(f"✅ Passed: {tests['passed']}")
    report.append(f"❌ Failed: {tests['failed']}")
    report.append(f"⏭️ Skipped: {tests['skipped']}")
    report.append("")
    
    # Phase completion
    report.append("📊 PHASE COMPLETION:")
    report.append("-" * 30)
    
    next_tasks = []
    
    for phase, task_results in tasks.items():
        stats = phase_stats[phase]
        pct = int(100 * stats["completed"] / stats["total"]) if stats["total"] > 0 else 0
        bar = generate_progress_bar(stats["completed"], stats["total"])
        
        report.append(f"\n{phase}: {stats['completed']}/{stats['total']} tasks ({pct}%)")
        report.append(f"  {bar}")
        
        for task_num, info in sorted(task_results.items()):
            icon = "✅" if info["complete"] else "❌"
            report.append(f"  {icon} Task {task_num}: {info['name']}")
            
            if not info["complete"]:
                next_tasks.append(f"Task {task_num}: {info['name']}")
    
    report.append("")
    
    # Overall progress
    overall_pct = int(100 * total_completed / total_tasks) if total_tasks > 0 else 0
    report.append("🎯 OVERALL PROGRESS:")
    report.append("-" * 30)
    report.append(f"Completed: {total_completed}/{total_tasks} tasks ({overall_pct}%)")
    report.append("")
    
    for phase, stats in phase_stats.items():
        pct = int(100 * stats["completed"] / stats["total"]) if stats["total"] > 0 else 0
        bar = generate_progress_bar(stats["completed"], stats["total"])
        report.append(f"  {phase}: {bar} {pct}%")
    
    report.append("")
    
    # Next steps
    report.append("📝 NEXT STEPS:")
    report.append("-" * 30)
    if next_tasks:
        for task in next_tasks[:5]:
            report.append(f"  → {task}")
    else:
        report.append("  🎉 All tasks completed!")
    
    report.append("")
    report.append("=" * 50)
    
    # Print and save
    report_text = "\n".join(report)
    print(report_text)
    
    # Save to file
    report_path = PROJECT_ROOT / "STATUS_REPORT.txt"
    with open(report_path, "w") as f:
        f.write(report_text)
    
    print(f"\n📄 Report saved to: {report_path}")
    
    return report_text

if __name__ == "__main__":
    generate_report()
