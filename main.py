import asyncio
from aiogram import Bot, Dispatcher, F #F is a filtering events
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

bot = Bot(token='8193806907:AAFO_VnhDBIpeY3a18SOL5-rMPPcBUsv5I8')
dp = Dispatcher() 

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello! I am a CineBob!')
    await message.reply(" I can help you to find a movie to watch.")

@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('How can I help you?')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')

