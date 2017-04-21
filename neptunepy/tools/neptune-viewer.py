# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-20 23:22:49
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-20 23:23:37

def main():
	global displayed_stars

	neptune = Neptune()
	neptune.save('raw_universe_data.json', neptune.raw_universe_data)
	neptune.save('intel.json', neptune.intel)

	fig, ax = plt.subplots()
	ax.set_title(neptune.name)

	# Load icons
	icons = []
	for key, player in neptune.players.items():
		icons.append(plt.imread("data/assets/{}.png".format(player.uid)))

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
	colors = iter(cm.rainbow(np.random.uniform(0,1,64)))
	for pkey, player in neptune.players.items():
		x = []
		y = []
		for key, star in neptune.stars.items():
			if star.owner == player.uid:
				x.append(star.position.x)
				y.append(-star.position.y)
		ax.scatter(x, y, zorder=1, color=next(colors))

	fig.canvas.mpl_connect('pick_event', onpick)

	plt.show()

def onpick(event):
    print("You selected: {}".format(displayed_stars[event.ind[0]]))

if __name__ == "__main__":
	main()