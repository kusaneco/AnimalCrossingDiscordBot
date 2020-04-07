import discord
import configparser
import textwrap
from datetime import date, datetime, timedelta
from redis_repository import RedisRepository

# load bot settings
config = configparser.ConfigParser()
config.read('discord_bot.conf')
TOKEN = config['discord']['token']

client = discord.Client()
repository = RedisRepository()

@client.event
async def on_message(message):

    if message.author.bot:
        return

    split_message = message.content.split(' ')
    command = split_message[0]

    # 後々コマンドクラスを作っていこう……
    # カブコマンド
    if command == '/kabu':

        async def help_kabu(message):
            # ヘルプを表示する
            reply_message = f'{message.author.mention} カブ価を記録するときは以下のように打ってちょうだいね'
            reply_message += textwrap.dedent("""
                ```
                今のカブ価を記録したい：/kabu {カブ価}
                特定日時のカブ価を記録したい：/kabu YYYY-mm-dd {am or pm} {カブ価}
                今週のカブ価のログを見たい：/kabu log
                ```
                """)
            await message.channel.send(reply_message)

        try:
            # /kabu {カブ価}
            if len(split_message) == 2 and split_message[1].isdecimal():
                price = int(split_message[1])
                # redis 記録処理
                # now の場合は日付や午前午後も自動で取得する
                key = f'{message.author}_{datetime.now().strftime("%Y-%m-%d_%p")}'
                repository.set(key, price)
                reply_message = f'{message.author.mention} さんの今のカブ価は {price} ね。記録しておくだなも'
                await message.channel.send(reply_message)
            # /kabu log
            elif len(split_message) == 2 and split_message[1] == 'log':
                reply_message = f'{message.author.mention} さんの今週のカブ価のログはこんな感じだなも```'
                today = date.today()
                start_date = today - timedelta(days=today.weekday()) # 月曜日始まり

                tmp_message_list = []
                for i in range(6):
                    check_date = start_date + timedelta(days=i)
                    key = f'{message.author}_{check_date}'
                    for suffix in ['AM', 'PM']:
                        price = repository.get(f'{key}_{suffix}')
                        if price is None:
                            price = '未集計'
                        tmp_message_list.append(f'{check_date} ({suffix}): {price}')
                reply_message += '\n'.join(tmp_message_list)

                reply_message += '```'

                await message.channel.send(reply_message)
            # /kabu help
            elif len(split_message) == 2 and split_message[1] == 'help':
                await help_kabu(message)
            else:
                raise ValueError
        except ValueError:
            await help_kabu(message)

client.run(TOKEN)