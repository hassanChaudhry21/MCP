MCP Model Context Protocol (MCP)
Connecting agents to data sources such as databases or APIs.
MCP consists of a Host, Client, and Server — like a brain’s working memory for APIs.

Overview
MCP is an open standard designed to connect AI systems with external data sources. It enables two-way communication between clients (AI assistants or tools) and servers (data sources).

A developer can expose data by building an MCP server for a data source (database, API).

Or create an MCP client (AI tool) that connects to existing servers.

The protocol uses JSON-RPC messages to replace ad-hoc integrations, enabling any MCP-compatible client and server to interoperate seamlessly.

MCP Architecture
Clients (e.g., FastAPI app) send requests like “get joint angles” to servers (e.g., Tritium/Ameca interface), and servers respond accordingly.

MCP can also send commands from agents back to clients.

Roles:
The FastAPI app likely acts as an MCP server exposing Ameca sensor data and an MCP client to AI agents.

Study existing MCP servers for examples (e.g., GitHub, Postgres).

Integrating Ameca via FastAPI (AMI Client)
FastAPI app exposes HTTP endpoints that translate into Ameca API calls.

Example: /motion route triggers Ameca joint movements by calling Tritium’s script endpoints.

Use Tritium’s Python scripting API to make requests (e.g., POST /start_script).

FastAPI handles MCP JSON-RPC messages from AI agents, forwarding them to Ameca.

Steps:
Authenticate with Tritium robot OS.

Call its API via REST or WebSocket.

Wrap calls in FastAPI endpoints conforming to MCP schema.

Outcome:
Actual data exchange between robot and external systems is verified.

MCP Client Implementation
Implement MCP JSON-RPC client logic in Python.

Use FastAPI to receive MCP requests, translate, and dispatch them to Ameca/Tritium.

Use REST or WebSocket APIs from Tritium if available.

Test each API endpoint with scripts to ensure expected responses.

Handle authentication tokens for Tritium and MCP sessions securely.

MAI - 2: Current Status
✅ Achieved:
Functional MCP server infrastructure with FastAPI backend

Authentication (/token)

Commands (/command)

Google search (/google-query)

TTS and translation

Face recognition (/start-face-recognition)

Reminder scheduling

Static file serving

❌ Not Yet Done:
Ameca API integration

No active hardware control, speech output, facial expressions, or movement control

Need a client connection (ROS, WebSocket, serial, TCP) to send commands to Ameca

MAI - 3: RobotClient CLI - Documentation
How to Run Backend and Setup
Install prerequisites:

bash
Copy
Edit
pip install fastapi uvicorn requests
Start the FastAPI backend:

bash
Copy
Edit
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Configure network address for Tritium:

Open test3.py

Update the line:

python
Copy
Edit
self.api_url = "http://192.168.0.100:8000/command"
Replace with your FastAPI server’s IP/hostname.

Get Bearer Token for authentication:

Visit the OpenAPI docs at http://0.0.0.0:8000/docs after the FastAPI server is running.

Go to the /token endpoint.

Click Try it out.

Enter credentials:

Username: robot

Password: secret123

Execute to get a JWT bearer token.

Copy the token and paste it into:

python
Copy
Edit
self.token = "<your_token_here>"
inside your test3.py file.

Run test3.py.
The web app will be available at http://0.0.0.0:8000/.

View logs and endpoint status codes in your terminal where FastAPI is running to debug API calls.

RobotClient CLI
This Python script provides a command-line interface (CLI) client for interacting with the MCP API server.

Requirements
Python 3.6+

requests package (pip install requests)

Usage
Run the CLI script:

bash
Copy
Edit
python your_script_name.py
Use commands at the prompt (>) as described below. Use login first to authenticate before protected endpoints.

CLI Commands Summary
Command	Description	Example
login	Authenticate and get access token	login
set-command [lang]	Send a command with optional language code	set-command "turn on the lights" eng
get-command	Retrieve current command	get-command
google-query	Send a Google/DuckDuckGo search query	google-query "weather in London"
remind-me HH:MM	Set a reminder for a task at specific time	remind-me "call mom" 18:30
add-face	Upload a face image file for recognition	add-face aahil /path/to/Aahil.png
start-face	Start face recognition process	start-face
fact	Fetch a fun fact	fact
translate	Translate text from source to target language	translate "Bonjour" fr en
exit	Exit the CLI	exit

RobotClient Class Methods (Highlights)
authenticate(): Login and get JWT token.

headers(): Return auth headers for requests.

set_command(action, language_code="eng"): Send commands.

get_command(): Get current command.

google_query(query): Search query.

remind_me(task, time_str): Schedule reminders.

add_face(name, filepath): Upload face images.

start_face_recognition(): Begin face detection.

get_fact(): Retrieve a fun fact.

translate(text, source_lang="auto", target_lang="en"): Translate text.

MAI - 4: Acceptance Criteria and Progress
✅ Documented:
MCP and Ameca architecture and APIs

Explored endpoints and JWT-based authentication

Command flow and interaction mapping

⚠️ Challenges Identified:
Face encoding validation during live recognition

Forwarding MCP commands to Ameca animation/motion controllers

No unified pipeline from recognition to actions

Lack of sandbox environment for safe testing

Conversion of prototypes to reusable Python modules
