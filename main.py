import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import asyncio
from utils import init_db, add_entry, get_random, get_by_link, delete_entry, get_by_entry, delete_db, idx2week, week2idx
from datetime import datetime
from zoneinfo import ZoneInfo

init_db()
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
time = 3 * 24
CHANNEL = 1428598017656619100 # general chat
ECHANNEL = 1434310637936447488 # eboard general chat
ANNOUNCE = 1434239578457509958 # announcement chat
EANNOUNCE = 1434589025158824130 # eboard announcement chat
ME = 699427677383294986 # Nick T. user ID
online = False
task_day = 2
task_hour = 17
task_minute = 0

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.polls = True
intents.bans = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    if not send.is_running():
        send.start()
    if not task_scheduler.is_running():
        task_scheduler.start()

@bot.event
async def on_member_join(member):
    pass

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.command()
@commands.has_role("E-Board")
async def add(ctx, *, message):
    message = [m.strip() for m in message.split(',')]
    content = message[0]
    category = message[1].lower()
    author_id = ctx.author.id
    if len(message) > 2:
        link = message[2]
    else:
        link = None
    confirm = f"CONFIRM: You are adding `{content}` as `{category}`"
    entry = get_by_entry(content)
    # dblink = get_by_link(link) // Obsolete --> Allowing multiple entries with same link
    if entry:
        await ctx.send(f"{content} already exists")
        return
    if link:
        confirm += f" with link {link}"
    confirm += "? `[yes/no]`"
    await ctx.send(confirm)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower().strip() in ["yes", "no"]
    try:
        response = await bot.wait_for("message", check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. Entry not added.")
        return
    if response.content.lower() == "yes":
        add_entry(content, category, author_id, link)
        await ctx.send("Entry added")
    else:
        await ctx.send("Entry cancelled.")

@bot.command()
@commands.has_role("E-Board")
async def pull(ctx):
    await ctx.message.delete()
    content = get_random()
    if content:
        category = content['category']
        if category != 'discussion' and category != 'trivia':
            category = category.capitalize()
            category += ' discussion'
        else:
            category = category.capitalize()
        message = f"**{category}:** {content['content']}"
        if content['link']:
            message += f" {content['link']}"
        await ctx.send(message)
    else:
        await ctx.send("Database empty")

@tasks.loop(hours=time)
async def send():
    channel = bot.get_channel(CHANNEL)
    if channel and online:
        content = get_random()
        if content:
            msg = f"**{content['category'].capitalize()} discussion:** {content['content']}"
            if content['link']:
                msg += f" {content['link']}"
            await channel.send(msg)

@bot.command()
@commands.has_role("E-Board")
async def set_interval(ctx, *, message):
    try:
        days = float(message)
    except ValueError:
        await ctx.send("Please specify an integer timeframe in days. For example, !set 3")
        return
    global time
    time = days * 24
    send.change_interval(hours=time)
    await ctx.send(f"Interval has been updated to {time / 24} day(s)")


@bot.command()
@commands.has_role("E-Board")
async def help(ctx):
    global task_minute
    global time
    global task_hour
    global task_day
    minute_message = str(task_minute)
    if task_minute < 10:
        minute_message = "0" + minute_message
    await ctx.send(
f'''I will randomly select an entry every {time / 24} day(s) to stimulate discussion. Please use !set_interval to update this interval. Use !get_interval to see the currently set interval.

Use !add [content], [category], [optional link] to add to the database.
    *Content*: The actual ride name, trivia fact, manufacturer, ride element, etc.
    *Category*: Any of the following: park, manufacturer, ride, element, model, trivia, or discussion. Do not diverge from this list.
    *Link*: Optional link, but extremely recommended. Use RCDB.com for links.

Use !delete [content] to remove an entry if there is a duplicate for example. Spelling must be exact. Use !wipe to delete the entire database. This CANNOT be undone!

Use !pull to force pull an entry. This should typcially only be used for testing or for manually changing the discussion early. The original !pull message will be deleted to hide this.

Use !task to announce incomplete E-Board tasks. This command will automatically be called every {idx2week[task_day]} at {task_hour}:{minute_message}. Use !set_task_time [day] [24-hour time] to change weekly reminders. Use !get_task_time to see what it is currently set to.

Use !disable to turn off random selection. Every other bot feature will still be available. Use !enable to turn it back on, and !status to see current status.

Only members with the E-Board flair will be able to use any of the bot commands, including !help
''')

@bot.command()
@commands.has_role("E-Board")
async def delete(ctx, *, message):
    message = message.strip()
    content = get_by_entry(message, True)
    if not content:
        await ctx.send(f"`{message}` does not exist in the database.")
        return
    confirmation_message = f"`{content['content']}`, `{content['category']}`"
    if(content['link']):
        confirmation_message += f", {content['link']}"
    await ctx.send(f"CONFIRM: You are deleting {confirmation_message}. This cannot be undone `[yes/no]`")
    def check(m):
        return (
            m.author == ctx.author
            and m.channel == ctx.channel
            and m.content.lower().strip() in ["yes", "no"]
        )
    try:
        response = await bot.wait_for("message", check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. Entry not deleted.")
        return
    if response.content.lower() == "yes":
        delete_entry(message)
        await ctx.send(f"`{content['content']}` has been deleted.")
    else:
        await ctx.send("Deletion cancelled.")

@bot.command()
@commands.has_role("E-Board")
async def get_interval(ctx):
    global time
    await ctx.send(f"Current interval is {time / 24} day(s). Use !set [interval] to change this.")

@bot.command()
@commands.has_role("E-Board")
async def wipe(ctx):
    await ctx.send("**WARNING:** You are about to delete ALL entries. This cannot be undone. Type `yes` to confirm.")
    def check(m):
        return (
            m.author == ctx.author
            and m.channel == ctx.channel
            and m.content.lower().strip() in ["yes", "no"]
        )
    try:
        response = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. No entries were deleted.")
        return
    if response.content.lower().strip() == "yes":
        delete_db()
        await ctx.send("All entries have been deleted.")
    else:
        await ctx.send("Deletion cancelled.")

async def send_to_channel(ctx, message, target_channel_id):
    if ctx.guild is not None:
        return
    if ctx.author.id != ME:
        return

    channel = bot.get_channel(target_channel_id)
    if channel is not None:
        await channel.send(message)


@bot.command()
async def say(ctx, *, message):
    await send_to_channel(ctx, message, CHANNEL)


@bot.command()
async def esay(ctx, *, message):
    await send_to_channel(ctx, message, ECHANNEL)


@bot.command()
@commands.has_role("E-Board")
async def disable(ctx):
    global online
    online = False
    await ctx.send("Discussion disabled")

@bot.command()
@commands.has_role("E-Board")
async def enable(ctx):
    global online
    online = True
    await ctx.send("Discussion enabled")

@bot.command()
@commands.has_role("E-Board")
async def status(ctx):
    global online
    if(online):
        await ctx.send("Discussion is currently enabled")
    else:
        await ctx.send("Discussion is currently disabled")

@bot.command()
@commands.has_role("E-Board")
async def announce(ctx, *, message):
    channel = bot.get_channel(ANNOUNCE)
    if channel:
        await channel.send(message)

from tasks import get_tasks, get_pie, IDs
import pytz
async def run_tasks():
    channel = bot.get_channel(EANNOUNCE)
    e_tasks, pie = get_tasks()
    if channel:
        for role, task_list in e_tasks.items():
            if not task_list: # Currently ignores member if no tasks
                continue

            mention = f"<@{IDs[role]}>"
            lines = []
            for task in task_list:
                if task.due_date:
                    lines.append(
                        f"• **{task.title}** — Due: {task.due_date} — Status: {task.status}"
                    )
                else:
                    lines.append(
                        f"• **{task.title}** — Due: Weekly — Status: {task.status}"
                    )
            message_content = mention + "\n" + "\n".join(lines)
            if pie[role] + len(task_list) >= 3:
                pie_message = "🥧" + get_pie() + "🥧"
                message_content += "\n" + pie_message
            await channel.send(message_content)

@bot.command()
@commands.has_role("E-Board")
async def task(ctx):
    await run_tasks()

@tasks.loop(minutes=1)
async def task_scheduler():
    now = datetime.now(pytz.timezone("US/Eastern"))
    if now.weekday() == task_day and now.hour == task_hour and now.minute == task_minute:
        await run_tasks()

@bot.command()
@commands.has_role("E-Board")
async def get_task_time(ctx):
    minute_message = str(task_minute)
    if task_minute < 10:
        minute_message = "0" + minute_message
    await ctx.send(f"Current task reminder time is set to {idx2week[task_day]} at {task_hour}:{minute_message}. Use !set_task_time [day] [24-hour time] to change this.")

@bot.command()
@commands.has_role("E-Board")
async def set_task_time(ctx, *, message):
    import re

    VALID_DAYS = {
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    }

    parts = message.strip().split()
    if len(parts) != 2:
        await ctx.send("Format: !set_task_time [day] [24-hour time]")
        return
    day, time_str = parts
    if day not in week2idx:
        await ctx.send("Invalid weekday. Must be capitalized (e.g., Wednesday).")
        return
    match = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", time_str)
    if not match:
        await ctx.send("Time must be 24-hour HH:MM (e.g., 17:30).")
        return
    
    global task_day, task_hour, task_minute
    task_day = week2idx[day]
    task_hour = int(match.group(1))
    task_minute = int(match.group(2))
    minute_message = str(task_minute)
    if task_minute < 10:
        minute_message = "0" + minute_message
    await ctx.send(f"Task reminder time set to {idx2week[task_day]} at {task_hour}:{minute_message}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)