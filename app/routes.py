from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Base, Hero, validate_awaken, validate_level, validate_weapon, validate_medals, hero_progress, \
    total_medals, rarity_medals, ArtBase, Artifact, validate_art, BossBase, Bossteam, display_raid_dps
from werkzeug.urls import url_parse
from app.heroDict import heroDict, frostwing, bosses
from sqlalchemy.orm import joinedload
import sys


@app.route('/')
@app.route('/index')
# @login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    errorType = 2
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(u'Invalid username or password.', 'error')
            return redirect(url_for('login', errorType=errorType))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash(u'You are now logged in as {}.'.format(user.username), 'info')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, errorType=errorType, loginactive=1)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    errorType = 1
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # Create entries for every hero for the registered user.
        base = Base.query.all()
        for i in base:
            hero = Hero(level=0, awaken=0, wpn=0, medals=0, runedAtk=0, runedHp=0, runedDef=0, runedAps=0, runedCrit=0,
                        runedCritDmg=0, player=user, baseStats=i)
            db.session.add(hero)
        # Create normal artifact slots for user
        emptyArt = ArtBase.query.get(81)
        for j in range(22):
            art = Artifact(type="N", owner=user, artBase=emptyArt)
            db.session.add(art)
        # Create event artifact slots for user
        for k in range(17):
            eventArt = Artifact(type="E", owner=user, artBase=emptyArt)
            db.session.add(eventArt)
        # Create empty boss teams for user
        bosses = BossBase.query.all()
        for boss in bosses:
            for n in range(10):
                entry = Bossteam(hero="Slot "+str(n+1), damage=0, manager=user, bossBase=boss)
            db.session.add(entry)

        db.session.commit()
        flash(u'Your account has been created! Login to access the features of this website.', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form, errorType=errorType, registeractive=1)


@app.route('/account/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.options(joinedload('baseStats')).filter_by(player=user).all()

    if request.method == "GET":
        return render_template(
            'account.html',
            user=user,
            heroes=heroes,
            elementOrder=["Water", "Fire", "Earth", "Light", "Dark"],
            rarityOrder = ["Common", "Rare", "Epic", "Legendary"],
            title='Account',
            useractive=1
        )

    else:
        for i in heroes:
            current = str(i.id)
            # also handle empty inputs.. if not request.form.. = 0
            try:
                int(request.form.get(current + "level"))
                int(request.form.get(current + "awaken"))
                int(request.form.get(current + "wpn"))
                int(request.form.get(current + "medal"))
            except:
                flash(u'Invalid input', 'error')
                return redirect(url_for('account'))

            try:
                int(request.form.get("prismPower"))
                int(request.form.get("heroPower"))
                int(request.form.get("artifactPower"))
                int(request.form.get("daysPlayed"))
            except:
                flash(u'Invalid input', 'error')
                return redirect(url_for('account', username=current_user.username))

        for j in heroes:
            current = str(j.id)
            level = validate_level(int(request.form.get(current + "level")))
            awaken = validate_awaken(int(request.form.get(current + "awaken")), level)
            wpn = validate_weapon(int(request.form.get(current + "wpn")), j.wpn)
            medals = validate_medals(int(request.form.get(current + "medal")), level)

            hero = Hero.query.get(j.id)
            hero.level = level
            hero.awaken = awaken
            hero.wpn = wpn
            hero.medals = medals

        prismPower = int(request.form.get("prismPower"))
        heroPower = int(request.form.get("heroPower"))
        artifactPower = int(request.form.get("artifactPower"))
        daysPlayed = int(request.form.get("daysPlayed"))

        user.prismPower = prismPower
        user.heroPower = heroPower
        user.artifactPower = artifactPower
        user.daysPlayed = daysPlayed

        db.session.commit()

        flash(u'Your data was updated successfully!', 'info')
        return redirect(url_for('account', username=current_user.username))


@app.route('/collection/<username>')
@login_required
def collection(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user)
    return render_template('collection.html', user=user, heroes=heroes, title='Hero Collection', heroactive=1)


# This mess needs to be refactored, I just created and kept going without thinking ahead.
# Data can be returned and presented in a much more elegant and efficient way
@app.route('/progress/<username>')
@login_required
def progress(username):
    user = User.query.filter_by(username=username).first_or_404()
    waterCommon = hero_progress(user, "Water", "Common")
    waterRare = hero_progress(user, "Water", "Rare")
    waterEpic = hero_progress(user, "Water", "Epic")
    fireCommon = hero_progress(user, "Fire", "Common")
    fireRare = hero_progress(user, "Fire", "Rare")
    fireEpic = hero_progress(user, "Fire", "Epic")
    earthCommon = hero_progress(user, "Earth", "Common")
    earthRare = hero_progress(user, "Earth", "Rare")
    earthEpic = hero_progress(user, "Earth", "Epic")
    lightCommon = hero_progress(user, "Light", "Common")
    lightRare = hero_progress(user, "Light", "Rare")
    lightEpic = hero_progress(user, "Light", "Epic")
    lightLegendary = hero_progress(user, "Light", "Legendary")
    darkCommon = hero_progress(user, "Dark", "Common")
    darkRare = hero_progress(user, "Dark", "Rare")
    darkEpic = hero_progress(user, "Dark", "Epic")
    darkLegendary = hero_progress(user, "Dark", "Legendary")
    waterMedals = total_medals(user, "Water")
    fireMedals = total_medals(user, "Fire")
    earthMedals = total_medals(user, "Earth")
    lightMedals = total_medals(user, "Light")
    darkMedals = total_medals(user, "Dark")
    waterCommonMedals = rarity_medals(user, "Water", "Common")
    waterRareMedals = rarity_medals(user, "Water", "Rare")
    waterEpicMedals = rarity_medals(user, "Water", "Epic")
    fireCommonMedals = rarity_medals(user, "Fire", "Common")
    fireRareMedals = rarity_medals(user, "Fire", "Rare")
    fireEpicMedals = rarity_medals(user, "Fire", "Epic")
    earthCommonMedals = rarity_medals(user, "Earth", "Common")
    earthRareMedals = rarity_medals(user, "Earth", "Rare")
    earthEpicMedals = rarity_medals(user, "Earth", "Epic")
    lightCommonMedals = rarity_medals(user, "Light", "Common")
    lightRareMedals = rarity_medals(user, "Light", "Rare")
    lightEpicMedals = rarity_medals(user, "Light", "Epic")
    lightLegendaryMedals = rarity_medals(user, "Light", "Legendary")
    darkCommonMedals = rarity_medals(user, "Dark", "Common")
    darkRareMedals = rarity_medals(user, "Dark", "Rare")
    darkEpicMedals = rarity_medals(user, "Dark", "Epic")
    darkLegendaryMedals = rarity_medals(user, "Dark", "Legendary")

    return render_template('progress.html', user=user, title='Hero Progress', waterCommon=waterCommon,
                           waterRare=waterRare, waterEpic=waterEpic,
                           fireCommon=fireCommon, fireRare=fireRare, fireEpic=fireEpic, earthCommon=earthCommon,
                           earthRare=earthRare, earthEpic=earthEpic,
                           lightCommon=lightCommon, lightRare=lightRare, lightEpic=lightEpic,
                           lightLegendary=lightLegendary, darkCommon=darkCommon, darkRare=darkRare,
                           darkEpic=darkEpic, darkLegendary=darkLegendary, waterMedals=waterMedals,
                           fireMedals=fireMedals, earthMedals=earthMedals, lightMedals=lightMedals,
                           darkMedals=darkMedals,
                           waterCommonMedals=waterCommonMedals, waterRareMedals=waterRareMedals,
                           waterEpicMedals=waterEpicMedals,
                           fireCommonMedals=fireCommonMedals, fireRareMedals=fireRareMedals,
                           fireEpicMedals=fireEpicMedals,
                           earthCommonMedals=earthCommonMedals, earthRareMedals=earthRareMedals,
                           earthEpicMedals=earthEpicMedals,
                           lightCommonMedals=lightCommonMedals, lightRareMedals=lightRareMedals,
                           lightEpicMedals=lightEpicMedals, lightLegendaryMedals=lightLegendaryMedals,
                           darkCommonMedals=darkCommonMedals, darkRareMedals=darkRareMedals,
                           darkEpicMedals=darkEpicMedals, darkLegendaryMedals=darkLegendaryMedals,
                           progressactive=1)


@app.route('/Hero/<heroid>', methods=["GET", "POST"])
@login_required
def hero(heroid):
    user = User.query.join(Hero).filter(Hero.id == heroid)
    selectedHero = Hero.query.get(heroid)
    if request.method == "GET":
        return render_template('hero.html', selectedHero=selectedHero, title=selectedHero.baseStats.name, user=user,
                               heroDict=heroDict, heroactive=1)
    else:
        try:
            float(request.form.get(str(selectedHero.id) + "runedAtk"))
            float(request.form.get(str(selectedHero.id) + "runedHp"))
            float(request.form.get(str(selectedHero.id) + "runedDef"))
            float(request.form.get(str(selectedHero.id) + "runedAps"))
            float(request.form.get(str(selectedHero.id) + "runedCrit"))
            float(request.form.get(str(selectedHero.id) + "runedCritDmg"))
        except:
            flash(u'Invalid input', 'error')
            return render_template('hero.html', selectedHero=selectedHero, title=selectedHero.baseStats.name, user=user,
                                   heroDict=heroDict, heroactive=1)

        runedAtk = float(request.form.get(str(selectedHero.id) + "runedAtk"))
        runedHp = float(request.form.get(str(selectedHero.id) + "runedHp"))
        runedDef = float(request.form.get(str(selectedHero.id) + "runedDef"))
        runedAps = float(request.form.get(str(selectedHero.id) + "runedAps"))
        runedCrit = float(request.form.get(str(selectedHero.id) + "runedCrit"))
        runedCritDmg = float(request.form.get(str(selectedHero.id) + "runedCritDmg"))

        selectedHero.runedAtk = runedAtk
        selectedHero.runedHp = runedHp
        selectedHero.runedDef = runedDef
        selectedHero.runedAps = runedAps
        selectedHero.runedCrit = runedCrit
        selectedHero.runedCritDmg = runedCritDmg
        db.session.commit()

        flash(u'Rune values updated!', 'info')
        return render_template('hero.html', selectedHero=selectedHero, title=selectedHero.baseStats.name, user=user,
                               heroDict=heroDict, heroactive=1)


@app.route('/about', methods=["GET", "POST"])
def about():
    return render_template('about.html', title='About', aboutactive=1)


@app.route('/artifacts/<username>', methods=["GET", "POST"])
@login_required
def artifacts(username):
    user = User.query.filter_by(username=username).first_or_404()
    normal = Artifact.query.filter_by(owner=user, type="N")
    event = Artifact.query.filter_by(owner=user, type="E")
    artifact_base = ArtBase.query.all()

    if request.method == "GET":
        return render_template('artifacts.html', user=user, title='Artifacts', artifact_base=artifact_base, event=event,
                               normal=normal, artifactactive=1)
    else:
        artifacts = Artifact.query.filter_by(owner=user)
        for artifact in artifacts:
            current = str(artifact.id)
            try:
                int(request.form.get(current + "art"))
                int(request.form.get(current + "level"))
            except:
                flash(u'Invalid input', 'error')
                return redirect(url_for('artifacts', username=current_user.username))

        # Populate dictionary with artifact base_id as key, and count as value to ensure no duplicates
        art_dict = {}
        for artifact in artifacts:
            current = str(artifact.id)
            if request.form.get(current + "art") != "81":
                # create new key with current submitted artifacts base_id, increase its value by 1 (except 'empty')
                art_dict[request.form.get(current + "art")] = art_dict.get(request.form.get(current + "art"), 0) + 1
        for count in art_dict.values():
            # if any artifact has a count greater than 1 we have a duplicate and generate error.
            if count > 1:
                flash(u'You may not have duplicate Artifacts', 'error')
                return redirect(url_for('artifacts', username=current_user.username))

        for i in artifacts:
            current = str(i.id)
            art = Artifact.query.get(i.id)
            # Bring empty artifacts back 0 if needed
            if request.form.get(current + "art") == "81":
                art.level = 0
            else:
                art.level = validate_art(art, request.form.get(current + "level"))
            art.artbase_id = request.form.get(current + "art")

        db.session.commit()

        flash(u'Artifacts updated successfully!', 'info')
        return redirect(url_for('artifacts', username=current_user.username))


@app.route('/bossTeam/<username>')
@login_required
def bossTeam(username):
    user = User.query.filter_by(username=username).first_or_404()
    load_kraken = Bossteam.query.filter_by(bossbase_id=1, user_id=user.id).all()
    load_deepseaking = Bossteam.query.filter_by(bossbase_id=2, user_id=user.id).all()
    load_frostwing = Bossteam.query.filter_by(bossbase_id=3, user_id=user.id).all()
    load_odin = Bossteam.query.filter_by(bossbase_id=4, user_id=user.id).all()
    load_lightmech = Bossteam.query.filter_by(bossbase_id=5, user_id=user.id).all()
    load_astrolab = Bossteam.query.filter_by(bossbase_id=6, user_id=user.id).all()
    load_sandclaw = Bossteam.query.filter_by(bossbase_id=7, user_id=user.id).all()
    load_voodootank = Bossteam.query.filter_by(bossbase_id=8, user_id=user.id).all()
    load_undeadsamurai = Bossteam.query.filter_by(bossbase_id=9, user_id=user.id).all()
    load_valkenbot = Bossteam.query.filter_by(bossbase_id=10, user_id=user.id).all()
    load_firegorge = Bossteam.query.filter_by(bossbase_id=11, user_id=user.id).all()
    load_madking = Bossteam.query.filter_by(bossbase_id=12, user_id=user.id).all()
    load_beetle = Bossteam.query.filter_by(bossbase_id=13, user_id=user.id).all()
    load_hauntinghead = Bossteam.query.filter_by(bossbase_id=14, user_id=user.id).all()
    load_gunlord = Bossteam.query.filter_by(bossbase_id=15, user_id=user.id).all()
    filter_team = "hej"
    kraken_dict = {}
    for entry in load_kraken:
        kraken_dict[entry.hero] = display_raid_dps(entry.damage)
    deepseaking_dict = {}
    for entry in load_deepseaking:
        deepseaking_dict[entry.hero] = display_raid_dps(entry.damage)
    frostwing_dict = {}
    for entry in load_frostwing:
        frostwing_dict[entry.hero] = display_raid_dps(entry.damage)
    odin_dict = {}
    for entry in load_odin:
        odin_dict[entry.hero] = display_raid_dps(entry.damage)
    lightmech_dict = {}
    for entry in load_lightmech:
        lightmech_dict[entry.hero] = display_raid_dps(entry.damage)
    astrolab_dict = {}
    for entry in load_astrolab:
        astrolab_dict[entry.hero] = display_raid_dps(entry.damage)
    sandclaw_dict = {}
    for entry in load_sandclaw:
        sandclaw_dict[entry.hero] = display_raid_dps(entry.damage)
    voodootank_dict = {}
    for entry in load_voodootank:
        voodootank_dict[entry.hero] = display_raid_dps(entry.damage)
    undeadsamurai_dict = {}
    for entry in load_undeadsamurai:
        undeadsamurai_dict[entry.hero] = display_raid_dps(entry.damage)
    valkenbot_dict = {}
    for entry in load_valkenbot:
        valkenbot_dict[entry.hero] = display_raid_dps(entry.damage)
    firegorge_dict = {}
    for entry in load_firegorge:
        firegorge_dict[entry.hero] = display_raid_dps(entry.damage)
    madking_dict = {}
    for entry in load_madking:
        madking_dict[entry.hero] = display_raid_dps(entry.damage)
    beetle_dict = {}
    for entry in load_beetle:
        beetle_dict[entry.hero] = display_raid_dps(entry.damage)
    hauntinghead_dict = {}
    for entry in load_hauntinghead:
        hauntinghead_dict[entry.hero] = display_raid_dps(entry.damage)
    gunlord_dict = {}
    for entry in load_gunlord:
        gunlord_dict[entry.hero] = display_raid_dps(entry.damage)

    return render_template('bossTeam.html', user=user, title='Boss Teams', kraken_dict=kraken_dict,
                           deepseaking_dict=deepseaking_dict, frostwing_dict=frostwing_dict, odin_dict=odin_dict,
                           lightmech_dict=lightmech_dict, astrolab_dict=astrolab_dict, sandclaw_dict=sandclaw_dict,
                           voodootank_dict=voodootank_dict, undeadsamurai_dict=undeadsamurai_dict,
                           valkenbot_dict=valkenbot_dict, firegorge_dict=firegorge_dict, madking_dict=madking_dict,
                           beetle_dict=beetle_dict, hauntinghead_dict=hauntinghead_dict, gunlord_dict=gunlord_dict,
                           bossactive=1, filter_team=filter_team)


@app.route('/calculate/<username>/<boss>')
@login_required
def calculate(username, boss):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user).filter(Hero.level > 0).options(joinedload(Hero.baseStats, innerjoin=True)).all()
    boss_name = BossBase.query.get(boss)
    id_help = Bossteam.query.filter_by(bossbase_id=boss, user_id=user.id).first()
    boss = bosses[str(id_help.bossBase.nameSafe)]
    team_list = []
    team = {}

    print(f"### bossTeam algorithm initiated; {boss_name.name} for {user.username} ###", file=sys.stderr)

    # Populate dictionary with all artifact atk bonuses by element
    atk = {
        "Water": user.art_atk("Water"),
        "Fire": user.art_atk("Fire"),
        "Earth": user.art_atk("Earth"),
        "Light": user.art_atk("Light"),
        "Dark": user.art_atk("Dark")
    }
    # Populate dictionary with all artifact critDmg bonuses by element
    crit_dmg = {
        "Water": user.art_crit_dmg("Water"),
        "Fire": user.art_crit_dmg("Fire"),
        "Earth": user.art_crit_dmg("Earth"),
        "Light": user.art_crit_dmg("Light"),
        "Dark": user.art_crit_dmg("Dark")
    }
    # Populate dictionary with a collection of all artifact bonuses, by stat
    art_bonus = {
        "atk": atk,
        "aps": user.art_aps(),
        "crit": user.art_crit(),
        "critDmg": crit_dmg
    }

    # filter_team = user.filter_heroes(heroes, boss, art_bonus)

    if len(heroes) > 10:
        print(f"{len(heroes)} heroes found; filter_heroes", file=sys.stderr)
        filter_team = user.filter_heroes(heroes, boss, art_bonus)
        print(f"RAIDTEAM - Calling (filtered, {len(filter_team)} heroes)", file=sys.stderr)
        team = user.raid_team(team, team_list, filter_team, boss, art_bonus)
    else:
        print(f"RAIDTEAM - Calling (unfiltered, {len(heroes)} heroes)", file=sys.stderr)
        team = user.raid_team(team, team_list, heroes, boss, art_bonus)

    team_id = int(id_help.id)
    for hero, damage in team.items():
        slot = Bossteam.query.get(team_id)
        slot.hero = hero
        slot.damage = damage
        db.session.add(slot)
        team_id += 1
    db.session.commit()


    flash(u'Calculation complete, your data has been saved.', 'info')
    return redirect(url_for('bossTeam', username=current_user.username))


@app.route('/test/<username>')
@login_required
def test(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user).filter(Hero.level > 0).all()
    teamList = []
    team = {}

    atk = {
        "Water": user.art_atk("Water"),
        "Fire": user.art_atk("Fire"),
        "Earth": user.art_atk("Earth"),
        "Light": user.art_atk("Light"),
        "Dark": user.art_atk("Dark")
    }

    critDmg = {
        "Water": user.art_crit_dmg("Water"),
        "Fire": user.art_crit_dmg("Fire"),
        "Earth": user.art_crit_dmg("Earth"),
        "Light": user.art_crit_dmg("Light"),
        "Dark": user.art_crit_dmg("Dark")
    }

    artBonus = {
        "atk": atk,
        "aps": user.art_aps(),
        "crit": user.art_crit(),
        "critDmg": critDmg
    }

    buffs = {
        "Water": user.raidbuffs(heroes, "Water"),
        "Fire": user.raidbuffs(heroes, "Fire"),
        "Earth": user.raidbuffs(heroes, "Earth"),
        "Light": user.raidbuffs(heroes, "Light"),
        "Dark": user.raidbuffs(heroes, "Dark")
    }

    filterTeam = []
    if len(heroes) > 10:
        filterTeam = user.raidteam2(heroes, frostwing, artBonus)
        testTeam = user.raidteam(team, teamList, filterTeam, frostwing, artBonus)
    else:
        testTeam = user.raidteam(team, teamList, heroes, frostwing, artBonus)

    return render_template('test.html', user=user, title='Boss Teams', heroes=heroes, frostwing=frostwing,
                           teamList=teamList, team=team, buffs=buffs, artBonus=artBonus, testTeam=testTeam,
                           filterTeam=filterTeam)

