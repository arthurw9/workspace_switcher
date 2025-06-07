#!/usr/bin/python3

import sys
import subprocess

def run_command(command):
  result = subprocess.run(command, capture_output=True, shell=True, text=True)
  if result.returncode == 0:
    return result.stdout
  else:
    return f"Error: code {result.returncode}\n{result.stderr}"

def list_windows(desktop):
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

def help():
  print("""
examples:
  workspace move 7 8
    moves all windows from desktop 7 to desktop 8.
""")

def move(source_desktop, dest_desktop):
  for win_id in list_windows(source_desktop):
    move_window_to_desktop(win_id, dest_desktop)

def main():
  command = sys.argv[1]
  if command == "help":
    help()
  if command == "move":
    source_desktop = sys.argv[2]
    dest_desktop = sys.argv[3]
    move(source_desktop, dest_desktop)

if __name__ == "__main__":
  main()

