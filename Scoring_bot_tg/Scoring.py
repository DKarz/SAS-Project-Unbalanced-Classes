import telebot
import time
import sys
import pickle
import dataframe_image as dfi
import pandas as pd
import lxml
import matplotlib.font_manager
import os
sys.stderr = open(os.devnull, "w")

model = pickle.load(open('pre_trained.pkl', 'rb'))

qs = [
  'What is your age?',
  'How many family members do you have?\n(This includes yourself, your partner and kids)',
  'What is your monthly income?',
  'How many mortgage loans do you currently have?',
  'How many other loans do you currently have?',
  'What is your current total unpaid loan (for all credits)?',
  'Have you ever delayed your loan payment?\nIf more than one applies, you will be able to pick them one-by-one.',
  'What is your desired credit limit?',
  'What is your account balance?'
]

def tryf(x, typ= float):
  try:
    if typ == float:
      return(typ(x))
    else:
      return(typ(float(x)))
  except: return(None)

def verdict(msg, info, last= False):
  try:
    id = msg.chat.id
    
    if not last:
      df = pd.DataFrame({**{'Name': [info[0]], 'Age': [info[1]], 'Family size': [info[2]], 'Income': [info[3]], 'Mortgages': [info[4]],
       'Other loans': [info[5]],'Total loan': info[6]}, **{ (_[4:-7] + 'delay'):info[7][_] for _ in info[7]}, **{'Limit': [info[8]], 'Balance': [info[9]]}}).T
      df.columns = ['']
      dfi.export(df, f'{id}.png', table_conversion = 'matplotlib', max_rows= -1)
      bot.send_photo(id, open(f'{id}.png', 'rb'))
      os.remove(f'{id}.png')
      user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
      user_markup.row('Yes', 'No')
      msg = bot.send_message(id, 'Is everything correct?', reply_markup= user_markup)
      bot.register_next_step_handler(msg, verdict, info, True )
      return
    elif msg.text == 'No':
        end(id, 'Try again')
        return

    #179780428
      
    
    if id not in [179780428, 347044498]: bot.send_message(347044498, f"{msg.chat.last_name} {msg.chat.first_name} (@{msg.chat.username}) used the bot")
    #bot.send_message(id, f'Your answers were: {info}')

    temp = 0
    for i in info[7]:
      if i == 'Yes, 30-59 days overdue': temp += info[7][i]
      elif i == 'Yes, 90+ days overdue': temp += info[7][i] * 3
      else: temp += info[7][i] * 2
    df = pd.DataFrame([[info[9] / info[8], info[1],
                        info[3] / info[2], info[5], info[4], info[6], temp]],
                        columns= ['credit_card_utilization', 'age',
                        'monthly_income', 'credits_loans',
                         'mortgage_loans', 'debt', 'overdue'])

    
    pred = model.predict_proba(df)[0][1]


    
    #df.columns = ['cu', 'age', 'inc', 'loans', 'mort', 'debt', 'overdue']
    #dfi.export(df, f'{id}.png', table_conversion = 'matplotlib', max_rows= -1)
    #bot.send_photo(id, open(f'{id}.png', 'rb'))
    #os.remove(f'{id}.png')


    
    if pred > .75: end(id,
      f'Unfortunately, we will not be able to provide you with credit.')
    else: end(id, f'We will be happy to open your credit card account.')
          
  except Exception as E:
    print(sys._getframe().f_code.co_name, E)
    error(id, f"Verdict fault: {E}")



global bot
telegram_token = '1708078772:AAEdW5N73xq1Bm8ytGfA-4s3bhu23mzW6NI'

bot = telebot.TeleBot(telegram_token)

def abort(msg_id):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Leave loan application')
    bot.send_message(msg_id, "Canceled...", reply_markup=user_markup)

def end(msg_id, txt):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Leave loan application')
    bot.send_message(msg_id, txt, reply_markup=user_markup)

def error(msg_id, err):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Leave loan application')
    bot.send_message(msg_id, f"Error ({err}), aborting...", reply_markup=user_markup)
    
@bot.message_handler(commands=["start"])
def hello(msg):
    end(msg.chat.id, 'Welcome')

@bot.message_handler(content_types=["text"])
def tex(msg):
  try:
    if msg.text == 'Leave loan application':
      info, n = [], 0
      #markup = telebot.types.ReplyKeyboardRemove(selective=False)
      user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
      cancel = telebot.types.KeyboardButton('Cancel')
      user_markup.row(cancel)
      msg = bot.send_message(msg.chat.id, 'What is your name?', reply_markup=user_markup)
      bot.register_next_step_handler(msg, q, n, info)
    else:
      end(msg.chat.id, 'Wrong command, going back to beginning')
  except Exception as E:
    print(sys._getframe().f_code.co_name, E)
    error(msg.chat.id, 'my bad...')

def overdue(msg, n, info, to_ask):
  if msg.text == 'Cancel' or msg.text == '/start':
    abort(msg.chat.id)
    return
  if msg.text == 'No' or len(to_ask) == 0:
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Cancel')
    msg = bot.send_message(msg.chat.id, qs[n], reply_markup= user_markup)
    n += 1
    bot.register_next_step_handler(msg, q, n, info)
    return
  if msg.text in to_ask:
    to_ask.remove(msg.text)
  else:
    msg = bot.send_message(msg.chat.id, 'Wrong command, try again')
    bot.register_next_step_handler(msg, overdue, n, info, to_ask)
    return
    
    
  user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
  user_markup.row('Cancel')
  temp = msg
  msg = bot.send_message(msg.chat.id, 'How many times did that happen?', reply_markup= user_markup)
  bot.register_next_step_handler(msg, get_num, n, info, temp, to_ask)

def get_num(msg, n, info, temp, to_ask):
  if msg.text == 'Cancel' or msg.text == '/start':
    abort(msg.chat.id)
    return
  _ = tryf(msg.text)
  if (_ == None) or (_ < 0):
    if _ == None: msg = bot.send_message(msg.chat.id, 'Your answer should be a real number, try again')
    else:     msg = bot.send_message(msg.chat.id, 'Your answer should be nonnegative, try again')
    bot.register_next_step_handler(msg, get_num, n, info, temp, to_ask)
    return
  msg.text = _
  
  info[n][temp.text] = msg.text
  if len(to_ask) == 0:
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Cancel')
    msg = bot.send_message(msg.chat.id, qs[n], reply_markup= user_markup)
    n += 1
    bot.register_next_step_handler(msg, q, n, info)
    return
  user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
  for i in to_ask:
    user_markup.row(i)
  user_markup.row('No', 'Cancel')
  msg = bot.send_message(msg.chat.id, 'Any more?', reply_markup= user_markup)
  bot.register_next_step_handler(msg, overdue, n, info, to_ask)

def q(msg, n, info):
  try:
    ans = msg.text

    if ans == '/start' or ans == 'Cancel':
      abort(msg.chat.id)
      return

    if n not in [0, 7]:
      if n in [1, 2, 4, 5]: temp = tryf(ans, int)
      else:           temp = tryf(ans) 
      if n == 8 and temp == 0:
        msg = bot.send_message(msg.chat.id, 'Credit limit cannot be 0, try again')
        bot.register_next_step_handler(msg, q, n, info)
        return
      
      if (temp == None) or (temp < 0) or (n in [2, 3] and temp == 0) or (n == 1 and temp < 18):
        if temp == None:                           msg = bot.send_message(msg.chat.id, 'The answer you have provided is not a real number, please, try again')
        elif temp < 0:                             msg = bot.send_message(msg.chat.id, 'The answer to this question cannot be negative, please, try again')
        elif n == 2:                               msg = bot.send_message(msg.chat.id, 'Including yourself...')
        elif n == 1:                               msg = bot.send_message(msg.chat.id, 'You have to be 18 to take loans')
        else:
          end(msg.chat.id, 'Sorry, you can not take loans without any income')
          return
        bot.register_next_step_handler(msg, q, n, info)
        return
      ans = temp

    info.append(ans)
    if n == 8 and (info[3]/2) < ans:
      bot.send_message(msg.chat.id, f'You can not take loans, which exceed 50% of your income, so it will be set to {info[3]/2} instead')
      info[8] = info[3]/2
    
    if n == 0:
      bot.send_message(msg.chat.id, f'Nice to meet you, {info[0]}.\nYou will now be asked a few questions to help our bank decide on you credit, note that all quastions about money imply USD as currency. This will not take long.')
    if n == len(qs):
      verdict(msg, info)
      return
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Cancel')
    if n == 6:
      to_ask = ['Yes, 30-59 days overdue', 'Yes, 60-89 days overdue', 'Yes, 90+ days overdue']
      user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
      for i in to_ask:
        user_markup.row(i)
      user_markup.row('No', 'Cancel')
    msg = bot.send_message(msg.chat.id, qs[n], reply_markup= user_markup)
    n += 1
    if n != 7: bot.register_next_step_handler(msg, q, n, info)
    else:
      info.append({})
      bot.register_next_step_handler(msg, overdue, n, info, to_ask)
      
  except Exception as E:
    print(sys._getframe().f_code.co_name, E)
    error(msg.chat.id, 'phone handling')
  

try:
    bot.polling(none_stop=True, interval=0)
except Exception as E:
    print(E)
    time.sleep(10)
