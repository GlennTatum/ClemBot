import asyncio
import typing as t

import discord

from bot.clem_bot import ClemBot
from bot.consts import Claims
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class DeleteMessageService(BaseService):
    """
    This service allows for messages sent by the bot to be deleted
    The messages by default are allowed by deleted by admins and the person who called the bot
    """

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)
        self.messages = dict[int, dict[str, t.Any]]()

    # Called When a cog would like to be able to delete a message or messages
    @BaseService.listener(Events.on_set_deletable)
    async def set_message_deletable(
        self,
        *,
        msg: list[discord.Message],
        roles: list[discord.Role] = [],
        author: t.Optional[discord.Member] = None,
        timeout: t.Optional[int] = None
    ) -> None:

        if not isinstance(msg, list):
            msg = [msg]
        if not isinstance(roles, list):
            roles = [roles]

        # stores the message info
        self.messages[msg[-1].id] = {
            "MessagesToDelete": msg,
            "Roles": roles,
            "Author": author.id if author else None,
        }

        # the emoji is placed on the last message in the list
        await msg[-1].add_reaction("🗑️")
        if timeout:
            await asyncio.sleep(timeout)
            try:
                await msg[-1].clear_reaction("🗑️")
                del self.messages[msg[-1].id]
            except:
                pass
            finally:
                log.info("Message: {message} timed out as deletable", message=msg[-1].id)

    @BaseService.listener(Events.on_reaction_add)
    async def delete_message(
        self, reaction: discord.Reaction, user: discord.User | discord.Member
    ) -> None:
        role_ids = [role.id for role in user.roles] if isinstance(user, discord.Member) else []
        delete = False

        if reaction.emoji != "🗑️" or reaction.message.id not in self.messages:
            return
        elif await self.bot.claim_route.check_claim_user(
            Claims.delete_message, t.cast(discord.Member, user)
        ):
            delete = True
        elif user.id == self.messages[reaction.message.id]["Author"]:
            delete = True
        elif isinstance(user, discord.Member):
            if user.guild_permissions.administrator:
                delete = True
            elif any(
                True for role in self.messages[reaction.message.id]["Roles"] if role.id in role_ids
            ):
                delete = True

        if delete:
            for msg in self.messages[reaction.message.id]["MessagesToDelete"]:
                log.info("Message {message} deleted by delete message service", message=msg.id)
                await msg.delete()
            del self.messages[reaction.message.id]

    async def load_service(self) -> None:
        pass
