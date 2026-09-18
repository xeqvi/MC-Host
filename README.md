MC Host

MC Host is a lightweight desktop application for managing local Minecraft Paper servers through a clean PyQt6 interface.

It allows you to create Minecraft servers, automatically download the required Paper server JAR, configure server settings, start/stop/restart servers, access the Minecraft console, monitor system resources, and manage server files — all from one application.

Status: Version 1.0.0
Platform: Windows, macOS, Linux
Server Software: PaperMC

✨ Features
🖥️ Server Management

Create multiple Minecraft servers.

Automatically create the server directory structure.

Automatically download server.jar from PaperMC.

Start Minecraft servers directly from the application.

Stop running servers gracefully.

Force-stop servers when necessary.

Restart servers.

Delete servers and their files.

Open individual server folders.

⚙️ Minecraft Configuration

Configure common Minecraft server properties including:

Minecraft version

Server MOTD

Gamemode

Survival

Creative

Adventure

Spectator

Difficulty

Peaceful

Easy

Normal

Hard

Maximum players

View distance

Simulation distance

Online mode

Whitelist

PvP

Server IP / bind address

Server port

Configuration is automatically written to:

server.properties

☕ Java / JVM Configuration

Each server can have its own Java configuration.

Supported options include:

Custom Java executable

RAM allocation

CPU core configuration

JVM arguments

Additional Minecraft arguments

For example:

-Xms4096M
-Xmx4096M
-XX:+UseG1GC

🖥️ Live Console

Each server has its own console window.

You can:

View server output.

View errors.

Send Minecraft commands.

Execute commands directly from the application.

Example:

say Hello from MC Host

📊 Resource Monitoring

MC Host displays system and server resource information, including:

System CPU usage

System RAM usage

Minecraft server CPU usage

Minecraft server memory usage

Server running/stopped status

🎨 Customizable Interface

The application includes multiple themes:

Dark

Midnight

Light

You can also customize:

Accent color

Font family

Font size

UI corner radius

Animations are intentionally disabled in version 1.0.0.

📁 Server File Management

MC Host automatically creates useful server directories:

server/
├── backups/
├── logs/
├── mods/
├── plugins/
└── server.jar


The application provides buttons for opening these folders directly.

💬 Discord Settings

The server configuration includes optional Discord integration settings such as:

Discord integration toggle

Discord invite

Discord webhook

Note: Discord configuration fields are currently stored as settings. A complete Discord bot/webhook integration is not implemented in this version.

💾 Persistent Configuration

Application settings are stored locally in:

data/settings.json


Server configurations are stored in:

data/servers.json

📋 Requirements
Python

Python 3.10 or newer is recommended.

You can check your Python version with:

python --version


or:

python3 --version

Python Packages

MC Host requires:

PyQt6

psutil

Install them with:

pip install PyQt6 psutil

Java

A Java installation is required to run Minecraft servers.

The application expects the Java executable to be available as:

java


You can verify Java with:

java -version


If Java is installed somewhere else, you can specify the full Java executable path through:

Server → Advanced Settings → Java executable

🚀 Installation
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/MC-Host.git


Enter the project directory:

cd MC-Host

2. Create a virtual environment

Recommended:

python -m venv .venv


Activate it on Windows:

.venv\Scripts\activate


On macOS/Linux:

source .venv/bin/activate

3. Install dependencies
pip install PyQt6 psutil

4. Run MC Host

If your Python file is named main.py:

python main.py


On some Linux/macOS systems:

python3 main.py

🎮 Usage
Creating a server

Launch MC Host.

Click Create Server.

Enter a server name.

Select the Minecraft version.

Select the amount of RAM.

Select the CPU core allocation.

Select the server port.

Click Create & Download.

MC Host will create the server directory and download the appropriate Paper server JAR automatically.

Starting a server

After creating a server:

Find the server in Your Servers.

Click Start.

MC Host will launch Java and start the Paper server.

The server status should change to:

RUNNING

Stopping a server

Click:

Stop


MC Host sends the Minecraft:

stop


command to the server so it can shut down normally.

Restarting a server

Click:

Restart


If the server is running, MC Host stops it and starts it again after a short delay.

Using the console

Click:

Console


You can enter Minecraft commands directly.

For example:

say Welcome to the server!


or:

list

⚙️ Server Settings

The Settings button allows you to configure basic server resources:

RAM

CPU cores

Port

For more advanced configuration, use:

Advanced Settings


Advanced settings include Minecraft gameplay options, network configuration, Java/JVM options, Discord settings, and server file access.

📂 Project Structure

After running the application, the project will look approximately like this:

MC-Host/
│
├── main.py
│
├── data/
│   ├── settings.json
│   └── servers.json
│
└── servers/
    └── My Survival Server/
        ├── backups/
        ├── logs/
        ├── mods/
        ├── plugins/
        ├── eula.txt
        ├── server.jar
        └── server.properties


The data/ and servers/ directories are created automatically by the application.

🌐 PaperMC

MC Host currently uses the PaperMC API to download Paper server builds.

The application retrieves the available stable build for the selected Minecraft version and downloads the server JAR automatically.

PaperMC:

https://papermc.io/

🔒 Important Notes
EULA

The application automatically creates:

eula.txt


with:

eula=true


Only use this if you have read and agree to the Minecraft EULA.

Backups

The backups/ directory is created automatically, but automatic backup functionality is not currently implemented.

Discord

Discord settings are currently configuration fields. MC Host does not currently provide a full Discord bot or webhook service.

Internet Connection

An internet connection is required when creating a server because MC Host needs to download the Paper server JAR.

Security

Be careful when exposing a Minecraft server to the internet.

If you configure:

server-ip=0.0.0.0


the server may listen on available network interfaces. Configure your firewall and network port forwarding appropriately.

🛠️ Troubleshooting
Could not start Java/Minecraft

Check that Java is installed:

java -version


If Java is installed but isn't available through your system PATH, open:

Advanced Settings


and set the Java executable to the correct path.

server.jar is missing

Open the server directory and make sure:

server.jar


exists.

If it doesn't, recreate the server or download the appropriate Paper server JAR.

Paper download fails

Make sure:

Your internet connection is working.

The selected Minecraft version is supported by PaperMC.

PaperMC's API is available.

Your firewall isn't blocking the application.

🧑‍💻 Development

The application is currently implemented as a single Python application using:

Python
PyQt6
psutil
PaperMC API


The main components include:

MinecraftProcess
ServerManager
CreateServerDialog
ServerSettingsDialog
AdvancedServerSettingsDialog
ConsoleDialog
ServerCard
AppSettingsDialog
MainWindow

🗺️ Possible Future Features

Potential improvements for future versions include:

Automatic server backups

Scheduled restarts

Automatic crash recovery

Auto-restart configuration

Plugin management

Mod management

Server log viewer

Player list

Online player count

Server TPS monitoring

Network traffic monitoring

Server status monitoring

Better download progress reporting

Java version detection

Server import/export

Server duplication

Server update management

Full Discord integration

Built-in server properties editor

System tray support

Packaged Windows executable

Packaged Linux application

Packaged macOS application

📜 License

Choose a license for your project before publishing.

For example, if you want to use the MIT License, create a file named:

LICENSE


and add the MIT license text.

⭐ Contributing

Contributions, suggestions, and bug reports are welcome.

Before submitting a pull request:

Test your changes.

Make sure the application still starts correctly.

Avoid committing generated server files.

Avoid committing personal configuration or secrets.

📌 Recommended .gitignore

Create a .gitignore file containing:

# Python
__pycache__/
*.py[cod]
*.pyo

# Virtual environment
.venv/
venv/
env/

# IDE
.vscode/
.idea/

# Application data
data/settings.json
data/servers.json

# Minecraft servers
servers/

# Logs
*.log

# Build files
build/
dist/
*.spec

# OS files
.DS_Store
Thumbs.db


This prevents your personal server data and generated files from being uploaded to GitHub.
