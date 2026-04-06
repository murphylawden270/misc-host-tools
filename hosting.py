import discord
import random
import io
import re
import os
import webserver

token = os.environ['token']

class Client(discord.Client):
    async def on_ready(self):
        print(f"logged on as {self.user}")

    async def on_message(self, message):
        if message.guild is not None:
            return
        
        if re.search(r'\bschedule\b', message.content, re.IGNORECASE):
            removed_schedule = re.sub(r'\bschedule\b', '', message.content, flags=re.IGNORECASE)


            team_icon_pair = {}

            teams_with_icons = []
            for line in removed_schedule.split("\n"):
                clean = line.strip()
                if clean:
                    teams_with_icons.append(clean)

            if len(teams_with_icons)%2 !=0:
                teams_with_icons.append("Bye")
            
            warn = []
            teams = []
            for i in teams_with_icons:
                if re.search(r':([^:]+):', i, re.IGNORECASE):
                    removed_icon = re.findall(r':[\w-]+:', i, re.IGNORECASE)
                    if len(removed_icon) == 1:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team] = removed_icon[0]
                        teams.append(icon_removed_team)                        
                    elif removed_icon[0] == removed_icon[1]:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team] = removed_icon[0]
                        teams.append(icon_removed_team)
                    elif removed_icon[0] != removed_icon[1]:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team] = ""
                        teams.append(icon_removed_team)
                        warn.append(f'WARNING! Team icon {removed_icon[0]} and {removed_icon[1]} do not match!\nNo icon was be printed for {icon_removed_team}.')
                    else:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team] = ""
                        teams.append(icon_removed_team)
                        warn.append(f'WARNING! More than 2 team icons detected!\nNo icon was be printed for {icon_removed_team}.')                        

            pair = []
            matchup = []
            matchups = []
            reply = []

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
                    zamatchup = f'{team_icon_pair[j[0]]}{j[0]} vs {j[1]}{team_icon_pair[j[1]]}'
                    reply.append(zamatchup)
                reply.append("")
        
            send = "\n".join(reply)
            send_string = io.BytesIO(send.encode("utf-8"))
            schedule = discord.File(fp=send_string, filename='schedule.txt')
            await message.channel.send(file=schedule)
            if warn:
                await message.channel.send("\n".join(warn))


intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

webserver.keep_alive()
client.run(token)
