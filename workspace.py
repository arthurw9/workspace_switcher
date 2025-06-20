#!/usr/bin/python3

import sys
import subprocess


def help():
    print(
        """
Examples:
  -------------------------------------------------------------------------
  | workspace help               | Display this help.                     |
  | workspace list               | List all workspaces.                   |
  | workspace listwin            | List all windows.                      |
  | workspace listwin 8          | List all windows in workspace 8.       |
  | workspace switch 4           | Switch to workspace 4.                 |
  | workspace rename 3 "foo bar" | Rename workspace 3 to "foo bar".       |
  | workspace insert             | Insert a workspace before the current. |
  | workspace insert 3           | Insert a workspace before workspace 3. |
  | workspace delete             | Delete the current workspace.          |
  | workspace delete 3           | Delete workspace 3.                    |
  | workspace movewins 7 8       | Moves all windows from desktop 7 to 8. |
  | workspace debug command      | Print debugging while running command. |
  -------------------------------------------------------------------------

  TODO: 
  -------------------------------------------------------------------------
  | workspace swap 3 5           | Swap the order of workspace 3 and 5.   |
  | workspace swapleft           | Swap the current workspace to the left.|
  | workspace swapright          | Swap the curr workspace to the right.  |
  | workspace move 3 5           | Move workspace 3 to just before 5.     |
  -------------------------------------------------------------------------
"""
    )


debugging = False


def argv_or(n, default):
    return argv_or_impl(sys.argv, n, default)


def argv_or_impl(argv, n, default):
    if len(argv) < 2:
        return default
    if argv[1] == "debug":
        debugging = True
        n = n + 1
    if len(argv) > n:
        return argv[n]
    return default


def debug(msg):
    if debugging:
        print(f"debug: {msg}")


def run_command(command):
    result = subprocess.run(command, capture_output=True, shell=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        return f"Error: code {result.returncode}\n{result.stderr}"


def get_window_info(desktop):
    debug(f"get_window_info: d {desktop}")
    window_info = []
    result = run_command("wmctrl -l")
    windows = result.split("\n")
    for window in windows:
        a = window.split(" ")
        if len(a) < 3:
            continue
        win_id = a[0]
        i = 1
        if a[i] == "":
            i += 1
        win_desktop = a[i]
        if desktop != "none" and int(win_desktop) != int(desktop):
            continue
        i += 2
        win_name = " ".join(a[i:])
        debug(f"get_window_info: {win_id} {win_desktop} {win_name}")
        window_info.append((win_id, win_desktop, win_name))
    return window_info


def move_window_to_desktop(win_id, desktop):
    debug(f"move_window_to_desktop: w {win_id} -> d {desktop}")
    result = run_command(f"wmctrl -i -r {win_id} -t {desktop}")
    if result.startswith("Error:"):
        print(result)


def move_wins(source_desktop, dest_desktop):
    debug(f"move_wins: d {source_desktop} -> d {dest_desktop}")
    for win_info in get_window_info(source_desktop):
        move_window_to_desktop(win_info[0], dest_desktop)


def list_workspaces():
    desktop_info = get_desktop_info()
    desktop_to_num_windows = {}
    win_info = get_window_info("none")
    for w in win_info:
        if not w[1] in desktop_to_num_windows:
            desktop_to_num_windows[w[1]] = 0
        desktop_to_num_windows[w[1]] += 1
    debug(f"list_workspaces: d to #w: {desktop_to_num_windows}")
    for d in desktop_info["list"]:
        num_windows = 0
        if d[0] in desktop_to_num_windows:
            num_windows = desktop_to_num_windows[d[0]]
        curr = "-"
        if int(d[0]) == desktop_info["curr"]:
            curr = "*"
        print("%3s " % d[0], curr, "%2d " % num_windows, d[1])


def list_windows(desktop):
    for win_info in get_window_info(desktop):
        print(win_info[0], "%3s " % win_info[1], win_info[2])


def rename(desktop, new_name):
    # workspace-names are numbered from 1 but in wmctrl they are numbered from 0.
    desktop = int(desktop) + 1
    debug(f"rename: d {desktop - 1} -> [{new_name}]")
    result = run_command(
        f'gsettings set org.mate.Marco.workspace-names name-{desktop} "{new_name}"'
    )
    if result.startswith("Error:"):
        print(result)


def switch(desktop):
    debug(f"switch: d {desktop}")
    run_command(f"wmctrl -s {desktop}")


def get_desktop_info():
    desktop_info = {}
    desktop_info["list"] = []
    desktops = run_command("wmctrl -d")
    desktop_list = desktops.split("\n")
    for desktop in desktop_list:
        raw = desktop.split(" ")
        if len(raw) < 11:
            continue
        if raw[2] == "*":
            desktop_info["curr"] = int(raw[0])
        desktop_info["list"].append((raw[0], " ".join(raw[13:])))
        debug(f"get_desktop_info: d {raw[0]} = [{' '.join(raw[13:])}]")
    desktop_info["num"] = len(desktop_info["list"])
    return desktop_info


def insert_before(desktop):
    desktop_info = get_desktop_info()
    # add another desktop
    num_desktops = desktop_info["num"] + 1
    run_command(f"wmctrl -n {num_desktops}")
    if desktop == "none":
        desktop = desktop_info["curr"]
    desktop = int(desktop)
    # shift the other desktops down to make room
    for i in range(num_desktops - 2, int(desktop) - 1, -1):
        move_wins(i, i + 1)
        rename(i + 1, desktop_info["list"][i][1])
    rename(int(desktop), "new-desktop")
    curr = desktop_info["curr"]
    if desktop <= curr:
        switch(curr + 1)


def delete(desktop):
    desktop_info = get_desktop_info()
    if desktop == "none":
        desktop = desktop_info["curr"]
    desktop = int(desktop)
    # TODO: are there any other windows there?
    window_info = get_window_info(desktop)
    if len(window_info) > 0:
        print("Error: Close or move the windows first")
        return
    debug(f"delete: d {desktop} of {desktop_info['num']}")
    for i in range(desktop, desktop_info["num"] - 1):
        move_wins(i + 1, i)
        rename(i, desktop_info["list"][i + 1][1])
    num_desktops = desktop_info["num"] - 1
    run_command(f"wmctrl -n {num_desktops}")
    curr = desktop_info["curr"]
    if desktop <= curr:
        switch(curr - 1)


def main():
    command = argv_or(1, "help")
    if command == "help":
        help()
        return
    if command == "movewins":
        source_desktop = argv_or(2, "none")
        dest_desktop = argv_or(3, "none")
        move_wins(source_desktop, dest_desktop)
        return
    if command == "list":
        list_workspaces()
        return
    if command == "listwin":
        desktop = argv_or(2, "none")
        list_windows(desktop)
        return
    if command == "rename":
        desktop = argv_or(2, "none")
        new_name = argv_or(3, "none")
        rename(desktop, new_name)
        return
    if command == "switch":
        desktop = argv_or(2, "none")
        switch(desktop)
        return
    if command == "insert":
        desktop = argv_or(2, "none")
        insert_before(desktop)
        return
    if command == "delete":
        desktop = argv_or(2, "none")
        delete(desktop)
        return
    print(f"Error: Unknown command: {command}")


if __name__ == "__main__":
    main()
