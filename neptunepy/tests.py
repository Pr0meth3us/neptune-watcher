# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-24 12:58:15
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-28 12:37:42
from pkg_resources import resource_string, resource_listdir, resource_stream
from neptunepy.neptune import *
from neptunepy.neptune_viewer import *

def test_resources():
    # Itemize data files under neptunepy/resources/config:
    print(resource_listdir('neptunepy.resources.config', ''))
    configfile = resource_stream("neptunepy.resources.config", 'config.ini').read().decode()
    print(configfile)

def test_attackingships():
    neptune = Neptune()
    # neptune.connect("parzival", "DX6JI9YMRDNN")
    # neptune.setGameNumber(neptune.open_games[1]["number"])
    # neptune.fetchLiveReport()
    neptune.fetchFromFile('resources/api/example.json')

    my_fleets = [(val.name, val.owner) for key, val in neptune.report.fleets.items()]
    visible_enemies = [(val.owner) for key, val in neptune.report.fleets.items()]
    visible_enemies.extend([val.owner for key, val in neptune.report.stars.items() if val.visible])
    visible_enemies = set(visible_enemies)
    visible_enemies.remove(neptune.report.player_uid)

    enemy_fleets = [val for key, val in neptune.report.fleets.items() if val.owner in visible_enemies]

    enemy_fleets_inbound = [val.name for val in enemy_fleets if val.isTargetingPlayer(neptune.report.player_uid, neptune.report)]

    for fleet in enemy_fleets:
        print(fleet.name)
        print(fleet.getTargetStar())
    print(enemy_fleets_inbound)

    #print(my_fleets)

if __name__ == "__main__":
    test_attackingships()