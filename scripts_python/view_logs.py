#!/usr/bin/env python3

import curses
import glob
import os
from pathlib import Path
import subprocess

def get_latest_experiment():
    """Find the most recent experiment directory."""
    experiments = glob.glob("experiments/*")
    if not experiments:
        return None
    return max(experiments, key=os.path.getctime)

def get_task_dirs(experiment_dir):
    """Get all task directories within the experiment directory."""
    # Get all directories in the experiment directory
    return sorted([d for d in glob.glob(f"{experiment_dir}/*") if os.path.isdir(d)])

def get_test_dirs(task_dir):
    """Get all test directories within the task directory."""
    # Get all directories in the task directory
    return sorted([d for d in glob.glob(f"{task_dir}/*") if os.path.isdir(d)])

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.clear()
    
    # Get latest experiment
    experiment_dir = get_latest_experiment()
    if not experiment_dir:
        stdscr.addstr(0, 0, "No experiment directories found!")
        stdscr.refresh()
        stdscr.getch()
        return

    # Get task directories
    task_dirs = get_task_dirs(experiment_dir)
    if not task_dirs:
        stdscr.addstr(0, 0, f"No task directories found in {experiment_dir}!")
        stdscr.refresh()
        stdscr.getch()
        return

    # Get test directories from the first task directory
    test_dirs = get_test_dirs(task_dirs[0])
    if not test_dirs:
        stdscr.addstr(0, 0, f"No test directories found in {task_dirs[0]}!")
        stdscr.refresh()
        stdscr.getch()
        return

    # Display header
    stdscr.addstr(0, 0, f"Latest experiment: {experiment_dir}")
    stdscr.addstr(1, 0, f"Task directory: {os.path.basename(task_dirs[0])}")
    stdscr.addstr(2, 0, "Use ↑/↓ to select, Enter to open in Cursor, q to quit")
    stdscr.addstr(3, 0, "-" * 80)

    # Selection state
    current_idx = 0
    max_idx = len(test_dirs) - 1

    while True:
        # Display test directories
        for i, test_dir in enumerate(test_dirs):
            y = i + 4
            if y >= curses.LINES - 1:
                break
                
            # Highlight current selection
            if i == current_idx:
                stdscr.attron(curses.A_REVERSE)
            
            # Display directory name
            display_name = os.path.basename(test_dir)
            stdscr.addstr(y, 0, display_name)
            
            if i == current_idx:
                stdscr.attroff(curses.A_REVERSE)

        stdscr.refresh()

        # Handle input
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < max_idx:
            current_idx += 1
        elif key == ord('\n'):  # Enter key
            selected_dir = test_dirs[current_idx]
            log_file = os.path.join(selected_dir, "sessions", "agent.log")
            
            if os.path.exists(log_file):
                # Open the file in Cursor
                subprocess.run(['/Applications/Cursor.app/Contents/MacOS/Cursor', log_file])
            else:
                stdscr.addstr(curses.LINES - 1, 0, f"Log file not found: {log_file}")
                stdscr.refresh()
                stdscr.getch()
        elif key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main) 