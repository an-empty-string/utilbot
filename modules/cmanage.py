__regex__ = "@(join|part) (#.*)"
__permission__ = "core/channels"
__enabled__ = True


def run(bot, event):
    if event.match.group(1) == "join":
        bot.join(event.match.group(2))
    else:
        bot.part(event.match.group(2))
