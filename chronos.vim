if !has('python')
    echo "Error: Chronos needs vim compiled with python support."
    finish
endif

python << EOF
import vim
from datetime import *

def getExtension(fileName):
    splits = fileName.rsplit(".", 1)
    if len(splits) < 2:
        return None
    elif splits[0] == "":
        return None
    else:
        return splits[1]

class Chronos:
    def __init__(self):
        self.timerDict = {}
        self.statsDict = {"today": {}, "week": {}, "month": {}, "total": {}}

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
        weekNumber  = date.today().isocalendar()[1]
        monthNumber = date.today().month
        dayNumber   = date.today().day

        # We don't want to keep old month/day/week around.
        # FIXME: Don't store them in dicts but in object.
        if dayNumber not in self.statsDict["today"]:
            self.statsDict["today"].clear()
            self.statsDict["today"][dayNumber] = None
        if weekNumber not in self.statsDict["week"]:
            self.statsDict["week"].clear()
            # Ugly hack
            self.statsDict["week"][weekNumber] = None
        if monthNumber not in self.statsDict["month"]:
            self.statsDict["month"].clear()
            self.statsDict["month"][monthNumber] = None

        for when in ["today", "total", "week", "month"]:
            if ext in self.statsDict[when]:
                self.statsDict[when][ext] += elapsed
            else:
                self.statsDict[when][ext] = elapsed

    def printStatsFor(self, key):
        curBuf = vim.current.buffer
        for (ext, time) in self.statsDict[key].iteritems():
            curBuf.append("  %s" % ext)
            curBuf.append("    %s" % time)

chronos = Chronos()
EOF

function! StartTimer()
    py chronos.startTimer()
endfunction

function! StopTimer()
    py chronos.stopTimer()
endfunction

function! PrintStats()
    py chronos.showStats()
endfunction

augroup Chronos
    autocmd!
    autocmd Chronos BufEnter,FocusGained * silent! call StartTimer()
    autocmd Chronos BufLeave,FocusLost * silent! call StopTimer()
augroup END
