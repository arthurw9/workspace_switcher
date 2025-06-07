# Workspace Switcher for MATE desktop.

Update: I added a new workspace.py file that lets you:

List all workspaces:

`$ ./workspace.py list`

Move windows from one workspace to another (in this example 2 to 4):

`$ ./workspace.py move 2 4`

List all windows:

`$ ./workspace.py listwin`

List all windows in a workspace (in this example workspace 5):

`$ ./workspace.py listwin 5`

Rename a workspace:

`$ ./workspace.py rename 4 "misc"`

There is a shell script called switch_workspace.sh. For it to be useful, put it
somewhere and add a keyboard shortcut to run it. On my system keyboard shortcuts
can be found in the menu under
`System > Preferences > Hardware > Keyboard Shortcuts`.
I recommend binding the script to the key combination `<Mod4>-d` or `<Mod4>-<Alt>-d`.
Then when you press the key it will bring up a menu with all the desktop 
workspace names. You can jump directly to any one of them.

There is another shell script rename_workspace.sh. I recommend binding this to
the key `<Mod4>-r`. Then when you look at the list of desktop workspaces, you'll
see the new name you added.

The scripts have a dependency on wmctrl. This can be added via:
`sudo apt install wmctrl`

This was all tested on my local laptop with debian 12 running MATE.
