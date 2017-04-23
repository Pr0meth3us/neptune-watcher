# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-17 21:15:15
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-23 00:59:25
from bhutils import httpsession
import json, getpass, sys, os, time, math
import numpy as np

''' Server API for communicating with the EC2 instance '''
SERVER_API = {
	"root_url" : "http://ec2-34-201-27-166.compute-1.amazonaws.com:5000",
	"reports" : {
		"method" : "GET",
		"path" : "/neptune/reports/", # Add tick number suffix
		"content-type" : "application/x-www-form-urlencoded",
		"data" : {}
	}
}

''' Neptune API for communicating with the Neptune Pride servers '''
NEPTUNE_API = {
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
	''' Position of object on XY plane '''
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def distance(self, target):
		return math.sqrt((target.x - self.x)**2 + (target.y - self.y)**2)

# TODO(bhayes): Finish Fleet class, and it's json parsing
class Fleet():
	def __init__(self, fleet):
		self.uid = fleet["uid"]

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

class Report():
	def __init__(self, report):
		self.json_report = report

		self.fleet_speed = self.json_report["fleet_speed"]
		self.paused = self.json_report["paused"]
		self.productions = self.json_report["productions"]
		self.tick_fragment = self.json_report["tick_fragment"]
		self.now = self.json_report["now"]
		self.tick_rate = self.json_report["tick_rate"]
		self.production_rate = self.json_report["production_rate"]
		self.stars_for_victory = self.json_report["stars_for_victory"]
		self.game_over = self.json_report["game_over"]
		self.started = self.json_report["started"]
		self.start_time = self.json_report["start_time"]
		self.total_stars = self.json_report["total_stars"]
		self.production_counter = self.json_report["production_counter"]
		self.trade_scanned = self.json_report["trade_scanned"]
		self.tick = self.json_report["tick"]
		self.trade_cost = self.json_report["trade_cost"]
		self.name = self.json_report["name"]
		self.player_uid = self.json_report["player_uid"]
		self.admin = self.json_report["admin"]
		self.turn_based = self.json_report["turn_based"]
		self.war = self.json_report["war"]
		self.turn_based_time_out = self.json_report["turn_based_time_out"]

		# Generate fleet objects
		self.fleet = {}
		for key, fleet in self.json_report["fleets"].items():
			self.fleet[key] = Fleet(fleet)

		# Generate player objects
		self.players = {}
		for key, player in self.json_report["players"].items():
			self.players[key] = Player(player)

		# Generate star objects
		self.stars = {}
		for key, star in self.json_report["stars"].items():
			self.stars[key] = Star(star)

class Neptune():
	''' Main class to run Neptune Pride API methods '''
	def __init__(self):
		self.session = httpsession.HTTPSession()
		self.connected = False
		self.report = None
		self.report_history = {}
		self._gamenumber = None

	def updateIntel(self):
		# Get intel report
		rv = self.APICall(NEPTUNE_API, "intel_data")

		# TODO(bhayes): Do something interesting with this intel
		self.intel = rv

	def setGameNumber(self, gamenumber):
		if not self.connected:
			raise RuntimeError("You must connect first.")

		if gamenumber in self.valid_gamenumbers:
			self._gamenumber = gamenumber
			for key in NEPTUNE_API:
				if "data" in NEPTUNE_API[key]:
					if "game_number" in NEPTUNE_API[key]["data"]:
						NEPTUNE_API[key]["data"]["game_number"] = self._gamenumber
		else:
			raise RuntimeError("Invalid game number")

	def getGameNumber(self):
		return self._gamenumber

	def listGames(self):
		if not self.connected:
			raise RuntimeError("You must connect first")

	def fetchLiveReport(self):
		''' Download full universe report for latest tick from neptune server '''
		if not self.connected:
			raise RuntimeError("You must connect first")
		elif not self._gamenumber:
			raise RuntimeError("You must select a game number first.")

		rv = self.APICall(NEPTUNE_API, "full_universe_report")
		self.report = Report(rv["report"])
		self.report_history[self.report.tick] = self.report

	def fetchFromServer(self, tick):
		''' Download full universe report for specified tick from EC2 Instance'''
		SERVER_API["reports"]["path"] += str(tick)
		rv = self.APICall(SERVER_API, "reports")
		self.report = Report(rv["report"])
		self.report_history[self.report.tick] = self.report

	def fetchFromFile(self, filename):
		''' Load report data from a local file '''
		rv = self.loadJSON(filename)
		self.report = Report(rv["report"])
		self.report_history[self.report.tick] = self.report

	def fetchAllFromServer(self):
		''' Download tick "0" which tells server to send you all it's report data '''
		SERVER_API["reports"]["path"] += "0"
		rv = self.APICall(SERVER_API, "reports")
		for index, report in enumerate(rv["history"]):
			self.report = Report(rv["history"][index]["report"])
			self.report_history[self.report.tick] = self.report

	def loadJSON(self, filename):
		''' Loads JSON data to target variable '''
		with open(filename, 'r') as fp:
			return json.load(fp)

	def APICall(self, api, key):
		''' Issue API call using API and a corresponding key '''
		if api[key]["method"] == "GET":
			rv = self.session.GET(api["root_url"], api[key]["path"], api[key]["data"])
		elif api[key]["method"] == "POST":
			rv = self.session.POST(api["root_url"], api[key]["path"], api[key]["data"], {"Content-Type" : api[key]["content-type"]})
		if rv == None:
			raise RuntimeError("HTTP request failed")

		return rv

	def connect(self, username, password, attempts=3):
		''' Logs into Neptune's Pride 2 account using username/password '''

		# Load data with username and password info
		NEPTUNE_API["login"]["data"]["alias"] = username
		NEPTUNE_API["login"]["data"]["password"] = password

		# Issue login POST request
		while True:
			try:
				rv = self.session.POST(NEPTUNE_API["root_url"], NEPTUNE_API["login"]["path"], NEPTUNE_API["login"]["data"], {"Content-Type" : NEPTUNE_API["login"]["content-type"]})
				if (rv[0] != "meta:login_success"):
					raise ValueError('LOGIN FAILED')

				rv = self.session.POST(NEPTUNE_API["root_url"], NEPTUNE_API["init_player"]["path"], NEPTUNE_API["init_player"]["data"], {"Content-Type" : NEPTUNE_API["init_player"]["content-type"]})
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
			self.connected = True
			break

		self.games_in = rv[1]["games_in"]
		self.open_games = rv[1]["open_games"]
		self.valid_gamenumbers = [game["number"] for game in self.open_games]

		# TODO(bhayes): Store logged in JSON data into class for use later
		return rv

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