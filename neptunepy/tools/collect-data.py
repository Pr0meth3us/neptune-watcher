import neptune

np = neptune.Neptune(username='parzival', password='121692@Bry', gameIndex=1)
np.save("/home/ubuntu/out-{}.json".format(np.tick), np.raw_universe_data)

