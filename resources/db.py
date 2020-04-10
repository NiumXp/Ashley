import json
import discord
import datetime
import operator

from resources.translation import t_
from discord.ext import commands
from pymongo import MongoClient
from random import randint
from collections import Counter
from resources.utility import parse_duration, quant_etherny

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())

with open("data/config.json") as config:
    config = json.loads(config.read())

epoch = datetime.datetime.utcfromtimestamp(0)
cont = Counter()


class Database(object):
    def __init__(self, bot):
        self.bot = bot
        self._data_brute = MongoClient(_auth['db_url'] + "?retryWrites=false", connectTimeoutMS=30000)
        self._conn = self._data_brute.get_database(_auth['db_name'])

    def push_data(self, data, db_name):
        db = self._conn.get_collection(db_name)
        db.insert_one(data)

    def delete_data(self, data, db_name):
        db = self._conn.get_collection(db_name)
        db.delete_one(data)

    def update_data(self, data, update, db_name):
        db = self._conn.get_collection(db_name)
        db.update_one({'_id': data['_id']}, {
            '$set': update
        }, upsert=False)

    def update_all_data(self, search, update, db_name):
        db = self._conn.get_collection(db_name)
        db.update_many(search, {'$set': update})

    def get_data(self, key, value, db_name):
        db = self._conn.get_collection(db_name)
        data = db.find_one({key: value})
        if data is None:
            return None
        else:
            return data

    def get_all_data(self, db_name):
        db = self._conn.get_collection(db_name)
        data = db.find()
        return data

    def get_announcements(self):
        db = self._conn.get_collection("announcements")
        return db.find()

    def add_user(self, ctx, **data):
        db_name = data.get("db_name", "users")
        data = {
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id,
            "config": {
                "playing": False,
                "battle": False,
                "provinces": None,
                "vip": False,
                "roles": [],
                "points": 0
            },
            "user": {
                "experience": 0,
                "level": 1,
                "ranking": "Bronze",
                "titling": "Vagabond",
                "married": False,
                "stars": 0,
                "rec": 0
            },
            "rpg": {
                "Name": None,
                "Level": 1,
                "XP": 0,
                "Status": {
                    "con": 5,
                    "prec": 5,
                    "agi": 5,
                    "atk": 5,
                    "luk": 0,
                    "pdh": 0
                },
                "Class": 'Default',
                "itens": list(),
                "img": None
            },
            "treasure": {
                "money": 0,
                "gold": 0,
                "silver": 0,
                "bronze": 0
            },
            "inventory": {
                "medal": 0,
                "rank_point": 0,
                "coins": 10
            },
            "cooldown": {}
        }
        if self.get_data("user_id", ctx.author.id, db_name) is None:
            self.push_data(data, db_name)

    def add_guild(self, guild, data):
        db_name = data.get("db_name", "guilds")
        new_data = {
            "guild_id": guild.id,
            "vip": False,
            "data": {
                "commands": 0,
                "lang": "pt",
                "ranking": "Bronze",
                "items": dict(),
                "accounts": 0,
                "total_money": 0,
                "total_gold": 0,
                "total_silver": 0,
                "total_bronze": 0,
            },
            "treasure": {
                "total_money": 0,
                "total_gold": 0,
                "total_silver": 0,
                "total_bronze": 0
            },
            "log_config": {
                "log": data.get("log", False),
                "log_channel_id": data.get("log_channel_id", None),
                "msg_delete": data.get("msg_delete", True),
                "msg_edit": data.get("msg_edit", True),
                "channel_edit_topic": data.get("channel_edit_topic", True),
                "channel_edit_name": data.get("channel_edit_name", True),
                "channel_created": data.get("channel_created", True),
                "channel_deleted": data.get("channel_deleted", True),
                "channel_edit": data.get("channel_edit", True),
                "role_created": data.get("role_created", True),
                "role_deleted": data.get("role_deleted", True),
                "role_edit": data.get("role_edit", True),
                "guild_update": data.get("guild_update", True),
                "member_edit_avatar": data.get("member_edit_avatar", True),
                "member_edit_nickname": data.get("member_edit_nickname", True),
                "member_voice_entered": data.get("member_voice_entered", True),
                "member_voice_exit": data.get("member_voice_exit", True),
                "member_ban": data.get("member_ban", True),
                "member_unBan": data.get("member_unBan", True),
                "emoji_update": data.get("emoji_update", True)
            },
            "ia_config": {
                "auto_msg": data.get("auto_msg", False),
            },
            "rpg_config": {
                "rpg": data.get("rpg", False),
                "announcement": data.get("announcement", False),
                "announcement_id": data.get("announcement_id", None),
                "chat_farm": data.get("chat_farm", False),
                "chat_farm_id": data.get("chat_farm_id", None),
                "chat_battle": data.get("chat_battle", False),
                "chat_battle_id": data.get("chat_battle_id", None),
                "chat_pvp": data.get("chat_pvp", False),
                "chat_pvp_id": data.get("chat_pvp_id", None)
            },
            "bot_config": {
                "ash_news": data.get("ash_news", False),
                "ash_news_id": data.get("log", None),
                "ash_git": data.get("ash_news_id", False),
                "ash_git_id": data.get("ash_git_id", None),
                "ash_draw": data.get("ash_draw", False),
                "ash_draw_id": data.get("ash_draw_id", None),
            },
            "func_config": {
                "cont_users": data.get("cont_users", False),
                "cont_users_id": data.get("cont_users_id", None),
                "member_join": data.get("member_join", False),
                "member_join_id": data.get("member_join_id", None),
                "member_remove": data.get("member_remove", False),
                "member_remove_id": data.get("member_remove_id", None),
                "join_system": data.get("join_system", False),
                "join_system_id": data.get("join_system_id", None),
                "join_system_role": data.get("join_system_role", None),
                "join_system_member_state": dict()
            },
            "warn_config": {
                "warn": data.get("warn", False),
                "warn_channel_id": data.get("warn_channel_id", None),
                "bad_word": data.get("bad_word", False)
            }
        }
        if self.get_data("guild_id", guild.id, db_name) is None:
            self.push_data(new_data, db_name)

    async def take_money(self, ctx, amount: int = 0):
        data_user = self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        data_guild_native = self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        update_user['treasure']['money'] -= amount
        update_guild_native['data']['total_money'] -= amount
        self.bot.db.update_data(data_user, update_user, 'users')
        self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')
        return f"<:confirmado:519896822072999937>│**{amount}** ``DE`` **Ethernyas** ``RETIRADOS COM SUCESSO!``"

    async def give_money(self, ctx, amount: int = 0):
        data_user = self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        data_guild_native = self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        update_user['treasure']['money'] += amount
        update_guild_native['data']['total_money'] += amount
        self.bot.db.update_data(data_user, update_user, 'users')
        self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')
        return f"<:confirmado:519896822072999937>│**{amount}** ``DE`` **Ethernyas** ``ADICIONADOS COM SUCESSO!``"

    async def add_money(self, ctx, amount, ext=False):

        data_user = self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        change = randint(1, 100)
        msg = None
        answer = quant_etherny(amount)

        if data_user is not None:
            if update_user['user']['ranking'] == 'Bronze':
                await self.add_type(ctx, (answer['amount'] * 1), answer['list'])
                msg = f"**{answer['amount']}** ``Ethernyas``"
            elif update_user['user']['ranking'] == 'Silver':
                if change <= 75:
                    await self.add_type(ctx, (answer['amount'] * 1), answer['list'])
                    msg = f"**{answer['amount']}** ``Ethernyas``"
                else:
                    answer['list'][0] = (answer['list'][0] * 2)
                    answer['list'][1] = (answer['list'][1] * 2)
                    answer['list'][2] = (answer['list'][2] * 2)
                    await self.add_type(ctx, (answer['amount'] * 2), answer['list'])
                    msg = f"**{answer['amount'] * 2}** ``Ethernyas``"
            elif update_user['user']['ranking'] == 'Gold':
                if change <= 75:
                    await self.add_type(ctx, (answer['amount'] * 1), answer['list'])
                    msg = f"**{answer['amount']}** ``Ethernyas``"
                elif change <= 95:
                    answer['list'][0] = (answer['list'][0] * 2)
                    answer['list'][1] = (answer['list'][1] * 2)
                    answer['list'][2] = (answer['list'][2] * 2)
                    await self.add_type(ctx, (answer['amount'] * 2), answer['list'])
                    msg = f"**{answer['amount'] * 2}** ``Ethernyas``"
                else:
                    answer['list'][0] = (answer['list'][0] * 3)
                    answer['list'][1] = (answer['list'][1] * 3)
                    answer['list'][2] = (answer['list'][2] * 3)
                    await self.add_type(ctx, (answer['amount'] * 3), answer['list'])
                    msg = f"**{answer['amount'] * 3}** ``Ethernyas``"
            if ext:
                msg += f"\n``Sendo Elas:``\n" \
                       f"**{answer['list'][0]}**  {self.bot.money[0]}\n" \
                       f"**{answer['list'][1]}**  {self.bot.money[1]}\n" \
                       f"**{answer['list'][2]}**  {self.bot.money[2]}\n"
            return msg

    async def add_reward(self, ctx, list_):
        data_user = self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        response = '``Caiu pra você:`` \n'
        for item in list_:
            amount = randint(1, 3)
            try:
                update_user['inventory'][item] += amount
            except KeyError:
                update_user['inventory'][item] = amount
            response += f"**{amount}**: ``{self.bot.items[item][1]}``\n"
        self.bot.db.update_data(data_user, update_user, 'users')
        response += "```Jogue de novo para ganhar mais!```"
        return response

    async def add_type(self, ctx, amount, etherny):
        # DATA DO MEMBRO
        data_user = self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        update_user['treasure']['bronze'] += etherny[0] * 2
        update_user['treasure']['silver'] += etherny[1] * 2
        update_user['treasure']['gold'] += etherny[2] * 2
        update_user['treasure']['money'] += amount * 2
        self.bot.db.update_data(data_user, update_user, 'users')

        # DATA NATIVA DO SERVIDOR
        data_guild_native = self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        update_guild_native['data']['total_bronze'] += etherny[0] * 2
        update_guild_native['data']['total_silver'] += etherny[1] * 2
        update_guild_native['data']['total_gold'] += etherny[2] * 2
        update_guild_native['data']['total_money'] += amount * 2
        self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')

        # DATA DO SERVIDOR ATUAL
        data_guild = self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update_guild = data_guild
        update_guild['treasure']['total_bronze'] += etherny[0]
        update_guild['treasure']['total_silver'] += etherny[1]
        update_guild['treasure']['total_gold'] += etherny[2]
        update_guild['treasure']['total_money'] += amount
        self.bot.db.update_data(data_guild, update_guild, 'guilds')

    async def is_registered(self, ctx, **kwargs):
        if ctx.guild is not None:
            data_guild = self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
            data_user = self.bot.db.get_data("user_id", ctx.author.id, "users")

            update_user = data_user

            if data_guild is None:
                raise commands.CheckFailure('<:negate:520418505993093130>│``Sua guilda ainda não está registrada, por '
                                            'favor digite:`` **ash register guild** ``para cadastrar sua guilda '
                                            'no meu`` **banco de dados!**')

            if data_user is not None:
                try:
                    if kwargs.get("cooldown"):
                        time_diff = (datetime.datetime.utcnow() - epoch).total_seconds() \
                                     - update_user["cooldown"][str(ctx.command)]

                        time_left = kwargs.get("time") - time_diff

                        if time_diff < kwargs.get("time"):
                            raise commands.CheckFailure(f'<:negate:520418505993093130>│**Aguarde**: `Você deve '
                                                        f'esperar` **{{}}** `para usar esse comando '
                                                        f'novamente!`'.format(parse_duration(int(time_left))))
                        if self.bot.guilds_commands[ctx.guild.id] > 50 or str(ctx.command) != "daily work":
                            update_user['cooldown'][str(ctx.command)] = (datetime.datetime.utcnow()
                                                                         - epoch).total_seconds()
                except KeyError:
                    if self.bot.guilds_commands[ctx.guild.id] > 50 or str(ctx.command) != "daily work":
                        try:
                            update_user['cooldown'][str(ctx.command)] = (datetime.datetime.utcnow()
                                                                         - epoch).total_seconds()
                        except KeyError:
                            update_user['cooldown'] = {str(ctx.command): (datetime.datetime.utcnow() -
                                                                          epoch).total_seconds()}

                if self.bot.guilds_commands[ctx.guild.id] > 50 or str(ctx.command) != "daily work":
                    self.bot.db.update_data(data_user, update_user, 'users')

                if kwargs.get("g_vip") and data_guild['vip']:
                    return True
                elif kwargs.get("g_vip") and data_guild['vip'] is False:
                    raise commands.CheckFailure("<:negate:520418505993093130>│``APENAS SERVIDORES COM VIP ATIVO PODEM "
                                                "USAR ESSE COMANDO``\n **Para ganhar seu vip ATIVO DE SERVIDOR, O LIDER"
                                                " DA GUILDA precisa alcançar pelo menos 10 das 20 estrelas de "
                                                "recomendação**\n **OBS:** ``para ganhar recomendação é necessário usar"
                                                " o comando`` **ash daily rec** ``na pessoa que você deseja "
                                                "recomendar``")

                if kwargs.get("vip") and data_user['config']['vip']:
                    return True
                elif kwargs.get("vip") and data_user['config']['vip'] is False:
                    raise commands.CheckFailure("<:negate:520418505993093130>│``APENAS USUARIOS COM VIP ATIVO PODEM "
                                                "USAR ESSE COMANDO``\n **Para ganhar seu vip diário use ASH INVITE "
                                                "entre no meu canal de suporte e use o comando ASH VIP**")

                return True
            else:
                raise commands.CheckFailure(t_(ctx, f'<:negate:520418505993093130>│``Você ainda não está registrado, '
                                                    f'por favor use`` **ash register**.',
                                                    "guilds"))
        else:
            return True


class DataInteraction(object):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    def get_language(self, guild: str):
        data = self.db.get_data("guild_id", guild, "guilds")
        lang = data["data"].get("lang", "pt")
        return lang

    def set_language(self, guild: str, language):
        data = self.db.get_data("guild_id", guild, "guilds")
        update = data
        update['data'].__delitem__("lang")
        update["data"].__setitem__("lang", language)
        self.db.update_data(data, update, "guilds")

    async def add_experience(self, message, exp):
        record = self.db.get_data("user_id", message.author.id, "users")
        update = record
        if record is not None:
            try:
                if message.author.id == record["user_id"]:
                    time_diff = (datetime.datetime.utcnow() - epoch).total_seconds() - record["user"]['xp_time']
                    if time_diff >= 60:
                        change = randint(1, 200)
                        if 10 < update['user']['level'] < 20 and update['user']['ranking'] is not None:
                            if change == 200 and update['user']['ranking'] == "Bronze":
                                update['user']['ranking'] = "Silver"
                                update['inventory']['coins'] += 100
                                if not message.guild.id == 425864977996578816:
                                    try:
                                        await message.channel.send(
                                            '🎊 **PARABENS** 🎉 {} ``você upou para o ranking`` **{}** ``e ganhou a``'
                                            ' **chance** ``de garimpar mais ethernyas a partir de agora e`` **+100** '
                                            '``Fichas para jogar``'.format(message.author, "Silver"))
                                    except discord.errors.Forbidden:
                                        pass
                        elif 20 < update['user']['level'] < 30 and update['user']['ranking'] is not None:
                            if change == 200 and update['user']['ranking'] == "Silver":
                                update['user']['ranking'] = "Gold"
                                update['inventory']['coins'] += 200
                                if not message.guild.id == 425864977996578816:
                                    try:
                                        await message.channel.send(
                                            '🎊 **PARABENS** 🎉 {} ``você upou para o ranking`` **{}** ``e ganhou a``'
                                            ' **chance** ``de garimpar mais eternyas do que o ranking passado a partir '
                                            'de agora e`` **+200** ``Fichas para '
                                            'jogar``'.format(message.author, "Gold"))
                                    except discord.errors.Forbidden:
                                        pass
                        if message.guild.id == update['guild_id']:
                            update["guild_id"] = message.guild.id
                            update["guild_name"] = message.guild.name
                        update["user_name"] = message.author.name
                        update['user']['experience'] += exp * update['user']['level']
                        update["user"]['xp_time'] = (datetime.datetime.utcnow() - epoch).total_seconds()
                        self.db.update_data(record, update, "users")
            except KeyError:
                if message.author.id == record["user_id"]:
                    update["user"]['xp_time'] = (datetime.datetime.utcnow() - epoch).total_seconds()
                    self.db.update_data(record, update, "users")

    async def level_up(self, message):
        data = self.db.get_data("user_id", message.author.id, "users")
        update = data
        if data is not None:
            if message.author.id == data["user_id"]:
                experience = update['user']['experience']
                lvl_anterior = update['user']['level']
                lvl_now = int(experience ** (1 / 5))
                if lvl_anterior < lvl_now:
                    update['user']['level'] = lvl_now
                    update['inventory']['coins'] += 20
                    self.db.update_data(data, update, "users")
                    if not message.guild.id == 425864977996578816:
                        try:
                            await message.channel.send('🎊 **PARABENS** 🎉 {} ``você upou para o level`` **{}** ``e '
                                                       'ganhou`` **+20** ``Fichas para '
                                                       'jogar``'.format(message.author, lvl_now))
                        except discord.errors.Forbidden:
                            pass

    async def add_battle(self, ctx):
        data = self.db.get_data("user_id", ctx.author.id, "users")
        update = data
        if data is not None:
            if ctx.author.id == data["user_id"]:
                update['config']['battle'] = True
                update['config']['provinces'] = str(ctx.channel)
                self.db.update_data(data, update, "users")

    async def remove_battle(self, ctx):
        data = self.db.get_data("user_id", ctx.author.id, "users")
        update = data
        if data is not None:
            if ctx.author.id == data["user_id"]:
                update['config']['battle'] = False
                update['config']['provinces'] = None
                self.db.update_data(data, update, "users")

    async def add_announcement(self, ctx, announce):
        date = datetime.datetime(*datetime.datetime.utcnow().timetuple()[:6])
        data = {
            "_id": ctx.author.id,
            "data": {
                "status": False,
                "announce": announce,
                "date": "{}".format(date)
            }
        }
        self.db.push_data(data, "announcements")
        await ctx.send('<:confirmado:519896822072999937>│``Anuncio cadastrado com sucesso!``\n```AGUARDE APROVAÇÃO```')
        pending = self.bot.get_channel(619969149791240211)
        msg = f"{ctx.author.id}: **{ctx.author.name}** ``ADICIONOU UM NOVO ANUNCIO PARA APROVAÇÃO!``"
        await pending.send(msg)

    async def get_rank_xp(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['user'].get('experience')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_level(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['user'].get('level')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_money(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['treasure'].get('money')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.2f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > R$ " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_gold(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['treasure'].get('gold')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_silver(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['treasure'].get('silver')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_bronze(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['treasure'].get('bronze')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_point(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            if _['config'].get('points') is not None:
                dict_[str(_.get('user_id'))] = _['config'].get('points')
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    async def get_rank_commands(self, limit):
        data = self.db.get_all_data("users")
        dict_ = dict()
        for _ in data:
            dict_[str(_.get('user_id'))] = _['user'].get('commands', 0)
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=True)
        cont['list'] = 0

        def money_(money):
            a = '{:,.0f}'.format(float(money))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def counter():
            global cont
            cont['list'] += 1
            return cont['list']

        rank = "\n".join([str(counter()) + "º: " +
                          str(await self.bot.fetch_user(int(sorted_x[x][0]))).replace("'", "").replace("#", "_") +
                          " > " + str(money_(sorted_x[x][1])) for x in range(limit)])
        return rank

    def add_vip(self, **kwargs):
        if kwargs.get("target") == "users":
            data = self.db.get_data("user_id", kwargs.get("user_id"), "users")
            update = data
            if kwargs.get("state"):
                update['config']['vip'] = True
            else:
                update['config']['vip'] = False
            self.db.update_data(data, update, "users")
        elif kwargs.get("target") == "guilds":
            data = self.db.get_data("guild_id", kwargs.get("guild_id"), "guilds")
            update = data
            if kwargs.get("state"):
                update['vip'] = True
            else:
                update['vip'] = False
            self.db.update_data(data, update, "guilds")
