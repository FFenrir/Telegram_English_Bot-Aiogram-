import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor


from Config import API_TOKEN,app_id,app_key
import requests




logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


#MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    word_id = State()

#Commands

@dp.message_handler(commands=['Start','start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.word_id.set()

    await message.reply("HELLO! I AM YOUR ENGLISH BOT!\n"
                        "\nI can help you studying the English language!\n"
                        "\nJust type a word and you will get everything you need to know about it!\n"
                        "\nWhat word do you want to know about?")


@dp.message_handler(commands=['Word','word'])
async def cmd_start(message: types.Message):

    # Set state
    await Form.word_id.set()

    await message.reply("What word are you looking for?")



@dp.message_handler(state='*', commands='/cancel')
@dp.message_handler(Text(equals='/cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())



@dp.message_handler(state=Form.word_id)
async def process_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['word_id'] = message.text

        language = 'en-gb'
        fields = 'definitions,pronunciations'

        url = 'https://od-api.oxforddictionaries.com:443/api/v2/entries/' + language + '/' + data['word_id'].lower() + '?fields=' + fields

        r = requests.get(url,headers={'app_id':app_id,'app_key':app_key})

        word = r.json()

        # Remove keyboard
        markup = types.ReplyKeyboardRemove()

        # And send message
    
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text(md.bold(data['word_id'],"\n")),
                md.text("Definition: ",md.bold(word['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0].capitalize(),'\n')),
                md.text("Transcription type : ",md.bold(word['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['phoneticNotation']),'\n'),
                md.text("Transcription: ",md.bold(word['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['phoneticSpelling'],'\n')),
                md.text("Pronunciation: ",md.bold(word['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['audioFile']),'\n'),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )    

    # Finish conversation
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)