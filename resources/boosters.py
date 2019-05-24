from random import randint, choice


class Booster(object):
    def __init__(self, items_):
        self.items = items_
        self.ranking = None
        self.is_vip = None
        self.item_ = None
        self.legend = {"Comum": 0, "Normal": 1, "Raro": 2, "Super Raro": 3, "Ultra Raro": 4, "Secret": 5}
        self.rarity = {"Comum": 500, "Normal": 400, "Raro": 300, "Super Raro": 200, "Ultra Raro": 150, "Secret": 100}
        self.booster_choice = None
        self.booster_bronze = {"Comum": 95, "Normal": 1, "Raro": 1, "Super Raro": 1, "Ultra Raro": 1, "Secret": 1}
        self.booster_silver = {"Comum": 60, "Normal": 36, "Raro": 1, "Super Raro": 1, "Ultra Raro": 1, "Secret": 1}
        self.booster_gold = {"Comum": 50, "Normal": 46, "Raro": 1, "Super Raro": 1, "Ultra Raro": 1, "Secret": 1}
        self.booster_vip = {"Comum": 50, "Normal": 30, "Raro": 15, "Super Raro": 2, "Ultra Raro": 1, "Secret": 1}
        self.booster_secret = {"Comum": 40, "Normal": 30, "Raro": 20, "Super Raro": 8, "Ultra Raro": 2, "Secret": 1}
        self.box = {"status": {"active": True, "secret": 0, "ur": 0, "sr": 0, "r": 0, "n": 0, "c": 0}}

        # contadores de itens
        self.secret = 0
        self.ur = 0
        self.sr = 0
        self.r = 0
        self.n = 0
        self.c = 0

        # contador de itens por box
        self.box_count = 0

        # Limites dos itens
        self.l_secret = 1  # 1 item de limite
        self.l_ur = 2 * len([x for x in self.items.keys() if self.items[x][3] == 4])  # 20 itens
        self.l_sr = 3 * len([x for x in self.items.keys() if self.items[x][3] == 3])  # 57 itens
        self.l_r = 6 * len([x for x in self.items.keys() if self.items[x][3] == 2])  # 36 itens
        self.l_n = 28 * len([x for x in self.items.keys() if self.items[x][3] == 1])  # 308 itens
        self.l_c = 60 * len([x for x in self.items.keys() if self.items[x][3] == 0])  # 600 itens

    def reset_counts(self):
        self.box = {"status": {"active": True, "secret": 0, "ur": 0, "sr": 0, "r": 0, "n": 0, "c": 0}}
        self.box_count = 0
        self.secret = 0
        self.ur = 0
        self.sr = 0
        self.r = 0
        self.n = 0
        self.c = 0

    def create_booster(self, ranking, is_vip):
        self.reset_counts()
        self.ranking = ranking
        self.is_vip = is_vip
        rarity = choice(list(self.rarity.keys()))
        size = self.rarity[rarity]
        self.box['status']['rarity'] = rarity
        self.box['status']['size'] = size
        self.box['items'] = dict()
        while self.box_count < size:
            item: object = choice(list(self.items.keys()))
            if self.items[item][3] == 5:
                if self.secret < self.l_secret:
                    if item not in self.box['items']:
                        self.box['items'][item] = {"size": 1, "data": self.items[item]}
                        self.box['status']['secret'] += 1
                    self.secret += 1
                    self.box_count += 1
            elif self.items[item][3] == 4:
                if self.ur < self.l_ur:
                    if item not in self.box['items']:
                        self.box['items'][item] = {"size": 1, "data": self.items[item]}
                        self.box['status']['ur'] += 1
                    else:
                        self.box['items'][item]['size'] += 1
                        self.box['status']['ur'] += 1
                    self.ur += 1
                    self.box_count += 1
            elif self.items[item][3] == 3:
                if self.sr < self.l_sr:
                    if item not in self.box['items']:
                        self.box['items'][item] = {"size": 1, "data": self.items[item]}
                        self.box['status']['sr'] += 1
                    else:
                        self.box['items'][item]['size'] += 1
                        self.box['status']['sr'] += 1
                    self.sr += 1
                    self.box_count += 1
            elif self.items[item][3] == 2:
                if self.r < self.l_r:
                    if item not in self.box['items']:
                        self.box['items'][item] = {"size": 1, "data": self.items[item]}
                        self.box['status']['r'] += 1
                    else:
                        self.box['items'][item]['size'] += 1
                        self.box['status']['r'] += 1
                    self.r += 1
                    self.box_count += 1
            elif self.items[item][3] == 1:
                if self.n < self.l_n:
                    if item not in self.box['items']:
                        self.box['items'][item] = {"size": 1, "data": self.items[item]}
                        self.box['status']['n'] += 1
                    else:
                        self.box['items'][item]['size'] += 1
                        self.box['status']['n'] += 1
                    self.n += 1
                    self.box_count += 1
            elif self.items[item][3] == 0:
                if self.c < self.l_c:
                    if item not in self.box['items']:
                        self.box['items'][item] = {"size": 1, "data": self.items[item]}
                        self.box['status']['c'] += 1
                    else:
                        self.box['items'][item]['size'] += 1
                        self.box['status']['c'] += 1
                    self.c += 1
                    self.box_count += 1
        return self.box

    def buy_item(self, box_, ranking, is_vip):
        self.ranking = ranking
        self.is_vip = is_vip

        if self.ranking == "Bronze":
            self.booster_choice = self.booster_bronze
        elif self.ranking == "Silver":
            self.booster_choice = self.booster_silver
        elif self.ranking == "Gold":
            self.booster_choice = self.booster_gold

        if self.is_vip:
            self.booster_choice = self.booster_bronze

        chance = randint(1, 100)
        if chance == 100:
            self.booster_choice = self.booster_secret

        list_items = []
        for i_, amount in self.booster_choice.items():
            list_items += [i_] * amount
        result = choice(list_items)

        self.item_ = choice(list(box_['items'].values()))
        while list(self.legend.keys())[list(self.legend.values()).index(self.item_['data'][-2])] != result:
            self.item_ = choice(list(box_['items'].values()))

        return self.item_
