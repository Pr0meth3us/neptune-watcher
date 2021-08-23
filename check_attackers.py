#!/usr/local/bin/python3

import math
import neptunepy.neptune as ntp
import requests
import json
import os

from pprint import pprint
from decouple import config

try:
  discord_webhook = os.environ['DISCORDWEBHOOK']
except Exception as e:
  print(f'Unable to find {e}, loading from .env file')
  discord_webhook = config('DISCORDWEBHOOK')
  
try:
  np_user = os.environ['NPUSERNAME']
except Exception as e:
  print(f'Unable to find {e}, loading from .env file')
  np_user = config('NPUSERNAME')

try:
  np_pass = os.environ['NPPASSWORD']
except Exception as e:
  print(f'Unable to find {e}, loading from .env file')
  np_pass = config('NPPASSWORD')

try:
  np_game_url = os.environ['NPGAMEURL']
except Exception as e:
  print(f'Unable to find {e}, loading from .env file')
  np_game_url = config('NPGAMEURL')


def calculate_winner(defender_level, defender_ships, attacker_level, attacker_ships):
  attacker_remaining = attacker_ships - math.ceil(defender_ships / attacker_level) * (defender_level)
  defender_remaining = defender_ships - (math.ceil(attacker_ships / defender_level) - 1) * attacker_level

  if defender_remaining > 0:
    result = {
      'result': f'Defender wins with {defender_remaining} ships remaining',
      'color': '255'
    }
  else:
    result = {
      'result': f'Attacker wins with {attacker_remaining} ships remaining',
      'color': '16711680'
    }

  return result

def post_to_discord(data):
  customHeaders = {
    'Content-Type': 'application/json'
  }
  try:
    response = requests.post(discord_webhook, data=json.dumps(data), headers=customHeaders)
    if response.status_code != 204:
      print('Failed: {}'.format(response.reason))
  except:
      print('Error POSTing to Discord for some reason, something in the requests library')

def main():
  neptune = ntp.Neptune()
  neptune.connect(np_user, np_pass)
  games = neptune.listGames()
  neptune.setGameNumber(neptune.open_games[0]["number"])
  neptune.fetchLiveReport()
  latest_report = neptune.report

  current_player = latest_report.players[str(latest_report.player_uid)]
  current_player_name = current_player.alias
  current_player_tech = current_player.tech
  current_player_weapons = current_player_tech.weapons['level']

  print(f'Current player: {current_player_name}\n')

  my_fleets = [(val.name, val.owner) for key, val in latest_report.fleets.items()]
  visible_enemies = [(val.owner) for key, val in latest_report.fleets.items()]
  visible_enemies.extend([val.owner for key, val in latest_report.stars.items() if val.visible])
  visible_enemies = set(visible_enemies)
  visible_enemies.remove(latest_report.player_uid)

  enemy_fleets = [val for key, val in latest_report.fleets.items() if val.owner in visible_enemies]


  enemy_fleets_inbound = [val.name for val in enemy_fleets if val.isTargetingPlayer(latest_report.player_uid, neptune.report)]

  for fleet in enemy_fleets:
      # pprint(vars(fleet))
      # print(f'Ship name: {fleet.name}')
      if fleet.getTargetStar() != None and enemy_fleets_inbound:
        print(f'Fleets inbound: {enemy_fleets_inbound}')
        target_star = latest_report.stars[str(fleet.getTargetStar())]
        target_star_name = target_star.name
        target_star_ships = target_star.shipCount
        attacker_name = latest_report.players[str(fleet.owner)].alias

        attacker = latest_report.players[str(fleet.owner)]
        attacker_name = attacker.alias
        attacker_weapons_level = attacker.tech
        attacker_weapons_level = attacker_weapons_level.weapons['level']
        try:
          target_star_name = latest_report.stars[str(fleet.getTargetStar())].name
        except:
          target_star_name = None

        target_star_name = target_star.name
        target_star_ships = target_star.shipCount

        defense_level = current_player_weapons + 1
        attack_result_obj = calculate_winner(defense_level, target_star_ships, attacker_weapons_level, fleet.shipCount)
        attack_result = attack_result_obj['result']
        result_color = attack_result_obj['color']

        postContent = {
          'username': current_player_name,
          'embeds': [{
            'author': {
              'name': f'{current_player_name} is getting attacked by {attacker_name}!',
              'url': np_game_url
            },
            'fields': [
              {
                'name': 'Target Star',
                'value': target_star_name,
                'inline': True
              },
              {
                'name': 'Attacker',
                'value': attacker_name,
                'inline': True
              },
              {
                'name': 'Attacker Level',
                'value': attacker_weapons_level,
                'inline': True
              },
              {
                'name': 'Fleet Name',
                'value': fleet.name,
                'inline': True
              },
              {
                'name': 'Fleet Size',
                'value': fleet.shipCount,
                'inline': True
              },
              {
                'name': 'Your Defense Level',
                'value': defense_level,
                'inline': True
              },
              {
                'name': 'Target Star Ships',
                'value': target_star_ships,
                'inline': True
              },
              {
                'name': 'Result',
                'value': attack_result,
                'inline': True
              },
              {
                'name': 'Tick Number',
                'value': latest_report.tick,
                'inline': True
              }
            ],
            'color': result_color
          }]
        }
        if target_star_name:
          post_to_discord(postContent)
        
        

if __name__ == '__main__':
  main()
