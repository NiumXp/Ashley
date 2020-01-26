import discord

from discord.ext import commands


class RoleUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.guild is not None:
            data = self.bot.db.get_data("guild_id", before.guild.id, "guilds")
            if data is not None:
                try:
                    if data['log_config']['log'] and data['log_config']['role_edit']:
                        if before.name != after.name:
                            canal = self.bot.get_channel(data['log_config']['log_channel_id'])
                            if canal is None:
                                return
                            to_send = discord.Embed(
                                title=":star2: **Cargo Editado**",
                                color=self.color,
                                description=f"**Cargo:** {before.mention}")
                            to_send.add_field(name='Nome Antigo', value=f'**{before.name}**')
                            to_send.add_field(name='Nome Novo', value=f'**{after.name}**')
                            to_send.set_footer(text="Ashley ® Todos os direitos reservados.")
                            await canal.send(embed=to_send)
                except AttributeError:
                    pass
                except discord.errors.HTTPException:
                    pass
                except TypeError:
                    pass


def setup(bot):
    bot.add_cog(RoleUpdate(bot))
    print('\033[1;33m( * ) | O evento \033[1;34mROLE_UPDATE\033[1;33m foi carregado com sucesso!\33[m')
