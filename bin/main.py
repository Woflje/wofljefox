
cffile = "config.json"
dbfile = "printerdb.json"

from telegram.ext import *
import ujson
from tinydb import TinyDB

import commands as cmd
import callbacks as cbs

cf = ujson.load(open(cffile, "r"))
db = TinyDB(dbfile)



#           Command      Function     Level
commands = {"start":    (cmd.start,     0),
            "help":     (cmd.help,      0),
            "info":     (cmd.info,      0),
            "stats":    (cmd.stats,     1),
            "raph":     (cmd.raph,      1),
            "trello":   (cmd.trello,    2),
            "purge":    (cmd.purge,     2),
            "grant":    (cmd.grant,     2),
            "revoke":   (cmd.revoke,    2),
            "sleep":    (cmd.sleep,     2),
            "wake":     (cmd.wake,      2)}



if __name__ == '__main__':
    ud = Updater(cf['token'])
    dp = ud.dispatcher

    mhandler = cbs.handler(cf, db)

    filters = [Filters.text, Filters.document, Filters.photo, Filters.sticker]

    for command, (handler, level) in commands.items():
        dp.add_handler(CommandHandler(command, handler(level, mhandler).handlecmd))

    for filter in filters:
        dp.add_handler(MessageHandler(filter, mhandler.message))

    ud.start_polling(1)
    ud.idle()
