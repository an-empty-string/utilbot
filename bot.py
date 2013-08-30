from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import argparse
import importlib
import json
import os
import time
import re
import sys


class BotPermissions:
    def __init__(self, permfile):
        self.perms = json.loads(open(permfile).read())
        self.permfile = permfile

    def save(self):
        f = open(self.permfile, "w")
        f.write(json.dumps(self.perms))
        f.close()

    def has_perm(self, perm, userhost):
        for i in self.perms:
            uhtest = i.replace("*", ".*").replace("?", ".")
            if re.match(uhtest, userhost):  # Check for nick!user@host
                for j in self.perms[i]:
                    if re.match(j, perm):
                        return True
        return False

    def add_perm(self, perm, userhost):
        if userhost not in self.perms:
            self.perms[userhost] = []
        if perm not in self.perms[userhost]:
            self.perms[userhost].append(perm)
        self.save()

    def rm_perm(self, perm, userhost):
        if userhost in self.perms and perm in self.perms[userhost]:
            del self.perms[userhost][perm]
        self.save()


class BotConfig:
    def __init__(self, conffile):
        self.__dict__["conf"] = json.loads(open(conffile).read())
        self.__dict__["conffile"] = conffile

    def __getattr__(self, attr):
        return self.__dict__["conf"][attr]

    def __setattr__(self, attr, value):
        self.__dict__["conf"][attr] = value
        cfile = open(self.__dict__["conffile"], "w")
        cfile.write(json.dumps(self.__dict__["conf"]))


class EventLogger:
    def __init__(self, conf):
        self.handle = open(conf.logfile, "a")

    def log(self, thing):
        self.handle.write("{0} {1}\n".format(thing,
                                             time.asctime(time.localtime(
                                                          time.time()))))


class MessageEvent:
    def __init__(self, user, channel, message, match=None):
        self.user = user
        self.channel = channel
        self.message = message
        self.match = match


class UtilBot(irc.IRCClient):
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.factory.logger.log("[connected to server]")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.factory.logger.log("[disconnected from server ({0})]".
                                format(reason))

    def signedOn(self):
        self.setNick(str(self.factory.config.nick))
        for channel in self.factory.config.default_channels:
            self.join(str(channel))

    def joined(self, channel):
        self.factory.logger.log("Joined channel {0}".format(channel))

    def privmsg(self, user, channel, msg):
        self.factory.logger.log("<{0}> {1}".format(user, msg))
        for i in self.modules:
            match = re.match(self.modules[i].__regex__, msg)
            if match:
                if self.perms.has_perm(self.modules[i].__permission__, user):
                    event = MessageEvent(user, channel, msg, match)
                    self.modules[i].run(self, event)
                else:
                    self.say(channel, "You do not have permission to perform \
this action.")


class UtilBotFactory(protocol.ClientFactory):
    def __init__(self, config):
        self.config = config
        self.permissions = BotPermissions(self.config.permfile)
        self.logger = EventLogger(self.config)

    def buildProtocol(self, addr):
        protocol = UtilBot()
        protocol.factory = self
        protocol.modules = self.load_modules()
        protocol.config = self.config
        protocol.logger = self.logger
        protocol.perms = self.permissions
        return protocol

    def load_modules(self):
        modlist = os.listdir("modules")
        modlist = ["modules.%s" % (i[:-3]) for i in modlist
                   if i.endswith(".py")]
        mods = {i: importlib.import_module(i) for i in modlist}
        mods = {i: mods[i] for i in mods if mods[i].__enabled__}

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        self.logger.log("[connection failed ({0})]".format(reason))
        reactor.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config",
                        help="specify the location of the bot config file")
    args = parser.parse_args()
    config = BotConfig(args.config)
    log.startLogging(sys.stdout)
    factory = UtilBotFactory(config)
    factory.logger.log("[connecting to {0}:{1}]".
                       format(config.host, config.port))
    reactor.connectTCP(config.host, config.port, factory)
    reactor.run()
