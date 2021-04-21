# Standard
from asyncio.tasks import sleep
from typing import Any, Dict, List, Optional

# Community
import discord
from discord.channel import CategoryChannel, VoiceChannel
from discord.errors import Forbidden
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

# Custom
from Settings import settings


######################
#  Global Variables  #
######################

extra_args = {}
if not settings.USE_GLOBAL_COMMANDS:
    extra_args["guild_ids"] = settings.COMMAND_GUILDS


class Driving(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_next_category(
        all: List[CategoryChannel], current: CategoryChannel, up: bool
    ) -> CategoryChannel:
        print([c.name for c in all])
        category_num = all.index(current)
        new_category_num = category_num + (-1 if up else 1)

        if new_category_num < len(all):
            return all[new_category_num]
        else:
            return all[0]

    @cog_ext.cog_slash(
        name="drive",
        description='Move the VC you\'re in, if it ends in " Car" up or down as many spots as you specify in distance.',
        options=[
            create_option(
                "direction",
                "The direction to drive in",
                option_type=str,
                required=True,
                choices=["up", "down"],
            ),
            create_option(
                "distance",
                "The distance to drive",
                option_type=int,
                required=True,
            ),
        ],
        **extra_args,
    )
    async def _drive(self, ctx: SlashContext, direction: str, distance: int):
        HIDDEN = True
        await ctx.defer(hidden=HIDDEN)
        direction_int = -1 if direction == "up" else 1

        # Get target voice channel the user is in
        voice_state = ctx.author.voice
        target_vc: Optional[VoiceChannel] = (
            voice_state if voice_state is None else voice_state.channel
        )
        if target_vc is None:
            await ctx.send("Please join a voice channel to drive around", hidden=HIDDEN)
            return

        # Make sure the VC is a car
        if not (target_vc.name.endswith("Car") or target_vc.name.endswith("Truck")):
            await ctx.send("The voice channel you're in is not a car", hidden=HIDDEN)
            return

        # Move the voice channel
        for _ in range(distance):
            move_kwargs: Dict[str, Any] = {}

            max_location = len(target_vc.category.voice_channels) - 1
            current_location = target_vc.category.voice_channels.index(target_vc)
            new_location = current_location + direction_int

            # Move without changing categories
            if 0 <= new_location <= max_location:
                move_kwargs["beginning"] = True
                move_kwargs["offset"] = new_location
                move_kwargs["category"] = target_vc.category
            # Move up a category
            elif new_location < 0:
                move_kwargs["end"] = True
                move_kwargs["category"] = self.get_next_category(
                    all=ctx.guild.categories,
                    current=target_vc.category,
                    up=True,
                )
            # Move down a category
            elif new_location > max_location:
                move_kwargs["beginning"] = True
                move_kwargs["category"] = self.get_next_category(
                    all=ctx.guild.categories,
                    current=target_vc.category,
                    up=False,
                )

            # Move the VC
            try:
                await target_vc.move(**move_kwargs)
            except Forbidden:
                await ctx.send(
                    "I do not have permission to move channels, please contact the admins to fix this issue.",
                    hidden=HIDDEN,
                )
                return

            # Wait a bit
            await sleep(1)

        await ctx.send(f"You have arrived at your destination!", hidden=HIDDEN)


def setup(bot):
    bot.add_cog(Driving(bot))
