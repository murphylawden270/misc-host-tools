import discord
import random
import io
import re
import os
import webserver
from supabase import create_client
import asyncio

token = os.environ['token']
url = os.environ['url']
key = os.environ['key']

class Client(discord.Client):
    async def on_ready(self):
        print(f"logged on as {self.user}")

    async def on_message(self, message):        
        if message.guild is not None:
            return
        
        if message.author == client.user:
            return
        
        if re.search(r'(?<!\w)@help(?!\w)', message.content, re.IGNORECASE):
            command_1 = '''# 1. Season Schedule (command: @schedule [case-insensitive])
To create season schedule for a team tournament, use @schedule followed by the team names, each in a separate line. Note: This command supports :pokemon: icons; however, you must maintain certain formatting:
* Team :white_check_mark:
* :pokemon: Team :pokemon: | :pokemon:Team:pokemon: :white_check_mark: 
* :pokemon: Team | :pokemon:Team | Team: pokemon: | Team:pokemon: :white_check_mark:
* :pokemon1:Team:pokemon2: | :pokemon1: Team: pokemon2: :x: No icon will be printed for that team.
* :pokemon: icons must not have any space. For Pokemon names with more than one word, use hyphen "-" to separate them. e.g. :urshifu-rapid-strike:
* If a team has three or more icons (presumably accidentally), the first icon is used only if the first two icons are the same.
* Smogon BB code may or may not work.  e.g. of workng BB code: ":salamence-mega:[B] [COLOR=rgb(120, 189, 218)]India[/COLOR][/B]:Salamence-mega:"'''
            
            await message.channel.send(command_1)   

        if re.search(r'(?<!\w)@schedule(?!\w)', message.content, re.IGNORECASE):
            removed_schedule = re.sub(r'(?<!\w)@schedule(?!\w)', '', message.content, flags=re.IGNORECASE)

            if removed_schedule == "":
                await message.channel.send("**Please enter participant!**")
                return

            team_icon_pair = {}

            teams_with_icons = []
            for line in removed_schedule.split("\n"):
                clean = line.strip()
                if clean:
                    teams_with_icons.append(clean)

            if len(teams_with_icons)%2 !=0:
                teams_with_icons.append("Bye")
                team_icon_pair["Bye"] = "" 
            
            warn = []
            teams = []
            for i in teams_with_icons:
                if re.search(r':([^:]+):', i, re.IGNORECASE):
                    removed_icon = re.findall(r':[\w-]+:', i, re.IGNORECASE)         
                    if len(removed_icon) == 1:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team.strip()] = removed_icon[0]
                        teams.append(icon_removed_team.strip())                        
                    elif removed_icon[0].lower() != removed_icon[1].lower():
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team.strip()] = ""
                        teams.append(icon_removed_team.strip())
                        warn.append(f'**WARNING!** Team icon {removed_icon[0]} and {removed_icon[1]} do not match!\nNo icon was printed for {icon_removed_team.strip()}.')
                    elif removed_icon[0].lower() == removed_icon[1].lower() and len(removed_icon) == 2:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team.strip()] = removed_icon[0]
                        teams.append(icon_removed_team.strip())
                    elif removed_icon[0].lower() == removed_icon[1].lower() and len(removed_icon) >= 3:
                        icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                        team_icon_pair[icon_removed_team.strip()] = removed_icon[0]
                        teams.append(icon_removed_team.strip())
                        warn.append(f'**WARNING!** More than two icons detected in {icon_removed_team.strip()}!\nHowever, the first two icons were the same. Therefore, they were used.')        
                else:
                    team_icon_pair[i.strip()] = ""
                    teams.append(i.strip()) 

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

        if re.search(r'(?<!\w)@teams(?!\w)', message.content, re.IGNORECASE):
            header = re.search(r'(?<!\w)@teams(?!\w)(.*)', message.content, re.IGNORECASE)
            if header.group(1).strip() == "":
                await message.channel.send("**Please enter tournament name and number of teams!**")
                return  
            
            values = header.group(1).strip().split(":")
            if len(values)==1:
                if re.search(r'^\d+$', values[0].strip()):
                    await message.channel.send("**Please enter tournament name!**")
                    return                     
                else:
                    await message.channel.send("**Please enter number of teams!**")
                    return         
            elif len(values)==2:
                if re.search(r'^\d+$', values[0].strip()):
                    await message.channel.send("**Invalid Values or Values Swapped! Team name should be first!**")
                    return
                elif not re.search(r'^\d+$', values[1].strip()):
                    await message.channel.send("**Invalid Values or Values Swapped! Number of teams should be second!**")
                    return
                else:
                    tour, team =  values[0].strip(), int(values[1].strip())
                    print(tour,team)
            else:
                await message.channel.send("**Invalid format! Use: `@teams tournament name : number of teams`**")
                return

            removed_teams = re.sub(r'(?<!\w)@teams(?!\w)(.*)', '', message.content, flags=re.IGNORECASE)
            if removed_teams.strip() == "":
                await message.channel.send("**Please enter participant!**")
                return  
            
            lappland = create_client(url, key) 

            deleted_old_teams = lappland.table("teams").delete(
                ).eq("tour", tour).eq("created_by", str(message.author.id))
            try:
                await asyncio.to_thread(deleted_old_teams.execute)
            except Exception as e:
                print(e)
            deleted_old_team_keys = lappland.table("team_keys").delete(
                ).eq("tour", tour).eq("created_by", str(message.author.id))
            try:
                await asyncio.to_thread(deleted_old_team_keys.execute)
            except Exception as e:
                print(e)

            meowone = lappland.table("teams").insert(
                {"tour": tour,
                 "created_by": str(message.author.id),
                 "teams": team
                 })
            try:
                await asyncio.to_thread(meowone.execute)
            except Exception as e:
                print(e)
            
            meowtwo = lappland.table("team_keys").insert(
                {"tour": tour,
                 "created_by": str(message.author.id),
                 "team_keys": team
                 })
            try:
                await asyncio.to_thread(meowtwo.execute)
            except Exception as e:
                print(e)

            tournament_teams = []
            for line in removed_teams.split("\n"):
                clean = line.strip()
                if clean:
                    tournament_teams.append(clean)
            if len(tournament_teams) != team:
                tournament_teams = []
                deleted_teams = lappland.table("teams").delete(
                ).eq("tour", tour).eq("created_by", str(message.author.id)).eq("teams", team)
                try:
                    await asyncio.to_thread(deleted_teams.execute)
                except Exception as e:
                    print(e)
                deleted_team_keys = lappland.table("team_keys").delete(
                ).eq("tour", tour).eq("created_by", str(message.author.id)).eq("team_keys", team)
                try:
                    await asyncio.to_thread(deleted_team_keys.execute)
                except Exception as e:
                    print(e)
                await message.channel.send("**Mismatched team number! Please enter the right number of teams!**")
                return
            
            for f, i in enumerate(tournament_teams, start=1):
                store = i.split(":")
                tm = store[0].strip()
                tg = store[1].strip()
                update_team =  lappland.table("teams").update({
                f"team_{f}": tm
                }).eq("tour", tour).eq("created_by", str(message.author.id)).eq("teams", team)
                try:
                    await asyncio.to_thread(update_team.execute)
                except Exception as e:
                    print(e)
                update_key = lappland.table("team_keys").update({
                f"team_key_{f}": tg
                }).eq("tour", tour).eq("created_by", str(message.author.id)).eq("team_keys", team)
                try:
                    await asyncio.to_thread(update_key.execute)
                except Exception as e:
                    print(e) 
            
            
intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

webserver.keep_alive()
client.run(token)
