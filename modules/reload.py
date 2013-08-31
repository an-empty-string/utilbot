import importlib
import json
import os

__regex__ = "@reload"
__permission__ = "core/reload"
__enabled__ = True


def run(bot, event):
    modlist = os.listdir("modules")
    modlist = ["modules.%s" % (i[:-3]) for i in modlist if i.endswith(".py")]
    mods = {}
    for i in modlist:
        if i in bot.modules:
            mods[i] = reload(bot.modules[i])
        else:
            mods[i] = importlib.import_module(i)
    mods = {i: mods[i] for i in mods if mods[i].__enabled__}
    bot.modules = mods
    bot.perms.perms = json.loads(open(bot.perms.permfile).read())
    bot.say(event.channel, "Permissions and modules reloaded.")
