import datetime
import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from asyncio import TimeoutError


class RegisterAnnounce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, vip=True, cooldown=True, time=300))
    @commands.command(name='announce', aliases=['anuncio'])
    async def announce(self, ctx, *, announce: str = None):
        """Usado pra anunciar na ashley
        Exemplo: ash announce <texto do anuncio aqui>
        seu texto será analizado por um dos desenvolvedores por questoes de segurança"""
        if ctx.author.id != ctx.guild.owner.id:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del update_['cooldown'][str(ctx.command)]
            await self.bot.db.update_data(data_, update_, 'users')
            return await ctx.send("<:negate:721581573396496464>│``Apenas donos de Guilda vip podem usar esse "
                                  "comando!``")

        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        if data_guild['vip'] is False:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del update_['cooldown'][str(ctx.command)]
            await self.bot.db.update_data(data_, update_, 'users')
            return await ctx.send("<:negate:721581573396496464>│``Você é o líder da guilda, mas sua Guilda ainda "
                                  "nao é VIP, você precisa conquistar 10 estrelas para tornar sua guilda VIP!``")

        if announce is None:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:negate:721581573396496464>│``Você precisa colocar um anuncio, para que eu'
                                  ' adicione no banco de dados!``')

        for data in await self.bot.db.get_announcements():
            if data['_id'] == ctx.author.id:
                await ctx.send("<:alert:739251822920728708>│``Você já tem um anuncio em vigor, se colocar"
                               " outro anuncio vai sobrepor seu anuncio antigo. Deseja mesmo assim proseguir?`` "
                               "**Responda com: S ou N**")

                def check(m):
                    return m.author.id == ctx.author.id and m.content.upper() == 'S' or m.author.id == ctx.author.id \
                           and m.content.upper() == 'N'

                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=30.0)
                except TimeoutError:
                    data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                    update_ = data_
                    del update_['cooldown'][str(ctx.command)]
                    await self.bot.db.update_data(data_, update_, 'users')
                    return await ctx.send('<:negate:520418505993093130>│``Desculpe, você demorou muito:`` '
                                          '**COMANDO CANCELADO**')
                if answer.content.upper() == "N":
                    return await ctx.send('<:negate:520418505993093130>│ **COMANDO CANCELADO**')
                else:
                    update = data
                    update['data']['status'] = False
                    date = datetime.datetime(*datetime.datetime.utcnow().timetuple()[:6])
                    update['data']['date'] = date
                    update['data']['announce'] = announce
                    await self.bot.db.update_data(data, update, "announcements")
                    await ctx.send('<:confirmed:721581574461587496>│``Anuncio cadastrado com sucesso!``\n'
                                   '```AGUARDE APROVAÇÃO```')
                    pending = self.bot.get_channel(619969149791240211)
                    msg = f"{ctx.author.id}: **{ctx.author.name}** ``ADICIONOU UM NOVO ANUNCIO PARA APROVAÇÃO!``"
                    return await pending.send(msg)
        await self.bot.data.add_announcement(ctx, announce)

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='verify', aliases=['verificar'])
    async def verify(self, ctx):
        """apenas desenvolvedores
        mostra a lista de anuncios pendentes"""
        announces = list()
        for data in await self.bot.db.get_announcements():
            if data['data']['status'] is False:
                announces.append(data)
        for announce in range(len(announces)):
            await ctx.send(f"{announce + 1}º Anuncio:\n{announces[announce]}")
        if len(announces) > 0:
            await ctx.send("<:alert:739251822920728708>│``Qual anuncio você deseja verificar? Obs: Digite o "
                           "numero do anuncio``")
        else:
            return await ctx.send("<:alert:739251822920728708>│``VOCE NAO TEM ANUNCIOS DISPONIVEIS!``")

        def check(m):
            return m.author.id == ctx.author.id and m.content.isdigit()

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)
            num = int(answer.content)
            answer = int(answer.content)
            if answer < 0:
                answer = 0
        except TimeoutError:
            return await ctx.send('<:negate:520418505993093130>│``Desculpe, você demorou muito:`` '
                                  '**COMANDO CANCELADO**')
        if len(announces) >= answer > 0:
            pass
        else:
            return await ctx.send('<:negate:520418505993093130>│ **DESCULPE VOCÊ DIGITOU UM NUMERO INEXISTENTE!**')

        await ctx.send(announces[num - 1])
        await ctx.send("<:alert:739251822920728708>│``Esse anuncio é valido?  Obs: Digite"
                       " S ou N``")

        def check(m):
            return m.author.id == ctx.author.id and m.content.upper() == 'S' or m.author.id == ctx.author.id \
                   and m.content.upper() == 'N'

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            return await ctx.send('<:negate:520418505993093130>│``Desculpe, você demorou muito:`` '
                                  '**COMANDO CANCELADO**')
        if answer.content.upper() == "S":
            pass
        else:
            data = announces[num - 1]
            await self.bot.db.delete_data(data, 'announcements')
            await ctx.send("<:confirmed:721581574461587496>│``Anuncio verificado com sucesso!``")
            try:
                member = self.bot.get_user(data['_id'])
                await member.send("<:negate:520418505993093130>│``Seu anuncio foi verificado, mas não foi aprovado!``")
            except discord.errors.Forbidden:
                pass
            return await ctx.send('<:negate:520418505993093130>│ **ANUNCIO DELETADO**')

        data = announces[num - 1]
        update = data
        update['data']['status'] = True
        await self.bot.db.update_data(data, update, "announcements")
        await ctx.send("<:confirmed:721581574461587496>│``Anuncio verificado com sucesso!``")
        try:
            member = self.bot.get_user(data['_id'])
            await member.send("<:confirmed:721581574461587496>│``Seu anuncio foi verificado e foi aprovado"
                              " parabens!``")
        except discord.errors.Forbidden:
            pass


def setup(bot):
    bot.add_cog(RegisterAnnounce(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mREGISTER_ANNOUNCE\033[1;32m foi carregado com sucesso!\33[m')
