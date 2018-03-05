import tkinter as tk
from tkinter import ttk

from gui.agent_frames.base_agent_frame import BaseAgentFrame
from gui.utils import get_file
from utils.agent_creator import get_base_import_package
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
        self.agent_config = BaseAgent.create_agent_configurations()

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

        for header_index, (header_name, header) in enumerate(self.agent_config.headers.items()):
            if header_name == 'Bot Location' or header_name == "Bot Parameters":
                continue
            total_count = 0
            header_frame = tk.Frame(window, borderwidth=8)
            header_frame.rowconfigure(0, minsize=25)
            ttk.Label(header_frame, text=header_name, anchor="center").grid(row=total_count, column=0,
                                                                            columnspan=2, sticky="new")
            total_count += 1

            self.grid_custom_options_header(header_frame, header, ["name"], 0, 0)
            header_frame.grid(row=0, column=header_index)

        self.wait_window(window)

    def configure_rlbot(self):
        window = tk.Toplevel()
        window.resizable(0, 0)
        window.minsize(300, 300)
        window.grab_set()
        window.update()

        def load_agent_class():
            agent_file_path = get_file(
                filetypes=[("Python File", "*.py")],
                title="Choose a file")
            if agent_file_path:
                self.agent_path.set(get_base_import_package(agent_file_path))
                self.load_agent_from_path(agent_file_path)
                self.agent_config = self.agent_class.create_agent_configurations().parse_file(self.agent_config)
                initialize_custom_config()

        def initialize_custom_config():
            options_window = tk.Frame()
            self.grid_custom_options_header(options_window, self.agent_config["Bot Parameters"], [], 1, 0)

        ttk.Label(window, text="Agent location: ", anchor="e").grid(row=0, column=0)
        ttk.Entry(window, textvariable=self.agent_path, state="readonly").grid(row=0, column=1)
        ttk.Button(window, text="Select file", command=load_agent_class).grid(row=0, column=2)

        button_frame = tk.Frame()
        # ttk.Button(button_frame, text="Load", command= )

        self.wait_window(window)

    def link_variables(self):
        self.overall_config["Participant Configuration"] \
            .set_value("participant_team", self.team_index, self.overall_index) \
            .set_value("participant_is_bot", self.is_bot, self.overall_index) \
            .set_value("participant_is_rlbot_controlled", self.rlbot_controlled, self.overall_index) \
            .set_value("participant_bot_skill", self.bot_level, self.overall_index)

        self.agent_config.set_value("Bot Loadout", "name", self.in_game_name)
        self.agent_config.set_value("Bot Loadout Orange", "name", self.in_game_name)
        self.agent_config.set_value("Bot Location", "agent_module", self.agent_path)

    def load_config(self, overall_config_file, overall_index):
        super().load_config(overall_config_file, overall_index)

    @staticmethod
    def grid_custom_options_header(header_frame, header, exceptions=None, row_offset=0, column_offset=0):
        for parameter_index, (parameter_name, parameter) in enumerate(header.values.items()):
            if exceptions is not None:
                if parameter_name in exceptions:
                    continue

            ttk.Label(header_frame, text=parameter_name + ":", anchor='e').grid(
                row=parameter_index + row_offset, column=0 + column_offset, sticky="ew")
            big = 20000000
            if parameter.type == int:
                if parameter.value is None:
                    parameter.value = tk.IntVar(value=parameter.default)
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.IntVar(value=parameter.value)
                widget = tk.Spinbox(header_frame, textvariable=parameter.value, from_=0, to=big)
            elif parameter.type == float:
                if parameter.value is None:
                    parameter.value = tk.DoubleVar(value=parameter.default)
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.DoubleVar(value=parameter.value)
                widget = tk.Spinbox(header_frame, textvariable=parameter.value, from_=0, to=big,
                                    increment=.0001)
            elif parameter.type == bool:
                if parameter.value is None:
                    parameter.value = tk.BooleanVar()
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.BooleanVar(value=parameter.value)
                widget = ttk.Combobox(header_frame, textvariable=parameter.value, values=(False, True),
                                      state="readonly")
                widget.current(parameter.default)
            elif parameter.type == str:
                if parameter.value is None:
                    parameter.value = tk.StringVar(value=parameter.default)
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.StringVar(value=parameter.value)
                widget = ttk.Entry(header_frame, textvariable=parameter.value)
            else:
                widget = ttk.Label("Unknown type")

            if parameter.default is not None and parameter.type is not bool:
                parameter.value.set(parameter.default)

            widget.grid(row=parameter_index + row_offset, column=1 + column_offset, sticky="ew")
