from time import perf_counter_ns
import datetime

import lightbulb
import hikari
import psutil

from src.models import BBombsBot

misc = lightbulb.Plugin('misc')

@misc.command
@lightbulb.command('ping', description = 'Get performance statistics for the bot')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.SlashContext):
    start = perf_counter_ns()
    await ctx.respond('Testing...')
    end = perf_counter_ns()

    tdelta = datetime.datetime.now() - ctx.app.start_time
    tdelta_str = str(tdelta).split('.')[0].split(':')

    me = ctx.app.get_me()
    process = psutil.Process()

    await ctx.edit_last_response(
        '',
        embed=hikari.Embed(
            title=f'⌛️ {me.username} Info',
            description=f"""Developer: **BBombs**
Server Count: **{len(ctx.app.cache.get_guilds_view())}**
Uptime: **{tdelta_str[0]} hours, {tdelta_str[1]} minutes**
Invite: [Click here](https://discord.com/oauth2/authorize?client_id={me.id}&permissions=1099914800342&scope=bot+applications.commands)
Source: [Click here](https://github.com/bbombss/bbombsbot)""",
            colour=ctx.app.embed_colour
        )
        .add_field(
            name='Latency',
            value=f'Gateway: {ctx.bot.heartbeat_latency * 1000:,.0f}ms\nREST: {(end-start)/ 1000000:,.0f}ms'
        )
        .add_field(
            name='CPU Use',
            value=f'{round(psutil.cpu_percent())}%',
            inline=True
        )
        .add_field(
            name='Memory Use',
            value=f'{round(process.memory_info().vms / 1048576)}MB',
            inline=True
        )
    )

def load(bot: BBombsBot) -> None:
    bot.add_plugin(misc)

def unload(bot: BBombsBot) -> None:
    bot.remove_plugin(misc)