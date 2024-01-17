import requests
import json

# Function to load configuration from the Traktarr config file
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    radarr_url = config['radarr']['url']
    radarr_api_key = config['radarr']['api_key']
    sonarr_url = config['sonarr']['url']
    sonarr_api_key = config['sonarr']['api_key']
    blacklisted_tmdb_ids = set(config['filters']['movies']['blacklisted_tmdb_ids'])
    blacklisted_tvdb_ids = set(config['filters']['shows']['blacklisted_tvdb_ids'])
    return radarr_url, radarr_api_key, sonarr_url, sonarr_api_key, blacklisted_tmdb_ids, blacklisted_tvdb_ids

# Function to fetch TMDB IDs from Radarr
def fetch_tmdb_ids(radarr_url, radarr_api_key):
    headers = {
        'accept': 'application/json',
        'X-Api-Key': radarr_api_key
    }
    endpoint = f'{radarr_url}/api/v3/exclusions'
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return [item['tmdbId'] for item in response.json() if 'tmdbId' in item]
    else:
        print(f"Error fetching data: Status code {response.status_code}")
        return []

# Function to fetch TVDB IDs from Sonarr
def fetch_tvdb_ids(sonarr_url, sonarr_api_key):
    headers = {
        'accept': 'application/json',
        'X-Api-Key': sonarr_api_key
    }
    endpoint = f'{sonarr_url}/api/v3/importlistexclusion'
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return [item['tvdbId'] for item in response.json() if 'tvdbId' in item]
    else:
        print(f"Error fetching data: Status code {response.status_code}")
        return []

# Function to update blacklisted TMDB IDs in the config file
def update_blacklisted_tmdb_ids(new_tmdb_ids, blacklisted_tmdb_ids):
    new_ids = set(new_tmdb_ids)

    # Find missing IDs
    missing_ids = new_ids - blacklisted_tmdb_ids

    if missing_ids:
        config['filters']['movies']['blacklisted_tmdb_ids'].extend(missing_ids)
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Added missing TMDB IDs to config file: {missing_ids}")
    else:
        print("No new TMDB IDs to add.")

def update_blacklisted_tvdb_ids(new_tvdb_ids, blacklisted_tvdb_ids):

    new_ids = set(new_tvdb_ids)
    
    # Find missing IDs
    missing_ids = new_ids - blacklisted_tvdb_ids

    if missing_ids:
        config['filters']['shows']['blacklisted_tvdb_ids'].extend(missing_ids)
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Added missing TVDB IDs to config file: {missing_ids}")
    else:
        print("No new TVDB IDs to add.")

# Main function
def main():
    config_path = '/opt/traktarr/config.json'  # Update with the path to your config file
    radarr_url, radarr_api_key, sonarr_url, sonarr_api_key, blacklisted_tmdb_ids, blacklisted_tvdb_ids = load_config(config_path)

    #radarr
    radarr_url = radarr_url.rstrip('/')
    tmdb_ids = fetch_tmdb_ids(radarr_url, radarr_api_key)
    update_blacklisted_tmdb_ids(tmdb_ids, blacklisted_tmdb_ids)

    #sonarr
    sonarr_url = sonarr_url.rstrip('/')
    tvdb_ids = fetch_tvdb_ids(sonarr_url, sonarr_api_key)
    update_blacklisted_tvdb_ids(tvdb_ids, blacklisted_tvdb_ids)

if __name__ == '__main__':
    main()
