from ia.scripts import ia
from discord.ext import commands
from config import data as config
from random import choice, randint
from resources.ia_heart import HeartIA
from resources.utility import get_response, include

C_SIM, C_NAO = 98, 98
chance, chance_not = 0, 0
ASHLEY = ["ashley"]


class IaInteractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg = {}
        self.scripts = [ia.about_me, ia.concept, ia.deeping, ia.introduction, ia.responses, ia.commands, ia.common]
        self.heart = HeartIA(self.scripts, 0.9)

    async def send_message(self, message, content=None):
        link_ = f'images/avatar/possessed_ashley.png'
        if content is None:
            msg = await get_response(message)
        else:
            msg = content
        name = choice(['Possessed Ashley'])
        ctx = await self.bot.get_context(message)
        return await self.bot.web_hook_rpg(ctx, link_, name, msg, 'Ashley')

    @commands.Cog.listener()
    async def on_message(self, message):
        global chance, chance_not
        if message.guild is not None and str(message.author.id) not in self.bot.blacklist:
            data_guild = await self.bot.db.get_data("guild_id", message.guild.id, "guilds")
            user_data = await self.bot.db.get_data("user_id", message.author.id, "users")
            dg, ud = data_guild, user_data
            if dg is not None and ud is not None and dg['ia_config']['auto_msg']:

                # filtro de comandos ( para nao haver iteração em cima de comandos )
                # -----------======================-----------
                ctx = await self.bot.get_context(message)
                if ctx.command is not None:
                    return
                # -----------======================-----------

                # verificação de permissão para enviar msg e ler

                # -----------======================-----------
                perms = ctx.channel.permissions_for(ctx.me)
                if not perms.send_messages or not perms.read_messages:
                    return
                if not perms.embed_links or not perms.attach_files:
                    return
                # -----------======================-----------

                # sistema de chance da ashley  responder a um usuario

                # --------------============================--------------
                chance = randint(1, 100)
                chance_not = randint(1, 100)
                # --------------============================--------------

                # desativação da auto resposta
                # -----------======================-----------
                if not ud['user']['ia_response']:
                    chance = 0
                    chance_not = 0
                # -----------======================-----------

                # filtro de mensagem contra o criador kkkk

                # --------------============================--------------
                if 'denky' in message.content.lower() and data_guild['ia_config']['auto_msg']:
                    if message.author.id != self.bot.owner_id:
                        for c in range(0, len(config['questions']['denky_r'])):
                            if config['questions']['denky_r'][c] in message.content:
                                msg = '**Ei,** {}**! Eu to vendo você falar mal do meu pai!**\n```VOU CONTAR TUDO ' \
                                      'PRO PAPAI```'.format(message.author.mention)
                                return await self.send_message(message, msg)
                # --------------============================--------------

                # filtro de quantidade de mensagens salvas por usuario
                try:
                    # filtro de pergunta repetida a longo prazo
                    if len(self.msg[message.author.id]) >= 10:
                        for msg in self.msg[message.author.id]:
                            if message.content == msg and "?" in message.content:
                                if chance >= C_SIM or include(message.content, ASHLEY):
                                    content = choice(self.bot.config['answers']['repeat'])
                                    return await self.send_message(message, content)

                    self.msg[message.author.id].append(message.content)
                    if len(self.msg[message.author.id]) >= 20:
                        self.msg[message.author.id] = [message.content]

                except KeyError:
                    self.msg[message.author.id] = [message.content]

                # filtro de repetição de perguntas e mensagens
                try:
                    if self.msg[message.author.id][-1] == self.msg[message.author.id][-2]:
                        if self.msg[message.author.id][-1] == self.msg[message.author.id][-3]:
                            if chance >= C_SIM or include(message.content, ASHLEY):
                                content = choice(self.bot.config['answers']['repeated'])
                                return await self.send_message(message, content)
                except IndexError:
                    pass

                # remoção do codi-name "ash" ou "ashley"
                # --------------------============================--------------------
                content_ = message.content.lower()
                content_ = content_.replace("ashley", "").replace("ash", "")
                content_ = content_.replace(" ?", "?").replace("  ", " ").strip()
                # --------------------============================--------------------

                # sistema de IA
                if chance >= C_SIM or include(message.content, ASHLEY):
                    if '?' in message.content and len(message.content) > 2:
                        response = self.heart.get_response(content_)
                        if response is not None:
                            return await self.send_message(message, response)
                        else:
                            return await self.send_message(message)
                    else:
                        response = self.heart.get_response(content_)
                        if response is not None:
                            return await self.send_message(message, response)
                        else:
                            if 'bom dia' in message.content.lower() or 'boa tarde' in message.content.lower():
                                content = choice(config['salutation']['day'])
                                return await self.send_message(message, content)
                            elif 'boa noite' in message.content.lower():
                                content = choice(config['salutation']['night'])
                                return await self.send_message(message, content)
                else:
                    if chance_not >= C_NAO and "?" in message.content:
                        content = choice(self.bot.config['answers']['upset'])
                        return await self.send_message(message, content)


def setup(bot):
    bot.add_cog(IaInteractions(bot))
    print('\033[1;33m( 🔶 ) | O evento \033[1;34mIA_INTERACTIONS\033[1;33m foi carregado com sucesso!\33[m')
