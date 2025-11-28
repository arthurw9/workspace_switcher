#!/usr/bin/python3

import unittest
import workspace
import time
import fake_desktop
import io
from unittest.mock import patch


def ShortSleep():
    # It seems some time required before renames are visible to wmctrl.
    # TODO: Figure out a way around this.
    time.sleep(0.1)  # sleep in seconds.


# Real tests use the real desktop not the fake one. These tests attempt to
# leave the final state of the desktop the same as before the test.
run_real_tests = True


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

    def test_real_insert_and_delete_should_move_current_workspace(self):
        if not run_real_tests:
            return
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

    def test_real_swap(self):
        if not run_real_tests:
            return
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

    def test_real_swapleft(self):
        if not run_real_tests:
            return
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
        workspace.switch(curr)

    def test_real_swapright(self):
        if not run_real_tests:
            return
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
        workspace.switch(curr)

    @patch("workspace.run_command")
    def test_switch(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "extra", "cool"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "extra")
        workspace.switch(2)
        self.assertEqual(f.GetCurrWorkspace(), "cool")

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("workspace.run_command")
    def test_list(self, fake_run_command, mock_stdout):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "extra", "cool"])

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.list_workspaces()

        # columns are: workspace idx, curr, num-windows, and workspace name
        self.assertIn(" 0  *  0  main\n", mock_stdout.getvalue())
        self.assertIn(" 1  -  0  extra\n", mock_stdout.getvalue())
        self.assertIn(" 2  -  0  cool\n", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("workspace.run_command")
    def test_list_with_some_windows(self, fake_run_command, mock_stdout):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "extra", "cool"])
        f.OpenWindow(0, "gmail - chromium")
        f.OpenWindow(1, "TuxRacer")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(2, "Terminal")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.list_workspaces()

        # columns are: workspace idx, curr, num-windows, and workspace name
        self.assertIn(" 0  *  1  main\n", mock_stdout.getvalue())
        self.assertIn(" 1  -  1  extra\n", mock_stdout.getvalue())
        self.assertIn(" 2  -  3  cool\n", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("workspace.run_command")
    def test_listwin_on_a_workspace(self, fake_run_command, mock_stdout):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "extra", "cool"])
        f.OpenWindow(0, "gmail - chromium")
        f.OpenWindow(1, "TuxRacer")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(2, "Terminal")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.list_windows("2")

        # columns are: window id, desktop idx, window name
        self.assertNotIn("0x00000001  -1  Bottom Panel", mock_stdout.getvalue())
        self.assertNotIn("0x00000002   0  gmail - chromium", mock_stdout.getvalue())
        self.assertNotIn("0x00000003   1  TuxRacer", mock_stdout.getvalue())
        self.assertIn("0x00000004   2  Terminal", mock_stdout.getvalue())
        self.assertIn("0x00000005   2  Terminal", mock_stdout.getvalue())
        self.assertIn("0x00000006   2  Terminal", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("workspace.run_command")
    def test_listwin(self, fake_run_command, mock_stdout):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "extra", "cool"])
        f.OpenWindow(0, "gmail - chromium")
        f.OpenWindow(1, "TuxRacer")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(2, "Terminal")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.list_windows("none")

        # columns are: window id, desktop idx, window name
        self.assertIn("0x00000001  -1  Bottom Panel", mock_stdout.getvalue())
        self.assertIn("0x00000002   0  gmail - chromium", mock_stdout.getvalue())
        self.assertIn("0x00000003   1  TuxRacer", mock_stdout.getvalue())
        self.assertIn("0x00000004   2  Terminal", mock_stdout.getvalue())
        self.assertIn("0x00000005   2  Terminal", mock_stdout.getvalue())
        self.assertIn("0x00000006   2  Terminal", mock_stdout.getvalue())

    @patch("workspace.run_command")
    def test_rename(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "extra", "cool"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.rename(1, "middle")
        self.assertEqual(f.GetWorkspaces(), ["main", "middle", "cool"])

        workspace.rename(2, "last")
        self.assertEqual(f.GetWorkspaces(), ["main", "middle", "last"])

    @patch("workspace.run_command")
    def test_insert_new_at_end(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before(2)
        self.assertEqual(f.GetWorkspaces(), ["main", "last", "new-desktop"])

    @patch("workspace.run_command")
    def test_insert_new_at_start(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before(0)
        self.assertEqual(f.GetWorkspaces(), ["new-desktop", "main", "last"])

    @patch("workspace.run_command")
    def test_insert_new_in_middle(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "new-desktop", "last"])

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("workspace.run_command")
    def test_insert_moves_windows(self, fake_run_command, mock_stdout):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")
        f.OpenWindow(0, "gmail - chromium")
        f.OpenWindow(1, "TuxRacer")
        f.OpenWindow(1, "Terminal")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "new-desktop", "last"])

        workspace.list_windows("none")

        # columns are: window id, desktop idx, window name
        self.assertIn("0x00000001  -1  Bottom Panel", mock_stdout.getvalue())
        self.assertIn("0x00000002   0  gmail - chromium", mock_stdout.getvalue())
        self.assertIn("0x00000003   2  TuxRacer", mock_stdout.getvalue())
        self.assertIn("0x00000004   2  Terminal", mock_stdout.getvalue())

    @patch("workspace.run_command")
    def test_insert_moves_the_current_workspace_if_it_should(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "last")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "new-desktop", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "last")

    @patch("workspace.run_command")
    def test_insert_does_not_moves_the_current_workspace_if_it_should_not(
        self, fake_run_command
    ):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        f.Switch(0)
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "new-desktop", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

    @patch("workspace.run_command")
    def test_insert_before_current_workspace(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "a", "b", "last"])
        f.Switch(2)
        self.assertEqual(f.GetCurrWorkspace(), "b")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.insert_before("none")
        self.assertEqual(f.GetWorkspaces(), ["main", "a", "new-desktop", "b", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "b")

    @patch("workspace.run_command")
    def test_delete_at_end(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        f.Switch(0)
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete(1)
        self.assertEqual(f.GetWorkspaces(), ["main"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

    @patch("workspace.run_command")
    def test_delete_at_start(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "last"])
        f.Switch(0)
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete(0)
        self.assertEqual(f.GetWorkspaces(), ["last"])
        self.assertEqual(f.GetCurrWorkspace(), "last")

    @patch("workspace.run_command")
    def test_delete_in_middle(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "middle", "last"])
        f.Switch(0)
        self.assertEqual(f.GetCurrWorkspace(), "main")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

    @patch("workspace.run_command")
    def test_delete_moves_the_current_workspace_if_it_should(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "middle", "last"])
        f.Switch(2)
        self.assertEqual(f.GetCurrWorkspace(), "last")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "last")

    @patch("workspace.run_command")
    def test_delete_moves_windows_if_it_should(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "middle", "two", "last"])
        f.Switch(2)
        self.assertEqual(f.GetCurrWorkspace(), "two")
        f.OpenWindow(0, "gmail - chromium")
        f.OpenWindow(2, "TuxRacer")
        f.OpenWindow(2, "Terminal")
        f.OpenWindow(3, "Terminal")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete(1)
        self.assertEqual(f.GetWorkspaces(), ["main", "two", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "two")
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["gmail - chromium"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), ["TuxRacer", "Terminal"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(2), ["Terminal"])

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("workspace.run_command")
    def test_delete_fails_if_there_are_windows_on_the_workspace(
        self, fake_run_command, mock_stdout
    ):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "middle", "last"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "middle")
        f.OpenWindow(1, "Terminal")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete(1)
        self.assertIn("Error: Close or move the windows first", mock_stdout.getvalue())
        self.assertEqual(f.GetWorkspaces(), ["main", "middle", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "middle")

    @patch("workspace.run_command")
    def test_curr_workspace_is_deleted(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "middle", "last"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "middle")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.delete("none")
        self.assertEqual(f.GetWorkspaces(), ["main", "last"])
        self.assertEqual(f.GetCurrWorkspace(), "main")

    @patch("workspace.run_command")
    def test_movewins(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["main", "middle", "last"])
        f.OpenWindow(0, "Terminal")
        f.OpenWindow(1, "Life Expectancy - Chromium")
        f.OpenWindow(1, "Inbox - Chromium")
        f.OpenWindow(2, "TuxRacer")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.move_wins(1, 2)

        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["Terminal"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), [])
        self.assertCountEqual(
            f.GetWindowsOnWorkspace(2),
            ["Life Expectancy - Chromium", "Inbox - Chromium", "TuxRacer"],
        )

    @patch("workspace.run_command")
    def test_swap(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["first", "middle", "last"])
        f.OpenWindow(0, "Terminal")
        f.OpenWindow(0, "Select items")
        f.OpenWindow(1, "Life Expectancy - Chromium")
        f.OpenWindow(1, "Inbox - Chromium")
        f.OpenWindow(2, "TuxRacer")
        f.OpenWindow(2, "Sudoku")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.swap(0, 2)

        self.assertEqual(f.GetWorkspaces(), ["last", "middle", "first"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["TuxRacer", "Sudoku"])
        self.assertCountEqual(
            f.GetWindowsOnWorkspace(1),
            ["Life Expectancy - Chromium", "Inbox - Chromium"],
        )
        self.assertCountEqual(f.GetWindowsOnWorkspace(2), ["Terminal", "Select items"])

    @patch("workspace.run_command")
    def test_swapleft(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["a", "b", "c"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "b")

        f.OpenWindow(0, "a1")
        f.OpenWindow(0, "a2")
        f.OpenWindow(1, "b1")
        f.OpenWindow(1, "b2")
        f.OpenWindow(2, "c1")
        f.OpenWindow(2, "c2")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.swapleft()

        self.assertEqual(f.GetWorkspaces(), ["b", "a", "c"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["b1", "b2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), ["a1", "a2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(2), ["c1", "c2"])

    @patch("workspace.run_command")
    def test_swapright(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["a", "b", "c"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "b")

        f.OpenWindow(0, "a1")
        f.OpenWindow(0, "a2")
        f.OpenWindow(1, "b1")
        f.OpenWindow(1, "b2")
        f.OpenWindow(2, "c1")
        f.OpenWindow(2, "c2")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.swapright()

        self.assertEqual(f.GetWorkspaces(), ["a", "c", "b"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["a1", "a2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), ["c1", "c2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(2), ["b1", "b2"])

    @patch("workspace.run_command")
    def test_move(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["a", "b", "c", "d", "e"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "b")

        f.OpenWindow(0, "a1")
        f.OpenWindow(0, "a2")
        f.OpenWindow(1, "b1")
        f.OpenWindow(1, "b2")
        f.OpenWindow(2, "c1")
        f.OpenWindow(2, "c2")
        f.OpenWindow(3, "d1")
        f.OpenWindow(3, "d2")
        f.OpenWindow(4, "e1")
        f.OpenWindow(4, "e2")

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        self.assertEqual(f.GetWorkspaces(), ["a", "b", "c", "d", "e"])
        self.assertEqual(f.GetCurrWorkspace(), "b")

        workspace.move(3, 1)

        self.assertEqual(f.GetWorkspaces(), ["a", "d", "b", "c", "e"])
        self.assertEqual(f.GetCurrWorkspace(), "b")
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["a1", "a2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), ["d1", "d2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(2), ["b1", "b2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(3), ["c1", "c2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(4), ["e1", "e2"])

        workspace.move(4, 0)

        self.assertEqual(f.GetWorkspaces(), ["e", "a", "d", "b", "c"])
        self.assertEqual(f.GetCurrWorkspace(), "b")
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["e1", "e2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), ["a1", "a2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(4), ["c1", "c2"])

        workspace.move(0, 5)

        self.assertEqual(f.GetWorkspaces(), ["a", "d", "b", "c", "e"])
        self.assertEqual(f.GetCurrWorkspace(), "b")
        self.assertCountEqual(f.GetWindowsOnWorkspace(0), ["a1", "a2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(1), ["d1", "d2"])
        self.assertCountEqual(f.GetWindowsOnWorkspace(4), ["e1", "e2"])

        workspace.move(2, 0)

        self.assertEqual(f.GetWorkspaces(), ["b", "a", "d", "c", "e"])
        self.assertEqual(f.GetCurrWorkspace(), "b")

        workspace.move(0, 5)

        self.assertEqual(f.GetWorkspaces(), ["a", "d", "c", "e", "b"])
        self.assertEqual(f.GetCurrWorkspace(), "b")
        self.assertCountEqual(f.GetWindowsOnWorkspace(4), ["b1", "b2"])

        workspace.move(2, 0)

        self.assertEqual(f.GetWorkspaces(), ["c", "a", "d", "e", "b"])
        self.assertEqual(f.GetCurrWorkspace(), "b")
        self.assertCountEqual(f.GetWindowsOnWorkspace(4), ["b1", "b2"])

    @patch("workspace.run_command")
    def test_gui_rename(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["a", "b", "c"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "b")
        f.expect_command(
            "zenity --text='Rename Current Workspace' --entry --entry-text='b'",
            "",
            "new_name_123",
        )

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.gui_rename()

        self.assertEqual(f.GetWorkspaces(), ["a", "new_name_123", "c"])

    @patch("workspace.run_command")
    def test_gui_switch(self, fake_run_command):
        f = fake_desktop.FakeDesktop()
        f.SetWorkspaces(["a", "b", "c"])
        f.Switch(1)
        self.assertEqual(f.GetCurrWorkspace(), "b")
        f.expect_command(
            "zenity --list --column=num --column=Curr --column='Desktop Name' --hide-column=1 --height=540 --width=300",
            "0\n.\na\n1\n>>>>\nb\n2\n.\nc\n",
            "2",
        )

        def fake_run(command, stdin=""):
            return f.run_command(command, stdin)

        fake_run_command.side_effect = fake_run

        workspace.gui_switch()

        self.assertEqual(0, len(f.unexpected_commands), f.unexpected_commands)

        self.assertEqual(f.GetCurrWorkspace(), "c")


if __name__ == "__main__":
    unittest.main()
