from __future__ import annotations

import enum
import typing as t
from contextlib import suppress

import hikari
from Levenshtein import distance

if t.TYPE_CHECKING:
    from src.models.bot import BBombsBot

from src.models.ratelimiter import MessageRateLimiter
from src.static.re import *
from src.utils import can_mod

MESSAGE_SPAM_RATELIMITER = MessageRateLimiter(5, 5)
DUPLICATE_SPAM_RATELIMITER = MessageRateLimiter(10, 4, 4)
INVITE_SPAM_RATELIMITER = MessageRateLimiter(30, 2)
LINK_SPAM_RATELIMITER = MessageRateLimiter(30, 3)
ATTACHMENT_SPAM_RATELIMITER = MessageRateLimiter(30, 2)
MENTION_SPAM_RATELIMITER = MessageRateLimiter(30, 3, 2)

BLOCK_INVITES = True
BLOCK_FAKE_URL = True
MENTION_FILTER_LIMIT = 9


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
        with suppress(hikari.NotFoundError):
            message.delete()

    async def find_message_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for common types of spam.

        Return False if the check fails otherwise True.
        """
        MESSAGE_SPAM_RATELIMITER.add_message(message)
        if MESSAGE_SPAM_RATELIMITER.is_rate_limited(message):
            reason = "sending messages too frequently."
            await self.moderate(
                message, AutoModOffenceType.SPAM, AutoModMediaType.MESSAGE, reason
            )
            return False

        return True

    async def find_duplicate_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for duplicate message spamming.

        Returns False if the check fails otherwise True.
        """
        if not message.content:
            return True

        queue = DUPLICATE_SPAM_RATELIMITER.get_messages(message)

        if queue is None:
            DUPLICATE_SPAM_RATELIMITER.add_message(message)
            return True

        prev_msg = self.app.cache.get_message(queue[-1])
        print(prev_msg.content)
        if prev_msg and distance(prev_msg.content.strip(), message.content.strip()) < 5:
            print("yes")
            DUPLICATE_SPAM_RATELIMITER.add_message(message)
            if DUPLICATE_SPAM_RATELIMITER.is_rate_limited(message):
                reason = "spamming copied and pasted messages."
                await self.moderate(
                    message, AutoModOffenceType.SPAM, AutoModMediaType.DUPLICATE, reason
                )
                return False

        return True

    async def find_invite_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with invites being spammed.

        Return False if the check fails otherwise True.
        """
        if message.content and INVITE_REGEX.findall(message.content):
            INVITE_SPAM_RATELIMITER.add_message(message)

        if INVITE_SPAM_RATELIMITER.is_rate_limited(message):
            reason = "sending discord invites too frequently."
            await self.moderate(
                message, AutoModOffenceType.SPAM, AutoModMediaType.INVITE, reason
            )
            return False

        return True

    async def find_link_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with links being spammed.

        Return False if the check fails otherwise True.
        """
        if message.content and URL_REGEX.findall(message.content):
            LINK_SPAM_RATELIMITER.add_message(message)

        if LINK_SPAM_RATELIMITER.is_rate_limited(message):
            reason = "sending links too frequently."
            await self.moderate(
                message, AutoModOffenceType.SPAM, AutoModMediaType.LINK, reason
            )
            return False

        return True

    async def find_attach_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with attachments being spammed.

        Return False if the check fails otherwise True.
        """
        if message.attachments:
            ATTACHMENT_SPAM_RATELIMITER.add_message(message)

        if ATTACHMENT_SPAM_RATELIMITER.is_rate_limited(message):
            reason = "sending attachments too frequently."
            await self.moderate(
                message, AutoModOffenceType.SPAM, AutoModMediaType.ATTACHMENT, reason
            )
            return False

        return True

    async def find_mention_spam(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with mentions being spammed.

        Return False if the check fails otherwise True.
        """
        if message.user_mentions:
            for mention in message.user_mentions.values():
                if mention.is_bot or mention.id == message.author.id:
                    return True

            MENTION_SPAM_RATELIMITER.add_message(message)

        if MENTION_SPAM_RATELIMITER.is_rate_limited(message):
            reason = "mentioning users too frequently."
            await self.moderate(
                message, AutoModOffenceType.SPAM, AutoModMediaType.MENTION, reason
            )
            return False

        return True

    async def block_invites(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with invite links.

        Return False if the check fails otherwise True.
        """
        # Placeholder for custom automod configs
        if BLOCK_INVITES and message.content and INVITE_REGEX.findall(message.content):
            reason = "invite links are not allowed."
            await self.moderate(
                message, AutoModOffenceType.BLOCKED, AutoModMediaType.INVITE, reason
            )
            return False

        return True

    async def block_fake_links(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with hyperlinks where the hyperlink text is also a url.

        Return False if the check fails otherwise True.
        """
        # Placeholder for custom automod configs
        if BLOCK_FAKE_URL and message.content and FAKE_URL_REGEX.findall(message.content):
            reason = "hyperlink contains link as text string."
            await self.moderate(
                message, AutoModOffenceType.BLOCKED, AutoModMediaType.HYPERLINK, reason
            )
            return False

    async def filter_mentions(self, message: hikari.PartialMessage) -> bool:
        """Check for messages with lots of mentions of different users.

        Return False if the check fails otherwise True.
        """
        if mentions := message.user_mentions:
            count = sum(
                mention.id != message.author.id and not mention.is_bot
                for mention in mentions.values()
            )

            if count > MENTION_FILTER_LIMIT:
                reason = "mentioning too many users in one message."
                await self.moderate(
                    message, AutoModOffenceType.FILTERED, AutoModMediaType.MENTION, reason
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
                (
                    await self.find_message_spam(message),
                    await self.find_duplicate_spam(message),
                    await self.find_invite_spam(message),
                    await self.find_link_spam(message),
                    await self.find_attach_spam(message),
                    await self.find_mention_spam(message),
                    await self.block_invites(message),
                    await self.block_fake_links(message),
                    await self.filter_mentions(message),
                )
            )
        elif isinstance(event, hikari.GuildMessageUpdateEvent):
            all(
                (
                    await self.block_invites(message),
                    await self.block_fake_links(message),
                    await self.filter_mentions(message),
                )
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
