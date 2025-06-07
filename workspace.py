#!/usr/bin/python3

import sys
import subprocess

def help():
  print("""
examples:
  -------------------------------------------------------------------------
  | workspace help               | Display this help.                     |
  | workspace move 7 8           | Moves all windows from desktop 7 to 8. |
  | workspace list               | List all workspaces.                   |
  | workspace listwin            | List all windows.                      |
  | workspace listwin 8          | List all windows in workspace 8.       |
  | workspace rename 3 "foo bar" | Rename workspace 3 to "foo bar".       |
  | workspace switch 4           | switch to workspace 4.
  -------------------------------------------------------------------------
""")

def argv_or(n, default):
  if len(sys.argv) > n:
    return sys.argv[n]
  return default

def run_command(command):
  result = subprocess.run(command, capture_output=True, shell=True, text=True)
  if result.returncode == 0:
    return result.stdout
  else:
    return f"Error: code {result.returncode}\n{result.stderr}"

def iterate_windows(desktop):
  result = run_command("wmctrl -l")
  windows = result.split("\n")
  for window in windows:
    a = window.split(" ")
    if len(a) < 3:
      continue
    win_id = a[0]
    i = 1
    while a[i].strip() == "":
      i += 1
    if desktop == a[i]:
      yield win_id

def move_window_to_desktop(win_id, desktop):
  run_command(f"wmctrl -i -r {win_id} -t {desktop}")

def move(source_desktop, dest_desktop):
  for win_id in iterate_windows(source_desktop):
    move_window_to_desktop(win_id, dest_desktop)

def list_workspaces():
  print(run_command("wmctrl -d"))

def list_windows(desktop):
  result = run_command("wmctrl -l")
  if desktop == "none":
    print(result)
    return
  windows = result.split("\n")
  for window in windows:
    a = window.split(" ")
    if len(a) < 3:
      continue
    win_id = a[0]
    i = 1
    while a[i].strip() == "":
      i += 1
    if desktop == a[i]:
      print(window)

def rename(desktop, new_name):
  # workspace-names are numbered from 1 but in wmctrl they are numbered from 0.
  desktop = int(desktop) + 1
  print(run_command(f"gsettings set org.mate.Marco.workspace-names name-{desktop} \"{new_name}\""))

def switch(desktop):
  run_command(f"wmctrl -s {desktop}")

def main():
  command = sys.argv[1]
  if command == "help":
    help()
  if command == "move":
    source_desktop = argv_or(2, "none")
    dest_desktop = argv_or(3, "none")
    move(source_desktop, dest_desktop)
  if command == "list":
    list_workspaces()
  if command == "listwin":
    desktop = argv_or(2, "none")
    list_windows(desktop)
  if command == "rename":
    desktop = argv_or(2, "none")
    new_name = argv_or(3, "none")
    rename(desktop, new_name)
  if command == "switch":
    desktop = argv_or(2, "none")
    switch(desktop)

if __name__ == "__main__":
  main()

