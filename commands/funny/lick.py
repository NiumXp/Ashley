import discord

from random import choice
from discord.ext import commands
from resources.db import Database
from resources.check import check_it


class LickClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='lick', aliases=['lambida'])
    async def lick(self, ctx):
        try:
            lickimg = ['https://media1.tenor.com/images/5f73f2a7b302a3800b3613095f8a5c40/tenor.gif?itemid=10005495',
                       'https://media1.tenor.com/images/0c608b33607b4e92350198b53c8940c7/tenor.gif?itemid=16735374',
                       'https://media1.tenor.com/images/ec2ca0bf12d7b1a30fea702b59e5a7fa/tenor.gif?itemid=13417195',
                       'https://media1.tenor.com/images/c1d9ff6f013a3deba4b7941fa00374e5/tenor.gif?itemid=16150817',
                       'https://media1.tenor.com/images/6b701503b0e5ea725b0b3fdf6824d390/tenor.gif?itemid=12141727']
            lick = choice(lickimg)
            lickemb = discord.Embed(title='Lambida :heart:',
                                    description='**{}** Ele(a) recebeu uma lambida de **{}**! Que casal fofo! '
                                                ':heart_eyes: '.format(ctx.message.mentions[0].name, ctx.author.name),
                                    color=self.color)
            lickemb.set_image(url=lick)
            lickemb.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=lickemb)
        except IndexError:
            await ctx.send('<:negate:520418505993093130>│``Você precisa mencionar um usuário específico para '
                           'lamber!``')


def setup(bot):
    bot.add_cog(LickClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mLICKCLASS\033[1;32m foi carregado com sucesso!\33[m')
