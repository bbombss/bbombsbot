from contextlib import redirect_stdout
from io import StringIO
from textwrap import indent

import hikari
import lightbulb

from src.models import BBombsBot, BBombsBotPrefixContext
from src.static import *

admin = lightbulb.Plugin("admin")
admin.add_checks(lightbulb.owner_only)


@admin.command
@lightbulb.option("extension", "Extension to load")
@lightbulb.command("load", "Loads extension", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ext_load(ctx: BBombsBotPrefixContext, extension: str) -> None:
    ctx.app.load_extensions(extension)
    await ctx.respond_with_success(f"**Loaded {extension}**")


@admin.command
@lightbulb.option("extension", "Extension to reload")
@lightbulb.command("reload", "Reloads extension", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ext_reload(ctx: BBombsBotPrefixContext, extension: str) -> None:
    ctx.app.reload_extensions(extension)
    await ctx.respond_with_success(f"**Reloaded {extension}**")


@admin.command
@lightbulb.option("extension", "Extension to unload")
@lightbulb.command("unload", "Unloads extension", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ext_unload(ctx: BBombsBotPrefixContext, extension: str) -> None:
    ctx.app.unload_extensions(extension)
    await ctx.respond_with_success(f"**Unloaded {extension}**")


@admin.command
@lightbulb.command("sync", "Sync application commands")
@lightbulb.implements(lightbulb.PrefixCommand)
async def sync_commands(ctx: BBombsBotPrefixContext) -> None:
    await ctx.app.sync_application_commands()
    await ctx.respond_with_success("**Synced application commands**")


@admin.command
@lightbulb.option("code", "Code to run", modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command("eval", "Evaluate python code", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def eval_python(ctx: BBombsBotPrefixContext, code: str) -> None:
    await ctx.wait()

    env = {
        "ctx": ctx,
        "app": ctx.app,
        "guild": ctx.get_guild(),
        "channel": ctx.get_channel(),
        "author": ctx.author,
    }

    env.update(globals())
    ready_code = code.replace("```py", "").replace("`", "").strip()

    code_lines = ready_code.splitlines()
    formated_code_lines = []

    for line in code_lines:
        if line.strip():
            formated_code_lines.append(f">> {line}")

    fcode = "\n".join(formated_code_lines)
    to_eval = f"async def foo():\n{indent(ready_code, " ")}"

    try:
        exec(to_eval, env)

    except Exception as exc:
        await ctx.respond_with_failure(
            f"**An exception occured during evaluation:**\n\n```{fcode}\n\n{exc}```",
            edit=True,
        )
        return

    foo = env["foo"]
    output = StringIO()

    try:
        with redirect_stdout(output):
            await foo()

    except Exception as exc:
        await ctx.respond_with_failure(
            f"**An exception occured during evaluation:**\n\n```{fcode}\n\n{exc}```",
            edit=True,
        )
        return

    output = output.getvalue()
    await ctx.respond_with_success(
        f"**Evaluated code with python:**\n\n```{fcode}\n\n{output}```",
        edit=True,
    )


@admin.command
@lightbulb.option(
    "code",
    "Code to run, overidden by attached file.",
    required=False,
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command("sql", "Execute sql command from message or file.", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def eval_sql(ctx: BBombsBotPrefixContext, code: str) -> None:
    await ctx.wait()

    if ctx.attachments and ctx.attachments[0].filename.endswith(".sql"):
        sql = (await ctx.attachments[0].read()).decode()
    elif code:
        sql = code.replace("```sql", "").replace("`", "").strip()
    else:
        await ctx.respond_with_failure(
            "**Could not find attached file or sql in message**", edit=True
        )

    output = await ctx.app.db.execute(sql)
    await ctx.respond_with_success(
        f"**SQL command executed successfully:**\n\n```{output}```", edit=True
    )


@admin.command()
@lightbulb.command("kill", "Shutdown the bot")
@lightbulb.implements(lightbulb.PrefixCommand)
async def kill_bot(ctx: BBombsBotPrefixContext) -> None:
    confirm_msg = {
        "embed": hikari.Embed(
            title=None,
            description="⚠️ Shutting down...",
            colour=WARN_EMBED_COLOUR,
        )
    }
    cancel_msg = {
        "embed": hikari.Embed(
            title=None,
            description=f"{FAIL_EMOJI} Shutdown cancelled",
            colour=FAIL_EMBED_COLOUR,
        )
    }

    confirmation = await ctx.get_confirmation(
        "Are you sure you want to shut down BBombsBot, this cannot be undone?",
        confirm_msg=confirm_msg,
        cancel_msg=cancel_msg,
    )

    if confirmation:
        await ctx.app.close()
        return


def load(bot: BBombsBot) -> None:
    bot.add_plugin(admin)


def unload(bot: BBombsBot) -> None:
    bot.remove_plugin(admin)


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
