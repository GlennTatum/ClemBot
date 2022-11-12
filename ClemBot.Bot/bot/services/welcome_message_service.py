import discord

from bot.clem_bot import ClemBot
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class WelcomeMessageService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_user_join_initialized)
    async def user_joined(self, user: discord.Member) -> None:
        message = await self.bot.welcome_message_route.get_welcome_message(user.guild.id)

        # TODO create try/except clause to handle users which have server "Direct Messages" disabled
        # Traceback exception: https://discord.com/channels/386585461285715968/729492221904158781/1041112145166876682

        if message and not user.bot:
            await user.send(message)

    async def load_service(self) -> None:
        pass
