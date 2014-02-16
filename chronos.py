import vim
import sys
from datetime import *
import os
import pickle

clearStatsWarning = """Warning:
    If you do this, your stats will be forgoten and will not
    be recoverable. If you really want to do this, run this
    command again."""

def getExtension(fileName):
    splits = fileName.rsplit(".", 1)
    if len(splits) < 2:
        return None
    elif splits[0] == "":
        return None
    else:
        return splits[1]

def formatTimeDelta(delta):
    secs = delta.total_seconds()
    result = ""

    suffixes = [ ("y", 24 * 60 * 60 * 365)
               , ("m", 24 * 60 * 60 * 30)
               , ("w", 24 * 60 * 60 * 7)
               , ("d", 24 * 60 * 60)
               , ("h", 60 * 60)
               , ("m", 60)
               , ("s", 1)]
    for (s, t) in suffixes:
        q = int(secs) / t
        if q > 0:
            result += "%d%s " % (q, s)
        secs = secs % t
    return result.rstrip()

class ChronosState:
    def __init__(self):
        self.month = date.today().month
        self.day   = date.today().day
        self.week  = date.today().isocalendar()[1]
        self.statsDict = {"today": {}, "week": {}, "month": {}, "total": {}}

class Chronos:
    def __init__(self):
        self.timerDict     = {}
        self.confirmClear  = False
        self.savedTimespan = None
        try:
            with open(".chronos", "r") as file:
                self.state = pickle.load(file)
        except:
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
        vim.current.buffer.options["buftype"] = "nofile"
        curBuf = vim.current.buffer
        del curBuf[:]
        curBuf.append("")
        curBuf.append("Chronos time stats")
        curBuf.append("")
        curBuf.append("Today")
        self.printStatsFor("today")
        curBuf.append("")
        curBuf.append("This week")
        self.printStatsFor("week")
        curBuf.append("")
        curBuf.append("This month")
        self.printStatsFor("month")
        curBuf.append("")
        curBuf.append("All time")
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
        # TODO: Add configurable threshold.
        if elapsed.total_seconds() >= 10 * 60:
            self.savedTimespan = (elapsed, curExt)
        else:
            self.addToStats(curExt, elapsed)

    def addToStats(self, ext, elapsed):
        for when in ["today", "total", "week", "month"]:
            if ext in self.state.statsDict[when]:
                self.state.statsDict[when][ext] += elapsed
            else:
                self.state.statsDict[when][ext] = elapsed

    def addSaved(self):
        if self.savedTimespan:
            self.addToStats(self.savedTimespan[1], self.savedTimespan[0])
            print "Added %s to stats for %s" % self.savedTimespan
            self.savedTimespan = None

    def printStatsFor(self, key):
        curBuf = vim.current.buffer
        for (ext, time) in self.state.statsDict[key].iteritems():
            curBuf.append("  %s" % ext)
            curBuf.append("    %s" % formatTimeDelta(time))

    def clearStats(self):
        if self.confirmClear:
            self.state        = ChronosState()
            self.confirmClear = False
            print "All your stats are belong to the void."
        else:
            sys.stderr.write(clearStatsWarning)
            self.confirmClear = True

chronos = Chronos()
