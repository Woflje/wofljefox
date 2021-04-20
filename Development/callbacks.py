from escpos.printer import Serial
from tinydb import Query
from datetime import datetime
import tinydb.operations as tdbop
from escpos import *
from PIL import Image
from time import sleep
from emoji import demojize
import pytz

from text import *


class printer:
    def __init__(self, config, queue, db):
        self.cf = config
        self.queue = queue
        self.db = db
        self.p = Serial(devfile=self.cf['port'], baudrate=self.cf['baud'])


    def doeprinten(self, context):

        # Voor alle items in queue, check voor text, qr codes, image
        for item in self.queue:
            if item['printed'] is False:

                # Check if the message has at least some data. It should, but you never know.
                if item['text'] or item['urls'] or item['image']:
                    if item['level'] < 2:
                        self.p.text(f"Name: {item['name']}\nID:   {item['id']}\nDate: {item['date'].split('+')[0]}\n\n")
                    context.bot.send_message(chat_id=item['id'], text=printing_text)

                    # Print text if text exists
                    if item['text']:
                        self.p.text(f"{item['text']}\n\n")

                    # Print URLs if URLs exist
                    if item['urls']:
                        for url in item['urls']:
                            self.p.text(f"URL: {url}\n")
                            self.p.qr(url)

                    # Print image if image exists
                    if item['image']:
                        self.p.image(item['image'])

                    # Cut if auto_cut is enabled
                    if self.cf['auto_cut']:
                        self.p.cut()

                    # Update queue
                    self.queue.update(tdbop.set("printed", True), Query().date == item['date'])

                    # If an image was printed, give the printer two seconds to cool down
                    if item['image']:
                        sleep(2)

        # After queue is empty, remove queue
        self.db.drop_table('queue')

class handler:
    def __init__(self, config, db):
        self.cf = config
        self.db = db
        self.sleep = False

        self.queue = self.db.table("queue")
        self.users = db.table("users")
        self.printunit = printer(self.cf,
                                 self.queue, self.db)

        # If the "users" document does not exist, create it and add the admin account
        if not "users" in db.tables():
            self.users.insert({"name": "admin",
                               "uname": "admin",
                               "id": self.cf["admin_id"],
                               "added": str(datetime.utcnow().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Europe/Amsterdam"))).split('.')[0],
                               "level": 2,
                               "messages": 0,
                               "characters": 0,
                               "images": 0})


    def get_level(self, id):
        result = self.users.search(Query().id == id)
        if result != []:
            level = result[0]['level']
        else:
            level = -1
        return level


    def message(self, update, context):
        message = update.message
        date = message.date
        level = self.get_level(message.chat.id)

    # LEVEL check
        if level <1:
            message.reply_text(no_print_access)
        else:
            text = message.text
            image = None
            imageFile = None
            urls = []
            self.users.update(tdbop.increment("messages"), Query().id == message.chat.id)

            if text is not None:
                text = demojize(text)
                newchars = self.users.search(Query().id == message.chat.id)[0]['characters'] + len(text)
                self.users.update(tdbop.set("characters", newchars), Query().id == message.chat.id)

                # Check for URLs or haikus, if URL set urls var, if haiku change text to be made up properly
                urls = self.findurls(text, urls)
                text = self.haiku(text)

    # IMAGE check + processing
            # DOCUMENT check
            if message.document is not None:
                imageFile = context.bot.get_file(message.document.file_id)

            # STICKER check
            elif message.sticker is not None:
                if message.sticker.is_animated:
                    message.reply_text("Sorry, I can't print animated stickers at the moment :c")
                else:
                    imageFile = context.bot.get_file(message.sticker.file_id)

            # PHOTO check
            elif message.photo:
                imageFile = context.bot.get_file(message.photo[-1].file_id)

            # Only process and add image if an image exists
            if imageFile is not None:
                self.users.update(tdbop.increment("images"), Query().id == message.chat.id)
                image = imageFile.download(custom_path=f"./imgcache/{imageFile.file_id}.{imageFile.file_path.split('.')[-1]}")
                img = Image.open(image)
                img = img.convert('RGBA')
                tempimg = Image.new('RGBA', img.size, "WHITE")
                tempimg.paste(img, (0,0), img)
                img = tempimg.convert('RGB')
                if img.size[0] > img.size[1] and img.size[0] < 3 * img.size[1] or img.size[1] > 3 * img.size[0]:
                    img = img.rotate(angle=90, expand=True)
                img = img.resize((self.cf['max_width'], int(img.size[1] * self.cf['max_width']/img.size[0])))
                img.save(f"./imgcache/{imageFile.file_unique_id}.jpeg", 'JPEG')
                image = f"./imgcache/{imageFile.file_unique_id}.jpeg"

    # QUEUE updating
            # Add gathered data to queue, if no text/urls/image, Null will be inserted into the respective entry
            if message.chat.last_name != None:
                name = f"{message.chat.first_name} {message.chat.last_name}"
            else:
                name = message.chat.first_name
            self.queue.insert({"name": name,
                               "id": message.chat.id,
                               "level": level,
                               "date": str(date.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Europe/Amsterdam"))),
                               "text": text,
                               "image": image,
                               "urls": urls,
                               "printed": False})
            if self.sleep:
                message.reply_text(f"Hey, I'm sleeping right now, I will print your message when I wake up again!")
            else:
                self.printunit.doeprinten(context)


    def findurls(self, text, urls):

        for start_tag in self.cf['url_start_tags']:
            if start_tag in text:
                start_index = text.find(start_tag)

                if start_index > -1:
                    newtext = text[start_index : len(text)]
                    term = len(newtext)

                    for end_tag in self.cf['url_end_tags']:
                        end_index = newtext[1:len(newtext)].find(end_tag)
                        if end_index == -1:
                            end_index = len(newtext)
                        term = min(term, end_index+1)

                    url = newtext[0:term]
                    if url not in urls:
                        urls.append(url)
                    self.findurls(newtext[term:len(newtext)], urls)
        return urls


    def haiku(self, text):
        return text


    def stats(self, update, context):
        message = update.message
        msgs = self.users.search(Query().id == message.chat.id)[0]['messages']
        chars = self.users.search(Query().id == message.chat.id)[0]['characters']
        imgs = self.users.search(Query().id == message.chat.id)[0]['images']
        time = self.users.search(Query().id == message.chat.id)[0]['added'].split(" ")[0]
        date = self.users.search(Query().id == message.chat.id)[0]['added'].split(" ")[1].split(".")[0]
        message.reply_text(f"You have sent:\n- {msgs} messages\n- {chars} characters\n- {imgs} images\nsince {date}, {time}")


    def purgetable(self, update, context):
        context.bot.send_message(chat_id=self.cf['admin_id'], text=f"Emptying queue...")
        self.db.drop_table('queue')


    def gosleep(self, update, context):
        context.bot.send_message(chat_id=self.cf['admin_id'], text=f"Sleeping...")
        self.sleep = True


    def wake(self, update, context):
        context.bot.send_message(chat_id=self.cf['admin_id'], text=f"Good morning!")
        self.sleep = False
        self.printunit.doeprinten(context)
