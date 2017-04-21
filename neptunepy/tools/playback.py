# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-20 00:50:07
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-20 01:13:39
import neptune as nept
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.misc import imread
from mpldatacursor import datacursor
import matplotlib.cm as cm

displayed_stars = []

neptune = nept.Neptune(local=True)
color_array = np.random.uniform(0,1,64)

for filename in os.listdir('../data/universedata'):
	if filename.endswith('.json'):
		neptune.updateUniverse(source=os.path.join('../data/universedata', filename))
		fig, ax = plt.subplots()
		ax.set_title(neptune.name)

		# Graph all stars
		x = []
		y = []
		displayed_stars = []
		for key, star in neptune.stars.items():
			x.append(star.position.x)
			y.append(-star.position.y)
			displayed_stars.append(star.name)
		ax.scatter(x, y, zorder=1, picker=True)

		# Graph all stars for each player (colored marks)
		x = []
		y = []
		colors = iter(cm.rainbow(color_array))
		for pkey, player in neptune.players.items():
			x = []
			y = []
			for key, star in neptune.stars.items():
				if star.owner == player.uid:
					x.append(star.position.x)
					y.append(-star.position.y)
			ax.scatter(x, y, zorder=1, color=next(colors))

		fig.savefig(filename.strip('.') + ".png")
		fig.clf()
