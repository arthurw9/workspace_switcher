class FakeDesktop:
    def __init__(self):
        # List of names
        self._workspaces = []
        # map from id (like 0x03800def) to (workspace_idx, window_name)
        self._windows = {}
        self._curr_workspace_idx = 0
        self._next_window_id = 1
        self.OpenWindow(-1, "Bottom Panel")
        # Key = (command, stdin). Value = response
        self._expected_commands = {}
        self.unexpected_commands = []

    def _WorkspaceRow(self, idx, name):
        curr = "-"
        if idx == self._curr_workspace_idx:
            curr = "*"
        return f"{idx:<2} {curr} DG: 1920x1080  VP: N/A  WA: 0,0 1920x1052  {name}"

    def _WindowRow(self, win_id, workspace_idx, window_name):
        return f"0x{win_id:08X} {workspace_idx:>2} FooHost {window_name}"

    def _ListWins(self):
        result = []
        for win_id in self._windows:
            result.append(
                self._WindowRow(
                    win_id, self._windows[win_id][0], self._windows[win_id][1]
                )
            )
        return "\n".join(result)

    def _ListWorkspaces(self):
        return "\n".join(
            [self._WorkspaceRow(i, name) for (i, name) in enumerate(self._workspaces)]
        )

    def Switch(self, new_workspace_idx):
        self._curr_workspace_idx = new_workspace_idx

    def SetWorkspaces(self, names):
        self._workspaces = names

    def OpenWindow(self, workspace_idx, name):
        self._windows[self._next_window_id] = [workspace_idx, name]
        self._next_window_id += 1

    def GetCurrWorkspace(self):
        return self.GetWorkspace(self._curr_workspace_idx)

    def GetWorkspace(self, idx):
        return self._workspaces[idx]

    def GetWorkspaces(self):
        return list(self._workspaces)

    def GetWindowsOnWorkspace(self, workspace_idx):
        result = []
        for win_id in self._windows:
            if self._windows[win_id][0] == workspace_idx:
                win_name = self._windows[win_id][1]
                result.append(win_name)
        return result

    def expect_command(self, expected_command, expected_stdin, response):
        self._expected_commands[(expected_command, expected_stdin)] = response

    def run_command(self, command, stdin=""):
        if command == "wmctrl -l":
            return self._ListWins()
        if command == "wmctrl -d":
            return self._ListWorkspaces()
        if command.startswith("wmctrl -s "):
            self._curr_workspace_idx = int(command[len("wmctrl -s ") :])
            return ""
        if command.startswith("gsettings set org.mate.Marco.workspace-names name-"):
            workspace_idx = int(command.split(" ")[3][5:])
            # Mate Marco uses 1-based indexes. Need to convert to 0-based.
            workspace_idx -= 1
            new_name = command.split(" ")[4]
            # Need to strip the quotes off
            new_name = new_name[1:-1]
            if len(self._workspaces) >= workspace_idx + 1:
                self._workspaces[workspace_idx] = new_name
            return ""
        if command.startswith("wmctrl -n "):
            new_num_workspaces = int(command.split(" ")[2])
            num_workspaces = len(self._workspaces)
            if new_num_workspaces > num_workspaces:
                for i in range(num_workspaces, new_num_workspaces):
                    self._workspaces.append("")
            if new_num_workspaces < num_workspaces:
                self._workspaces = self._workspaces[0:new_num_workspaces]
            for win_id in self._windows:
                if self._windows[win_id][0] >= new_num_workspaces:
                    self._windows[win_id][0] = num_num_workspaces - 1
            if self._curr_workspace_idx >= new_num_workspaces:
                self._curr_workspace_idx = new_num_workspaces - 1
            return ""
        if command.startswith("wmctrl -i -r ") and " -t " in command:
            # TODO: We should handle more ways of naming windows.
            win_id = int(command.split()[3], 16)
            new_workspace_idx = int(command.split()[5])
            self._windows[win_id][0] = new_workspace_idx
            return ""
        if (command, stdin) in self._expected_commands:
            return self._expected_commands[(command, stdin)]
        result = f"Error: Unknown Command: {command}"
        self.unexpected_commands.append((command, stdin))
        print(result)
        return result


# f = FakeDesktop()
# f.SetWorkspaces(["main", "health"])
# f.Switch(1)
# f.OpenWindow(1, "Register | hoopla - Chromium")
# r = f.run_command("wmctrl -d")
# r = f.run_command("wmctrl -l")
# print(r)
