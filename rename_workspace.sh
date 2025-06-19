#!/bin/sh
available() { command -v $1 > /dev/null; }
if ! available wmctrl; then
  echo
  echo "Missing dependency needs to be installed:"
  echo "  sudo apt install wmctrl"
else
  desktop_number=$(wmctrl -d | grep '*' | awk '{ print $1 }')
  desktop_number=$(expr $desktop_number + 1)
  name=$(gsettings get org.mate.Marco.workspace-names name-$desktop_number)
  new_name=$(zenity --text="Rename Current Workspace" --entry --entry-text="$name")
  if ! [ -z "$new_name" ]; then
    gsettings set org.mate.Marco.workspace-names name-$desktop_number "$new_name"
  fi
fi
