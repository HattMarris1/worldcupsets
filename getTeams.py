import json
import requests

import os
api_key = os.getenv("API_KEY")
if api_key != "":
    print("key is good")
else:
    print("Key empty")
# Set up the API endpoint and headers
url = "http://worldcup26.ir:3050/get/teams"

headers = {
    'accept': "application/json",
}

# League 1 is the FIFA World Cup, Season 2026
querystring = {"league": "1", "season": "2026"}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check for HTTP errors
    
    data = response.json()
    teams = data.get("teams", [])
    
    # Format the data cleanly
    team_list = []
    for item in teams:
        team_info = {
            "id": item["_id"],
            "name": item["name_en"],
            "fifa_code": item["fifa_code"],
            "logo": item["flag"],
            "rank_points": 1000  # Placeholder: Edit this manually later!
        }
        team_list.append(team_info)
        
    # Print it out as pretty JSON so you can copy/paste it into a file
    print(json.dumps(team_list, indent=2))

except requests.exceptions.RequestException as e:
    print(f"Error fetching teams: {e}")