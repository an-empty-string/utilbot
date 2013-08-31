__regex__ = "@perms? (set|unset) (.*) (.*)"
__permission__ = "core/permissions"
__enabled__ = True


def run(bot, event):
    if event.match.group(1) == "set":
        if bot.perms.has_perm("core/permissions/set", event.user):
            bot.perms.add_perm(event.match.group(3), event.match.group(2))
            bot.say(event.channel, "Permissions set.")
        else:
            bot.say(event.channel,
                    "You do not have permission to add a permission.")
    else:
        if bot.perms.has_perm("core/permissions/unset", event.user):
            bot.perms.rm_perm(event.match.group(3), event.match.group(2))
            bot.say(event.channel, "Permissions set.")
        else:
            bot.say(event.channel,
                    "You do not have permission to delete a permission.")
