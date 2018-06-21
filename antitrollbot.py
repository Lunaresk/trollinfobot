from telegram import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters)
from telegram.error import (Unauthorized, BadRequest)
from ..errorCallback import error_callback
from . import dbFuncs
from . import helpFuncs
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

ID, ALIAS, REASON, CONFIRM, SEND, CHANGE = range(6)
adminKeyboard = [u'/add Troll hinzufügen', '/remove Troll entfernen', u'/change Trollinfos ändern']
userKeyboard = ['/check Bin ich ein Troll?']
channel = '@ufzfjfhdnfj'

def start(bot, update):
  bot.send_message(chat_id = update.message.chat_id, text = "Willkommen beim deutschen Anti Troll Bot.\nDie aktive Benutzung ist auf wenige, vertrauenswürdige Personen beschränkt. Administratoren von Gruppen können diesen Bot einladen und werden dann gewarnt, wenn ein vermeintlicher Troll die Gruppe betritt.", reply_markup = Keyboard(userKeyboard))
  if update.message.chat_id in dbFuncs.getAdmins():
    bot.send_message(chat_id = update.message.chat_id, text = "Du gehörst zu den Admins des Bots. Ausschließlich Admins haben das Recht, Trolle in die Datenbank einzutragen.", reply_markup = Keyboard(adminKeyboard))

def disclaimer(bot, update):
  bot.send_message(chat_id = update.message.chat_id, text = "Dieser Bot ist zur digitalen Unterstützung des Kanals " + channel + " gedacht. Alle Daten, die beim Bot gespeichert werden, werden auch auf dem Kanal hochgeladen. Diese Daten sind nicht dazu gedacht, verarbeitet oder an Dritte weitergeleitet zu werden. Darüber hinaus werden nur ohnehin öffentliche Informationen abgefragt.\nDer Bot und sein Programmierer übernehmen keine Haftung für die Benutzung des Bots. Die Daten werden weder von dem Programmierer eingegeben, noch kann der Programmierer nachvollziehen, von wem sie eingegeben wurden.")
  bot.send_message(chat_id = update.message.chat_id, text = "Disclaimer Gruppe:\nDiese Gruppe wird durch den @Trollinfobot unterstützt. Durch Beitritt in die Gruppe akzeptieren die Mitglieder, durch starkes, negatives, störendes Auftreten (so genanntes trollen) einen Eintrag in dem Kanal " + channel + " zu riskieren.\nSollte ein schon bekannter Troll die Gruppe betreten, werden die Administratoren der Gruppe privat angeschrieben (sofern möglich) und davor gewarnt.")
  bot.send_message(chat_id = update.message.chat_id, text = "Disclaimer Privat:\nDurch weiteres privates Anschreiben dieser Art stimmst du zu, wissentlich einen Eintrag in dem Kanal " + channel + " zu riskieren. Solltest du dein Verhalten mir gegenüber nicht anpassen, sehe ich mich gezwungen, die Administration des besagten Kanals auf dich aufmerksam zu machen.")

def trollCheck(bot, update):
  bot.send_message(chat_id = update.message.chat_id, text = isTroll(update.message.from_user['id']))
  return USER

def addTroll(bot, update, user_data):
  bot.send_message(chat_id = update.message.chat_id, text = "Ein neuer Troll also. Bitte schick mir seine Telegram ID zur Identifikation (funktioniert nicht immer). Alternativ kannst du auch eine Nachricht von ihm hierher weiterleiten.", reply_markup = ReplyKeyboardRemove())
  return ID

def insertId(bot, update, user_data):
  if update.message.forward_from != None:
    user_data['id'] = update.message.forward_from.id
  else:
    try:
      user_data['id'] = int(update.message.text)
    except ValueError:
      bot.send_message(chat_id = update.message.chat_id, text = "Die ID enthält ungültige Zeichen. Versuch es bitte noch einmal. Zum abbrechen, /cancel eingeben.")
      return ID
  if dbFuncs.isTroll(user_data['id']):
    bot.send_message(chat_id = update.message.chat_id, text = "Dieser User scheint schon in der Datenbank vorhanden zu sein.")
    return cancel(bot, update, user_data)
  try:
    bot.send_message(chat_id = update.message.chat_id, text = helpFuncs.linkUser(user_data['id']) + "\nBitte bestätige: ist das der User, den du meinst?", parse_mode = 'Markdown', reply_markup = yesno())
    return CONFIRM
  except BadRequest:
    bot.send_message(chat_id = update.message.chat_id, text = "Diese User-ID kann ich noch nicht zuordnen. Bitte leite eine Nachricht von ihm weiter oder sorge dafür, dass er in irgendeiner Weise mit mir interagiert, egal ob privat oder in einer Gruppe.")
    return ID

def trollConfirm(bot, update, user_data):
  if update.message.text == 'Ja':
    if 'alias' not in user_data:
      bot.send_message(chat_id = update.message.chat_id, text = "Alles klar. Gib jetzt bitte einen Alias für den Troll ein. Mehrere sind auch möglich, aber nur der Erste wird als Link zu seinem Profil benutzt. Mehrere Aliasse bitte durch Kommas trennen.")
      return ALIAS
    return trolltextConfirm(bot, update.message.chat_id, user_data)
  elif update.message.text == 'Nein':
    bot.send_message(chat_id = update.message.chat_id, text = "Dann versuchen wir es nochmal. Bitte gib eine ID ein oder leite eine Nachricht von ihm weiter.")
    return ID
  bot.send_message(chat_id = update.message. chat_id, text = "Das habe ich nicht verstanden. Bitte antworte mit Ja oder Nein oder sende /cancel um den Vorgang abzubrechen.")
  return CONFIRM

def insertAlias(bot, update, user_data):
  aliases = update.message.text.split(',')
  for i in range(len(aliases)):
    aliases[i] = aliases[i].strip()
  user_data['alias'] = aliases
  if 'reason' not in user_data:
    bot.send_message(chat_id = update.message.chat_id , text = "Verstanden. ID und Alias temporär gespeichert. Gib bitte jetzt den Grund ein, wieso er auf die Troll Liste und in den " + channel + " Channel sollte.")
    return REASON
  return trolltextConfirm(bot, update.message.chat_id, user_data)

def insertReason(bot, update, user_data):
  user_data['reason'] = update.message.text
  return trolltextConfirm(bot, update.message.chat_id, user_data)

def trolltextConfirm(bot, chatId, user_data):
  trolltext = helpFuncs.linkUser(user_data['id'], user_data['alias'][0]) + " (ID: {})".format(user_data['id'])
  if len(user_data['alias']) > 1:
    trolltext += u'\nAuch bekannt als {}'.format(', '.join(user_data['alias'][1:]))
  trolltext += u'\n\nGrund:\n{}'.format(user_data['reason'])
  user_data['trolltext'] = trolltext
  bot.send_message(chat_id = chatId, text = trolltext, parse_mode = 'Markdown')
  bot.send_message(chat_id = chatId, text = "Sind die Informationen so richtig? Kann ich das so in den Kanal posten?\nBitte daran denken! Um sich selbst rechtlich abzusichern, sollte der Troll wenigstens eine Vorwarnung bekommen. Einen netten Text kann man unter /disclaimer erhalten.", reply_markup = yesno())
  return SEND

def saveTroll(bot, update, user_data):
  if update.message.text == 'Ja':
    try:
      channelmsg = bot.send_message(chat_id = channel, text = user_data['trolltext'], parse_mode = 'Markdown').message_id
      dbFuncs.insertTroll(user_data['id'], ','.join(user_data['alias']), user_data['reason'], channelmsg)
      bot.send_message(chat_id = update.message.chat_id, text = "Troll ist in der Datenbank gespeichert und im Channel veröffentlicht. Gute Arbeit.", reply_markup = Keyboard(adminKeyboard))
      user_data.clear()
      return ConversationHandler.END
    except Unauthorized:
      bot.send_message(chat_id = update.message.chat_id, text = "Ich scheine noch keine Berechtigung zu haben, um in den " + channel + " Kanal zu schreiben. Dieses Recht ist notwendig. Die Daten bleiben bis dahin gespeichert, wenn du es erneut versuchen willst, sende einfach wieder 'Ja'.", reply_markup = yesno())
      return SEND
  elif update.message.text == 'Nein':
    bot.send_message(chat_id = update.message.chat_id, text = "Was daran möchtest du nochmal ändern?\nDenk dran, zum abbrechen /cancel eingeben.", reply_markup = Keyboard(['ID', 'Alias', 'Grund']))
    return CHANGE
  bot.send_message(chat_id = update.message. chat_id, text = "Das habe ich nicht verstanden. Bitte antworte mit Ja oder Nein oder sende /cancel um den Vorgang abzubrechen.", reply_markup = yesno())
  return SEND

def changeChoice(bot, update, user_data):
  if update.message.text == "ID":
    bot.send_message(chat_id = update.message.chat_id, text = "Verstanden. Gib bitte jetzt die neue ID ein oder leite eine Nachricht der Person weiter.")
    return ID
  elif update.message.text == "Alias":
    bot.send_message(chat_id = update.message.chat_id, text = "Verstanden. Gib bitte jetzt die neuen Aliases ein. Mehrere Aliases bitte mit einem Komma trennen")
    return ALIAS
  elif update.message.text == "Grund":
    bot.send_message(chat_id = update.message.chat_id, text = "Verstanden. Gib bitte jetzt den neuen Grund ein, weswegen er gemeldet wird.")
    return REASON
  bot.send_message(chat_id = update.message.chat_id, text = "Das habe ich nicht verstanden. Bitte benutze das Keyboard um eine Auswahl zu treffen.")
  return CHANGE

def removeTroll(bot, update, user_data):
  bot.send_message(chat_id = update.message.chat_id, text = "Rehabilitation? Welcher Troll soll von der Liste wieder entfernt werden? Gib dafür die ID des Trolls ein, leite eine Nachricht von ihm oder die entsprechende Nachricht aus dem " + channel + " Kanal hier weiter.")
  return ID

def chooseRemove(bot, update, user_data):
  if update.message.forward_from != None:
    user_data['id'] = update.message.forward_from.id
  elif update.message.forward_from_chat != None:
    for i in update.message.entities:
      if i.user != None:
        user_data['id'] = i.user['id']
        break
    if 'id' not in user_data:
      bot.send_message(chat_id = update.message.chat_id, text = "Ich konnte die Entität des Users nicht feststellen. Bitte beachte, dass ich nur User entfernen kann, die ich auch hinzugefügt habe. Bitte versuch es nochmal.")
  else:
    try:
      user_data['id'] = int(update.message.text)
    except ValueError:
      bot.send_message(chat_id = update.message.chat_id, text = "Die ID enthält ungültige Zeichen. Versuch es bitte noch einmal. Zum abbrechen, /cancel eingeben.")
      return ID
  if not dbFuncs.isTroll(user_data['id']):
    bot.send_message(chat_id = update.message.chat_id, text = "Der User, den ich entfernen soll, ist bei mir nicht als Troll abgespeichert. Wenn das ein unerwartetes Verhalten ist, schreibe bitte den Programmierer an oder versuch es noch einmal.", reply_markup = Keyboard(adminKeyboard))
    return cancel(bot, update, user_data)
  bot.send_message(chat_id = update.message.chat_id, text = u"{}\nIst das der User, den ich entfernen soll?".format(helpFuncs.linkUser(user_data['id'])), parse_mode = 'Markdown', reply_markup = yesno())
  return CONFIRM

def confirmRemoval(bot, update, user_data):
  if update.message.text == 'Ja':
    channelmsg = dbFuncs.getMessageFromId(user_data['id'])
    try:
      bot.delete_message(chat_id = channel, message_id = channelmsg)
      dbFuncs.removeTroll(user_data['id'])
      bot.send_message(chat_id = update.message.chat_id, text = "Troll erfolgreich entfernt.", reply_markup = Keyboard(adminKeyboard))
      user_data.clear()
      return ConversationHandler.END
    except Unauthorized:
      bot.send_message(chat_id = update.message.chat_id, text = "Ich scheine nicht die nötigen Rechte zu haben. Bitte füge mich als Administrator in den Channel hinzu und sende erneut 'Ja'.")
  elif update.message.text == 'Nein':
    bot.send_message(chat_id = update.message.chat_id, text = "Dann versuchen wir es noch einmal. Sende mir bitte die ID des Trolls, den ich entfernen soll, leite eine Nachricht von ihm weiter oder eine Nachricht des Channels, in dem ich ihn gepostet habe.")
    return ID
  else:
    bot.send_message(chat_id = update.message.chat_id, text = "Das habe ich nicht verstanden. Bitte sende 'Ja' oder 'Nein'.")
  return CONFIRM

def changeTroll(bot, update, user_data):
  bot.send_message(chat_id = update.message.chat_id, text = "Die Informationen welches Trolls sollen geändert werden? Schick mir seine ID, eine Nachricht von ihm oder die Nachricht aus dem Channel " + channel + ", in der er erwähnt wird.")
  return ID

def confirmChangeTroll(bot, update, user_data):
  if update.message.forward_from != None:
    user_data['id'] = update.message.forward_from.id
  elif update.message.forward_from_chat != None:
    for i in update.message.entities:
      if i.user != None:
        user_data['id'] = i.user['id']
        break
    if 'id' not in user_data:
      bot.send_message(chat_id = update.message.chat_id, text = "Ich konnte die Entität des Users nicht feststellen. Bitte beachte, dass ich nur User entfernen kann, die ich auch hinzugefügt habe. Bitte versuch es nochmal.")
  else:
    try:
      user_data['id'] = int(update.message.text)
    except ValueError:
      bot.send_message(chat_id = update.message.chat_id, text = "Die ID enthält ungültige Zeichen. Versuch es bitte noch einmal. Zum abbrechen, /cancel eingeben.")
      return ID
  if not dbFuncs.isTroll(user_data['id']):
    bot.send_message(chat_id = update.message.chat_id, text = u"Der User, dessen Informationen ich ändern soll, ist bei mir nicht als Troll abgespeichert. Wenn das ein unerwartetes Verhalten ist, schreibe bitte den Programmierer an oder versuch es noch einmal.", reply_markup = Keyboard(adminKeyboard))
    return cancel(bot, update, user_data)
  else:
    bot.send_message(chat_id = update.message.chat_id, text = dbFuncs.getTroll(user_data['id']))
    user_data['alias'], user_data['reason'], user_data['channelmsg'] = dbFuncs.getTroll(user_data['id'])
    user_data['alias'] = user_data['alias'].split(',')
    bot.send_message(chat_id = update.message.chat_id, text = user_data['alias'])
    bot.send_message(chat_id = update.message.chat_id, text = "Was möchtest du bei diesem Troll ändern?\nDenk dran, zum abbrechen /cancel eingeben.", reply_markup = Keyboard(['Alias', 'Grund']))
    return CHANGE

#TODO
def saveChanges(bot, update, user_data):
  if update.message.text == 'Ja':
    try:
      bot.edit_message_text(chat_id = channel, message_id=user_data['channelmsg'], text = user_data['trolltext'], parse_mode = 'Markdown')
      dbFuncs.updateTroll(user_data['id'], ','.join(user_data['alias']), user_data['reason'])
      bot.send_message(chat_id = update.message.chat_id, text = "Die Informationen wurden aktualisiert. Gute Arbeit.", reply_markup = Keyboard(adminKeyboard))
      user_data.clear()
      return ConversationHandler.END
    except Unauthorized:
      bot.send_message(chat_id = update.message.chat_id, text = "Ich scheine noch keine Berechtigung zu haben, um in den " + channel + " Kanal zu schreiben. Dieses Recht ist notwendig. Die Daten bleiben bis dahin gespeichert, wenn du es erneut versuchen willst, sende einfach wieder 'Ja'.", reply_markup = yesno())
      return SEND
  elif update.message.text == 'Nein':
    bot.send_message(chat_id = update.message.chat_id, text = "Was daran möchtest du nochmal ändern?\nDenk dran, zum abbrechen /cancel eingeben.", reply_markup = Keyboard(['Alias', 'Grund']))
    return CHANGE
  bot.send_message(chat_id = update.message. chat_id, text = "Das habe ich nicht verstanden. Bitte antworte mit Ja oder Nein oder sende /cancel um den Vorgang abzubrechen.", reply_markup = yesno())
  return SEND
#TODO

def cancel(bot, update, user_data):
  user_data.clear()
  bot.send_message(chat_id = update.message.chat_id, text = "Aktion abgebrochen. Alle zwischengespeicherten Daten wurden gelöscht.", reply_markup = Keyboard(adminKeyboard))
  return ConversationHandler.END

def Keyboard(keylist):
  keyboard = []
  for i in keylist:
    keyboard.append([KeyboardButton(i)])
  reply_markup = ReplyKeyboardMarkup(keyboard, True, True)
  return reply_markup

def yesno():
  keyboard = [[KeyboardButton('Ja'), KeyboardButton('Nein')]]
  reply = ReplyKeyboardMarkup(keyboard, True, True)
  return reply

def main(updater):
  dispatcher = updater.dispatcher
  dbFuncs.initDB()

  addingTroll = ConversationHandler(
    entry_points = [CommandHandler('add', addTroll, filters = Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), pass_user_data = True)],
    states = {
      ID: [MessageHandler(Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins())&(Filters.text | Filters.forwarded), insertId, pass_user_data = True)],
      CONFIRM: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), trollConfirm, pass_user_data = True)],
      ALIAS: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), insertAlias, pass_user_data = True)],
      REASON: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), insertReason, pass_user_data = True)],
      SEND: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), saveTroll, pass_user_data = True)],
      CHANGE: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), changeChoice, pass_user_data = True)],
    },
    fallbacks = [CommandHandler('cancel', cancel, Filters.private, pass_user_data = True)]
  )

  removingTroll = ConversationHandler(
    entry_points = [CommandHandler('remove', removeTroll, filters = Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), pass_user_data = True)],
    states = {
      ID: [MessageHandler(Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins())&(Filters.text | Filters.forwarded), chooseRemove, pass_user_data = True)],
      CONFIRM: [MessageHandler(Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), confirmRemoval, pass_user_data = True)]
    },
    fallbacks = [CommandHandler('cancel', cancel, Filters.private, pass_user_data = True)]
  )

  changingTroll = ConversationHandler(
    entry_points = [CommandHandler('change', changeTroll, filters = Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), pass_user_data = True)],
    states = {
      ID: [MessageHandler(Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins())&(Filters.text | Filters.forwarded), confirmChangeTroll, pass_user_data = True)],
      CHANGE: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), changeChoice, pass_user_data = True)],
      ALIAS: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), insertAlias, pass_user_data = True)],
      REASON: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), insertReason, pass_user_data = True)],
      SEND: [MessageHandler(Filters.text&Filters.private&Filters.chat(chat_id = dbFuncs.getAdmins()), saveChanges, pass_user_data = True)]
    },
    fallbacks = [CommandHandler('cancel', cancel, Filters.private, pass_user_data = True)]
  )

  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(addingTroll)
  dispatcher.add_handler(removingTroll)
  dispatcher.add_handler(changingTroll)
  dispatcher.add_handler(CommandHandler('disclaimer', disclaimer))
  dispatcher.add_error_handler(error_callback)

  updater.start_polling()

  updater.idle()

  updater.stop()


if __name__ == '__main__':
  from ..bottoken import getToken
  main(getToken('antitrollbot'))
