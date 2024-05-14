import asyncio
import datetime
import logging
import traceback

import hikari
import lightbulb

from src.models import BBombsBot, BBombsBotContext
from src.static import FAIL_EMBED_COLOUR, FAIL_EMOJI

logger = logging.getLogger(__name__)

errorhandler = lightbulb.Plugin("errorhandler")


async def log_error(
    error: str,
    ctx: BBombsBotContext | None = None,
    event: hikari.ExceptionEvent | None = None,
) -> None:
    """Log an error to the discord bot logs channel.

    Parameters
    ----------
    error : str
        Error message for logging.
    ctx : BBombsBotContext, optional
        Context for more information if provided, defaults to None.
    event : hikari.ExceptionEvent, optional
        Event for more information if provided, defaults to None.

    """
    error_lines = error.splitlines()
    paginator = lightbulb.utils.StringPaginator(prefix="```py\n", suffix="```")

    if ctx:
        guild = ctx.get_guild()
        if guild:
            msg = f"# Uncaught exception in command {ctx.command.name} invoked by {ctx.author} ({ctx.author.id}) in {guild.name} ({ctx.guild_id})"

    elif event:
        msg = f"# Uncaught exception in event {event.failed_event.__class__.__name__}"

    else:
        msg = "# Uncaught exception:"

    paginator.add_line(msg)

    for line in error_lines:
        paginator.add_line(line)

    logs_channel = errorhandler.app.config.LOGGING_CHANNEL_ID

    if not logs_channel:
        return

    try:
        for page in paginator.build_pages():
            await errorhandler.app.rest.create_message(logs_channel, page)
    except hikari.ForbiddenError:
        logger.error("Missing access to logs channel.")


@errorhandler.listener(lightbulb.SlashCommandErrorEvent)
@errorhandler.listener(lightbulb.MessageCommandErrorEvent)
@errorhandler.listener(lightbulb.UserCommandErrorEvent)
async def application_command_error_handler(event: lightbulb.CommandErrorEvent) -> None:
    ctx: BBombsBotContext = event.context
    error = event.exception.__cause__ or event.exception

    if isinstance(error, lightbulb.CommandIsOnCooldown):
        await ctx.respond_with_failure(
            f"**Command is on cooldown, try again in {round(error.retry_after)} seconds**",
            ephemeral=True,
        )
        return

    if isinstance(error, lightbulb.MaxConcurrencyLimitReached):
        await ctx.respond_with_failure(
            "**Concurrency limit reached for this command, try again later**",
            ephemeral=True,
        )
        return

    if isinstance(error, lightbulb.MissingRequiredPermission):
        await ctx.respond_with_failure(
            "**You lack the required permissions to execute this command**",
            ephemeral=True,
        )
        return

    if isinstance(error, lightbulb.BotMissingRequiredPermission):
        await ctx.respond_with_failure(
            "**I am missing permissions required to execute this command**",
            ephemeral=True,
        )
        return

    if isinstance(error, lightbulb.OnlyInGuild):
        await ctx.respond_with_failure(
            "**This command can only be used within a server**", ephemeral=True
        )
        return

    if isinstance(error, lightbulb.CommandInvocationError):
        if isinstance(error.original, hikari.InternalServerError):
            await ctx.respond_with_failure(
                "**An issue with Discord's servers prevented this, try again shortly**",
                edit=True,
            )
            return

        if isinstance(error.original, hikari.ForbiddenError):
            await ctx.respond_with_failure(
                f"**I do not have permission to perform this action:\n\n**```{error.original}```",
                edit=True,
            )
            return

        if isinstance(error.original, hikari.UnauthorizedError):
            await ctx.respond_with_failure(
                f"**I am unauthorised to access resources at this endpoint:\n\n**```{error.original}```",
                edit=True,
            )
            return

        if isinstance(error.original, asyncio.TimeoutError):
            await ctx.respond_with_failure("**Command timed out**", edit=True)
            return

    logger.error(
        f"Unhandled exception in {ctx.guild_id} /{ctx.command.name} -> {error.__class__.__name__}: {error}"
    )

    error = error.original if hasattr(error, "original") else error

    await ctx.delete_last_response()

    await ctx.respond(
        embed=hikari.Embed(
            title=f"{FAIL_EMOJI} Unknown Error",
            description="""An unhandled exception has occured in the BBombsBot application.
This has been automatically logged, contact the bot administrator or raise an issue on [GitHub](https://github.com/bbombss/bbombsbot) if this issue persists.""",
            colour=FAIL_EMBED_COLOUR,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        .add_field(name="Error", value=f"```{error.__class__.__name__}: {error}```")
        .set_footer(ctx.guild_id)
    )

    error_str = "\n".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    await log_error(error_str, ctx=ctx)


@errorhandler.listener(lightbulb.PrefixCommandErrorEvent)
async def prefix_command_error_handler(event: lightbulb.PrefixCommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandNotFound):
        return
    if isinstance(event.exception, lightbulb.CheckFailure):
        return

    error = (
        event.exception.original
        if hasattr(event.exception, "original")
        else event.exception
    )
    ctx: BBombsBotContext = event.context

    await ctx.respond_with_failure(
        f"**Uncaught exception:**\n\n```{error.__class__.__name__}: {error}```", edit=True
    )

    error_str = "\n".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    await log_error(error_str, ctx)


@errorhandler.listener(hikari.ExceptionEvent)
async def event_error_handler(event: hikari.ExceptionEvent) -> None:
    logger.error(
        f"Unhandled exception in event listener {event.failed_event.__class__.__name__}"
    )

    error_str = "\n".join(traceback.format_exception(*event.exc_info))
    await log_error(error_str, event=event)


def load(bot: BBombsBot) -> None:
    bot.add_plugin(errorhandler)


def unload(bot: BBombsBot) -> None:
    bot.remove_plugin(errorhandler)


# Copyright (C) 2024 BBombs

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
