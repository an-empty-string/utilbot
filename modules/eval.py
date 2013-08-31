__regex__ = "@code (.*)"
__permission__ = "core/eval"
__enabled__ = True
import sys
from io import StringIO


def run(bot, event):
    bugger = StringIO()
    sys.stdout = bugger
    exec(event.match.group(1))
    sys.stdout = sys.__stdout__
    bot.say(event.channel, bugger.getvalue())
