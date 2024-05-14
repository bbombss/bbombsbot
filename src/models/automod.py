from __future__ import annotations

import enum
import typing as t

import hikari

if t.TYPE_CHECKING:
    from src.models.bot import BBombsBot

from src.models.ratelimiter import MessageRateLimiter
from src.static.re import *
from src.utils import can_mod

MESSAGE_SPAM_RATELIMITER = MessageRateLimiter(5, 6)
DUPLICATE_SPAM_RATELIMITER = MessageRateLimiter(10, 4, 4)


class AutoModMediaType(enum.Enum):
    """Types of media the automod handles as enums."""
    MENTION = "mentions"
    INVITE = "invites"
    LINK = "links"
    HYPERLINK = "hyperlinks"
    ATTACHMENT = "attachments"
    DUPLICATE = "duplicates"
    MESSAGE = "messages"
    UNDEFINED = "undefined"


class AutoModOffenceType(enum.Enum):
    """Types of offences the automod handles as enums."""
    SPAM = "spam"
    BLOCKED = "blocked"
    FILTERED = "filtered"


class AutoMod:
    """AutoMod class for automatically moderating members."""

    def __init__(self, app: BBombsBot) -> None:
        self._app: BBombsBot = app

    @property
    def app(self) -> BBombsBot:
        """Returns the linked application."""
        return self._app

    def can_automod(self, member: hikari.Member, bot: hikari.Member) -> bool:
        """Determine if a member should be moderated by automoderator.

        Parameters
        ----------
        member : hikari.Member
            The member to check.
        bot : hikari.Member
            The member for BBombsBot.

        """
        if not isinstance(member, hikari.Member):
            return False

        if member.is_bot:
            return False

        if member.id in self.app.owner_ids:
            return False

        if not can_mod(member, bot):
            return False

        return True

    async def moderate(
        self,
        message: hikari.PartialMessage,
        offence: AutoModOffenceType,
        media: AutoModMediaType,
        reason: str,
    ) -> None:
        """Carry out the suitable moderation action for the offending message.

        Parameters
        ----------
        message : hikari.PartialMessage
            The offending message.
        offence : AutoModOffenceType
            The type of offence.
        media : AutoModMediaType
            The type of media that caused this offence.
        reason : str
            The reason this message is being moderated.

        """
        print("!!! PUNISH")

    async def check_for_message_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for common types of spam.

        Return False if the check fails otherwise True.
        """
        MESSAGE_SPAM_RATELIMITER.add_message(message)
        if MESSAGE_SPAM_RATELIMITER.is_rate_limited(message):
            reason = "Spamming messages."
            await self.moderate(
                message, AutoModOffenceType.SPAM, AutoModMediaType.MESSAGE, reason
            )
            return False

        return True

    async def check_for_duplicate_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for duplicate message spamming.

        Returns False if the check fails otherwise True.
        """
        queue = DUPLICATE_SPAM_RATELIMITER.get_messages(message)

        if queue is None:
            DUPLICATE_SPAM_RATELIMITER.add_message(message)

        elif queue[-1].strip() == message.content.strip():
            DUPLICATE_SPAM_RATELIMITER.add_message(message)
            if DUPLICATE_SPAM_RATELIMITER.is_rate_limited(message):
                reason = "Spamming duplicate messages."
                await self.moderate(
                    message, AutoModOffenceType.SPAM, AutoModMediaType.DUPLICATE, reason
                )
                return False

        return True

    async def check(
        self, event: hikari.GuildMessageUpdateEvent | hikari.GuildMessageCreateEvent
    ) -> None:
        """Run automod checks on created or updated messages."""
        message = event.message

        if not message.author:
            return

        member = self.app.cache.get_member(message.guild_id, message.author.id)
        bot = self.app.cache.get_member(message.guild_id, self.app.user_id)

        if not self.can_automod(member, bot):
            return

        if isinstance(event, hikari.GuildMessageCreateEvent):
            all(
                await self.check_for_message_spam(message),
                await self.check_for_duplicate_spam(message),
            )


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
