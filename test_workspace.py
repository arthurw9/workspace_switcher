import unittest
import workspace
import time

class TestWorkspace(unittest.TestCase):

  def test_insert_and_delete_should_move_current_workspace(self):
    desktop_info = workspace.get_desktop_info()
    curr = desktop_info["curr"]
    win_info = workspace.get_window_info("none")

    workspace.insert_before(curr)

    # It seems some time required before renames are visible to wmctrl.
    # TODO: Figure out a way around this.
    time.sleep(0.1)  # sleep in seconds.

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

if __name__ == '__main__':
  unittest.main()

