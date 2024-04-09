import hikari
import lightbulb

from src.models import BBombsBot
from src.static import *

admin = lightbulb.Plugin("admin")


@admin.command
@lightbulb.option("extension", "Extension to load")
@lightbulb.command("load", "Loads extension", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ext_load(ctx: lightbulb.PrefixContext, extension: str) -> None:
    ctx.app.load_extensions(extension)
    await ctx.respond(
        "",
        embed=hikari.Embed(
            title=None,
            description=f"{SUCCESS_EMOJI}  Loaded {extension}",
            colour=SUCCESS_EMBED_COLOUR,
        ),
    )


@admin.command
@lightbulb.option("extension", "Extension to reload")
@lightbulb.command("reload", "Reloads extension", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ext_reload(ctx: lightbulb.PrefixContext, extension: str) -> None:
    ctx.app.reload_extensions(extension)
    await ctx.respond(
        "",
        embed=hikari.Embed(
            title=None,
            description=f"{SUCCESS_EMOJI}  Reloaded {extension}",
            colour=SUCCESS_EMBED_COLOUR,
        ),
    )


@admin.command
@lightbulb.option("extension", "Extension to unload")
@lightbulb.command("unload", "Unloads extension", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ext_unload(ctx: lightbulb.PrefixContext, extension: str) -> None:
    ctx.app.unload_extensions(extension)
    await ctx.respond(
        "",
        embed=hikari.Embed(
            title=None,
            description=f"{SUCCESS_EMOJI}  Unloaded {extension}",
            colour=SUCCESS_EMBED_COLOUR,
        ),
    )


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
