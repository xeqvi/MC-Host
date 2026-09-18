import sys
import os
import json
import shutil
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

import psutil

from PyQt6.QtCore import Qt, QTimer, QProcess
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDialog,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPlainTextEdit,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QMessageBox,
    QCheckBox,
    QProgressDialog,
    QGroupBox,
)


# ============================================================
# APP
# ============================================================

APP_NAME = "MC Host"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SERVERS_DIR = BASE_DIR / "servers"

DATA_DIR.mkdir(exist_ok=True)
SERVERS_DIR.mkdir(exist_ok=True)

SETTINGS_FILE = DATA_DIR / "settings.json"
SERVERS_FILE = DATA_DIR / "servers.json"


# ============================================================
# SETTINGS
# ============================================================

DEFAULT_SETTINGS = {
    "theme": "Dark",
    "accent": "#58A6FF",
    "font_family": "Inter",
    "font_size": 14,
    "corner_radius": 12,
}


THEMES = {
    "Dark": {
        "background": "#0B0F14",
        "surface": "#11161D",
        "surface2": "#171D26",
        "hover": "#1D2633",
        "border": "#293241",
        "text": "#F0F4F8",
        "secondary": "#8B98A8",
        "muted": "#647184",
        "input": "#080C11",
        "success": "#3FB950",
        "danger": "#F85149",
        "warning": "#D29922",
    },

    "Midnight": {
        "background": "#070A11",
        "surface": "#0E1420",
        "surface2": "#141D2D",
        "hover": "#1A2639",
        "border": "#273650",
        "text": "#F5F7FB",
        "secondary": "#94A3B8",
        "muted": "#64748B",
        "input": "#080C14",
        "success": "#34D399",
        "danger": "#FB7185",
        "warning": "#FBBF24",
    },

    "Light": {
        "background": "#F3F5F8",
        "surface": "#FFFFFF",
        "surface2": "#EEF1F4",
        "hover": "#E6EAF0",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "secondary": "#656D76",
        "muted": "#8C959F",
        "input": "#FFFFFF",
        "success": "#1A7F37",
        "danger": "#CF222E",
        "warning": "#9A6700",
    },
}


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


SETTINGS = DEFAULT_SETTINGS.copy()
SETTINGS.update(load_json(SETTINGS_FILE, {}))
save_json(SETTINGS_FILE, SETTINGS)


def load_servers():
    data = load_json(SERVERS_FILE, [])
    return data if isinstance(data, list) else []


def save_servers(servers):
    save_json(SERVERS_FILE, servers)


def theme():
    return THEMES.get(
        SETTINGS.get("theme", "Dark"),
        THEMES["Dark"]
    )


def server_path(server):
    return SERVERS_DIR / server["name"]


def sanitize_name(name):
    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "-_ "
    )

    return "".join(
        c for c in name
        if c in allowed
    ).strip()


def format_bytes(value):
    value = float(value)

    if value >= 1024 ** 3:
        return f"{value / 1024 ** 3:.2f} GB"

    if value >= 1024 ** 2:
        return f"{value / 1024 ** 2:.1f} MB"

    if value >= 1024:
        return f"{value / 1024:.1f} KB"

    return f"{int(value)} B"


def open_folder(path):
    try:
        if sys.platform == "win32":
            os.startfile(str(path))

        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])

        else:
            subprocess.Popen(["xdg-open", str(path)])

    except Exception as e:
        QMessageBox.warning(
            None,
            "Folder Error",
            str(e)
        )


# ============================================================
# STYLES
# ============================================================

def stylesheet():

    t = theme()

    return f"""
    * {{
        font-family: "{SETTINGS["font_family"]}";
        font-size: {SETTINGS["font_size"]}px;
    }}

    QMainWindow,
    QDialog {{
        background: {t["background"]};
        color: {t["text"]};
    }}

    QWidget {{
        color: {t["text"]};
    }}

    QLabel#logo {{
        color: {SETTINGS["accent"]};
        font-size: 28px;
        font-weight: 800;
    }}

    QLabel#subtitle {{
        color: {t["secondary"]};
    }}

    QLabel#sectionTitle {{
        color: {t["text"]};
        font-size: 21px;
        font-weight: 800;
    }}

    QLabel#dialogTitle {{
        color: {SETTINGS["accent"]};
        font-size: 24px;
        font-weight: 800;
    }}

    QLabel#serverName {{
        color: {t["text"]};
        font-size: 19px;
        font-weight: 800;
    }}

    QLabel#statTitle {{
        color: {t["secondary"]};
        font-size: 11px;
        font-weight: 700;
    }}

    QLabel#statValue {{
        color: {t["text"]};
        font-size: 25px;
        font-weight: 800;
    }}

    QLabel#running {{
        color: {t["success"]};
        font-weight: 800;
    }}

    QLabel#stopped {{
        color: {t["danger"]};
        font-weight: 800;
    }}

    QFrame#statCard,
    QFrame#serverCard {{
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: {SETTINGS["corner_radius"]}px;
    }}

    QFrame#serverCard:hover {{
        border-color: {SETTINGS["accent"]};
        background: {t["hover"]};
    }}

    QPushButton {{
        background: {t["surface2"]};
        color: {t["text"]};
        border: 1px solid {t["border"]};
        border-radius: {max(6, SETTINGS["corner_radius"] - 3)}px;
        padding: 9px 14px;
        font-weight: 700;
    }}

    QPushButton:hover {{
        background: {t["hover"]};
        border-color: {SETTINGS["accent"]};
    }}

    QPushButton#primary {{
        background: {SETTINGS["accent"]};
        color: white;
        border: none;
    }}

    QPushButton#danger {{
        color: {t["danger"]};
    }}

    QLineEdit,
    QSpinBox,
    QComboBox {{
        background: {t["input"]};
        color: {t["text"]};
        border: 1px solid {t["border"]};
        border-radius: {max(6, SETTINGS["corner_radius"] - 3)}px;
        padding: 9px;
    }}

    QLineEdit:focus,
    QSpinBox:focus,
    QComboBox:focus {{
        border-color: {SETTINGS["accent"]};
    }}

    QPlainTextEdit {{
        background: #050709;
        color: #59FF91;
        border: 1px solid {t["border"]};
        border-radius: {SETTINGS["corner_radius"]}px;
        font-family: Consolas, monospace;
    }}

    QGroupBox {{
        border: 1px solid {t["border"]};
        border-radius: {SETTINGS["corner_radius"]}px;
        margin-top: 12px;
        padding: 12px;
        font-weight: 700;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {SETTINGS["accent"]};
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 9px;
    }}

    QScrollBar::handle:vertical {{
        background: {t["border"]};
        border-radius: 4px;
        min-height: 35px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {SETTINGS["accent"]};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """


# ============================================================
# SIMPLE BUTTON
# NO ANIMATION
# ============================================================

class AppButton(QPushButton):

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setMinimumHeight(38)


# ============================================================
# PAPER DOWNLOAD
# ============================================================

PAPER_API = "https://fill.papermc.io/v3"

USER_AGENT = (
    "MC-Host/1.0.0 "
    "(https://example.com/mc-host)"
)


def download_paper(version, destination):

    api_url = (
        f"{PAPER_API}/projects/paper/"
        f"versions/{version}/builds"
    )

    request = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=20
    ) as response:

        raw = response.read()

    builds = json.loads(
        raw.decode("utf-8")
    )

    if not isinstance(builds, list):
        raise RuntimeError(
            "PaperMC returned an unexpected response."
        )

    stable = [
        build
        for build in builds
        if build.get("channel") == "STABLE"
    ]

    if not stable:
        raise RuntimeError(
            f"No stable Paper build found for Minecraft {version}."
        )

    build = stable[0]

    downloads = build.get(
        "downloads",
        {}
    )

    server_download = downloads.get(
        "server:default"
    )

    if not server_download:
        raise RuntimeError(
            "Paper server download was not found."
        )

    url = server_download.get("url")

    if not url:
        raise RuntimeError(
            "Paper download URL is missing."
        )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=60
    ) as response:

        total = response.headers.get(
            "Content-Length"
        )

        total = (
            int(total)
            if total
            else 0
        )

        downloaded = 0

        with open(
            destination,
            "wb"
        ) as file:

            while True:

                chunk = response.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file.write(chunk)

                downloaded += len(chunk)

    if not destination.exists():
        raise RuntimeError(
            "server.jar was not created."
        )

    if destination.stat().st_size < 1024 * 1024:
        raise RuntimeError(
            "Downloaded server.jar appears invalid."
        )

    return build.get(
        "id",
        "unknown"
    )


# ============================================================
# SERVER PROCESS
# ============================================================

class MinecraftProcess:

    def __init__(
        self,
        server,
        output_callback,
        finished_callback
    ):

        self.server = server

        self.output_callback = (
            output_callback
        )

        self.finished_callback = (
            finished_callback
        )

        self.process = QProcess()

        self.process.setWorkingDirectory(
            str(server_path(server))
        )

        self.process.readyReadStandardOutput.connect(
            self.read_stdout
        )

        self.process.readyReadStandardError.connect(
            self.read_stderr
        )

        self.process.finished.connect(
            self.finished
        )

    def start(self):

        folder = server_path(
            self.server
        )

        jar = folder / "server.jar"

        if not jar.exists():

            raise FileNotFoundError(
                "server.jar is missing.\n"
                "Use the Download Server button."
            )

        java = self.server.get(
            "java_path",
            "java"
        )

        ram = int(
            self.server.get(
                "ram",
                4096
            )
        )

        jvm_args = self.server.get(
            "jvm_args",
            "-XX:+UseG1GC"
        )

        extra_args = self.server.get(
            "extra_args",
            ""
        )

        arguments = [
            f"-Xms{ram}M",
            f"-Xmx{ram}M",
        ]

        if jvm_args.strip():
            arguments.extend(
                jvm_args.split()
            )

        arguments.extend([
            "-jar",
            "server.jar",
            "--nogui",
        ])

        if extra_args.strip():
            arguments.extend(
                extra_args.split()
            )

        self.process.start(
            java,
            arguments
        )

        if not self.process.waitForStarted(
            5000
        ):

            raise RuntimeError(
                "Could not start Java/Minecraft."
            )

    def read_stdout(self):

        data = (
            self.process
            .readAllStandardOutput()
            .data()
            .decode(
                "utf-8",
                errors="replace"
            )
        )

        if data:
            self.output_callback(data)

    def read_stderr(self):

        data = (
            self.process
            .readAllStandardError()
            .data()
            .decode(
                "utf-8",
                errors="replace"
            )
        )

        if data:
            self.output_callback(data)

    def send(self, command):

        if self.is_running():

            self.process.write(
                (
                    command + "\n"
                ).encode("utf-8")
            )

    def stop(self):

        self.send("stop")

    def kill(self):

        if self.is_running():
            self.process.kill()

    def is_running(self):

        return (
            self.process.state()
            != QProcess.ProcessState.NotRunning
        )

    def finished(self):

        self.finished_callback()


# ============================================================
# SERVER MANAGER
# ============================================================

class ServerManager:

    def __init__(self):
        self.processes = {}

    def is_running(self, name):

        process = self.processes.get(name)

        return (
            process is not None
            and process.is_running()
        )

    def start(
        self,
        server,
        callback
    ):

        name = server["name"]

        if self.is_running(name):
            return

        def finished():

            self.processes.pop(
                name,
                None
            )

            callback(
                name,
                "\n[MC HOST] Server stopped.\n"
            )

        process = MinecraftProcess(
            server,
            lambda text:
            callback(
                name,
                text
            ),
            finished
        )

        process.start()

        self.processes[name] = process

    def stop(self, server):

        process = self.processes.get(
            server["name"]
        )

        if process:
            process.stop()

    def kill(self, server):

        process = self.processes.get(
            server["name"]
        )

        if process:
            process.kill()

    def send(
        self,
        server,
        command
    ):

        process = self.processes.get(
            server["name"]
        )

        if process:
            process.send(command)


# ============================================================
# CREATE SERVER
# ============================================================

class CreateServerDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Create Server"
        )

        self.resize(
            580,
            600
        )

        root = QVBoxLayout(self)

        title = QLabel(
            "Create Minecraft Server"
        )

        title.setObjectName(
            "dialogTitle"
        )

        root.addWidget(title)

        subtitle = QLabel(
            "The server folder and Paper server.jar "
            "will be created automatically."
        )

        subtitle.setObjectName(
            "subtitle"
        )

        subtitle.setWordWrap(True)

        root.addWidget(subtitle)

        form = QFormLayout()

        self.name = QLineEdit()

        self.name.setPlaceholderText(
            "My Survival Server"
        )

        self.version = QComboBox()

        self.version.addItems([
            "1.21.11",
            "1.21.10",
            "1.21.9",
            "1.21.8",
            "1.21.7",
            "1.21.6",
            "1.21.5",
            "1.21.4",
            "1.20.6",
            "1.20.4",
            "1.8.8",
        ])

        self.ram = QSpinBox()

        self.ram.setRange(
            512,
            65536
        )

        self.ram.setValue(
            4096
        )

        self.ram.setSuffix(
            " MB"
        )

        max_cpu = (
            os.cpu_count()
            or 1
        )

        self.cpu = QSpinBox()

        self.cpu.setRange(
            1,
            max_cpu
        )

        self.cpu.setValue(
            min(4, max_cpu)
        )

        self.cpu.setSuffix(
            " cores"
        )

        self.port = QSpinBox()

        self.port.setRange(
            1024,
            65535
        )

        self.port.setValue(
            25565
        )

        form.addRow(
            "Server name:",
            self.name
        )

        form.addRow(
            "Minecraft version:",
            self.version
        )

        form.addRow(
            "RAM:",
            self.ram
        )

        form.addRow(
            "CPU cores:",
            self.cpu
        )

        form.addRow(
            "Port:",
            self.port
        )

        root.addLayout(form)

        info = QLabel(
            "Currently the automatic server download uses PaperMC."
        )

        info.setStyleSheet(
            f"color:{theme()['secondary']};"
        )

        root.addWidget(info)

        root.addStretch()

        buttons = QHBoxLayout()

        cancel = AppButton("Cancel")
        create = AppButton("Create & Download")

        create.setObjectName("primary")

        cancel.clicked.connect(
            self.reject
        )

        create.clicked.connect(
            self.create_server
        )

        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(create)

        root.addLayout(buttons)

    def create_server(self):

        name = sanitize_name(
            self.name.text()
        )

        if not name:

            QMessageBox.warning(
                self,
                "Invalid Name",
                "Enter a valid server name."
            )

            return

        servers = load_servers()

        if any(
            s["name"].lower()
            == name.lower()
            for s in servers
        ):

            QMessageBox.warning(
                self,
                "Already Exists",
                "This server already exists."
            )

            return

        server = {
            "name": name,
            "version": self.version.currentText(),
            "type": "Paper",

            "ram": self.ram.value(),
            "cpu": self.cpu.value(),
            "port": self.port.value(),

            "motd": "A Minecraft Server",
            "gamemode": "survival",
            "difficulty": "normal",
            "max_players": 20,

            "view_distance": 10,
            "simulation_distance": 10,

            "online_mode": True,
            "whitelist": False,
            "pvp": True,

            "bind_ip": "0.0.0.0",

            "java_path": "java",
            "jvm_args": "-XX:+UseG1GC",
            "extra_args": "",

            "auto_restart": False,
            "restart_delay": 5,

            "discord_enabled": False,
            "discord_invite": "",
            "discord_webhook": "",

            "jar_build": None,
        }

        folder = server_path(server)

        try:

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            for directory in [
                "mods",
                "plugins",
                "logs",
                "backups",
            ]:

                (
                    folder / directory
                ).mkdir(
                    exist_ok=True
                )

            jar = folder / "server.jar"

            progress = QProgressDialog(
                "Downloading Paper server...",
                "Cancel",
                0,
                0,
                self
            )

            progress.setWindowTitle(
                "MC Host"
            )

            progress.setAutoClose(False)
            progress.setAutoReset(False)

            progress.show()

            QApplication.processEvents()

            try:

                build = download_paper(
                    server["version"],
                    jar
                )

                server["jar_build"] = build

            finally:

                progress.close()

            # eula
            with open(
                folder / "eula.txt",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "eula=true\n"
                )

            # Basic server.properties
            self.write_server_properties(
                server
            )

            servers.append(server)

            save_servers(servers)

            QMessageBox.information(
                self,
                "Server Created",
                "Server created successfully.\n\n"
                f"Location:\n{folder}\n\n"
                "server.jar downloaded automatically."
            )

            self.accept()

        except Exception as error:

            if folder.exists():
                try:
                    shutil.rmtree(folder)
                except Exception:
                    pass

            QMessageBox.critical(
                self,
                "Download Error",
                f"Could not create the server.\n\n{error}"
            )

    def write_server_properties(self, server):

        folder = server_path(server)

        properties = {
            "server-port":
                server["port"],

            "server-ip":
                server["bind_ip"],

            "motd":
                server["motd"],

            "gamemode":
                server["gamemode"],

            "difficulty":
                server["difficulty"],

            "max-players":
                server["max_players"],

            "view-distance":
                server["view_distance"],

            "simulation-distance":
                server["simulation_distance"],

            "online-mode":
                str(
                    server["online_mode"]
                ).lower(),

            "white-list":
                str(
                    server["whitelist"]
                ).lower(),

            "pvp":
                str(
                    server["pvp"]
                ).lower(),
        }

        with open(
            folder / "server.properties",
            "w",
            encoding="utf-8"
        ) as f:

            for key, value in properties.items():

                f.write(
                    f"{key}={value}\n"
                )


# ============================================================
# ADVANCED SETTINGS
# ============================================================

class AdvancedServerSettingsDialog(QDialog):

    def __init__(
        self,
        server,
        parent=None
    ):

        super().__init__(parent)

        self.server = server.copy()

        self.setWindowTitle(
            f"Advanced Settings - {server['name']}"
        )

        self.resize(
            760,
            760
        )

        root = QVBoxLayout(self)

        title = QLabel(
            "Advanced Server Settings"
        )

        title.setObjectName(
            "dialogTitle"
        )

        root.addWidget(title)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        content = QWidget()

        layout = QVBoxLayout(content)

        # ----------------------------------------------------
        # MINECRAFT
        # ----------------------------------------------------

        mc_box = QGroupBox(
            "Minecraft"
        )

        mc = QFormLayout(mc_box)

        self.motd = QLineEdit(
            self.server.get(
                "motd",
                "A Minecraft Server"
            )
        )

        self.gamemode = QComboBox()

        self.gamemode.addItems([
            "survival",
            "creative",
            "adventure",
            "spectator",
        ])

        self.gamemode.setCurrentText(
            self.server.get(
                "gamemode",
                "survival"
            )
        )

        self.difficulty = QComboBox()

        self.difficulty.addItems([
            "peaceful",
            "easy",
            "normal",
            "hard",
        ])

        self.difficulty.setCurrentText(
            self.server.get(
                "difficulty",
                "normal"
            )
        )

        self.max_players = QSpinBox()

        self.max_players.setRange(
            1,
            1000
        )

        self.max_players.setValue(
            self.server.get(
                "max_players",
                20
            )
        )

        self.view_distance = QSpinBox()

        self.view_distance.setRange(
            2,
            32
        )

        self.view_distance.setValue(
            self.server.get(
                "view_distance",
                10
            )
        )

        self.simulation_distance = QSpinBox()

        self.simulation_distance.setRange(
            2,
            32
        )

        self.simulation_distance.setValue(
            self.server.get(
                "simulation_distance",
                10
            )
        )

        self.online_mode = QCheckBox(
            "Online mode"
        )

        self.online_mode.setChecked(
            self.server.get(
                "online_mode",
                True
            )
        )

        self.whitelist = QCheckBox(
            "Whitelist"
        )

        self.whitelist.setChecked(
            self.server.get(
                "whitelist",
                False
            )
        )

        self.pvp = QCheckBox(
            "PvP"
        )

        self.pvp.setChecked(
            self.server.get(
                "pvp",
                True
            )
        )

        mc.addRow(
            "MOTD:",
            self.motd
        )

        mc.addRow(
            "Gamemode:",
            self.gamemode
        )

        mc.addRow(
            "Difficulty:",
            self.difficulty
        )

        mc.addRow(
            "Max players:",
            self.max_players
        )

        mc.addRow(
            "View distance:",
            self.view_distance
        )

        mc.addRow(
            "Simulation distance:",
            self.simulation_distance
        )

        mc.addRow(
            "",
            self.online_mode
        )

        mc.addRow(
            "",
            self.whitelist
        )

        mc.addRow(
            "",
            self.pvp
        )

        layout.addWidget(mc)

        # ----------------------------------------------------
        # NETWORK
        # ----------------------------------------------------

        network_box = QGroupBox(
            "Network"
        )

        network = QFormLayout(
            network_box
        )

        self.bind_ip = QLineEdit(
            self.server.get(
                "bind_ip",
                "0.0.0.0"
            )
        )

        self.port = QSpinBox()

        self.port.setRange(
            1024,
            65535
        )

        self.port.setValue(
            self.server.get(
                "port",
                25565
            )
        )

        network.addRow(
            "Bind IP:",
            self.bind_ip
        )

        network.addRow(
            "Port:",
            self.port
        )

        layout.addWidget(network_box)

        # ----------------------------------------------------
        # JAVA
        # ----------------------------------------------------

        java_box = QGroupBox(
            "Java / JVM"
        )

        java = QFormLayout(
            java_box
        )

        self.java_path = QLineEdit(
            self.server.get(
                "java_path",
                "java"
            )
        )

        self.jvm_args = QLineEdit(
            self.server.get(
                "jvm_args",
                "-XX:+UseG1GC"
            )
        )

        self.extra_args = QLineEdit(
            self.server.get(
                "extra_args",
                ""
            )
        )

        java.addRow(
            "Java executable:",
            self.java_path
        )

        java.addRow(
            "JVM arguments:",
            self.jvm_args
        )

        java.addRow(
            "Extra arguments:",
            self.extra_args
        )

        layout.addWidget(java_box)

        # ----------------------------------------------------
        # DISCORD
        # ----------------------------------------------------

        discord_box = QGroupBox(
            "Discord"
        )

        discord = QFormLayout(
            discord_box
        )

        self.discord_enabled = QCheckBox(
            "Enable Discord integration"
        )

        self.discord_enabled.setChecked(
            self.server.get(
                "discord_enabled",
                False
            )
        )

        self.discord_invite = QLineEdit(
            self.server.get(
                "discord_invite",
                ""
            )
        )

        self.discord_invite.setPlaceholderText(
            "https://discord.gg/..."
        )

        self.discord_webhook = QLineEdit(
            self.server.get(
                "discord_webhook",
                ""
            )
        )

        self.discord_webhook.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        discord.addRow(
            "",
            self.discord_enabled
        )

        discord.addRow(
            "Discord invite:",
            self.discord_invite
        )

        discord.addRow(
            "Webhook:",
            self.discord_webhook
        )

        layout.addWidget(discord_box)

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        files_box = QGroupBox(
            "Server Files"
        )

        files = QGridLayout(
            files_box
        )

        folders = [
            ("Open Server Folder", ""),
            ("Open Mods", "mods"),
            ("Open Plugins", "plugins"),
            ("Open Logs", "logs"),
            ("Open Backups", "backups"),
        ]

        for index, (
            text,
            folder
        ) in enumerate(folders):

            button = AppButton(text)

            button.clicked.connect(
                lambda checked=False,
                f=folder:
                self.open_folder(f)
            )

            files.addWidget(
                button,
                index // 2,
                index % 2
            )

        layout.addWidget(files_box)

        layout.addStretch()

        scroll.setWidget(content)

        root.addWidget(scroll)

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        buttons = QHBoxLayout()

        cancel = AppButton("Cancel")

        save = AppButton(
            "Save Advanced Settings"
        )

        save.setObjectName("primary")

        cancel.clicked.connect(
            self.reject
        )

        save.clicked.connect(
            self.save
        )

        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(save)

        root.addLayout(buttons)

    def open_folder(self, folder):

        target = server_path(
            self.server
        )

        if folder:
            target = target / folder

        target.mkdir(
            parents=True,
            exist_ok=True
        )

        open_folder(target)

    def save(self):

        self.server.update({
            "motd":
                self.motd.text().strip(),

            "gamemode":
                self.gamemode.currentText(),

            "difficulty":
                self.difficulty.currentText(),

            "max_players":
                self.max_players.value(),

            "view_distance":
                self.view_distance.value(),

            "simulation_distance":
                self.simulation_distance.value(),

            "online_mode":
                self.online_mode.isChecked(),

            "whitelist":
                self.whitelist.isChecked(),

            "pvp":
                self.pvp.isChecked(),

            "bind_ip":
                self.bind_ip.text().strip()
                or "0.0.0.0",

            "port":
                self.port.value(),

            "java_path":
                self.java_path.text().strip()
                or "java",

            "jvm_args":
                self.jvm_args.text().strip(),

            "extra_args":
                self.extra_args.text().strip(),

            "discord_enabled":
                self.discord_enabled.isChecked(),

            "discord_invite":
                self.discord_invite.text().strip(),

            "discord_webhook":
                self.discord_webhook.text().strip(),
        })

        # update properties file
        folder = server_path(
            self.server
        )

        properties = {
            "server-port":
                self.server["port"],

            "server-ip":
                self.server["bind_ip"],

            "motd":
                self.server["motd"],

            "gamemode":
                self.server["gamemode"],

            "difficulty":
                self.server["difficulty"],

            "max-players":
                self.server["max_players"],

            "view-distance":
                self.server["view_distance"],

            "simulation-distance":
                self.server["simulation_distance"],

            "online-mode":
                str(
                    self.server["online_mode"]
                ).lower(),

            "white-list":
                str(
                    self.server["whitelist"]
                ).lower(),

            "pvp":
                str(
                    self.server["pvp"]
                ).lower(),
        }

        with open(
            folder / "server.properties",
            "w",
            encoding="utf-8"
        ) as f:

            for key, value in properties.items():
                f.write(
                    f"{key}={value}\n"
                )

        servers = load_servers()

        for i, server in enumerate(servers):

            if server["name"] == self.server["name"]:
                servers[i] = self.server
                break

        save_servers(servers)

        self.accept()


# ============================================================
# SERVER SETTINGS
# ============================================================

class ServerSettingsDialog(QDialog):

    def __init__(
        self,
        server,
        parent=None
    ):

        super().__init__(parent)

        self.server = server.copy()

        self.setWindowTitle(
            f"Server Settings - {server['name']}"
        )

        self.setFixedSize(
            520,
            420
        )

        root = QVBoxLayout(self)

        title = QLabel(
            "Server Settings"
        )

        title.setObjectName(
            "dialogTitle"
        )

        root.addWidget(title)

        form = QFormLayout()

        self.ram = QSpinBox()

        self.ram.setRange(
            512,
            65536
        )

        self.ram.setValue(
            server.get(
                "ram",
                4096
            )
        )

        self.ram.setSuffix(
            " MB"
        )

        max_cpu = (
            os.cpu_count()
            or 1
        )

        self.cpu = QSpinBox()

        self.cpu.setRange(
            1,
            max_cpu
        )

        self.cpu.setValue(
            min(
                server.get(
                    "cpu",
                    4
                ),
                max_cpu
            )
        )

        self.cpu.setSuffix(
            " cores"
        )

        self.port = QSpinBox()

        self.port.setRange(
            1024,
            65535
        )

        self.port.setValue(
            server.get(
                "port",
                25565
            )
        )

        form.addRow(
            "RAM:",
            self.ram
        )

        form.addRow(
            "CPU cores:",
            self.cpu
        )

        form.addRow(
            "Port:",
            self.port
        )

        root.addLayout(form)

        info = QLabel(
            "RAM controls the Java -Xms/-Xmx values."
        )

        info.setStyleSheet(
            f"color:{theme()['secondary']};"
        )

        root.addWidget(info)

        root.addStretch()

        save = AppButton("Save")

        save.setObjectName(
            "primary"
        )

        save.clicked.connect(
            self.save
        )

        root.addWidget(save)

    def save(self):

        self.server["ram"] = (
            self.ram.value()
        )

        self.server["cpu"] = (
            self.cpu.value()
        )

        self.server["port"] = (
            self.port.value()
        )

        servers = load_servers()

        for i, server in enumerate(servers):

            if server["name"] == self.server["name"]:
                servers[i] = self.server
                break

        save_servers(servers)

        self.accept()


# ============================================================
# CONSOLE
# ============================================================

class ConsoleDialog(QDialog):

    def __init__(
        self,
        server,
        manager,
        parent=None
    ):

        super().__init__(parent)

        self.server = server
        self.manager = manager

        self.setWindowTitle(
            f"Console - {server['name']}"
        )

        self.resize(
            950,
            650
        )

        root = QVBoxLayout(self)

        title = QLabel(
            f"Console - {server['name']}"
        )

        title.setObjectName(
            "dialogTitle"
        )

        root.addWidget(title)

        self.console = QPlainTextEdit()

        self.console.setReadOnly(True)

        root.addWidget(
            self.console
        )

        row = QHBoxLayout()

        self.command = QLineEdit()

        self.command.setPlaceholderText(
            "Enter Minecraft command..."
        )

        send = AppButton("Send")

        send.clicked.connect(
            self.send_command
        )

        self.command.returnPressed.connect(
            self.send_command
        )

        row.addWidget(
            self.command
        )

        row.addWidget(send)

        root.addLayout(row)

    def append_text(self, text):

        self.console.moveCursor(
            self.console.textCursor()
            .MoveOperation.End
        )

        self.console.insertPlainText(
            text
        )

        self.console.moveCursor(
            self.console.textCursor()
            .MoveOperation.End
        )

    def send_command(self):

        command = (
            self.command
            .text()
            .strip()
        )

        if not command:
            return

        self.manager.send(
            self.server,
            command
        )

        self.command.clear()


# ============================================================
# SERVER CARD
# ============================================================

class ServerCard(QFrame):

    def __init__(
        self,
        server,
        manager,
        main_window
    ):

        super().__init__()

        self.server = server
        self.manager = manager
        self.main_window = main_window

        self.setObjectName(
            "serverCard"
        )

        self.setMinimumHeight(
            220
        )

        root = QVBoxLayout(self)

        # header

        header = QHBoxLayout()

        name = QLabel(
            server["name"]
        )

        name.setObjectName(
            "serverName"
        )

        self.status = QLabel()

        header.addWidget(name)
        header.addStretch()
        header.addWidget(self.status)

        root.addLayout(header)

        # info

        info = QLabel(
            f"Paper {server.get('version', '?')}  |  "
            f"{server.get('ram', 4096)} MB RAM  |  "
            f"{server.get('cpu', 1)} cores  |  "
            f"Port {server.get('port', 25565)}"
        )

        info.setStyleSheet(
            f"color:{theme()['secondary']};"
        )

        root.addWidget(info)

        # resources

        resources = QHBoxLayout()

        self.cpu_label = QLabel(
            "CPU: 0%"
        )

        self.ram_label = QLabel(
            "RAM: 0 MB"
        )

        resources.addWidget(
            self.cpu_label
        )

        resources.addWidget(
            self.ram_label
        )

        resources.addStretch()

        root.addLayout(resources)

        # buttons

        buttons = QGridLayout()

        buttons.setSpacing(7)

        start = AppButton("Start")
        stop = AppButton("Stop")
        restart = AppButton("Restart")
        console = AppButton("Console")
        settings = AppButton("Settings")

        # IMPORTANT:
        # Advanced text is explicit and visible.
        advanced = AppButton(
            "Advanced Settings"
        )

        delete = AppButton("Delete")

        delete.setObjectName(
            "danger"
        )

        start.clicked.connect(
            self.start_server
        )

        stop.clicked.connect(
            self.stop_server
        )

        restart.clicked.connect(
            self.restart_server
        )

        console.clicked.connect(
            self.open_console
        )

        settings.clicked.connect(
            self.open_settings
        )

        advanced.clicked.connect(
            self.open_advanced
        )

        delete.clicked.connect(
            self.delete_server
        )

        buttons.addWidget(start, 0, 0)
        buttons.addWidget(stop, 0, 1)
        buttons.addWidget(restart, 0, 2)
        buttons.addWidget(console, 0, 3)

        buttons.addWidget(settings, 1, 0)
        buttons.addWidget(advanced, 1, 1, 1, 2)
        buttons.addWidget(delete, 1, 3)

        root.addLayout(buttons)

        self.update_status()

    def update_status(self):

        running = self.manager.is_running(
            self.server["name"]
        )

        if running:

            self.status.setText(
                "RUNNING"
            )

            self.status.setObjectName(
                "running"
            )

        else:

            self.status.setText(
                "STOPPED"
            )

            self.status.setObjectName(
                "stopped"
            )

        self.status.style().unpolish(
            self.status
        )

        self.status.style().polish(
            self.status
        )

        process = self.manager.processes.get(
            self.server["name"]
        )

        if process and process.is_running():

            try:

                pid = (
                    process.process
                    .processId()
                )

                if pid:

                    proc = psutil.Process(pid)

                    cpu = proc.cpu_percent(
                        interval=None
                    )

                    memory = proc.memory_info().rss

                    self.cpu_label.setText(
                        f"CPU: {cpu:.1f}%"
                    )

                    self.ram_label.setText(
                        "RAM: "
                        + format_bytes(memory)
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                pass

        else:

            self.cpu_label.setText(
                "CPU: 0%"
            )

            self.ram_label.setText(
                "RAM: 0 MB"
            )

    def start_server(self):

        try:

            self.manager.start(
                self.server,
                self.main_window.receive_console
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Start Error",
                str(error)
            )

        self.main_window.refresh_stats()

    def stop_server(self):

        self.manager.stop(
            self.server
        )

        self.main_window.refresh_stats()

    def restart_server(self):

        if self.manager.is_running(
            self.server["name"]
        ):

            self.manager.stop(
                self.server
            )

            QTimer.singleShot(
                3000,
                self.start_server
            )

        else:

            self.start_server()

    def open_console(self):

        self.main_window.open_console(
            self.server
        )

    def open_settings(self):

        dialog = ServerSettingsDialog(
            self.server,
            self
        )

        if dialog.exec():
            self.main_window.refresh()

    def open_advanced(self):

        dialog = AdvancedServerSettingsDialog(
            self.server,
            self
        )

        if dialog.exec():
            self.main_window.refresh()

    def delete_server(self):

        if self.manager.is_running(
            self.server["name"]
        ):

            QMessageBox.warning(
                self,
                "Server Running",
                "Stop the server before deleting it."
            )

            return

        answer = QMessageBox.question(
            self,
            "Delete Server",
            f"Delete '{self.server['name']}'?\n\n"
            "The entire server folder will be deleted."
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:

            folder = server_path(
                self.server
            )

            if folder.exists():
                shutil.rmtree(folder)

            servers = [
                s for s in load_servers()
                if s["name"] != self.server["name"]
            ]

            save_servers(servers)

            self.main_window.refresh()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Delete Error",
                str(error)
            )


# ============================================================
# APP SETTINGS
# ============================================================

class AppSettingsDialog(QDialog):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "Application Settings"
        )

        self.setFixedSize(
            560,
            430
        )

        root = QVBoxLayout(self)

        title = QLabel(
            "Application Settings"
        )

        title.setObjectName(
            "dialogTitle"
        )

        root.addWidget(title)

        form = QFormLayout()

        self.theme_box = QComboBox()

        self.theme_box.addItems(
            list(THEMES.keys())
        )

        self.theme_box.setCurrentText(
            SETTINGS["theme"]
        )

        self.accent = QLineEdit(
            SETTINGS["accent"]
        )

        self.font = QLineEdit(
            SETTINGS["font_family"]
        )

        self.font_size = QSpinBox()

        self.font_size.setRange(
            10,
            28
        )

        self.font_size.setValue(
            SETTINGS["font_size"]
        )

        self.radius = QSpinBox()

        self.radius.setRange(
            0,
            32
        )

        self.radius.setValue(
            SETTINGS["corner_radius"]
        )

        form.addRow(
            "Theme:",
            self.theme_box
        )

        form.addRow(
            "Accent color:",
            self.accent
        )

        form.addRow(
            "Font:",
            self.font
        )

        form.addRow(
            "Font size:",
            self.font_size
        )

        form.addRow(
            "Corner radius:",
            self.radius
        )

        root.addLayout(form)

        info = QLabel(
            "Animations are disabled in this version."
        )

        info.setStyleSheet(
            f"color:{theme()['secondary']};"
        )

        root.addWidget(info)

        root.addStretch()

        buttons = QHBoxLayout()

        cancel = AppButton("Cancel")
        save = AppButton("Save")

        save.setObjectName(
            "primary"
        )

        cancel.clicked.connect(
            self.reject
        )

        save.clicked.connect(
            self.save
        )

        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(save)

        root.addLayout(buttons)

    def save(self):

        color = QColor(
            self.accent.text().strip()
        )

        if not color.isValid():

            QMessageBox.warning(
                self,
                "Invalid Color",
                "Example: #58A6FF"
            )

            return

        SETTINGS["theme"] = (
            self.theme_box.currentText()
        )

        SETTINGS["accent"] = (
            self.accent.text().strip()
        )

        SETTINGS["font_family"] = (
            self.font.text().strip()
            or "Inter"
        )

        SETTINGS["font_size"] = (
            self.font_size.value()
        )

        SETTINGS["corner_radius"] = (
            self.radius.value()
        )

        save_json(
            SETTINGS_FILE,
            SETTINGS
        )

        self.accept()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.manager = ServerManager()

        self.console_windows = {}

        self.setWindowTitle(
            APP_NAME
        )

        self.resize(
            1250,
            850
        )

        self.build_ui()

        self.refresh()

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.refresh_stats
        )

        self.timer.start(1200)

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        root = QVBoxLayout(
            central
        )

        root.setContentsMargins(
            24,
            22,
            24,
            18
        )

        root.setSpacing(16)

        # top

        top = QHBoxLayout()

        logo = QLabel(
            "MC HOST"
        )

        logo.setObjectName(
            "logo"
        )

        subtitle = QLabel(
            "Local Minecraft Server Hosting"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        top.addWidget(logo)
        top.addWidget(subtitle)
        top.addStretch()

        settings = AppButton(
            "Application Settings"
        )

        create = AppButton(
            "Create Server"
        )

        create.setObjectName(
            "primary"
        )

        settings.clicked.connect(
            self.open_app_settings
        )

        create.clicked.connect(
            self.create_server
        )

        top.addWidget(settings)
        top.addWidget(create)

        root.addLayout(top)

        # stats

        stats = QGridLayout()

        stats.setSpacing(12)

        self.total_card = (
            self.make_stat(
                "SERVERS",
                "0"
            )
        )

        self.running_card = (
            self.make_stat(
                "RUNNING",
                "0"
            )
        )

        self.cpu_card = (
            self.make_stat(
                "SYSTEM CPU",
                "0%"
            )
        )

        self.ram_card = (
            self.make_stat(
                "SYSTEM RAM",
                "0 GB"
            )
        )

        stats.addWidget(
            self.total_card,
            0,
            0
        )

        stats.addWidget(
            self.running_card,
            0,
            1
        )

        stats.addWidget(
            self.cpu_card,
            0,
            2
        )

        stats.addWidget(
            self.ram_card,
            0,
            3
        )

        root.addLayout(stats)

        title = QLabel(
            "Your Servers"
        )

        title.setObjectName(
            "sectionTitle"
        )

        root.addWidget(title)

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        container = QWidget()

        self.server_layout = QVBoxLayout(
            container
        )

        self.server_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        self.server_layout.setSpacing(12)

        self.server_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll.setWidget(
            container
        )

        root.addWidget(
            self.scroll
        )

        footer = QLabel(
            f"{APP_NAME} {APP_VERSION}"
        )

        footer.setStyleSheet(
            f"color:{theme()['muted']};"
        )

        root.addWidget(footer)

    def make_stat(
        self,
        title,
        value
    ):

        card = QFrame()

        card.setObjectName(
            "statCard"
        )

        layout = QVBoxLayout(card)

        title_label = QLabel(title)

        title_label.setObjectName(
            "statTitle"
        )

        value_label = QLabel(value)

        value_label.setObjectName(
            "statValue"
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card

    def set_stat(
        self,
        card,
        value
    ):

        for label in card.findChildren(
            QLabel
        ):

            if label.objectName() == "statValue":
                label.setText(value)

    def refresh(self):

        while self.server_layout.count():

            item = self.server_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        servers = load_servers()

        if not servers:

            empty = QLabel(
                "No servers yet.\n\n"
                "Click Create Server to create one."
            )

            empty.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty.setMinimumHeight(300)

            empty.setStyleSheet(
                f"color:{theme()['secondary']};"
                "font-size:18px;"
            )

            self.server_layout.addWidget(
                empty
            )

            return

        for server in servers:

            card = ServerCard(
                server,
                self.manager,
                self
            )

            self.server_layout.addWidget(card)

    def refresh_stats(self):

        servers = load_servers()

        running = sum(
            self.manager.is_running(
                s["name"]
            )
            for s in servers
        )

        self.set_stat(
            self.total_card,
            str(len(servers))
        )

        self.set_stat(
            self.running_card,
            str(running)
        )

        self.set_stat(
            self.cpu_card,
            f"{psutil.cpu_percent():.1f}%"
        )

        self.set_stat(
            self.ram_card,
            format_bytes(
                psutil.virtual_memory().used
            )
        )

        for card in self.findChildren(
            ServerCard
        ):
            card.update_status()

    def create_server(self):

        dialog = CreateServerDialog(
            self
        )

        if dialog.exec():
            self.refresh()

    def receive_console(
        self,
        server_name,
        text
    ):

        dialog = self.console_windows.get(
            server_name
        )

        if dialog:

            try:
                dialog.append_text(text)

            except RuntimeError:
                self.console_windows.pop(
                    server_name,
                    None
                )

    def open_console(
        self,
        server
    ):

        old = self.console_windows.get(
            server["name"]
        )

        if old:

            old.show()
            old.raise_()
            old.activateWindow()

            return

        dialog = ConsoleDialog(
            server,
            self.manager,
            self
        )

        self.console_windows[
            server["name"]
        ] = dialog

        dialog.finished.connect(
            lambda:
            self.console_windows.pop(
                server["name"],
                None
            )
        )

        dialog.show()

    def open_app_settings(self):

        dialog = AppSettingsDialog(
            self
        )

        if dialog.exec():

            QApplication.instance().setStyleSheet(
                stylesheet()
            )

            self.refresh()


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(sys.argv)

    app.setApplicationName(
        APP_NAME
    )

    app.setStyleSheet(
        stylesheet()
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
