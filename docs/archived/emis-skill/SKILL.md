---
name: emis-access
description: Securely queries the VITO EMIS portal for environmental and energy data (e.g., BBT, legislation).
---

# VITO EMIS Access Skill

You have a tool, `scripts/run_query.py`, that can execute a live, authenticated query against the VITO EMIS portal.

## When to Use This Tool

Use this tool when the user asks for specific, non-public data from EMIS, BBT (Best Available Techniques), VITO, or Flemish environmental legislation.

Trigger examples:
- "Find recent BBT updates for water treatment."
- "What does EMIS say about waste management legislation in Flanders?"
- "Can you check the EMIS compendium for..."
- "Search EMIS for information about..."

## How to Use This Tool

1. **Formulate Query**: Take the user's natural language request and condense it into a clear, concise query string that would be effective for searching the EMIS portal.

2. **Execute Script**: Run the `scripts/run_query.py` script. The script will:
   - First try to use the backend API service (if available)
   - Automatically fall back to direct scraping if backend is unavailable
   - Handle all the complexity of connecting to EMIS portal

3. **Await Response**: The script will return a JSON object. This may take 10-30 seconds for a "live query" as it performs real-time scraping. Inform the user that you are "performing a live check on the EMIS portal" and that it may take a moment.

## How to Interpret the JSON Response

You will receive a JSON object with this schema:

```json
{
  "status": "success" | "error",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "citation": {
    "source_name": "EMIS Portal",
    "source_url": "https://emis.vito.be/...",
    "retrieved_on": "..."
  },
  "summary": "AI-generated summary of the findings.",
  "raw_data": [
    { "column1": "value1", "column2": "value2" }
  ],
  "error_message": "..." // Only if status is 'error'
}
```

## How to Report to the User

**On Success (`status: "success"`)**

1. Start by presenting the `summary` text if available, or create your own summary based on the `raw_data`.

2. Present the `raw_data` as a formatted markdown table if it is not too large (max 20 rows). If the data is extensive, summarize the key findings instead.

3. **CRITICAL: You MUST ALWAYS** conclude your answer with a "Source" or "Citation" block containing:
   - The `source_name` and `source_url` from the `citation`.
   - The `timestamp` of the data.
   - Note that this was a *live query* from the EMIS portal.

**On Failure (`status: "error"`)**

1. Inform the user that the query could not be completed.

2. Report the `error_message` in a user-friendly way (e.g., "The system reported: 'Login credentials have expired.'" or "The EMIS portal is currently unavailable.").

3. Suggest alternatives if appropriate (e.g., "Please try again in a few moments" or "You may need to check your EMIS portal access credentials.").

## Important Notes

- **Two Operating Modes**: 
  - **Backend Mode** (default): Connects to a separate backend API service. Requires backend to be running.
  - **Direct Mode** (fallback): Runs Playwright directly when backend is unavailable. Requires Playwright to be installed in the environment.
  
- **Automatic Fallback**: If the backend service is not available, the skill will automatically try direct scraping mode (if Playwright is installed). This means the skill can work without a backend service.

- This tool performs live queries against the EMIS portal. Each query requires authentication and may take 10-30 seconds.

- The tool maintains a session between queries to improve performance, but sessions may expire.

- If you receive an error, be respectful of rate limits and don't retry immediately.

- Always cite your sources when presenting data from EMIS.

## Troubleshooting

If the skill reports connection errors:
1. Verify the backend service is running by checking `http://localhost:38153/`
2. Ensure EMIS credentials are configured in the backend `.env` file
3. Check that the backend URL matches the configured `EMIS_BACKEND_URL` (defaults to `http://localhost:38153`)
4. See the project's QUICKSTART.md for detailed setup instructions

