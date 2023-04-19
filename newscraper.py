import requests, os, yaml, wget
from bs4 import BeautifulSoup
import tmdbsimple as tmdb
from sanitize_filename import sanitize


def get_episodes_from_soup(soup, tmdb_id=None, show_name=None, download_images=False, season_num=1):
    if not tmdb_id and not show_name:
        raise NameError("TMDB ID and Show Title Not Set")
    if not show_name:
        show = tmdb.TV(tmdb_id)
        info = show.info()
        show_name = info['name']
    if not tmdb_id:
        tmdb_id = "N/A"
    show_data = {
        'title': show_name,
        'tmdb_id': tmdb_id,
        'episodes': []
    }
    episode_cards = soup.find_all('div', class_='browse-item-card')
    for ep_object in episode_cards:
        episode = {}
        image_object = ep_object.find('img')
        # Extract the episode number and title
        episode['title'] = image_object['alt']
        num_label = ep_object.find('span', class_='media-episode')
        if num_label is None or "Episode" not in num_label.text:
            continue
        episode['episode_num'] = int(num_label.text.split(' ')[1])

        # Extract the episode description
        raw_description = ep_object.find('p')
        # Raw description can be None sometimes
        if raw_description:
            episode['desc'] = " " .join(word.strip() for word in raw_description.text.split())
        # Extract the URL for the episode image
        episode['img_url'] = url = image_object['src'].split('?')[0]  # Remove query params from URL
        if download_images:
            #File name of the form e00 - Episode title.jpg
            filename = f"e{episode['episode_num']:02d} - {episode['title']}.{url.split('.')[-1]}"
            filename = sanitize(filename)
            base_dir = f"imgs/{show_name}/Season {season_num}"
            os.makedirs(base_dir, exist_ok=True)
            path = os.path.join("imgs", show_name, f'Season {season_num}', filename)
            if os.path.exists(path):
                print("Existing File found:", filename)
            else:
                print("Downloading", filename, "from", url)
                wget.download(url, path)
        show_data['episodes'].append(episode)
    return show_data

def get_dropout_soup(show_url, session, season_num):
    full_url = f"https://www.dropout.tv/{show_url}/season:{season_num}"
    response = session.get(full_url)
    # Parse the HTML content of the page with BeautifulSoup
    return BeautifulSoup(response.content, 'html.parser')


debug = False
download_images = False
if debug:
    filename = "test.html"
    # Because i don't like with "with open() as f" blocks creating an indent
    with open(filename, 'rb') as html_file:
        html = html_file.read()
        soup = BeautifulSoup(html, 'html.parser')
    tmdb_id="89180"

    data = get_episodes_from_soup(soup, tmdb_id=tmdb_id)
    with open('test.yaml','w') as yaml_file:
        yaml.dump(data, yaml_file)
else:
    # Send a request to the login page to get the login token
    login_url = 'https://www.dropout.tv/login'
    response = requests.get(login_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    login_token = soup.find('meta', {'name': 'csrf-token'})['content']
    # Create a session to handle cookies
    session = requests.Session()

    with open('target_shows.yaml') as stream:
        target_shows = yaml.safe_load(stream)
    tmdb.API_KEY = target_shows['tmdb_api_key']
    for show in target_shows['shows']:
        print(f"Parsing show {show['name']}...")
        
        show_info = tmdb.TV(show['tmdb_id']).info()
        seasons = show_info['seasons']
        num_seasons = len(seasons)
        if seasons[0]['name'] == 'Specials' or seasons[0]['season_number'] == 0:
            num_seasons -= 1
            show['has_specials'] = True
        show['num_seasons'] = num_seasons
        if "seasons" not in show:
            show["seasons"] = []
        for i in range(1,num_seasons+1):
            print(f'\tSeason {i}...')
            soup = get_dropout_soup(show['show_url'], session, i)
            season = get_episodes_from_soup(soup, show_name=show['name'], download_images=download_images, season_num=i)
            show['seasons'].append({'season_num': i, 'episodes': season['episodes']})

    with open('data.yaml', 'w') as yaml_file:
        yaml.safe_dump(target_shows, yaml_file, sort_keys=False)
        

    


# tmdb_api_key = 'your_api_key'
# tmdb_show_url = f'https://api.themoviedb.org/3/tv/{tmdb_id}'
# params = {'api_key': tmdb_api_key}
# response = requests.get(tmdb_show_url, params=params)

# Extract the name of the show and the base URL for episode images from the API response
# show_name = response.yaml()['name']

# Find all the episode elements on the page and extract the necessary data

    # if tmdb_api_works:
    #     # Send an API request to the TMDb API to create a TV episode entry
    #     payload = {
    #         'api_key': tmdb_api_key,
    #         'name': episode_title,
    #         'overview': episode_description,
    #         'still_path': episode_image_url,
    #         'episode_number': episode_number,
    #         'season_number': 1,  # TODO MAKE A LOOP Assuming all episodes are in season 1 
    #         'show_id': tmdb_id,
    #         # Add any other necessary parameters here
    #     }
    #     response = requests.post(f'{tmdb_show_url}/season/1/episodes', data=payload)

    #     # Check the response status code to make sure the request was successful
    #     if response.status_code == 201:
    #         print(f'{show_name} episode {episode_number}: {episode_title} was successfully added to TMDb!')
    #     else:
    #         print(f'Error adding {show_name} episode {episode_number}: {response.text}')
    
