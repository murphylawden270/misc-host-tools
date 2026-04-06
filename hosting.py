import discord
from discord.ext import commands
import random
import io
import re
import os
import webserver

token = os.environ('token')

user_greeting_count = {}
class Client(commands.Bot):
    async def on_ready(self):
        print(f"logged on as {self.user}")

    async def on_message(self, message):
        if message.guild is not None:
            return
        
        if re.search(r'\bschedule\b', message.content, re.IGNORECASE):
            removed_schedule = re.sub(r'\bschedule\b', '', message.content, flags=re.IGNORECASE)
            teams = [t.strip() for t in removed_schedule.split("\n") if t.strip()]
            pair = []
            matchup = []
            matchups = []
            reply = []

            if len(teams)%2 !=0:
                teams.append("Bye")

            random.shuffle(teams)

            for j in range(0,len(teams)-1):
                for l in range(len(teams)//2):
                    pair.append(teams[l])
                    pair.append(teams[len(teams)-l-1])
                    random.shuffle(pair)
                    matchup.append(pair)
                    pair = []
                matchups.append(matchup)
                matchup = []
                move = teams[len(teams)-1]
                for i in range(len(teams)-1,0,-1):
                    teams[i] = teams[i-1]
                teams[i] = move
                
            random.shuffle(matchups)

            for week, i in enumerate(matchups, start=1):
                zaweek = f'Week {week}'
                reply.append(zaweek)
                for j in i:
                    zamatchup = f'{j[0]} vs {j[1]}'
                    reply.append(zamatchup)
                reply.append("")
        
            send = "\n".join(reply)
            send_string = io.BytesIO(send.encode("utf-8"))
            schedule = discord.File(fp=send_string, filename='schedule.txt')
            await message.channel.send(file=schedule)

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

webserver.keep_alive()
client.run(token)