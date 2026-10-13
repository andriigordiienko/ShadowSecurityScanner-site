"""Entry point for the scheduled marketing workflow.

Runs every few hours; each task decides whether it is due:
  release   every run         site version/changelog sync + release announcement
  metrics   once a day        stars / downloads / traffic snapshot
  mentions  once a day        new discussions + mentions → issue
  devto     once a day        next article to dev.to when the cadence allows
  kev       weekly (Mon ≥10 UTC)  KEV digest page for the previous week + post
  report    weekly (Mon ≥10 UTC)  metrics report → issue

`python run.py kev report` runs just those tasks, regardless of schedule.
Sets the step output site_changed=true when site files changed (→ deploy).
"""
from __future__ import annotations

import sys
import traceback

import devto
import kev_digest
import mentions
import metrics
import release_sync
from lib import CONFIG, gh_output, load_state, log, now, save_state, today


def due_tasks() -> dict:
    """Due task → the state marker to record once it succeeds."""
    state = load_state()
    t = now()
    week = "%d-w%02d" % t.isocalendar()[:2]
    tasks = {"release": None}
    if state.get("last_daily") != today().isoformat() and t.hour >= 6:
        tasks.update(metrics=("last_daily", today().isoformat()), mentions=None, devto=None)
    if t.weekday() == CONFIG["kev_digest_weekday"] and t.hour >= 10 and state.get("last_kev") != week:
        tasks["kev"] = ("last_kev", week)
    if t.weekday() == CONFIG["report_weekday"] and t.hour >= 10 and state.get("last_report") != week:
        tasks["report"] = ("last_report", week)
    return tasks


TASKS = {
    "release": release_sync.main,
    "metrics": lambda: metrics.snapshot() and False,
    "mentions": lambda: mentions.main() and False,
    "devto": lambda: devto.main(force="devto" in sys.argv[1:]),
    "kev": kev_digest.main,
    "report": lambda: metrics.weekly_report() and False,
}


def main() -> int:
    tasks = {t: None for t in sys.argv[1:]} or due_tasks()
    log(f"tasks: {', '.join(tasks)}")
    changed, failed = False, []
    for name, marker in tasks.items():
        try:
            changed |= bool(TASKS[name]())
        except Exception:
            traceback.print_exc()
            failed.append(name)
            continue
        if marker:  # tasks save state themselves, so re-read before marking
            state = load_state()
            state[marker[0]] = marker[1]
            save_state(state)
    gh_output(site_changed=str(changed).lower())
    if failed:
        log(f"failed tasks: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
