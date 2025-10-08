#!/usr/bin/python3

import unittest
import workspace
import time


def ShortSleep():
    # It seems some time required before renames are visible to wmctrl.
    # TODO: Figure out a way around this.
    time.sleep(0.1)  # sleep in seconds.


class TestWorkspace(unittest.TestCase):
    def test_argv_or(self):
        # create a shortcut to the function under test
        f = workspace.argv_or_impl
        # Get the first argument
        self.assertEqual("help", f(["workspace", "help"], 1, "default"))
        self.assertEqual("default", f(["workspace"], 1, "default"))
        # Get the first argument should omit the "debug" keyword
        # "debug" in position 1 is not considered an argument.
        self.assertEqual("help", f(["workspace", "debug", "help"], 1, "default"))
        self.assertEqual("default", f(["workspace", "debug"], 1, "default"))
        # second argument is "1"
        self.assertEqual("1", f(["ws", "mv", "1", "2"], 2, "default"))
        self.assertEqual("1", f(["ws", "debug", "mv", "1", "2"], 2, "default"))
        # missing argument returns default value
        self.assertEqual("default", f(["ws", "mv"], 2, "default"))
        self.assertEqual("default", f(["ws", "mv"], 3, "default"))
        self.assertEqual("default", f(["ws", "debug", "mv"], 2, "default"))
        self.assertEqual("none", f(["ws", "debug", "mv"], 2, "none"))
        workspace.debugging = False

    def test_insert_and_delete_should_move_current_workspace(self):
        desktop_info = workspace.get_desktop_info()
        curr = desktop_info["curr"]
        win_info = workspace.get_window_info("none")

        workspace.insert_before(curr)

        ShortSleep()

        desktop_info2 = workspace.get_desktop_info()
        win_info2 = workspace.get_window_info("none")

        workspace.delete(curr)

        desktop_info3 = workspace.get_desktop_info()
        win_info3 = workspace.get_window_info("none")

        self.assertEqual(curr + 1, desktop_info2["curr"])
        self.assertEqual(curr, desktop_info3["curr"])

        self.assertEqual(desktop_info["num"] + 1, desktop_info2["num"])
        self.assertEqual(desktop_info["num"], desktop_info3["num"])

        self.assertEqual(desktop_info, desktop_info3)
        self.assertEqual(win_info, win_info3)

        self.assertEqual(desktop_info2["list"][curr], (str(curr), "new-desktop"))

        self.assertNotEqual(desktop_info, desktop_info2)
        self.assertNotEqual(win_info, win_info2)

    def test_swap(self):
        desktop_info = workspace.get_desktop_info()
        curr = desktop_info["curr"]
        num = desktop_info["num"]
        workspace.insert_before(num)
        workspace.rename(num, "new-desktop-123")
        ShortSleep()
        workspace.swap(0, num)
        ShortSleep()
        desktop_info = workspace.get_desktop_info()
        self.assertEqual(desktop_info["list"][0][1], "new-desktop-123")
        workspace.swap(0, num)
        ShortSleep()
        desktop_info = workspace.get_desktop_info()
        self.assertEqual(desktop_info["list"][num][1], "new-desktop-123")
        workspace.delete(num)

    def test_swapleft(self):
        desktop_info = workspace.get_desktop_info()
        curr = desktop_info["curr"]
        num = desktop_info["num"]
        workspace.insert_before(num)
        workspace.rename(num, "new-desktop-B")
        ShortSleep()
        workspace.insert_before(num)
        workspace.rename(num, "new-desktop-A")
        ShortSleep()
        workspace.switch(num + 1)
        desktop_info = workspace.get_desktop_info()
        self.assertEqual(desktop_info["curr"], num + 1)
        self.assertEqual(desktop_info["list"][num][1], "new-desktop-A")
        self.assertEqual(desktop_info["list"][num + 1][1], "new-desktop-B")
        workspace.swapleft()
        desktop_info = workspace.get_desktop_info()
        self.assertEqual(desktop_info["curr"], num)
        self.assertEqual(desktop_info["list"][num][1], "new-desktop-B")
        self.assertEqual(desktop_info["list"][num + 1][1], "new-desktop-A")
        workspace.delete(num)
        workspace.delete(num)


    def test_swapright(self):
        desktop_info = workspace.get_desktop_info()
        curr = desktop_info["curr"]
        num = desktop_info["num"]
        workspace.insert_before(num)
        workspace.rename(num, "new-desktop-B")
        ShortSleep()
        workspace.insert_before(num)
        workspace.rename(num, "new-desktop-A")
        ShortSleep()
        workspace.switch(num)
        desktop_info = workspace.get_desktop_info()
        self.assertEqual(desktop_info["curr"], num)
        self.assertEqual(desktop_info["list"][num][1], "new-desktop-A")
        self.assertEqual(desktop_info["list"][num + 1][1], "new-desktop-B")
        workspace.swapright()
        desktop_info = workspace.get_desktop_info()
        self.assertEqual(desktop_info["curr"], num + 1)
        self.assertEqual(desktop_info["list"][num][1], "new-desktop-B")
        self.assertEqual(desktop_info["list"][num + 1][1], "new-desktop-A")
        workspace.delete(num)
        workspace.delete(num)


if __name__ == "__main__":
    unittest.main()
