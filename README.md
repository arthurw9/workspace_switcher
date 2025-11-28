# Workspace Switcher for MATE desktop.

## Overview
This script lets you easily create, delete, and move workspaces along with all
the windows in them.

## Requirements
This script requires `wmctrl`, `zenity`, and `python3`.

On a Debian system, these can be installed with:

`sudo apt install wmctrl`

`sudo apt install zenity`

`sudo apt install python3`
 
## Example Commands

Example Commands | Description
--- | ---
`workspace.py help` | Display this help.
`workspace.py list` | List all workspaces.
`workspace.py listwin` | List all windows.
`workspace.py listwin 8` | List all windows in workspace 8.
`workspace.py switch 4` | Switch to workspace 4.
`workspace.py rename 3 "foo bar"` | Rename workspace 3 to "foo bar".
`workspace.py insert` | Insert a workspace before the current.
`workspace.py insert 3` | Insert a workspace before workspace 3.
`workspace.py delete` | Delete the current workspace.
`workspace.py delete 3` | Delete workspace 3.
`workspace.py movewins 7 8` | Moves all windows from desktop 7 to 8.
`workspace.py debug insert` | Print debugging info while inserting a workspace. Any command can be run with debugging info like this.
`workspace.py swap 3 5` | Swap workspaces 3 and 5.
`workspace.py swapleft` | Swap the current workspace to the left.
`workspace.py swapright` | Swap the curr workspace to the right.
`workspace.py move 3 5` | Move workspace 3 to just before 5.
`workspace.py gui\_rename` | Open a dialog box to rename the current workspace.
`workspace.py gui\_switch` | Open a dialog box to list all the workspaces and allow the user to switch to another workspace.

## Installation

Copy the scripts to your favorite directory. Make sure its executable bit is on.

Now create keyboard shortcuts to your favorite commands. 

On my system running Debian MATE, the keyboard shortcuts can be found in the menu under
`System > Preferences > Hardware > Keyboard Shortcuts`, or it can be accessed directly by running: `mate-keybinding-properties`

I recommend the following key bindings

Key Combination | Command
 --- | ---
`<ctrl><alt>L` | `workspace.py gui_switch`
`<ctrl><alt>R` | `workspace.py gui_rename`

This works for me because it's similar to these pre-existing bindings:

Key Combination | Command
 --- | ---
`<ctrl><alt><left>` | switch one workspace to the left.
`<ctrl><alt><right>` | switch one workspace to the right.

If `<ctrl><alt>L` is bound to lock screen, then you could rebind
lock screen to `<mod4>L` instead.


