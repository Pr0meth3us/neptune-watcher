# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-22 23:39:39
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-23 00:40:14
from flask import Flask, jsonify, abort
from neptunepy import neptune
import os, json, time, threading, argparse

''' Parse command line arguments '''
parser = argparse.ArgumentParser()
parser.add_argument('--gamenumber', required=True)
parser.add_argument('--dir', required=True)
args = parser.parse_args()

app = Flask(__name__)

def collectdata():
    # Connect to neptune pride server
    instance = neptune.Neptune()
    instance.connect("bryantfhayes@gmail.com", "DX6JI9YMRDNN")

    # Collect data from indicated gamenumber
    print(args.gamenumber)
    instance.setGameNumber(args.gamenumber)

    # Get latest report
    instance.fetchLiveReport()

    # Save report to file
    path = os.path.join(args.dir, "tick-{}.json".format(instance.report.tick))
    print(instance.report)
    instance.save(path, instance.report.json_report)

    # Start timer to collect data again
    threading.Timer(900.0, collectdata).start()

@app.route('/neptune/reports/<int:tick>', methods=['GET'])
def get_report(tick):
    ''' HTTP get request for returning report at specified tick '''
    
    # If tick is zero, return all tick history
    if tick == 0:
        data = []
        for filename in os.listdir('.'):
            if filename.endswith(".json"):
                with open(filename, 'r') as fp:
                    data.append(json.load(fp))
        return jsonify({"history" : data})

    # See if specified tick exists
    data = None
    if os.path.isfile("out-{}.json".format(tick)):
        with open("out-{}.json".format(tick)) as fp:
            data = json.load(fp)

    # Return not found error if file does not exist
    if data == None:
        abort(404)

    return jsonify(data)

if __name__ == '__main__':
    # Spawn thread for data collection every X seconds
    collectdata()
    
    # Run Flask application
    app.run(host='0.0.0.0')