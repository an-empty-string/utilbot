__regex__ = "@help"
__permission__ = "core/help"
__enabled__ = True


def run(bot, event):
    modules = {i.replace("modules.", ""): bot.modules[i] for i in bot.modules}
    helptext = "Modules available: "
    for i in modules:
        helptext = "%s (permission: %s, trigger: %s)" % (i, modules[i].__permission__, modules[i].__regex__)
        bot.msg(event.user.split("!")[0], helptext)
