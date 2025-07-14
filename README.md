# MCP
Model Context Protocol = Connecting agents to data sources such as databases or API'S
MCP = Consists of a Host, Client and Server 
Like a brain working memory for the API.

. Identify the API calls or endpoints for each module.
Sensor/audio access: The robot has cameras/mics/speakers for sensing and TTS

FastAPI project: Define endpoints (e.g. /get_sensor_data, /move_joint) that will, in their handlers, communicate with Ameca via the Tritium interface.

MCP Protocol Fundamentals
(MCP) is an open standard to connect AI systems with external data sources

. Designed for two-way communication between clients (AI assistants or tools) and servers (data sources) 

. In MCP architecture, a developer can either expose data by building an MCP server for a given source (e.g. a database or API), or create an MCP client (an AI tool) that connects to existing servers. The protocol replaces ad-hoc integrations with JSON-RPC messages, so any client and server speaking MCP can interoperate. The key points: MCP defines a standard way for a client (like our FastAPI service) to request data from a server (which could be our Tritium/Ameca interface), and vice versa

. Our client will both send requests (e.g. “get joint angles”) and possibly receive commands from the agent.
Client vs Server: Decide which role we play. Likely our FastAPI app will be an MCP server for Ameca data (exposing sensor feeds, state) and an MCP client to any AI agent. Study examples (e.g. MCP servers for GitHub or Postgres) for guidance.
Integrating Ameca via FastAPI (AMI Client)

With the above in place, we can implement the AMI (Ameca interface) as an MCP client using FastAPI. Essentially, our FastAPI application will expose HTTP endpoints that translate into Ameca API calls. For example, a FastAPI route /motion could trigger joint movements on Ameca by calling Tritium’s script endpoints. 

Potential Approach:

Tritium’s Python scripting API: the FastAPI handler makes a request to Tritium (for instance, invoking a specific script via a POST to /start_script) and returns the result. The FastAPI app must also accept MCP messages (JSON-RPC) from the AI agent and forward them appropriately. As a Python-based client, FastAPI can leverage Tritium’s Python support

In summary, our integration steps are: authenticate with the Tritium robot OS, call its API in Python (via REST or WebSocket), and wrap those calls in FastAPI endpoints that conform to the MCP schema. Successful integration will satisfy “Ameca API has been thoroughly researched and tested” by demonstrating actual data exchange between the robot and external systems.

MCP Client: Implement the MCP JSON-RPC client logic in Python. Use FastAPI to receive MCP-formatted requests, then translate and dispatch them to Ameca/Tritium.

API Calls: If Tritium provides REST or HTTP APIs (e.g. to start scripts or fetch status), call these from Python. Otherwise, use the WebRTC peer or direct Python scripting on the robot.

Testing: Write test scripts to ping each Ameca API and ensure the FastAPI endpoint returns the expected response. Verify that these endpoints can be called via MCP from an agent.

Authentication: Ensure the FastAPI server handles any needed auth tokens for both the Tritium robot and for MCP (if MCP sessions require keys).

MAI - 2 
1. Build functional MCP server infrastructure
✔️ YES – Achieved:

You have a FastAPI backend with:

Auth (/token)

Commands (/command)

Google search (/google-query)

TTS and translation

Face recognition (/start-face-recognition)

Reminder scheduling

Static file serving

This is a working MCP server infrastructure.

2. Implement Ameca API integration
❌ NOT YET:

There’s no clear integration with Ameca (e.g., controlling hardware, speech output, facial expressions, movement, etc.).

If this happens through setting current_command for Ameca to act on, you partially have the infrastructure — but actual connection to Ameca is missing.

→ You’ll need:

A client (e.g., ROS, WebSocket, serial, or TCP connection) that sends current_command to Ameca’s API or control system.

MAI - 3

RobotClient CLI - Comprehensive Documentation
Overview
This Python script implements a command-line interface (CLI) client to interact with a Robot API hosted at http://192.168.0.100:8000. It provides authentication, command sending, querying, face recognition management, translation, and other utility features via REST API endpoints.

Setup
Requirements
Python 3.6+

requests package (pip install requests)

Configuration
The base API URL is configured in the BASE_URL constant. Update this if your API server runs elsewhere.

Components
RobotClient Class
Handles all API communication and stores the authentication token.

Methods
authenticate()

Prompts user for username and password, sends credentials to /token endpoint, and stores the received JWT access token for authorization.

headers()

Returns authorization headers including the bearer token. Raises an exception if not authenticated.

set_command(action, language_code="eng")

Sends a command action with an optional language code to the /command endpoint.

get_command()

Retrieves the current command from /command.

google_query(query)

Submits a Google/DuckDuckGo search query to /google-query.

remind_me(task, time_str)

Sets a reminder task with a specified time via /remind-me.

add_face(name, filepath)

Uploads a face image file for recognition, sending multipart/form-data with the file to /add-face/.

start_face_recognition()

Starts the face recognition process via /start-face-recognition.

get_fact()

Fetches a fun fact from /fact.

translate(text, source_lang="auto", target_lang="en")

Sends a translation request to /translate, optionally specifying source and target languages.

CLI Commands
Command	Description	Usage Example
login	Authenticate and get an access token	login
set-command <action> [lang]	Send a command with optional language code (default 'eng')	set-command "turn on the lights" eng
get-command	Retrieve the current command	get-command
google-query <query>	Send a search query to Google/DuckDuckGo	google-query "weather in London"
remind-me <task> <HH:MM>	Set a reminder for a task at a specific time	remind-me "call mom" 18:30
add-face <name> <filepath>	Upload a face image file for recognition	add-face aahil /Users/hassanchaudhry/Downloads/Aahil.png
start-face	Start the face recognition process	start-face
fact	Get a fun fact	fact
translate <text> [src] [dst]	Translate text from source language (default auto) to target language (default 'en')	translate "Bonjour" fr en
exit	Exit the CLI	exit

How to Run
Run the script:

bash
Copy
Edit
python your_script_name.py
Use commands at the prompt (>) as shown above.

Use login to authenticate before calling protected endpoints.

Important Details
Authentication

The login command prompts for credentials and stores a JWT token used for authorization in subsequent requests.

Command Parsing

Uses shlex.split() to handle quoted strings properly in CLI input.

File Upload

The add-face command requires a valid file path; otherwise, it will print an error.

Error Handling

Basic error handling is implemented with informative messages.

Exit

Use exit or press Ctrl+C to exit the CLI gracefully.

MAI - 4

 Acceptance Criteria
 Document existing research and prototypes relevant to MCP or Ameca.

 List current understanding of MCP (Modular Control Platform) and Ameca (Humanoid Robot by Engineered Arts).

 Identify technical challenges and knowledge gaps encountered during exploration or development.

 Create a clear baseline for tracking future progress and improvements.

📋 Tasks & Progress
🧠 1. Document Current MCP Knowledge and Research
✅ Explored the MCP architecture and how it interfaces with various robot control systems.

✅ Reviewed available MCP API endpoints, protocols (REST/ROS if applicable), and communication flow.

✅ Noted down how commands are structured (e.g., JSON payloads for movement or expressions).

✅ Observed any CLI or SDK tools that MCP provides for interaction.

🤖 2. List Ameca API Understanding
✅ Accessed the Ameca documentation via the local API endpoint (e.g., http://192.168.0.X:8000).

✅ Understood the endpoints available:

/add-face/ (Face recognition)

/start-face-recognition (Start detection)

/translate (Text translation)

/command, /google-query, etc.

✅ Identified that the system uses JWT token-based authentication and communicates via JSON over HTTP.

✅ Understood the command handling pipeline (e.g., how spoken commands translate into robot actions).

⚠️ 3. Identify Technical Challenges Faced
⛔ Understanding how face encodings are validated during live recognition.

⛔ Not sure how MCP will "forward" commands from the local CLI to Ameca’s expressions/motion controller.

⛔ No unified data flow yet between Ameca recognition events and MCP responses (e.g., a "face recognized" → "greet by name" pipeline).

⛔ Unsure how to simulate or test commands outside of local development (no sandbox environment).

⛔ Converting API prototypes into reusable Python modules/scripts for MCP is not fully understood.

📝 4. Create Progress Documentation in Confluence
✅ Created a new Confluence page: “Intern Progress – MCP x Ameca Integration”

✅ Structured it into the following sections:

Overview

MCP Architecture Understanding

Ameca Capabilities

Command Flow Mapping

Known Issues

Questions for Mentor

✅ Included annotated screenshots and code snippets (e.g., RobotClient class in Python CLI).

📊 Baseline Snapshot
Area	Current Status
MCP API Familiarity	Moderate
Ameca API Usage	High (face/command/translate)
Full System Integration	Not Yet Started
CLI Command Coverage	~80% Working
Auth & File Handling	Understood
Real-time Feedback Loop	Needs Help

🧭 Next Steps
 Validate that face recognition is triggering the correct events.

 Work with mentor to map MCP command to Ameca animation sets.

 Begin logging system for debugging command chains.

 Explore persistent storage of recognized faces and their events.



