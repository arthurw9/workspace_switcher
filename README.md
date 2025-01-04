# Workspace Switcher for MATE desktop.
This is a workspace switcher that displays a list of all desktop workspaces and
let's the user select one to switch to.

This is currently just a shell script. For it to be useful, put the
switch_workspace.sh shell script somewhere and add a keyboard shortcut to run
it. On my system keyboard shortcuts can be found in the menu under
System > Preferences > Hardware > Keyboard Shortcuts.
I recommend binding the script to the key combination <Mod4>-d or <Mod4>-<Alt>-d.
Then when you press the key it will bring up a menu with all the desktop 
workspace names. You can jump directly to any one of them.

There is another shell script rename_workspace.sh. I recommend binding this to
the key <Mod4>-r. Then when you look at the list of desktop workspaces, you'll
see the new name you added.

The scripts have a dependency on wmctrl. This can be added via:
`sudo apt install wmctrl`

This was all tested on my local laptop with debian 12 running MATE.
