from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from math import ceil


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

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def registeredProper(self, date):
        proper = date.strftime("%Y-%m-%d")
        return proper

    def totalPower(self):
        prism = self.prismPower
        hero = self.heroPower
        art = self.artifactPower
        total = prism+hero+art
        return '{:,}'.format(total).replace(',', ' ')

    def powerPerDay(self):
        total = int(self.prismPower + self.heroPower + self.artifactPower)
        days = self.daysPlayed
        # Avoid zero divison if days played = 0
        if days == 0:
            return '{:,}'.format(total).replace(',', ' ')
        total = int(total/days)
        return '{:,}'.format(total).replace(',', ' ')


class ArtBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    star = db.Column(db.Integer, index=True)
    name = db.Column(db.String(32), index=True)
    atk = db.Column(db.Integer, index=True)
    atkLevel = db.Column(db.Integer, index=True)
    critDmg = db.Column(db.Integer, index=True)
    critDmgLevel = db.Column(db.Integer, index=True)
    element = db.Column(db.String(16), index=True)
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

    def displayStat(self, stat):
        if stat < 1000:
            return str(int(round(stat, 0)))
        elif stat > 1000000:
            return str(round(stat/1000000, 2))+"M"
        else:
            return str(round(stat/1000, 2))+"K"

    def displayAps(self, aps):
        return round(aps, 2)

    def atk(self):
        # Temporary placeholder variable for runed values
        runedAttack = self.runedAtk
        base = self.baseStats.atk
        level = self.level
        awaken = self.awaken
        atk = int(base * (2 ** (level - 1)) * (1.5 ** awaken))
        runedAtk = atk + (atk * (runedAttack / 100))
        return int(runedAtk)


    def hp(self):
        # Temporary placeholder variable for runed values
        runedHP = self.runedHp
        base = self.baseStats.hp
        level = self.level
        awaken = self.awaken
        hp = int(base * (2 ** (level - 1)) * (1.5 ** awaken))
        runedHP = hp + (hp * (runedHP / 100))
        return int(runedHP)

    def defense(self):
        # Temporary placeholder variable for runed values
        runedDef = self.runedDef
        base = self.baseStats.defense
        level = self.level
        awaken = self.awaken
        defense = int(base * (2 ** (level - 1)) * (1.5 ** awaken))
        runedDef = defense + (defense * (runedDef / 100))
        return int(runedDef)

    def aps(self):
        # Temporary placeholder variable for runed values
        runedAps = self.runedAps
        base = self.baseStats.aps
        runedAps = base + (base * (runedAps / 100))
        return runedAps

    def crit(self):
        # Temporary placeholder variable for runed values
        runedCrit = self.runedCrit
        base = self.baseStats.crit
        return (base + runedCrit)/100

    def critDmg(self):
        # Temporary placeholder variable for runed values
        runedDmg = self.runedCritDmg
        base = self.baseStats.critDmg
        return (base + runedDmg)/100

    def critDmgDisplay(self):
        # Temporary placeholder variable for runed values
        runedDmg = 25.75
        base = self.baseStats.critDmg
        return base + runedDmg

    def dps(self):
        # (atk * aps * (1-crit rate)) + (atk  * aps * critRate * critDmg)
        atk = self.atk()
        aps = self.aps()
        crit = self.crit()
        critDmg = self.critDmg()
        dps = (atk * aps * (1-crit)) + (atk * aps * crit * critDmg)
        dps = int(round(dps))
        return '{:,}'.format(dps).replace(',', ' ')

    def dpsSP2(self):
        # (atk * aps * (1-crit rate)) + (atk  * aps * critRate * critDmg)
        sp2 = 1
        sp2num = 5
        atk = self.atk()
        aps = self.aps()
        crit = self.crit()
        critDmg = self.critDmg()
        dps = ((atk * aps * (1-crit)) + (atk * aps * crit * critDmg)) * (6 + sp2 * sp2num)/7
        #  x (6 + sp2_damage x sp2_num_attacks)/7
        dps = int(round(dps))
        return '{:,}'.format(dps).replace(',', ' ')



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
        return '{} {} {}/{}/{}'.format(self.id, self.baseStats.name, self.level, self.awaken, self.wpn)


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


def validateLevel(level):
    if level < 0:
        level = 0
    elif level > 7:
        level = 7
    return level


def validateAwaken(awaken, level):
    if awaken > level:
        awaken = level
    return awaken


def validateWeapon(wpn, prev):
    if wpn < 0:
        wpn = prev
    elif wpn > 9:
        wpn = prev
    return wpn


def validateMedals(medals, level):
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

def heroProgress(user, element, rarity):
    # Query players hero based on element and rarity
    heroes = Hero.query.filter_by(player=user).join(Base).filter(Base.element==element, Base.rarity==rarity)
    # Placeholder variables for count of heroes within query, total progress, and maxed heroes
    count = 0
    total = 0
    maxed = 0
    for i in heroes:
        count += 1
        total += i.progress()
    for i in heroes:
        if i.level == 7:
            maxed += 1
    # Return average progress within element and rarity, amount of maxed heroes and count within same.
    return round(total/count, 2), maxed, count

def totalMedals(user, element):
    heroes = Hero.query.filter_by(player=user).join(Base).filter(Base.element==element)
    total = 0
    maxMedals = 0
    for i in heroes:
        if i.level == 1:
            total += 10
        elif i.level == 2:
            total += 30
        elif i.level == 3:
            total += 80
        elif i.level == 4:
            total += 280
        elif i.level == 5:
            total += 880
        elif i.level == 6:
            total += 2380
        elif i.level == 7:
            total += 4880
        total += i.medals
        maxMedals += 4880
    return total, maxMedals


def rarityMedals(user, element, rarity):
    heroes = Hero.query.filter_by(player=user).join(Base).filter(Base.rarity == rarity, Base.element == element)
    total = 0
    for i in heroes:
        if i.level == 1:
            total += 10
        elif i.level == 2:
            total += 30
        elif i.level == 3:
            total += 80
        elif i.level == 4:
            total += 280
        elif i.level == 5:
            total += 880
        elif i.level == 6:
            total += 2380
        elif i.level == 7:
            total += 4880
        total += i.medals
    return total
