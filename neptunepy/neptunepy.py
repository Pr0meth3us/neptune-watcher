# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-17 21:15:15
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-20 23:39:18
from bhutils import httpsession
import json, getpass, sys, os, time, math
import numpy as np

APIDATA = {
	"root_url" : "https://np.ironhelmet.com",
	"login" : {
		"method" : "POST",
		"path" : "/arequest/login",
		"content-type" : "application/x-www-form-urlencoded",
		"data" : {
			"type" : "login",
			"alias" : "USERNAME",
			"password" : "PASSWORD"
		}
	},
	"init_player" : {
		"method" : "POST",
		"path" : "/mrequest/init_player",
		"content-type" : "application/x-www-form-urlencoded",
		"data" : {
			"type" : "init_player"
		}
	},
	"full_universe_report" : {
		"method" : "POST",
		"path" : "/trequest/order",
		"content-type" : "application/x-www-form-urlencoded",
		"data" : {
			"type" : "order",
			"order" : "full_universe_report",
			"game_number" : "GAMENUMBER"
		}
	},
	"fetch_unread_count" : {
		"method" : "POST",
		"path" : "/trequest/fetch_unread_count",
		"content-type" : "application/x-www-form-urlencoded",
		"data" : {
			"type" : "fetch_unread_count",
			"game_number" : "GAMENUMBER"
		}
	},
	"intel_data" : {
		"method" : "POST",
		"path" : "/trequest/intel_data",
		"content-type" : "application/x-www-form-urlencoded",
		"data" : {
			"type" : "intel_data",
			"game_number" : "GAMENUMBER"
		}
	}
}

class Position():
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def distance(self, target):
		return math.sqrt((target.x - self.x)**2 + (target.y - self.y)**2)

# TODO(bhayes): Finish Fleet class, and it's json parsing
class Fleet():
	def __init__(self, fleet):
		self.uid = fleet["uid"]

# TODO(bhayes): Finish Star class, and it's json parsing
class Star():
	def __init__(self, star):
		# Public information
		self.uid = star["uid"]
		self.owner = star["puid"]
		self.name = star["n"]
		self.visible = int(star["v"])
		self.position = Position(float(star["x"]), float(star["y"]))

		# Private information
		self.economy = None
		self.science = None
		self.industry = None
		self.garrison = None
		self.naturalResources = None
		self.totalResources = None
		self.shipCount = None

		if self.visible:
			self.economy = star["e"]
			self.science = star["s"]
			self.industry = star["i"]
			self.garrison = star["ga"]
			self.naturalResources = star["nr"]
			self.totalResources = star["r"]
			self.shipCount = star["st"]

	def distanceToStar(self, star):
		''' Returns distance between this star and the star object passed in '''
		return self.position.distance(star.postion)

# TODO(bhayes): Finish Player class, and it's json parsing
class Player():
	def __init__(self, player):
		self.uid = player["uid"]

class Neptune():
	''' Main class to run Neptune Pride API methods '''
	def __init__(self, gameIndex=0):
		self.API = APIDATA
		self.session = httpsession.HTTPSession()
		self.loggedIn = False
		self.setGameIndex(gameIndex)

	def updateIntel(self):
		# Get intel report
		try:
			rv = self.APICall("intel_data")
		except Exception as e:
			raise(e)

		# TODO(bhayes): Do something interesting with this intel
		self.intel = rv

	def updateUniverse(self, source=None):
		# Get Full Game Report
		try:
			if source == None:
				rv = self.APICall("full_universe_report")
			else:
				rv = self.load(source)
		except Exception as e:
			raise(e)

		self.fleet_speed = rv["report"]["fleet_speed"]
		self.paused = rv["report"]["paused"]
		self.productions = rv["report"]["productions"]
		self.tick_fragment = rv["report"]["tick_fragment"]
		self.now = rv["report"]["now"]
		self.tick_rate = rv["report"]["tick_rate"]
		self.production_rate = rv["report"]["production_rate"]
		self.stars_for_victory = rv["report"]["stars_for_victory"]
		self.game_over = rv["report"]["game_over"]
		self.started = rv["report"]["started"]
		self.start_time = rv["report"]["start_time"]
		self.total_stars = rv["report"]["total_stars"]
		self.production_counter = rv["report"]["production_counter"]
		self.trade_scanned = rv["report"]["trade_scanned"]
		self.tick = rv["report"]["tick"]
		self.trade_cost = rv["report"]["trade_cost"]
		self.name = rv["report"]["name"]
		self.player_uid = rv["report"]["player_uid"]
		self.admin = rv["report"]["admin"]
		self.turn_based = rv["report"]["turn_based"]
		self.war = rv["report"]["war"]
		self.turn_based_time_out = rv["report"]["turn_based_time_out"]

		self.fleet = {}
		for key, fleet in rv["report"]["fleets"].items():
			self.fleet[key] = Fleet(fleet)

		self.players = {}
		for key, player in rv["report"]["players"].items():
			self.players[key] = Player(player)

		self.stars = {}
		for key, star in rv["report"]["stars"].items():
			self.stars[key] = Star(star)

		self.raw_universe_data = rv

	def loadJSON(self, filename):
		''' Loads JSON data to target variable '''
		try:
			with open(filename, 'r') as fp:
				return json.load(fp)
		except Exception as e:
			raise(e)

	def APICall(self, key):
		if not self.loggedIn:
			raise ValueError("You must be logged in to do that!")

		# Issue API Call
		try:
			rv = self.session.POST(self.API["root_url"], self.API[key]["path"], self.API[key]["data"], {"Content-Type" : self.API[key]["content-type"]})
			if rv == None:
				raise SystemError("Bad post data")
			return rv
		except Exception as e:
			raise(e)

	def login(self, username, password, attempts=3):
		''' Logs into Neptune's Pride 2 account using username/password '''

		# Load data with username and password info
		self.API["login"]["data"]["alias"] = username
		self.API["login"]["data"]["password"] = password

		# Issue login POST request
		while True:
			try:
				rv = self.session.POST(self.API["root_url"], self.API["login"]["path"], self.API["login"]["data"], {"Content-Type" : self.API["login"]["content-type"]})
				if (rv[0] != "meta:login_success"):
					raise ValueError('LOGIN FAILED')

				rv = self.session.POST(self.API["root_url"], self.API["init_player"]["path"], self.API["init_player"]["data"], {"Content-Type" : self.API["init_player"]["content-type"]})
				if (rv[0] != "meta:init_player"):
					raise ValueError('INIT FAILED')
			except Exception as e:
				if attempts > 0:
					attempts -= 1
					continue
				else:
					print("ERROR: {}".format(e))
					sys.exit()

			# LOGIN SUCCESS!
			self.loggedIn = True
			break

		# TODO(bhayes): Store logged in JSON data into class for use later
		return rv

	def setGameIndex(self, index):
		''' Injects game number into API data '''
		try:
			self.gameIndex = index
			for key in self.API:
				if "data" in self.API[key]:
					if "game_number" in self.API[key]["data"]:
						self.API[key]["data"]["game_number"] = data[1]["open_games"][index]["number"]
		except Exception as e:
			raise(e)

	def save(self, filename, data):
		with open(filename, 'w') as fp:
			json.dump(data, fp, sort_keys = True, indent = 4)

	def load(self, filename):
		data = None
		try:
			with open(filename, 'r') as fp:
				data = json.load(fp)
		except Exception as e:
			print("ERROR: {}".format(e))
			sys.exit(1)

		return data