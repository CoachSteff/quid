# EMIS Knowledge Access Specification File

## Part 1: Technical Feasibility Report

### 1.1 Executive Summary

This report assesses the feasibility of developing an AI-driven Claude Skill to automate data retrieval from the EMIS (Energie- en milieu-informatiesysteem) portal.

The analysis concludes that the project is technically feasible but carries significant legal and operational risks. The primary challenge is not technical, but legal and contractual. The EMIS portal lacks a public API and is protected by a login, indicating that its data is not intended for public, automated redistribution.

Key Findings:

1. Technical Feasibility: Automating the login and data extraction is possible using modern browser automation frameworks like Playwright, which can be wrapped in a secure serverless API.
2. Security Risk: The Skill requires the use of organizational credentials. This necessitates an architecture where credentials are stored in a local .env file that is only accessible by the owner of the project.
3. Operational Risk: The EMIS site likely employs anti-bot detection (e.g., WAFs, rate limiting, behavioral analysis).6 An overly aggressive or poorly designed scraper will be detected and blocked, risking a "denial of service" for all organizational users. This means that our SKILL will be used primarily based on user interaction with a chatbot such as the Claude Desktop app.

Recommendation: The project should be approached as a medium-risk, high-reward initiative. The legal and security considerations are minimal, as this is a personal project running on a local computer. The technical architecture proposed in this document is contingent on the success of that engagement.

### 1.2 Access and Authentication Analysis

A preliminary analysis of the EMIS portal login page (emis.vito.be/en/user/login) reveals a standard, HTML-based form.8

- Form Structure: The page presents a simple email and password form with fields for "Email" ("Enter your email address") and "Password" ("Enter the password that accompanies your email address").8
- Authentication Type: The form appears to be a straightforward single-factor authentication (SFA) mechanism. There are no visible implementations of Two-Factor Authentication (2FA) (e.g., TOTP) 9 or Single Sign-On (SSO) federated identity providers on this specific page, although a separate VITO-specific login portal does exist.10
- Anti-Bot Mechanisms (Visible): The public login form does not display any visible anti-bot mechanisms, such as Google reCAPTCHA or hCaptcha.8

The simplicity of this form is deceptive. The absence of a visible CAPTCHA does not imply a lack of security. It often signifies the presence of more advanced, invisible, server-side bot detection.

### 1.3 Anti-Scraping and Bot Detection Analysis (The Real Challenge)

The primary technical hurdle is not the login form itself, but the inevitable, invisible anti-automation defenses deployed by a platform of this nature. It is standard practice for institutional portals to use a Web Application Firewall (WAF) (e.g., Cloudflare, AWS WAF, PerimeterX) to protect against automated threats.12

The Skill's automation backend must be designed to evade detection based on several vectors:

1. IP-Based Rate Limiting: Repeated, rapid requests from a single IP address (e.g., a serverless function's IP) are the most common trigger for a block.6 The system will need to manage a pool of rotating proxies to distribute its request footprint.6
2. Browser Fingerprinting: Headless browsers used by automation tools have unique digital fingerprints that make them trivial to detect.15 These include:
- navigator.webdriver flag set to true.18
- Mismatched User-Agent strings (e.g., "HeadlessChrome").19
- Inconsistent screen resolution, WebGL renderer, or font properties.16
1. Behavioral Analysis: Modern WAFs track user behavior, such as mouse movements, typing speed, and time between clicks.7 A bot that navigates and fills forms at a programmatic speed is easily flagged. The automation script must introduce randomized, human-like delays.17

Failure to address these detection vectors will result in HTTP 429 (Too Many Requests) errors, 403 (Forbidden) IP-level bans, or the presentation of invisible CAPTCHA challenges.6

### 1.4 Automation Tool Selection: Playwright vs. Puppeteer

To combat these defenses, a sophisticated, high-level browser automation tool is required. The choice is between the two leading Node.js-based frameworks: Playwright and Puppeteer.

|                 |                                                                 |                                                                                                                          |                                                                                                 |
| --------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| Feature         | Puppeteer                                                       | Playwright                                                                                                               | Recommendation                                                                                  |
| Browser Support | Chromium-focused. Firefox support is experimental.[22, 23]      | Cross-browser (Chromium, Firefox, WebKit).[24, 25]                                                                       | Playwright. Ensures compatibility if EMIS is optimized for a specific engine (e.g., Firefox).   |
| API & Features  | Robust, but simpler. Good for static pages and basic tasks.[24] | More advanced API. Better for complex, multi-page interactions, network interception, and parallel contexts.[23, 24, 25] | Playwright. The EMIS task (login, search, scrape, handle popups) is a complex, multi-step flow. |
| Community       | Larger, more established community.[23]                         | Smaller but rapidly growing; backed by Microsoft.[22]                                                                    | Puppeteer                                                                                       |
| Stealth         | Requires puppeteer-extra-plugin-stealth.                        | Requires playwright-stealth (or equivalent plugins).18                                                                   | Tie                                                                                             |

Conclusion: Playwright is the recommended tool.25 Its superior cross-browser support and more powerful API for handling complex interactions and network interception make it the more resilient and future-proof choice for this project.23

### 1.5 The "Stealth" Solution Stack

A default Playwright installation is easily detected.19 To be viable, the automation backend must integrate a "stealth" stack.

1. Use playwright-stealth Plugin: This is non-negotiable. This plugin (a port of the puppeteer-extra-plugin-stealth) automatically patches the Playwright instance to remove common automation flags.18 It will:
- Set navigator.webdriver to false.17
- Spoof a real User-Agent string.19
- Mimic realistic WebGL, plugin, and runtime properties.12
1. Randomize Fingerprint: The script must vary its fingerprint to avoid detection. This includes:
- User-Agent: Rotate User-Agent strings from a list of common, modern browsers.17
- Viewport: Set a realistic, common screen resolution (e.g., $1920 \times 1080$) and color depth, not a default headless-server viewport.16
1. Human-like Behavior: The script must not execute tasks instantaneously. It must simulate human interaction by:
- Adding small, randomized delays between actions (e.g., await page.waitFor(Math.random() * 2000 + 1000)).17
- Simulating typing into form fields rather than "pasting" values, if detection is highly aggressive.17

## Part 2: Secure Backend Architecture (The "Automation API")

### 2.1 Core Architectural Choice: Decoupled Serverless API

The Claude Skill itself must not contain the automation logic or credentials. Skills are designed to be lightweight triggers and front-ends.29

The recommended architecture is a decoupled, serverless API (e.g., using AWS Lambda and API Gateway) that the Claude Skill will call.31

- Claude Skill (Front-end): A simple script that takes the user's prompt and sends it to an API endpoint.34
- API Gateway (Middleware): A managed endpoint that authenticates the Skill (via an API key) and triggers the backend Lambda function.33
- AWS Lambda (Backend): A serverless function that contains the Playwright, playwright-stealth, and proxy logic.31

This decoupled model provides critical advantages:

- Security: Credentials and scraping logic are isolated on a secure backend, completely inaccessible to the Claude Skill or the end-user.37
- Scalability: AWS Lambda can scale automatically to handle multiple, concurrent queries without managing servers.31
- Maintainability: The scraping logic can be updated, fixed, or enhanced on the backend without needing to redeploy the Claude Skill.
- Cost-Efficiency: It is a "pay-as-you-use" model, only incurring costs when a query is actively running.31

### 2.2 Asynchronous Workflow (Handling the 30-Second Task)

A "live" scrape (launching a browser, logging in, navigating, and extracting data) can take 10-60 seconds. A synchronous API call from the Claude Skill will time out.

Therefore, the backend must be asynchronous, using a task queue pattern.40

1. Request: The Claude Skill calls a /start-query endpoint on the API Gateway.
2. Acknowledge: The API Gateway validates the request, triggers the Lambda function asynchronously, and immediately returns a unique task_id to the Skill. (Response time: <500ms).
3. Process: The Lambda function executes the 60-second Playwright scraping task. Upon completion, it saves the resulting JSON data to a temporary store (e.g., S3, Redis, or DynamoDB) indexed by the task_id.
4. Poll & Retrieve: The Claude Skill, having received the task_id, now polls a /get-result?task_id={...} endpoint every few seconds.
- For the first few polls, the API returns {"status": "processing"}.
- Once the Lambda job is complete, the API retrieves the JSON result from the temporary store and returns it to the Skill, completing the workflow.

This asynchronous pattern is the standard for integrating long-running tasks into responsive, real-time interfaces.40

### 2.3 Authentication and Session Persistence Workflow

Handling credentials and session state is the most critical security and performance component.

#### 2.3.1 Credential Storage

Credentials (email, password) must never be hardcoded or stored in environment variables in plain text. They must be managed by a dedicated, encrypted secrets manager.5

- Recommended Tools: AWS Secrets Manager or HashiCorp Vault.44
- Workflow:
1. The Lambda function is granted a specific IAM role.
2. This role gives it permission to read a specific secret (e.g., emis/production/credentials) from AWS Secrets Manager at runtime.
3. The credentials are loaded directly into memory within the Lambda function, used for the login, and then discarded when the function terminates.46
4. Crucially: Credentials are never logged or passed in any API request.5

#### 2.3.2 Session Persistence (The Performance Optimization)

Logging in for every single query is slow, costly, and "noisy" (it creates a high-risk, detectable event). A more advanced architecture will persist the session state.47

The recommended workflow for the Lambda function is:

1. Attempt to Load Session:
- The function attempts to load a "session state file" (containing cookies and local storage JSON) from a secure, encrypted S3 bucket.47
1. Validate Session:
- The function launches Playwright, injects this session state, and attempts to navigate to a protected page (e.g., emis.vito.be/dashboard).
1. Execute Path:
- IF SUCCESS (Session Valid): The login is bypassed. The script proceeds directly to scraping. This is the fast path (saves 10-20 seconds).
- IF FAILURE (Session Expired/Invalid): The script catches the failure, deletes the stale session file from S3, and proceeds to perform a full login using the vaulted credentials.49
1. Save New Session:
- After a successful full login, the script saves the new, valid session state (cookies, etc.) back to the encrypted S3 bucket, ready for the next query.47

This architecture 50 ensures the system is fast-by-default but resilient-by-design, only performing the high-risk login when absolutely necessary.

## Part 3: Claude Skill Prototype Skeleton

The Claude Skill itself is a "thin client." It follows the "black box" design pattern 29, where the Skill's code does not contain any business logic. Its sole purpose is to call the secure backend API. This is the most secure pattern, as it ensures no sensitive API keys or logic are ever exposed to the model.37

The Skill package is a simple folder containing three key files.52

### 3.1 Skill Manifest (config.yaml)

This file defines the Skill, its name, and its trigger. It tells Claude that this Skill's action is to run the run_query.py script.52

YAML

# config.yaml for emis-knowledge-access

name: emis-access

version: 0.1.0

description: Securely queries the VITO EMIS portal for environmental and energy data (e.g., BBT, legislation).

# This Skill is triggered by matching the description (e.g., "Check EMIS for...")

# It has no direct user inputs, as Claude will pass the full prompt.

inputs: {}

# This Skill's *only* action is to run its helper script.

# The script itself will read the user's prompt from its environment.

executable:

# The script is Python-based.

type: "script"

# The file 'run_query.py' must be in the same directory.

script: "run_query.py"

### 3.2 Skill Instructions (SKILL.md)

This is the "prompt" for the Skill.29 It is a "training manual" that teaches Claude how to use the run_query.py script and, most importantly, how to interpret the structured JSON it receives from the backend.

---

## name: emis-access description: Securely queries the VITO EMIS portal for environmental and energy data (e.g., BBT, legislation).

# VITO EMIS Access Skill

You have a tool, run_query.py, that can execute a live, authenticated query against the VITO EMIS portal.

## When to Use This Tool

Use this tool when the user asks for specific, non-public data from EMIS, BBT (Best Available Techniques), VITO, or Flemish environmental legislation.

Trigger examples:

- "Find recent BBT updates for water treatment."
- "What does EMIS say about waste management legislation in Flanders?"
- "Can you check the EMIS compendium for..."

## How to Use This Tool

1. Formulate Query: Take the user's natural language request and condense it into a clear, concise query string.
2. Execute Script: Run the run_query.py script. The script will automatically handle passing your query to the secure backend.
3. Await Response: The script will return a JSON object. This may take 10-30 seconds for a "live query." Inform the user that you are "performing a live check on the EMIS portal" and that it may take a moment.

## How to Interpret the JSON Response

You will receive a JSON object with this schema:json

{

"status": "success" | "error",

"query_type": "live_query" | "cached_rag",

"timestamp": "YYYY-MM-DDTHH:MM:SSZ",

"citation": {

"source_name": "EMIS Document XYZ",

"source_url": "[https://emis.vito.be/](https://emis.vito.be/)...",

"retrieved_on": "..."

},

"summary": "AI-generated summary of the findings.",

"raw_data": [

{ "column1": "value1", "column2": "value2" }

],

"error_message": "..." // Only if status is 'error'

}

## How to Report to the User

**On Success (`status: "success"`)**

1.  Start by presenting the `summary` text.

2.  Present the `raw_data` as a formatted markdown table if it is not too large.

3.  **CRITICAL: You MUST ALWAYS** conclude your answer with a "Source" or "Citation" block containing:

- The `source_name` and `source_url` from the `citation`.
- The `timestamp` of the data.
- The `query_type` (e.g., "This was a *live query* from..." or "This was retrieved from our *knowledge cache*...").

**On Failure (`status: "error"`)**

1.  Inform the user that the query could not be completed.

2.  Report the `error_message` (e.g., "The system reported: 'Login credentials have expired.'").

### 3.3 Backend Script Template (run_query.py)

This is the actual Python script 34 that lives in the Skill folder and gets executed by Claude. It acts as the "API client" for the serverless backend, implementing the asynchronous polling logic.

Python

#!/usr/bin/env python3

import os

import sys

import json

import requests

import time

# \--- CONFIGURATION ---

# These must be set as secure environment variables in the Claude Skill/Agent.

# [30, 37, 51]

API_ENDPOINT_URL = os.environ.get("EMIS_BACKEND_ENDPOINT")

API_KEY = os.environ.get("EMIS_BACKEND_API_KEY")

# \--- MAIN EXECUTION ---

def get_user_query_from_claude():

"""

Claude passes the user's prompt as a 'CLAUDE_PROMPT' env var

or as a command-line argument. This depends on the final

Skill SDK spec [54, 55], but we will assume an env var.

"""

# This is a hypothetical way Claude might pass the prompt.

query = os.environ.get("CLAUDE_PROMPT", "No query provided")

return query

def start_scrape_task(query):

"""

Calls the API Gateway to *start* the async task.

Returns a task_id.

"""

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

payload = {"query": query}

try:

response = requests.post(

f"{API_ENDPOINT_URL}/start-query",

headers=headers,

json=payload,

timeout=10

)

response.raise_for_status() # Raise HTTPError for bad responses

return response.json().get("task_id"), None

except requests.exceptions.RequestException as e:

return None, f"Error starting task: {e}"

def poll_for_result(task_id):

"""

Polls the /get-result endpoint until the data is ready.

(Implements the async pattern from 2.2)

"""

headers = {"X-API-Key": API_KEY}

poll_interval = 5 # seconds

max_wait = 60 # seconds

start_time = time.time()

while (time.time() - start_time) < max_wait:

try:

response = requests.get(

f"{API_ENDPOINT_URL}/get-result?task_id={task_id}",

headers=headers,

timeout=5

)

response.raise_for_status()

data = response.json()

if data.get("status") == "processing":

time.sleep(poll_interval)

continue # Keep polling

# Job is 'success' or 'error', so we return

return data

except requests.exceptions.RequestException as e:

return {"status": "error", "error_message": f"Polling failed: {e}"}

return {"status": "error", "error_message": "Query timed out after 60 seconds."}

def main():

"""

Main entry point for the Skill.

"""

if not API_ENDPOINT_URL or not API_KEY:

print(json.dumps({"status": "error", "error_message": "Skill is misconfigured. Secure environment variables (ENDPOINT, API_KEY) are not set."}))

sys.exit(1)

user_query = get_user_query_from_claude()

task_id, error = start_scrape_task(user_query)

if error:

print(json.dumps({"status": "error", "error_message": error}))

sys.exit(1)

final_result = poll_for_result(task_id)

# Print the final JSON output to stdout, which Claude will read.

print(json.dumps(final_result))

if **name** == "**main**":

main()

## Part 4: Dual-Mode Data Synchronization and RAG Strategy

The user's query ("factual querying... (read-only) or... synchronization to an internal database?") presents a false dilemma. A robust, scalable, and low-risk system requires both. A "Dual-Mode" strategy is proposed to balance data freshness, query speed, and operational risk.

This architecture supports two distinct workflows: a slow, real-time "Live Query" and a fast, cached "Knowledge Cache" (RAG).

Table 1: Data Synchronization Strategy

|            |                   |                                |                                 |                |                                                                 |
| ---------- | ----------------- | ------------------------------ | ------------------------------- | -------------- | --------------------------------------------------------------- |
| Workflow   | Name              | Trigger                        | Data Freshness                  | Speed          | Use Case                                                        |
| Workflow 1 | "Live Query"      | User's chat message            | Real-time (data is seconds old) | Slow (10-60s+) | High-stakes compliance checks, e.g., "Check for updates today." |
| Workflow 2 | "Knowledge Cache" | Scheduled (e.g., nightly cron) | Up to 24h old                   | Fast (<2s)     | General knowledge, e.g., "What is the BBT for...?"              |

### 4.1 Workflow 1: The "Live Query" (On-Demand Retrieval)

This is the on-demand workflow detailed in Part 2. It uses the asynchronous serverless architecture 31 to perform a live, targeted scrape in response to a user's query.

- Pros: Guarantees access to the most current data, as it scrapes the site at the moment of the query.56
- Cons:
1. Slow: The user must wait 10-60 seconds for browser startup, login, navigation, and scraping.
2. High-Risk: Every "live" execution is a "shot-on-goal" that risks triggering anti-bot detection.13 Frequent live queries from a small set of IPs is a classic bot behavior.
3. High-Cost: A serverless function running a full browser for 60 seconds is significantly more expensive than a 1-second database lookup.57
- Conclusion: This workflow is essential for time-sensitive compliance checks but must be used sparingly.

### 4.2 Workflow 2: The "Knowledge Cache" (Scheduled Synchronization for RAG)

This is the long-term, scalable solution.58 It separates data ingestion from data querying, forming the basis of a Retrieval-Augmented Generation (RAG) system.59

Ingestion Pipeline (Nightly Batch Job):

1. A Scheduled Task (e.g., n8n 14, AWS EventBridge 62, or a CRON node) triggers a dedicated "Batch Scraper" Lambda function.
2. This "Batch Scraper" Lambda performs a full, broad crawl of all relevant sections of EMIS (e.g., all BBT documents 63, all legislation, all compendia).
3. It passes the scraped HTML and PDFs to the Data Structuring Pipeline (Section 4.3).
4. The structured, chunked text 65 is then converted into vector embeddings.
5. These embeddings are stored in a Vector Database (e.g., Amazon OpenSearch Serverless 67, Chroma 68, Milvus 69).

Query Pipeline (RAG):

1. When the user queries Claude, the Skill's backend first tries to answer by querying this internal Vector DB.60
2. This is a simple, fast (sub-2-second) database lookup.
3. Only if the user explicitly asks "is this the latest data?" or "check for updates now" would the system escalate to the "Live Query" workflow.

Pros:

- Fast: 90% of queries will be answered in <2 seconds.
- Low-Risk: Reduces "live" interaction with the EMIS site from 100s of queries per day to one large batch query per night, minimizing the chance of being blocked.
- Scalable: Can support hundreds of users querying the cache without adding any load to the EMIS site.57

This RAG cache, however, becomes a high-risk, sensitive asset. It is a copy of VITO's protected data. This derivative database inherits all the same security and compliance requirements. It must be encrypted at rest, and all access must be controlled via strict IAM policies, just like any other production database containing confidential business information.75

### 4.3 Data Structuring Pipeline (ETL for AI)

This pipeline is the most critical component for the RAG workflow. It converts raw scraped content (HTML, PDFs) into clean, structured JSON and text chunks for AI ingestion.76

1. HTML Parsing:
- Task: Extracting text and, most importantly, tables 63 from the scraped HTML.
- Tools:
- Python lxml or BeautifulSoup 78: For parsing the main text content and identifying key <div> or <article> tags.
- Python pandas.read_html() 82: This is the most effective tool for "HTML table to JSON" conversion. It can instantly parse <table> tags on a page into a structured JSON array, which is far superior for AI ingestion than a simple text blob.
1. PDF Parsing (The "Hard Problem"):
- Task: EMIS contains many critical PDF-based guides and reports.64 These can be "digital" (text is selectable) or "scanned" (text is an image).
- Tool Comparison:
- Open Source (Tesseract) 84: This is a powerful, free OCR engine.
- Pros: Free.
- Cons: It produces raw text. It does not understand layout. If a PDF contains a table, Tesseract will return a jumbled, unformatted block of text. A developer must then write a second, complex, and brittle parser to guess where the table was and reconstruct it.
- Managed AI (AWS Textract) 84: This is a pay-per-page managed service.
- Pros: It is a document intelligence service, not just OCR. It uses AI to understand layout and natively exports tables, forms, and key-value pairs as structured JSON.
- Cons: Cost.

Recommendation: Use AWS Textract for the PDF pipeline.84 The goal of the project is AI ingestion.76 That ingestion requires structured data. The cost of paying for Textract per-page will be orders of magnitude lower than the engineering cost of building and maintaining a custom parser on top of Tesseract's unstructured output. It is the correct "buy-vs-build" decision for this use case.

## Part 5. Technical Audit and Logging Framework

To comply with GDPR and internal security policies, the system must create a "tamper-proof audit trail" 5 for accountability.

- Architecture: All components (Claude Skill, API Gateway, Lambda) 102 must log to a central, consolidated logging service (e.g., AWS CloudWatch). Logs must be set to immutable (infinite retention or read-only).102
- Traceability: A unique trace_id must be generated by the Skill for each user query and passed to all downstream services (API Gateway, Lambda).
- Log Events to Capture:
- `` "User prompt triggered EMIS query: '<query_text>'. TraceID: <trace_id>."
- [APIGateway] "Authenticated request from Skill. TraceID: <trace_id>. Triggering Lambda."
- [Lambda] "Starting query for TraceID: <trace_id>."
- [Lambda] "Session state loaded from S3." (or "Session state not found, performing full login.")
- [Lambda] "Navigated to /bbt. Extracted 10 rows."
- [Lambda] "Query complete. TraceID: <trace_id>. Returning 10 records."

This logging framework is not for debugging; it is a compliance tool. It allows a DPO to audit the system and prove, for any given query, exactly what data was accessed, by whom, and when.5

## Part 6: Concluding Recommendations and Phased Roadmap

This section provides a sequential, actionable plan to de-risk and build the "EMIS Knowledge Access Automator."

### 6.1 Phase 1: Build the Standalone Automation Backend (The "API")

- Action: Assuming legal approval, build the core "data-plane".31
- Components: API Gateway, Lambda (with Playwright + Stealth) 18, AWS Secrets Manager 44, S3 Session Store.47
- Deliverable: A stable, secure, asynchronous API. A developer can use Postman to POST a query ({"query": "BBT water"}) to /start-query and GET a structured JSON result from /get-result.

### 6.2 Phase 2: Integrate the Claude Skill (The "Chat UI")

- Action: Build the "AI front-end".52
- Components: The emis-access Skill folder containing config.yaml, SKILL.md, and the run_query.py script.
- Deliverable: A functional conversational agent. A user in the Claude chat interface can type "Find BBT for water treatment" and receive a human-readable, and cited answer. This deliverable achieves the "Live Query" (Workflow 1) capability.

### 6.3 Phase 3: Implement the RAG Pipeline (The "Knowledge Cache")

- Action: Build the scalable, long-term knowledge base.59 This is the most complex but highest-value phase.
- Components:
1. A new "Batch Scraper" Lambda, triggered by a nightly AWS EventBridge.62
2. The Data Structuring Pipeline (using AWS Textract 84 and Pandas 82).
3. A managed vector database (e.g., Amazon OpenSearch Serverless 67).
- Deliverable: A fully "Dual-Mode" system. 90% of queries are now answered instantly via the RAG cache 61, dramatically improving user experience and reducing the system's risk profile and operational cost.

**