# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-21 23:19:37
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-24 13:26:31
import neptunepy.neptune as npt
import getpass, os, time, json
import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import datacursor
import matplotlib.cm as cm

# TODO: Read config file and adjust behavior (login, defaults, etc.)

class NeptuneViewer(object):
    def __init__(self, neptune):
        self.neptune = neptune
        self.displayed_stars = []
        self.current_tick = 103
        self.color_rand = np.random.uniform(0,1,64)

    def display(self, report):
        fig, ax = plt.subplots()
        ax.set_title("{0} ({1})".format(report.name, report.tick))

        # Graph all stars
        x = []
        y = []
        self.displayed_stars = []
        for key, star in report.stars.items():
            x.append(star.position.x)
            y.append(-star.position.y)
            self.displayed_stars.append(star.name)
        ax.scatter(x, y, zorder=1, picker=True)

        # Graph all stars for each player (colored marks)
        x = []
        y = []
        colors = iter(cm.rainbow(self.color_rand))
        for pkey, player in report.players.items():
            x = []
            y = []
            for key, star in report.stars.items():
                if star.owner == player.uid:
                    x.append(star.position.x)
                    y.append(-star.position.y)
            ax.scatter(x, y, zorder=1, color=next(colors))

        fig.canvas.mpl_connect('pick_event', self.selectStar)

        plt.show()

    def selectStar(self, event):
        print("You selected: {}".format(self.displayed_stars[event.ind[0]]))

    def downloadHistory(self, neptune):
        if not os.path.exists("reports"):
            os.makedirs("reports")
        for index, report in neptune.report_history.items():
            fig, ax = plt.subplots()
            ax.set_title("{0} ({1})".format(report.name, report.tick))

            # Graph all stars
            x = []
            y = []
            displayed_stars = []
            for key, star in report.stars.items():
                x.append(star.position.x)
                y.append(-star.position.y)
                displayed_stars.append(star.name)
            ax.scatter(x, y, zorder=1, picker=True)

            # Graph all stars for each player (colored marks)
            x = []
            y = []
            colors = iter(cm.rainbow(self.color_rand))
            for pkey, player in report.players.items():
                x = []
                y = []
                for key, star in report.stars.items():
                    if star.owner == player.uid:
                        x.append(star.position.x)
                        y.append(-star.position.y)
                ax.scatter(x, y, zorder=1, color=next(colors))

            # Write img file
            fig.savefig("reports/tick-{}.png".format(report.tick))
            fig.clf()

            # Write json data file
            with open("reports/tick-{}.json".format(report.tick), 'w') as fp:
                json.dump(report.json_report, fp, sort_keys = True, indent = 4)

def main():
    # username = input("Username: ")
    # password = getpass.getpass("Password: ")

    neptune = npt.Neptune()
    # neptune.connect(username, password)

    # games = neptune.listGames()
    # print("Welcome. Please select a game.")

    # while True:
    #     for index, game in enumerate(neptune.open_games):
    #         print("({0}) {1}".format(index, game["name"]))
    #     _input = input(">> ")
    #     try:
    #         _input = int(_input)
    #         neptune.setGameNumber(neptune.open_games[_input]["number"])
    #         break
    #     except:
    #         print("ERROR: Invalid entry, try again.")
    #         continue

    neptune.fetchFromServer(239)

    nv = NeptuneViewer(neptune)
    nv.downloadHistory(neptune)

if __name__ == "__main__":
    main()
