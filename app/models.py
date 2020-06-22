from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import sys


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registered = db.Column(db.DateTime, default=datetime.utcnow)
    prismPower = db.Column(db.Integer, default=0, index=True)
    heroPower = db.Column(db.Integer, default=0, index=True)
    artifactPower = db.Column(db.Integer, default=0, index=True)
    daysPlayed = db.Column(db.Integer, default=0, index=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    heroes = db.relationship('Hero', backref='player', lazy='dynamic')
    artifacts = db.relationship('Artifact', backref='owner', lazy='dynamic')
    bossteams = db.relationship('Bossteam', backref='manager', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def registered_proper(self, date):
        proper = date.strftime("%Y-%m-%d")
        return proper

    def total_power(self):
        prism = self.prismPower
        hero = self.heroPower
        art = self.artifactPower
        total = prism+hero+art
        return '{:,}'.format(total).replace(',', ' ')

    def power_per_day(self):
        total = int(self.prismPower + self.heroPower + self.artifactPower)
        days = self.daysPlayed
        # Avoid zero divison if days played = 0
        if days == 0:
            return '{:,}'.format(total).replace(',', ' ')
        total = int(total/days)
        return '{:,}'.format(total).replace(',', ' ')

    def art_display(self, x):
        return '{:,}'.format(x).replace(',', ' ')

    def art_atk(self, element):
        """ Calculate the attack bonus from a users artifacts (including set bonus) for a given element.

        :param element: Element to calculate
        :return: An integer of attack bonus
        """
        artifacts = self.artifacts
        attack = 0
        # handle the special case of Gun Lord artifacts, effect is halved above 5.000.000 power
        glBreak = 5000000

        for artifact in artifacts:
            if artifact.artBase.element == element or artifact.artBase.element == "All":
                attack += artifact.artBase.atk + ((artifact.level - 1) * artifact.artBase.atkLevel)
            # Special case of Gun Lord artifact(s), only 79 (Soul Hands) matter from a damage perspective
            if artifact.artBase.id == 79:
                if self.heroPower < glBreak:
                    attack += (0.005 + (0.001 * artifact.level)) * self.heroPower
                else:
                    attack += (0.005 + (0.001 * artifact.level)) * (glBreak + ((self.heroPower - glBreak) / 2))

        vulcan = 0  # 16, 17, 18
        abaddon = 0  # 1, 2, 3
        phoenix = 0  # 34, 35, 36
        abyssal = 0  # 19, 20, 21
        efreeti = 0  # 37, 38, 39
        hades = 0  # 43, 44, 45

        # Calculate full sets of artifacts, adding 1 to set name per artifact, using the IDs
        for artifact in artifacts:
            if artifact.artbase_id == 16 or artifact.artbase_id == 17 or artifact.artbase_id == 18:
                vulcan += 1
            elif artifact.artbase_id == 1 or artifact.artbase_id == 2 or artifact.artbase_id == 3:
                abaddon += 1
            elif artifact.artbase_id == 34 or artifact.artbase_id == 35 or artifact.artbase_id == 36:
                phoenix += 1
            elif artifact.artbase_id == 19 or artifact.artbase_id == 20 or artifact.artbase_id == 21:
                abyssal += 1
            elif artifact.artbase_id == 37 or artifact.artbase_id == 38 or artifact.artbase_id == 39:
                efreeti += 1
            elif artifact.artbase_id == 43 or artifact.artbase_id == 44 or artifact.artbase_id == 45:
                hades += 1

        # Artifact set names, comments are their ID in ArtBase
        if vulcan == 3:
            attack += 10000
        if abaddon == 3:
            attack += 10000
        if phoenix == 3:
            attack += 4000
        if abyssal == 3:
            attack += 4000
        if hades == 3:
            attack += 1000
        return int(round(attack))

    def art_crit(self):
        artifacts = self.artifacts
        crit = 0
        phoenix = 0  # 34, 35, 36
        efreeti = 0  # 37, 38, 39
        for artifact in artifacts:
            if artifact.artbase_id == 34 or artifact.artbase_id == 35 or artifact.artbase_id == 36:
                phoenix += 1
            elif artifact.artbase_id == 37 or artifact.artbase_id == 38 or artifact.artbase_id == 39:
                efreeti += 1
        if phoenix == 3:
            crit += 15
        if efreeti == 3:
            crit += 10
        return crit

    def art_aps(self):
        artifacts = self.artifacts
        aps = 0
        atlantis = 0  # 13, 14, 15
        mermaid = 0  # 31, 32, 33
        poseidon = 0  # 49, 50, 51
        zeus = 0  # 52, 53, 54

        # Calculate full sets of artifacts, adding 1 to set name per artifact, using the IDs
        for artifact in artifacts:
            if artifact.artbase_id == 13 or artifact.artbase_id == 14 or artifact.artbase_id == 15:
                atlantis += 1
            elif artifact.artbase_id == 31 or artifact.artbase_id == 32 or artifact.artbase_id == 33:
                mermaid += 1
            elif artifact.artbase_id == 49 or artifact.artbase_id == 50 or artifact.artbase_id == 51:
                poseidon += 1
            elif artifact.artbase_id == 52 or artifact.artbase_id == 53 or artifact.artbase_id == 54:
                zeus += 1

        if atlantis == 3:
            aps += 20
        if mermaid == 3:
            aps += 15
        if poseidon == 3:
            aps += 10
        if zeus == 3:
            aps += 10
        return aps

    def art_crit_dmg(self, element):
        artifacts = self.artifacts
        crit_dmg = 0
        for artifact in artifacts:
            if artifact.artBase.element == element or artifact.artBase.element == "All":
                crit_dmg += artifact.artBase.critDmg + ((artifact.level - 1) * artifact.artBase.critDmgLevel)
        return int(round(crit_dmg, 0))

    def raid_team(self, team, team_list, heroes, boss, art):
        """ Calculate the optimal damage team for the current boss

        :param team: Dictionary to populate with top performing heroes, Key = hero name, Value = DPS
        :param team_list: Empty list to fill with heroes for calculations
        :param heroes: List of all heroes to calculate
        :param boss: Dictionary with the current boss's class weakness and elemental advantages
        :param art: Dictionary with the current users artifact bonus
        :return: Dictionary with the optimal team for the current boss, Key = hero name, Value = DPS
        """
        print(f"{datetime.now()} | TEAM SIZE {len(team_list)}", file=sys.stderr)
        high = sum(team.values())   # Used to calculate the top performing hero
        low = 1000000000000000      # Used to calculate the bottom performing hero (gotta be a better way)
        top = ""                    # Placeholder for top performing hero
        bottom = ""                 # Placeholder for bottom performing hero

        # Break out of recursion when team_list contain 10 heroes = team is full
        if len(team_list) == 10:
            for hero in team_list:
                team[hero.baseStats.name] = int(hero.raid_dps(self.raidbuffs(team_list, hero.baseStats.element), boss, art))
            return team

        # Handle input of less than 10 heroes, but still with correct ranking
        # At each recursion the top performing hero is removed from 'heroes', this will catch users with < 10 heroes
        if len(heroes) == 0:
            filler = len(team_list)
            for hero in team_list:
                team[hero.baseStats.name] = int(hero.raid_dps(self.raidbuffs(team_list, hero.baseStats.element), boss, art))
            for n in range(filler+1, 11):
                team["Slot "+str(n)] = 0
            return team

        # Iterate over all the users heroes to find the top performing one
        for consider in heroes:
            print(f"{datetime.now()} | CONSIDERING {consider}", file=sys.stderr)
            team_list.append(consider)
            # Calculate every hero in team_list in combination with the currently considered hero
            for hero in team_list:
                print(f"{datetime.now()} | Calculating {hero} with {consider}", file=sys.stderr)
                dmg = int(hero.raid_dps(self.raidbuffs(team_list, hero.baseStats.element), boss, art))
                team[hero.baseStats.name] = dmg
            print(f"{datetime.now()} | CALCULATIONS WITH {consider} COMPLETE", file=sys.stderr)
            if sum(team.values()) > high:
                high = sum(team.values())
                print(f"> Top: {consider}", file=sys.stderr)
                top = consider
            elif sum(team.values()) < low:
                print(f"> Bottom: {consider}", file=sys.stderr)
                low = sum(team.values())
                bottom = consider
            team_list.remove(consider)
            del team[consider.baseStats.name]

        team_list.append(top)
        team[top.baseStats.name] = int(top.raid_dps(self.raidbuffs(team_list, top.baseStats.element), boss, art))
        heroes.remove(top)
        # Remove the bottom performing hero if it's safe to do so
        # A bottom performing hero in the first recursion could hold a valuable buff (i.e. Kage)
        if len(heroes) > 20 and len(team_list) > 0:
            heroes.remove(bottom)
            print(f"RECURSION: removed {bottom}", file=sys.stderr)
        print(f"RECURSION: added {top}", file=sys.stderr)
        return self.raid_team(team, team_list, heroes, boss, art)

    def filter_heroes(self, heroes, boss, art):
        """ Filter a users heroes before the raidTeam algorithm.
        Heroes with no chance of making a top 10 team for the current boss are ruled out.

        :param heroes: List of all heroes for the current user
        :param boss: Dictionary with the current boss's class weakness and elemental advantages
        :param art: Dictionary with the current users artifact bonus
        :return: A filtered list of heroes, reduced to only those who could make the top 10
        """

        team = {}   # Dictionary to populate with current users hero's and their max dps including all available buffs
        keep = []   # List to fill with heroes to keep

        # Populate dictionary where Key = Hero, and Value = the hero's dps including all buffs
        for hero in heroes:
            print(f"...{hero}", file=sys.stderr)
            team[hero] = int(hero.raid_dps(self.raidbuffs(heroes, hero.baseStats.element), boss, art))
        print(f"filter_heroes - Dictionary complete", file=sys.stderr)
        # Add all heroes with a damage affecting buff
        print(f"filter_heroes - Adding damage affecting heroes", file=sys.stderr)
        for buff_hero in team:
            if buff_hero.baseStats.buffType == 1 and buff_hero.level > 3:
                keep.append(buff_hero)

        # Add additional 10 top performing heroes not included from above
        print(f"filter_heroes - Adding 10 top performing heroes", file=sys.stderr)
        for i in range(10):
            filler_hero = max(team, key=team.get)
            print(f"...consider {filler_hero}", file=sys.stderr)
            if filler_hero not in keep:
                keep.append(filler_hero)
                print(f"...added {filler_hero}", file=sys.stderr)
            del team[filler_hero]

        return keep

    def raidbuffs(self, heroes, element):
        """ Get all active buffs in the current team affecting the hero being calculated

        :param heroes: Current team (1-10 heroes)
        :param element: Element of the hero being calculated
        :return: Dictionary of buffs affecting the hero being calculated
        """
        buffs = {
            "atk": 0,
            "aps": 0,
            "critDmg": 0,
            "kage": 1
            }
        for hero in heroes:
            if hero.baseStats.buffType == 1 and hero.level > 3:
                # Only count buffs of the same element (and 'All') as the hero being calculated.
                if hero.baseStats.buffElement == element or hero.baseStats.buffElement == 'All':
                    buffs[hero.baseStats.buffStat] = buffs.get(hero.baseStats.buffStat) + (hero.baseStats.buff*(hero.level-3))
        return buffs


class BossBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    nameSafe = db.Column(db.String(32), index=True, unique=True)
    bosses = db.relationship('Bossteam', backref='bossBase', lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)


class Bossteam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero = db.Column(db.String(16), index=True)
    damage = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bossbase_id = db.Column(db.Integer, db.ForeignKey('boss_base.id'))

    def __repr__(self):
        return '<{}: {}>'.format(self.hero, self.damage)


class ArtBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    star = db.Column(db.Integer, index=True)
    name = db.Column(db.String(32), index=True)
    atk = db.Column(db.Integer, index=True)
    atkLevel = db.Column(db.Integer, index=True)
    critDmg = db.Column(db.Integer, index=True)
    critDmgLevel = db.Column(db.Integer, index=True)
    element = db.Column(db.String(16), index=True)
    color = db.Column(db.String(16), index=True)
    artifacts = db.relationship('Artifact', backref='artBase', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Artifact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, default=0, index=True)
    type = db.Column(db.String(16), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    artbase_id = db.Column(db.Integer, db.ForeignKey('art_base.id'))


class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, index=True)
    awaken = db.Column(db.Integer, index=True)
    wpn = db.Column(db.Integer, index=True)
    medals = db.Column(db.Integer, index=True)
    runedAtk = db.Column(db.Integer, index=True)
    runedHp = db.Column(db.Integer, index=True)
    runedDef = db.Column(db.Integer, index=True)
    runedAps = db.Column(db.Integer, index=True)
    runedCrit = db.Column(db.Integer, index=True)
    runedCritDmg = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    base_id = db.Column(db.Integer, db.ForeignKey('base.id'))

    def display_stat(self, stat):
        if stat < 1000:
            return str(int(round(stat, 0)))
        elif stat > 1000000:
            return str(round(stat/1000000, 2))+"M"
        else:
            return str(round(stat/1000, 2))+"K"

    def display_aps(self, aps):
        return round(aps, 2)

    def display_other(self, x):
        # Space divide thousands for HP and ATK
        return '{:,}'.format(x).replace(',', ' ')

    def atk(self):
        runedAttack = self.runedAtk
        base = self.baseStats.atk
        level = self.level
        awaken = self.awaken
        atk = int(base * (2 ** (level - 1)) * (1.5 ** awaken))
        runedAtk = atk + (atk * (runedAttack / 100))
        return int(runedAtk)

    def raid_atk(self, art, buff, weakness):
        """ Calculate a hero's attack within the current team against the current boss

        :param art: Attack bonus from artifacts for the current hero
        :param buff: Active attack team buffs affecting the current hero
        :param weakness: Current boss weakness to current hero's class
        :return: An integer, the hero's attack within the given raid environment
        """
        runedAttack = self.runedAtk
        base = self.baseStats.atk
        level = self.level
        awaken = self.awaken
        atk = base * (2 ** (level - 1)) * (1.5 ** awaken)
        runedAtk = (atk + (atk * ((runedAttack+art) / 100))) * self.baseStats.crusher * weakness + atk * buff / 100
        return runedAtk

    def hp(self):
        runedHP = self.runedHp
        base = self.baseStats.hp
        level = self.level
        awaken = self.awaken
        hp = int(base * (2 ** (level - 1)) * (1.5 ** awaken))
        runedHP = hp + (hp * (runedHP / 100))
        return int(runedHP)

    def defense(self):
        runedDef = self.runedDef
        base = self.baseStats.defense
        level = self.level
        awaken = self.awaken
        defense = int(base * (2 ** (level - 1)) * (1.5 ** awaken))
        runedDef = defense + (defense * (runedDef / 100))
        return int(runedDef)

    def aps(self):
        runedAps = self.runedAps
        base = self.baseStats.aps
        runedAps = base + (base * (runedAps / 100))
        return runedAps

    def raid_aps(self, art, buff):
        runedAps = self.runedAps
        base = self.baseStats.aps
        runedAps = base + (base * ((runedAps+art+buff) / 100))
        return runedAps

    def crit(self):
        runedCrit = self.runedCrit
        base = self.baseStats.crit
        return (base + runedCrit)/100

    def raid_crit(self, art):
        runedCrit = self.runedCrit
        base = self.baseStats.crit
        return (base + runedCrit + art)/100

    def critDmg(self):
        runedDmg = self.runedCritDmg
        base = self.baseStats.critDmg
        return (base + runedDmg)/100

    def raid_crit_dmg(self, art, buff):
        runedDmg = self.runedCritDmg
        base = self.baseStats.critDmg
        return (base + runedDmg + art + buff)/100

    def crit_dmg_display(self):
        runedDmg = self.runedCritDmg
        base = self.baseStats.critDmg
        return base + runedDmg

    def dps(self):
        atk = self.atk()
        aps = self.aps()
        crit = self.crit()
        critDmg = self.critDmg()
        dps = (atk * aps * (1-crit)) + (atk * aps * crit * critDmg)
        dps = int(round(dps))
        return atk, aps, crit, critDmg, dps

    def dps_sp2(self):
        sp2 = self.baseStats.sp2
        sp2num = self.baseStats.sp2num
        atk = self.atk()
        aps = self.aps()
        crit = self.crit()
        critDmg = self.critDmg()
        dps = ((atk * aps * (1-crit)) + (atk * aps * crit * (1+critDmg))) * (6 + sp2 * sp2num)/7
        dps = int(round(dps))
        return '{:,}'.format(dps).replace(',', ' ')

    def raid_dps(self, buff, boss, art):
        """ Calculate a hero's raid dps including team buffs, artifacts, boss weakness and elemental advantage

        :param buff: Dictionary with active buffs for current hero within current team
        :param boss: Dictionary with current boss's class weakness and elemental advantage
        :param art: Dictionary with artifact bonus affecting current hero
        :return: Current hero's dps within the set raid environment
        """
        sp2 = self.baseStats.sp2
        sp2num = self.baseStats.sp2num
        if self.baseStats.fly == 1:
            atk = self.raid_atk(art['atk'][self.baseStats.element], buff['atk'], boss[self.baseStats.job] + boss['Fly'])
        else:
            atk = self.raid_atk(art['atk'][self.baseStats.element], buff['atk'], boss[self.baseStats.job])
        aps = self.raid_aps(self.player.art_aps(), buff['aps'])
        crit = self.raid_crit(self.player.art_crit())
        critDmg = self.raid_crit_dmg(self.player.art_crit_dmg(self.baseStats.element), buff['critDmg'])

        # elemental advantage, multiplicative
        atk *= boss[self.baseStats.element]

        # dps formula
        dps = ((atk * aps * (1-crit)) + (atk * aps * crit * (1+critDmg))) * (6 + sp2 * sp2num)/7
        dps = int(round(dps))

        # Kage
        dps *= buff["kage"]
        # print(f"{datetime.now()} | ### RAIDDPS FINISHED FOR {self.baseStats.name} ### |", file=sys.stderr)
        return dps

    def progress(self):
        level = self.level
        medals = self.medals
        # 10, 30, 80, 280, 880, 2380, 4880
        if level == 0:
            accumulated = 0
            total = accumulated + medals
        elif level == 1:
            accumulated = 10
            total = accumulated + medals
        elif level == 2:
            accumulated = 30
            total = accumulated + medals
        elif level == 3:
            accumulated = 80
            total = accumulated + medals
        elif level == 4:
            accumulated = 280
            total = accumulated + medals
        elif level == 5:
            accumulated = 880
            total = accumulated + medals
        elif level == 6:
            accumulated = 2380
            total = accumulated + medals
        elif level == 7:
            accumulated = 4880
            total = accumulated + medals

        total = (total / 4880) * 100
        if total == 100:
            return int(total)
        return round(total, 2)

    def __repr__(self):
        return '{}'.format(self.baseStats.name)


class Base(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    nameSafe = db.Column(db.String(32), index=True, unique=True)
    job = db.Column(db.String(16), index=True)
    rarity = db.Column(db.String(16), index=True)
    element = db.Column(db.String(16), index=True)
    gender = db.Column(db.String(16), index=True)
    crusher = db.Column(db.Integer, index=True)
    fly = db.Column(db.Integer, index=True)
    blitz = db.Column(db.Integer, index=True)
    atk = db.Column(db.Integer, index=True)
    hp = db.Column(db.Integer, index=True)
    defense = db.Column(db.Integer, index=True)
    crit = db.Column(db.Integer, index=True)
    critDmg = db.Column(db.Integer, index=True)
    movespeed = db.Column(db.Integer, index=True)
    aps = db.Column(db.Integer, index=True)
    arange = db.Column(db.Integer, index=True)
    resistance = db.Column(db.Integer, index=True)
    frenzy = db.Column(db.Integer, index=True)
    dodge = db.Column(db.Integer, index=True)
    stun = db.Column(db.Integer, index=True)
    stunTime = db.Column(db.Integer, index=True)
    aoe = db.Column(db.Integer, index=True)
    ult = db.Column(db.Integer, index=True)
    kshp = db.Column(db.Integer, index=True)
    gold = db.Column(db.Integer, index=True)
    freeze = db.Column(db.Integer, index=True)
    freezeTime = db.Column(db.Integer, index=True)
    freezeDmg = db.Column(db.Integer, index=True)
    burn = db.Column(db.Integer, index=True)
    burnTime = db.Column(db.Integer, index=True)
    burnDmg = db.Column(db.Integer, index=True)
    poison = db.Column(db.Integer, index=True)
    poisonTime = db.Column(db.Integer, index=True)
    poisonDmg = db.Column(db.Integer, index=True)
    sp2 = db.Column(db.Integer, index=True)
    sp2num = db.Column(db.Integer, index=True)
    buffElement = db.Column(db.String(16), index=True)
    buffType = db.Column(db.Integer, index=True)
    buffStat = db.Column(db.String(16), index=True)
    buff = db.Column(db.Integer, index=True)

    heroes = db.relationship('Hero', backref='baseStats', lazy='dynamic')

    def __repr__(self):
        return '{} ({} {} {})'.format(self.name, self.rarity, self.element, self.job)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


def validate_level(level):
    if level < 0:
        level = 0
    elif level > 7:
        level = 7
    return level


def validate_awaken(awaken, level):
    # awaken cannot be greater than level
    if awaken > level:
        awaken = level
    return awaken


def validate_weapon(wpn, prev):
    if wpn < 0:
        wpn = prev
    elif wpn > 9:
        wpn = prev
    return wpn


def validate_medals(medals, level):
    accumulated = 0     # 10, 30, 80, 280, 880, 2380, 4880
    if level == 0:
        medals = 0
        return medals
    elif level == 1:
        accumulated = 10
    elif level == 2:
        accumulated = 30
    elif level == 3:
        accumulated = 80
    elif level == 4:
        accumulated = 280
    elif level == 5:
        accumulated = 880
    elif level == 6:
        accumulated = 2380
    elif level == 7:
        medals = 0
        return medals
    if accumulated + medals > 4880:
        medals = 4880
        medals -= accumulated
        return medals
    return medals


def hero_progress(user, element, rarity):
    # Query players hero based on element and rarity
    heroes = Hero.query.filter_by(player=user).join(Base).filter(Base.element==element, Base.rarity==rarity)
    # Placeholder variables for count of heroes within query, total progress, and maxed heroes
    count = 0
    total = 0
    maxed = 0
    for hero in heroes:
        count += 1
        total += hero.progress()
    for hero in heroes:
        if hero.level == 7:
            maxed += 1
    # Return average progress within element and rarity, amount of maxed heroes and count within same.
    return round(total/count, 2), maxed, count


def total_medals(user, element):
    heroes = Hero.query.filter_by(player=user).join(Base).filter(Base.element==element)
    total = 0
    max_medals = 0
    for hero in heroes:
        if hero.level == 1:
            total += 10
        elif hero.level == 2:
            total += 30
        elif hero.level == 3:
            total += 80
        elif hero.level == 4:
            total += 280
        elif hero.level == 5:
            total += 880
        elif hero.level == 6:
            total += 2380
        elif hero.level == 7:
            total += 4880
        total += hero.medals
        max_medals += 4880
    return total, max_medals


def rarity_medals(user, element, rarity):
    heroes = Hero.query.filter_by(player=user).join(Base).filter(Base.rarity == rarity, Base.element == element)
    total = 0
    for hero in heroes:
        if hero.level == 1:
            total += 10
        elif hero.level == 2:
            total += 30
        elif hero.level == 3:
            total += 80
        elif hero.level == 4:
            total += 280
        elif hero.level == 5:
            total += 880
        elif hero.level == 6:
            total += 2380
        elif hero.level == 7:
            total += 4880
        total += hero.medals
    return total


def validate_art(art, level):
    level = int(level)
    # spaghetti code for event artifacts because of poor table design in art_base
    three_star_event_art = [65, 69, 71, 72, 75, 78, 79, 80]
    four_star_event_art = [66, 67, 68, 70, 73, 74, 76, 77]

    # Make sure 7-star artifacts don't go above 60 (45+15 enhanced)
    if art.artBase.star == 7 and level > 60:
        level = 60
    # Same as above for 6-stars and level 55
    elif art.artBase.star == 6 and level > 55:
        level = 55
    # 5-star and 50
    elif art.artBase.star == 5 and level > 50:
        level = 50
    # 4-star and 45
    elif art.artBase.star == 4 and level > 45:
        level = 45
    # LEEROY
    elif art.artBase.id == 64 and level > 35:
        level = 35
    elif art.artBase.id in three_star_event_art and level > 40:
        level = 40
    elif art.artBase.id in four_star_event_art and level > 45:
        level = 45
    return level


def display_raid_dps(dmg):
    # Format dps within the thousand range
    if 1000 < dmg < 1000000:
        return str(round(dmg / 1000, 2)) + "K"
    # Format dps within the million range
    if 1000000 < dmg < 1000000000:
        return str(round(dmg / 1000000, 2)) + "M"
    # Format dps within the billion range
    elif 1000000000 < dmg < 1000000000000:
        return str(round(dmg / 1000000000, 2)) + "B"
    # ..within the Trillion range, you never know
    elif dmg > 1000000000000:
        return str(round(dmg / 1000000000000, 2)) + "T"
    # Damage below 1000
    return dmg


"""   
4-Star
four = [66, 67, 68, 70, 73, 74, 76, 77]
Frosty Sword            73
Frozen Flame            74
King's Gloves           77
King Rewards II         76
Samurai Helmet          70       
Cloak of Speed          68
Astro Time Warper II    66
Astro Head Start        67


3-Star
three = [65, 69, 71, 72, 75, 78, 79, 80] 
Frosty Shield           72
Frosty Dragon           71
King Rewards I          75
Flip Flops of Speed     69
Astro Time Warper I     65
Soul Hand               79
Soul Shield             80
Soul Boots              78

2-Star
Astrogem
----------
Set Bonus
Vulcan          10000%  ATK     ALL
Abaddon         10000%  ATK     ALL
Phoenix         4000%   ATK     ALL     15% CRIT ALL
Abyssal         4000%   ATK     ALL
Efreeti                                 10% CRIT ALL
Hades           1000%   ATK     ALL

Atlantis        20%     APS     ALL
Mermaid         15%     APS     ALL
Poseidon        10%     APS     ALL
Zeus            10%     APS     ALL
"""