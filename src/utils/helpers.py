import hikari
import lightbulb

from src.static.re import *


def has_permissions(
    member: hikari.Member, perms: hikari.Permissions, strict: bool = True
) -> bool:
    """Will return true if a member has specified permissions.

    Parameters
    ----------
    member : hikari.Member
        The member to check.
    perms : hikari.Permissions
        The permissions to check for.
    strict : bool
        Wether the member must poses all or at least one of the permissions.
        Defaults to True.

    """
    member_perms = lightbulb.utils.permissions_for(member)

    if member_perms == hikari.Permissions.NONE:
        return False

    if strict and (member_perms & perms) == perms:
        return True

    elif not strict:
        for perm in perms:
            if perm in member_perms:
                return True

    return False


def higher_role(member: hikari.Member, bot: hikari.Member) -> bool:
    """Will return true if the members highest role is higher than the bots."""
    member_role = member.get_top_role()
    bot_role = bot.get_top_role()

    if member_role.position > bot_role.position:
        return True
    return False


def can_mod(member: hikari.Member, bot: hikari.Member) -> bool:
    """Will return true if the bot can moderate the member."""
    guild = member.get_guild()

    if guild.owner_id == member.id:
        return False

    if higher_role(member, bot):
        return False

    perms = hikari.Permissions.ADMINISTRATOR | hikari.Permissions.MANAGE_GUILD

    if has_permissions(member, perms, strict=False):
        return False

    return True


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
