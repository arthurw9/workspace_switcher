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
  | workspace swap 3 5           | Swap workspaces 3 and 5.               |
  | workspace swapleft           | Swap the current workspace to the left.|
  | workspace swapright          | Swap the curr workspace to the right.  |
  | workspace move 3 5           | Move workspace 3 to just before 5.     |
  | workspace gui_rename         | Open a dialog box to rename the current|
  |                              | workspace.                             |
  | workspace gui_switch         | Open a dialog box to list all the      |
  |                              | workspaces and allow the user to switch|
  |                              | to another workspace.                  |
  -------------------------------------------------------------------------
"""
    )


debugging = False


def argv_or(n, default):
    return argv_or_impl(sys.argv, n, default)


def argv_or_impl(argv, n, default):
    global debugging
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


def run_command(command, stdin=""):
    result = subprocess.run(
        command, input=stdin, capture_output=True, shell=True, text=True
    )
    if result.returncode == 0:
        return result.stdout
    else:
        return f"Error: code {result.returncode}\n{result.stderr}"


def get_window_info(desktop):
    """Returns an array of tuples:
    (win_id, win_desktop, win_name)"""
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
    debug(f"rename: d {desktop} -> [{new_name}]")
    # TODO: Add support for other window managers besides Marco.
    rename_marco(desktop, new_name)


def rename_marco(desktop, new_name):
    # workspace-names are numbered from 1 but in wmctrl they are numbered from 0.
    desktop = int(desktop) + 1
    result = run_command(
        f'gsettings set org.mate.Marco.workspace-names name-{desktop} "{new_name}"'
    )
    if result.startswith("Error:"):
        print(result)


def switch(desktop):
    debug(f"switch: d {desktop}")
    run_command(f"wmctrl -s {desktop}")


def get_desktop_info():
    """returns a map with keys:

    curr: current desktop number
    num: number of desktops
    list: array of tuples(num, name)
    """
    desktop_info = {}
    desktop_info["list"] = []
    desktops = run_command("wmctrl -d")
    desktop_list = desktops.split("\n")
    for desktop in desktop_list:
        raw = desktop.split()
        if len(raw) < 10:
            continue
        if raw[1] == "*":
            desktop_info["curr"] = int(raw[0])
        desktop_info["list"].append((raw[0], " ".join(raw[9:])))
        debug(f"get_desktop_info: d {raw[0]} = [{' '.join(raw[9:])}]")
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


def swap(desktop1, desktop2):
    if desktop1 == "none" or desktop2 == "none":
        print("Error: Please specify 2 desktop numbers to swap")
        return
    desktop1 = int(desktop1)
    desktop2 = int(desktop2)
    desktop_info = get_desktop_info()
    num_desktops = desktop_info["num"]
    if (
        desktop1 < 0
        or desktop1 >= num_desktops
        or desktop2 < 0
        or desktop2 >= num_desktops
    ):
        print(f"Error: Desktop numbers must range from 0 to {num_desktops - 1}")
        return
    debug(f"swap {desktop1} {desktop2}")
    # temporarily add another desktop at the end
    run_command(f"wmctrl -n {num_desktops + 1}")
    move_wins(desktop1, num_desktops)
    move_wins(desktop2, desktop1)
    move_wins(num_desktops, desktop2)
    # remove the temporary desktop
    run_command(f"wmctrl -n {num_desktops}")
    rename(desktop1, desktop_info["list"][desktop2][1])
    rename(desktop2, desktop_info["list"][desktop1][1])


def swapleft():
    debug("swapleft")
    desktop_info = get_desktop_info()
    curr = desktop_info["curr"]
    if curr < 1:
        print(f"Error: Already at the far left")
        return
    swap(curr, curr - 1)
    switch(curr - 1)


def swapright():
    debug("swapright")
    desktop_info = get_desktop_info()
    curr = desktop_info["curr"]
    num = desktop_info["num"]
    if curr >= num - 1:
        print(f"Error: Already at the far right")
        return
    swap(curr, curr + 1)
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


def move(desktop, new_idx):
    if desktop == "none" or new_idx == "none":
        print("Error: Please specify the desktop to move and the new location")
        return
    desktop = int(desktop)
    new_idx = int(new_idx)
    desktop_info = get_desktop_info()
    num_desktops = desktop_info["num"]
    if desktop < 0 or desktop >= num_desktops:
        print(f"Error: Desktop number must range from 0 to {num_desktops - 1}")
        return
    if new_idx < 0 or new_idx > num_desktops:
        print(f"Error: The new location must range from 0 to {num_desktops}")
        return
    if new_idx == desktop:
        return
    debug(f"move {desktop} {new_idx}")
    insert_before(new_idx)
    if new_idx < desktop:
        desktop += 1
    swap(desktop, new_idx)
    delete(desktop)


def gui_rename():
    desktop_info = get_desktop_info()
    curr = desktop_info["curr"]
    name = desktop_info["list"][curr][1]
    name = run_command(
        f"zenity --text='Rename Current Workspace' --entry --entry-text='{name}'"
    )
    name = name.strip()
    # TODO: What if the actual name starts with Error. Need to fix run_command.
    if not name.startswith("Error"):
        rename(curr, name)


def gui_switch():
    desktop_info = get_desktop_info()
    num_desktops = desktop_info["num"]
    curr = desktop_info["curr"]
    cmd = "zenity --list --column=num --column=Curr --column='Desktop Name' --hide-column=1 --height=540 --width=300"
    stdin = ""
    for i in range(num_desktops):
        stdin += f"{i}\n"
        if curr == i:
            stdin += ">>>>\n"
        else:
            stdin += ".\n"
        stdin += desktop_info["list"][i][1] + "\n"
    result = run_command(cmd, stdin)
    result = result.strip()
    if not result.startswith("Error"):
        switch(result)


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
    if command == "swap":
        desktop1 = argv_or(2, "none")
        desktop2 = argv_or(3, "none")
        swap(desktop1, desktop2)
        return
    if command == "swapleft":
        swapleft()
        return
    if command == "swapright":
        swapright()
        return
    if command == "move":
        desktop = argv_or(2, "none")
        new_idx = argv_or(3, "none")
        move(desktop, new_idx)
        return
    if command == "gui_rename":
        gui_rename()
        return
    if command == "gui_switch":
        gui_switch()
        return
    print(f"Error: Unknown command: {command}")


if __name__ == "__main__":
    main()
