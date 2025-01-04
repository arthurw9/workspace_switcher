#!/bin/sh
available() { command -v $1 > /dev/null; }
if ! available wmctrl; then
  echo
  echo "Missing dependency needs to be installed:"
  echo "  sudo apt install wmctrl"
else
  list=$(wmctrl -d | awk '{ print $10 }' | nl -v 0)
  choice=$( zenity --list --column="num" --column="Desktop Name" --hide-column=1 --height=540 $list)
  if ! [ -z "$choice" ]; then
    wmctrl -s $choice
  fi
fi