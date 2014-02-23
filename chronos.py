import vim
import sys
from datetime import *
import os
import pickle

clearStatsWarning = """Warning:
    If you do this, your stats will be forgoten and will not
    be recoverable. If you really want to do this, run this
    command again."""

def formatTimeDelta(delta):
    """ Format a timedelta into a human-readble string.

    The output uses the format "1y 2m 3w 4d 5h 6m 7s", and if there are 0
    of some unit of time, it is not included in the output, except in the
    case where delta.total_seconds() is 0, in which case the output will
    be "0s" as to not output an empty string.
    """
    secs   = delta.total_seconds()
    result = ""

    # A list of our time-unit suffixes and their durations in seconds.
    suffixes = [ ("y", 24 * 60 * 60 * 365)
               , ("w", 24 * 60 * 60 * 7)
               , ("d", 24 * 60 * 60)
               , ("h", 60 * 60)
               , ("m", 60)
               , ("s", 1)]

    # Add every suffix to the suffix to the output where we have at least
    # 1 unit of time.
    for (s, t) in suffixes:
        q = int(secs) / t
        if q > 0:
            result += "%d%s " % (q, s)
        secs = secs % t

    # Needed so we don't display an empty in the case of 0s.
    if not result:
        result = "0s"

    # Remove the trailing space.
    return result.rstrip()

class ChronosState:
    """ Stores all the state chronos needs to persist across sessions. """

    def __init__(self):
        """ Initializes an empty chronos state.

        This should only ever happen in the case where the plugin has just
        been installed or for some other reason the state could not be read
        from the disk.
        """
        # These are needed to keep track of different #statistics 
        # across days, weeks and months.
        self.month = date.today().month
        self.day   = date.today().day
        # Current ISO week number.
        self.week  = date.today().isocalendar()[1]
        # The dictionary for all the statistics
        self.statsDict = {"today": {}, "week": {}, "month": {}, "total": {}}

class Chronos:
    """ The main class that does all the work.
    """
    def __init__(self):
        """ Initializes the plugin's state.

        Some state only lives for the duration of a session, while the
        usage statistics and some other stuff(See ChronosState) needs to be
        saved accross sessions.
        """

        # Used to keep track of how much time is spent in buffers.
        self.timerDict     = {}
        # Used as a confirmation when the user wants to clear his stats.
        self.confirmClear  = False
        # If the inactivity threshold is crossed, the timespan for that period
        # is stored here. This variable's state is also used to check if the
        # inactivity threshold was crossed. E.g. if it's None, no such thing
        # has happened. This is a tuple, (elapsed, extension).
        self.savedTimespan = None
        # We try loading the state from disk, creating a new, empty state if
        # it fails. No distinction is made between IO exceptions or pickle
        # exceptions.
        # TODO: Make distinction between IO exceptions and pickle exceptions.
        try:
            with open(".chronos", "r") as file:
                self.state = pickle.load(file)
        except:
            self.state = ChronosState()
        # Make sure we aren't mixing months/weeks/days.
        # Ugly, but I could see no better way to write this.
        # TODO: Make me beautiful
        if self.state.month != date.today().month:
            self.state.statsDict["month"].clear()
        if self.state.day != date.today().day:
            self.state.statsDict["today"].clear()
        if self.state.week != date.today().isocalendar()[1]:
            self.state.statsDict["week"].clear()

        # Set the inactivity threshold to the default if it isn't set.
        if "ChronosInactivityThreshold" in vim.vars:
            self.inactivityThreshold = int(
                vim.vars["ChronosInactivityThreshold"])
        else:
            vim.vars["ChronosInactivityThreshold"] = 10 * 60
            self.inactivityThreshold = 10 * 60

    def __del__(self):
        # Store the state when the session ends.
        with open(".chronos", "w") as file:
            pickle.dump(self.state, file)

    def showStats(self):
        """ Creates a scratch buffer and displays the statistics. """

        # TODO: This is really ugly. I'm sure there are better ways of doing
        # this.
        vim.command("vnew")
        vim.current.buffer.options["buftype"] = "nofile"
        vim.current.buffer.options["filetype"] = "chronos"
        vim.command("syntax on")
        curBuf = vim.current.buffer
        del curBuf[:]
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
        """ Start the timer for the current buffer.

        This uses the buffer's name as a key in a dictionary and stores the
        current time, to be used later when the user switches away from the
        buffer to calculate the time that was spent in the buffer.
        """
        curBuf = vim.current.buffer.name
        # We don't want to store information for no-name buffers.
        if not curBuf:
            return
        curTime = datetime.now()

        self.timerDict[curBuf] = curTime

    def stopTimer(self):
        """ Stops the timer and stores time spent in the buffer accordingly.

        When this is called, the start time for when the user switched to the
        current buffer should have been saved. This function calculates the
        difference and adds it to the statistics accordingly for the buffer's
        names extension.
        """
        curBuf = vim.current.buffer.name
        if not curBuf:
            return

        curExt = os.path.splitext(curBuf)[1][1:]
        if not curExt:
            return

        curTime = datetime.now()
        if curBuf not in self.timerDict:
            # This should never really happen, but if it does, we don't care.
            return

        startTime = self.timerDict[curBuf]
        # Make sure we aren't wasting memory.
        del self.timerDict[curBuf]

        elapsed = curTime - startTime
        # Don't add the elapsed time if it's longer than the inactivity
        # threshold.
        # TODO: Add warning back so the user actually knows the threshold was
        # crossed.
        if elapsed.total_seconds() >= self.inactivityThreshold:
            self.savedTimespan = (elapsed, curExt)
        else:
            self.addToStats(curExt, elapsed)

    def addToStats(self, ext, elapsed):
        """ Convenience function for adding timespan to statistics. """
        for when in ["today", "total", "week", "month"]:
            if ext in self.state.statsDict[when]:
                self.state.statsDict[when][ext] += elapsed
            else:
                self.state.statsDict[when][ext] = elapsed

    def addSaved(self):
        """ Add a saved timespan to the stats if the inactivitythreshold. was
        crossed."""
        if self.savedTimespan:
            self.addToStats(self.savedTimespan[1], self.savedTimespan[0])
            print "Added %s to stats for %s" % self.savedTimespan
            self.savedTimespan = None

    def printStatsFor(self, key):
        """ Print stats to current buffer. """
        curBuf = vim.current.buffer
        for (ext, time) in self.state.statsDict[key].iteritems():
            curBuf.append("  %s" % ext)
            curBuf.append("    %s" % formatTimeDelta(time))

    def clearStats(self):
        """ Clear the stats if the user *really* wants to. """
        if self.confirmClear:
            self.state        = ChronosState()
            self.confirmClear = False
            print "All your stats are belong to the void."
        else:
            sys.stderr.write(clearStatsWarning)
            self.confirmClear = True

# Create an instance of Chronos for this session.
chronos = Chronos()
