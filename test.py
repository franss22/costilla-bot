import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

client = MyClient()
client.run('ODQyOTMyNjEzMjc0MTQwNzQ0.YJ8gKw.iM8SEbSSy22PW5KBKTN9EPmoFMU')