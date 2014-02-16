import vim
from datetime import *
import os
import pickle

def getExtension(fileName):
    splits = fileName.rsplit(".", 1)
    if len(splits) < 2:
        return None
    elif splits[0] == "":
        return None
    else:
        return splits[1]

class ChronosState:
    def __init__(self):
        self.month = date.today().month
        self.day   = date.today().day
        self.week  = date.today().isocalendar()[1]
        self.statsDict = {"today": {}, "week": {}, "month": {}, "total": {}}

class Chronos:
    def __init__(self):
        self.timerDict = {}
        try:
            with open(".chronos", "r") as file:
                self.state = pickle.load(file)
        except:
            print "New state"
            self.state = ChronosState()
        if self.state.month != date.today().month:
            self.state.statsDict["month"].clear()
        if self.state.day != date.today().day:
            self.state.statsDict["today"].clear()
        if self.state.week != date.today().isocalendar()[1]:
            self.state.statsDict["week"].clear()

    def __del__(self):
        with open(".chronos", "w") as file:
            pickle.dump(self.state, file)

    def showStats(self):
        vim.command("vnew")
        curBuf = vim.current.buffer
        del curBuf[:]
        curBuf[0] = "Chronos time stats:"
        curBuf.append("Today:")
        self.printStatsFor("today")
        curBuf.append("This week:")
        self.printStatsFor("week")
        curBuf.append("This month:")
        self.printStatsFor("month")
        curBuf.append("All time:")
        self.printStatsFor("total")

    def startTimer(self):
        curBuf = vim.current.buffer.name
        if not curBuf:
            return
        curTime = datetime.now()

        self.timerDict[curBuf] = curTime

    def stopTimer(self):
        curBuf = vim.current.buffer.name
        if not curBuf:
            return

        curExt = getExtension(curBuf)
        if not curExt:
            return

        curTime = datetime.now()
        if curBuf not in self.timerDict:
            return
        startTime = self.timerDict[curBuf]
        del self.timerDict[curBuf]

        elapsed = curTime - startTime

        self.addToStats(curExt, elapsed)

    def addToStats(self, ext, elapsed):

        for when in ["today", "total", "week", "month"]:
            if ext in self.state.statsDict[when]:
                self.state.statsDict[when][ext] += elapsed
            else:
                self.state.statsDict[when][ext] = elapsed

    def printStatsFor(self, key):
        curBuf = vim.current.buffer
        for (ext, time) in self.state.statsDict[key].iteritems():
            curBuf.append("  %s" % ext)
            curBuf.append("    %s" % time)

chronos = Chronos()
