from text import *
from datetime import datetime
import tinydb.operations as tdbop
from tinydb import Query


class cmdhandler:
    def __init__(self, level, handler):
        self.level = level
        self.handler = handler

    def handlecmd(self, update, context):
        if self.handler.get_level(update.message.chat.id) == 2 and "/debug" in update.message.text:
            print(update.message)
            update.message.reply_text(update.message)
        elif self.handler.get_level(update.message.chat.id) >= self.level:
            self.callback(update, context)
        elif update.message.text == '/start':
            self.callback(update, context)
        else:
            update.message.reply_text(f"You do not have the required permissions to use this command. If you believe this is an error, please send a fax!")


class start(cmdhandler):
    def callback(self, update, context):
        message = update.message
        if self.handler.get_level(message.chat.id) > 0:
            message.reply_text("You have print access, use /help if you want more info.")
        elif self.handler.get_level(message.chat.id) == 0:
            message.reply_text("I've already requested print access for you, please be patient!")
        else:
            message.reply_text(start_text)
            username = '@' + message.chat.username if message.chat.username is not None else message.chat.first_name
            context.bot.send_message(chat_id=self.handler.cf['admin_id'], text=f"Print request from:\n{message.chat.id}\n{message.chat.username}\nDo you want to accept them?")
            context.bot.send_message(chat_id=self.handler.cf['admin_id'], text=f"/grant {message.chat.id}")
            self.handler.users.insert({"name": f"{message.chat.first_name} {message.chat.last_name}",
                                       "uname": message.chat.username,
                                       "id": message.chat.id,
                                       "added": str(datetime.now()).split('.')[0]+"01:00",
                                       "level": 0,
                                       "messages": 0,
                                       "characters": 0,
                                       "lines": 0,
                                       "images": 0})


class help(cmdhandler):
    def callback(self, update, context):
        update.message.reply_text(help_text)


class info(cmdhandler):
    def callback(self, update, context):
        update.message.reply_text(str(update))

class stats(cmdhandler):
    def callback(self, update, context):
        self.handler.stats(update, context)


class purge(cmdhandler):
    def callback(self, update, context):
        self.handler.purgetable(update, context)


class grant(cmdhandler):
    def callback(self, update, context):
        message = update.message
        user_id = int(message.text.split(" ")[1])
        if self.handler.get_level(user_id) > 0:
            message.reply_text("That user already has print access.")
        else:
            self.handler.users.update(tdbop.set("level", 1), Query().id == user_id)
            context.bot.send_message(chat_id=user_id, text=welcome_text)
            context.bot.send_message(chat_id=self.handler.cf['admin_id'], text=f"Okay, giving user {user_id} print access!")


class revoke(cmdhandler):
    def callback(self, update, context):
        message = update.message
        user_id = int(message.text.split(" ")[1])
        if self.handler.get_level(user_id) > 0:
            message.reply_text("Revoking print access")
            self.handler.users.update(tdbop.set("level", 0), Query().id == user_id)
            context.bot.send_message(chat_id=user_id, text=f"Your print license has been revoked. If you think this was an error, please contact a moderator.")
        elif self.handler.get_level(user_id) == 0:
            message.reply_text("That user does not have print access.")
        else:
            message.reply_text("That user does not exist.")


class sleep(cmdhandler):
    def callback(self, update, context):
        self.handler.gosleep(update, context)


class wake(cmdhandler):
    def callback(self, update, context):
        self.handler.wake(update, context)

class raph(cmdhandler):
    def callback(self, update, context):
        self.handler.message(update, context, raph=True)