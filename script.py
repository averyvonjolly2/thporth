import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Scraper Function
def scrape_sports_schedule():
    url = "https://www.livesportsontv.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {"error": "Failed to retrieve data"}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    sports_data = {}
    
    sports_sections = soup.find_all("div", class_="sport-container")  # Adjust class based on site structure
    
    for sport_section in sports_sections:
        sport_name = sport_section.find("h2").text.strip()
        leagues = {}
        
        league_sections = sport_section.find_all("div", class_="league-container")  # Adjust class accordingly
        for league_section in league_sections:
            league_name = league_section.find("h3").text.strip()
            games = []
            
            game_items = league_section.find_all("div", class_="game-item")  # Adjust class accordingly
            for game in game_items:
                game_info = game.text.strip()
                game_time = game.find("span", class_="game-time").text.strip() if game.find("span", class_="game-time") else "TBD"
                tv_channel = game.find("span", class_="tv-channel").text.strip() if game.find("span", class_="tv-channel") else "Not listed"
                games.append(f"{game_info} - {game_time} on {tv_channel}")
                
            leagues[league_name] = games
        
        sports_data[sport_name] = leagues
    
    return sports_data

@app.route('/')
def index():
    sports_schedule = scrape_sports_schedule()
    
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sports Schedule</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            ul { list-style-type: none; padding-left: 0; }
            .sport, .league { cursor: pointer; margin: 5px 0; }
            .league, .game { margin-left: 10px; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
    <h1>Sports Schedule</h1>
    <ul id="sportsList">
        {% for sport, leagues in sports_schedule.items() %}
            <li>
                <div class="sport" onclick="toggleVisibility('leagueList{{ loop.index }}')">{{ sport }}</div>
                <ul id="leagueList{{ loop.index }}" class="hidden">
                    {% for league, games in leagues.items() %}
                        <li>
                            <div class="league" onclick="toggleVisibility('gameList{{ loop.index }}{{ loop.index0 }}')">{{ league }}</div>
                            <ul id="gameList{{ loop.index }}{{ loop.index0 }}" class="hidden">
                                {% for game in games %}
                                    <li class="game">{{ game }}</li>
                                {% endfor %}
                            </ul>
                        </li>
                    {% endfor %}
                </ul>
            </li>
        {% endfor %}
    </ul>
    
    <script>
        function toggleVisibility(id) {
            const element = document.getElementById(id);
            if (element) {
                element.classList.toggle('hidden');
            }
        }
    </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template, sports_schedule=sports_schedule)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
