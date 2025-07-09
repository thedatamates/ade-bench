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

def get_all_test_dirs(experiment_dir):
    """Get all test directories from all task directories within the experiment."""
    all_test_dirs = []
    task_dirs = get_task_dirs(experiment_dir)
    
    for task_dir in task_dirs:
        task_name = os.path.basename(task_dir)
        test_dirs = sorted([d for d in glob.glob(f"{task_dir}/*") if os.path.isdir(d)])
        
        for test_dir in test_dirs:
            test_name = os.path.basename(test_dir)
            # Create a display name that includes both task and test info
            display_name = f"{task_name}/{test_name}"
            all_test_dirs.append({
                'path': test_dir,
                'task': task_name,
                'test': test_name,
                'display': display_name
            })
    
    return all_test_dirs

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

    # Get all test directories from all tasks
    all_test_dirs = get_all_test_dirs(experiment_dir)
    if not all_test_dirs:
        stdscr.addstr(0, 0, f"No test directories found in {experiment_dir}!")
        stdscr.refresh()
        stdscr.getch()
        return

    # Display header
    stdscr.addstr(0, 0, f"Latest experiment: {experiment_dir}")
    stdscr.addstr(1, 0, f"Found {len(all_test_dirs)} test results across all tasks")
    stdscr.addstr(2, 0, "Use ↑/↓ to select, Enter to open in Cursor, q to quit")
    stdscr.addstr(3, 0, "-" * 80)

    # Selection state
    current_idx = 0
    max_idx = len(all_test_dirs) - 1

    while True:
        # Display test directories
        for i, test_info in enumerate(all_test_dirs):
            y = i + 4
            if y >= curses.LINES - 1:
                break
                
            # Highlight current selection
            if i == current_idx:
                stdscr.attron(curses.A_REVERSE)
            
            # Display directory name with task info
            display_name = test_info['display']
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
            selected_dir = all_test_dirs[current_idx]['path']
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