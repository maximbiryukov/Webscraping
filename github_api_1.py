import requests
import json

user = 'maximbiryukov'

repos = requests.get(f'http://api.github.com/users/{user}/repos')

repos_json = repos.json()

file = open('mb_repos.json', 'w')

json.dump(repos_json, file)
