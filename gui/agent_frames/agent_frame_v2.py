import tkinter as tk
from tkinter import ttk

from gui.agent_frames.base_agent_frame import BaseAgentFrame
from gui.utils import get_file
from agents.base_agent import BaseAgent


class AgentFrameV2(BaseAgentFrame):
    name_widgets = None
    player_type_widgets = None
    bot_level_widgets = None
    rlbot_config_button = None
    agent_path_widgets = []

    def __init__(self, parent, team_index, *args, **kwargs):
        super().__init__(parent, team_index, *args, **kwargs)
        self.config(borderwidth=5)
        self.in_game_name = tk.StringVar()
        self.is_bot = tk.BooleanVar()
        self.rlbot_controlled = tk.BooleanVar()
        self.bot_level = tk.DoubleVar(value=1)
        self.player_type = tk.StringVar(value="Human")
        self.agent_path = tk.StringVar()
        self.looks_config = BaseAgent.create_agent_configurations()

    def initialize_widgets(self):
        # In-game name editable
        self.name_widgets = list()
        self.name_widgets.append(ttk.Label(self, text="In-game name:", anchor="e"))
        self.name_widgets.append(ttk.Entry(self, textvariable=self.in_game_name))

        # Combobox for changing type
        self.player_type_widgets = list()
        self.player_type_widgets.append(ttk.Label(self, text="Player type: ", anchor="e"))
        self.player_type_widgets.append(ttk.Combobox(
            self, textvariable=self.player_type, values=("Human", "Psyonix Bot", "RLBot"), state="readonly"))
        self.player_type_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.refresh_widgets())

        ttk.Button(self, text="Edit looks", command=self.edit_looks).grid(row=3, column=0, sticky="e")

        # Remove the agent
        ttk.Button(self, text="Remove", command=lambda: self.parent.master.remove_agent(self)).grid(row=3, column=2,
                                                                                                    sticky="e")

        # Psyonix bot level skill scale
        self.bot_level_widgets = list()
        self.bot_level_widgets.append(ttk.Label(self, text="Bot level: ", anchor="e"))
        self.bot_level_widgets.append(ttk.Scale(self, from_=0.0, to=1.0, variable=self.bot_level))

        # Configure bot popup
        self.rlbot_config_button = ttk.Button(self, text="Configure Bot", command=self.configure_rlbot)

        self.name_widgets[0].grid(row=0, column=0, sticky="nsew")
        self.name_widgets[1].grid(row=0, column=1, columnspan=2, sticky="nsew")

        self.player_type_widgets[0].grid(row=1, column=0, sticky="nsew")
        self.player_type_widgets[1].grid(row=1, column=1, columnspan=2, sticky="nsew")

        self.grid_columnconfigure(1, minsize=84)

    def refresh_widgets(self):
        for widget in self.grid_slaves(row=2):
            widget.grid_forget()
        for widget in self.grid_slaves(row=3, column=1):
            widget.grid_forget()
        if self.player_type.get() == "Human":
            self.is_bot = False
            self.rlbot_controlled = False
        elif self.player_type.get() == "Psyonix Bot":
            self.bot_level_widgets[0].grid(row=2, column=0, sticky="nsew")
            self.bot_level_widgets[1].grid(row=2, column=1, columnspan=2, sticky="nsew")
            self.is_bot = True
            self.rlbot_controlled = False
        else:
            self.rlbot_config_button.grid(row=3, column=1, sticky="e")
            self.is_bot = True
            self.rlbot_controlled = True

    def edit_looks(self):
        window = tk.Toplevel()
        window.grab_set()

        for header_index, (header_name, header) in enumerate(self.looks_config.headers.items()):
            if header_name == 'Bot Location':
                continue
            total_count = 0
            header_frame = tk.Frame(window, borderwidth=8)
            header_frame.rowconfigure(0, minsize=25)
            ttk.Label(header_frame, text=header_name, anchor="center").grid(row=total_count, column=0,
                                                                            columnspan=2, sticky="new")
            total_count += 1

            for parameter_index, (parameter_name, parameter) in enumerate(header.values.items()):
                if parameter_name == "name":
                    continue

                ttk.Label(header_frame, text=parameter_name + ":", anchor='e').grid(
                    row=total_count, column=0, sticky="ew")
                big = 20000000
                if parameter.type == int:
                    if parameter.value is None:
                        parameter.value = tk.IntVar(value=parameter.default)
                    widget = tk.Spinbox(header_frame, textvariable=parameter.value, from_=0, to=big)
                elif parameter.type == float:
                    if parameter.value is None:
                        parameter.value = tk.DoubleVar(value=parameter.default)
                    widget = tk.Spinbox(header_frame, textvariable=parameter.value, from_=0, to=big,
                                        increment=.0001)
                elif parameter.type == bool:
                    if parameter.value is None:
                        parameter.value = tk.BooleanVar()
                    widget = ttk.Combobox(header_frame, textvariable=parameter.value, values=(False, True),
                                          state="readonly")
                    widget.current(parameter.default)
                elif parameter.type == str:
                    if parameter.value is None:
                        parameter.value = tk.StringVar(value=parameter.default)
                    widget = ttk.Entry(header_frame, textvariable=parameter.value)
                else:
                    widget = ttk.Label("Unknown type")

                widget.grid(row=total_count, column=1, sticky="ew")
                total_count += 1
            header_frame.grid(row=0, column=header_index)

        self.wait_window(window)

    def configure_rlbot(self):
        window = tk.Toplevel()
        window.resizable(0, 0)
        window.minsize(300, 300)
        window.update()

        def load_agent_class():
            agent_file_path = get_file(
                filetypes=[("Python File", "*.py")],
                title="Choose a file")
            if agent_file_path:
                self.agent_path.set(agent_file_path)
                self.load_agent_from_path(agent_file_path)
                custom_header = self.agent_class.create_agent_configurations()

        def load_custom_config():
            print("Test")


        ttk.Label(window, text="Agent location: ", anchor="e").grid(row=0, column=0)
        ttk.Entry(window, textvariable=self.agent_path, state="readonly").grid(row=0, column=1)
        ttk.Button(window, text="Select file", command=load_agent_class).grid(row=0, column=2)


        window.wm_attributes("-topmost", 1)
        window.focus_force()
        self.wait_window(window)

    def link_variables(self):
        header = self.overall_config["Participant Configuration"]
        header["participant_team"].set_value(self.team_index, self.overall_index)
        header["participant_is_bot"].set_value(self.is_bot, self.overall_index)
        header["participant_is_rlbot_controlled"].set_value(self.rlbot_controlled, self.overall_index)
        header["participant_bot_skill"].set_value(self.bot_level, self.overall_index)

        self.looks_config.set_value("Bot Loadout", "name", self.in_game_name, self.overall_index)
        self.looks_config.set_value("Bot Loadout Orange", "name", self.in_game_name, self.overall_index)
        self.looks_config.set_value("Bot Location", "agent_module", self.agent_path)

    def load_config(self, overall_config_file, overall_index):
        super().load_config(overall_config_file, overall_index)
        if self.is_participant_bot() and not self.is_participant_custom_bot():
            self.player_type.set('Psyonix Bot')
        elif not self.is_participant_bot() and not self.is_participant_custom_bot():
            self.player_type.set('Human')
        else self.is_participant_bot() and self.is_participant_custom_bot():
            self.player_type.set('RLBot')
