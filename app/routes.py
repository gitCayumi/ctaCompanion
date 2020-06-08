from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Base, Hero, validateAwaken, validateLevel, validateWeapon, validateMedals, heroProgress, \
    totalMedals, rarityMedals, ArtBase, Artifact, artAtk, artCrit, artAps, artCritDmg, validateArt
from werkzeug.urls import url_parse
from app.heroDict import heroDict

@app.route('/')
@app.route('/index')
#@login_required
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
    return render_template('login.html', title='Sign In', form=form, errorType=errorType)


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
            hero = Hero(level=0, awaken=0, wpn=0, medals=0, runedAtk=0, runedHp=0, runedDef=0, runedAps=0, runedCrit=0, runedCritDmg=0, player=user, baseStats=i)
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
        db.session.commit()
        flash(u'Your account has been created! Login to access the features of this website.', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form, errorType=errorType)


@app.route('/account/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user)
    useractive = 1
    if request.method == "GET":
        return render_template('account.html', user=user, heroes=heroes, title='Account', useractive=useractive)

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
                return render_template('account.html', user=user, heroes=heroes, title='Account')

            try:
                int(request.form.get("prismPower"))
                int(request.form.get("heroPower"))
                int(request.form.get("artifactPower"))
                int(request.form.get("daysPlayed"))
            except:
                flash(u'Invalid input', 'error')
                return render_template('account.html', user=user, heroes=heroes, title='Account')

        for j in heroes:
            current = str(j.id)
            level = validateLevel(int(request.form.get(current + "level")))
            awaken = validateAwaken(int(request.form.get(current + "awaken")), level)
            wpn = validateWeapon(int(request.form.get(current + "wpn")), j.wpn)
            medals = validateMedals(int(request.form.get(current + "medal")), level)

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
        return render_template('account.html', user=user, heroes=heroes, title='Account')



@app.route('/collection/<username>')
@login_required
def collection(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user)
    heroactive = 1
    return render_template('collection.html', user=user, heroes=heroes, title='Hero Collection', heroactive=heroactive)


# This mess needs to be refactored, I just created and kept going without thinking ahead.
# Data can be returned and presented in a much more elegant and efficient way
@app.route('/progress/<username>')
@login_required
def progress(username):
    user = User.query.filter_by(username=username).first_or_404()
    waterCommon = heroProgress(user, "Water", "Common")
    waterRare = heroProgress(user, "Water", "Rare")
    waterEpic = heroProgress(user, "Water", "Epic")
    fireCommon = heroProgress(user, "Fire", "Common")
    fireRare = heroProgress(user, "Fire", "Rare")
    fireEpic = heroProgress(user, "Fire", "Epic")
    earthCommon = heroProgress(user, "Earth", "Common")
    earthRare = heroProgress(user, "Earth", "Rare")
    earthEpic = heroProgress(user, "Earth", "Epic")
    lightCommon = heroProgress(user, "Light", "Common")
    lightRare = heroProgress(user, "Light", "Rare")
    lightEpic = heroProgress(user, "Light", "Epic")
    lightLegendary = heroProgress(user, "Light", "Legendary")
    darkCommon = heroProgress(user, "Dark", "Common")
    darkRare = heroProgress(user, "Dark", "Rare")
    darkEpic = heroProgress(user, "Dark", "Epic")
    darkLegendary = heroProgress(user, "Dark", "Legendary")
    waterMedals = totalMedals(user, "Water")
    fireMedals = totalMedals(user, "Fire")
    earthMedals = totalMedals(user, "Earth")
    lightMedals = totalMedals(user, "Light")
    darkMedals = totalMedals(user, "Dark")
    waterCommonMedals = rarityMedals(user, "Water", "Common")
    waterRareMedals = rarityMedals(user, "Water", "Rare")
    waterEpicMedals = rarityMedals(user, "Water", "Epic")
    fireCommonMedals = rarityMedals(user, "Fire", "Common")
    fireRareMedals = rarityMedals(user, "Fire", "Rare")
    fireEpicMedals = rarityMedals(user, "Fire", "Epic")
    earthCommonMedals = rarityMedals(user, "Earth", "Common")
    earthRareMedals = rarityMedals(user, "Earth", "Rare")
    earthEpicMedals = rarityMedals(user, "Earth", "Epic")
    lightCommonMedals = rarityMedals(user, "Light", "Common")
    lightRareMedals = rarityMedals(user, "Light", "Rare")
    lightEpicMedals = rarityMedals(user, "Light", "Epic")
    lightLegendaryMedals = rarityMedals(user, "Light", "Legendary")
    darkCommonMedals = rarityMedals(user, "Dark", "Common")
    darkRareMedals = rarityMedals(user, "Dark", "Rare")
    darkEpicMedals = rarityMedals(user, "Dark", "Epic")
    darkLegendaryMedals = rarityMedals(user, "Dark", "Legendary")

    return render_template('progress.html', user=user, title='Hero Progress', waterCommon=waterCommon, waterRare=waterRare, waterEpic=waterEpic,
                           fireCommon=fireCommon, fireRare=fireRare, fireEpic=fireEpic, earthCommon=earthCommon, earthRare=earthRare, earthEpic=earthEpic,
                           lightCommon=lightCommon, lightRare=lightRare, lightEpic=lightEpic, lightLegendary=lightLegendary, darkCommon=darkCommon, darkRare=darkRare,
                           darkEpic=darkEpic, darkLegendary=darkLegendary, waterMedals=waterMedals, fireMedals=fireMedals, earthMedals=earthMedals, lightMedals=lightMedals, darkMedals=darkMedals,
                           waterCommonMedals=waterCommonMedals, waterRareMedals=waterRareMedals, waterEpicMedals=waterEpicMedals,
                           fireCommonMedals=fireCommonMedals, fireRareMedals=fireRareMedals, fireEpicMedals=fireEpicMedals,
                           earthCommonMedals=earthCommonMedals, earthRareMedals=earthRareMedals, earthEpicMedals=earthEpicMedals,
                           lightCommonMedals=lightCommonMedals, lightRareMedals=lightRareMedals, lightEpicMedals=lightEpicMedals, lightLegendaryMedals=lightLegendaryMedals,
                           darkCommonMedals=darkCommonMedals, darkRareMedals=darkRareMedals, darkEpicMedals=darkEpicMedals, darkLegendaryMedals=darkLegendaryMedals)


@app.route('/test/<username>')
@login_required
def test(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user)
    return render_template('test.html', user=user, heroes=heroes, title='TEST AREA')


@app.route('/Hero/<heroid>', methods=["GET", "POST"])
@login_required
def hero(heroid):
    user = User.query.join(Hero).filter(Hero.id==heroid)
    selectedHero = Hero.query.get(heroid)
    if request.method == "GET":
        return render_template('hero.html', selectedHero=selectedHero, title=selectedHero.baseStats.name, user=user, heroDict=heroDict)
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
            return render_template('hero.html', selectedHero=selectedHero, title=selectedHero.baseStats.name, user=user, heroDict=heroDict)

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
        return render_template('hero.html', selectedHero=selectedHero, title=selectedHero.baseStats.name, user=user, heroDict=heroDict)


@app.route('/contact', methods=["GET", "POST"])
def contact():

    return render_template('contact.html', title='Contact')


@app.route('/artifacts/<username>', methods=["GET", "POST"])
@login_required
def artifacts(username):
    user = User.query.filter_by(username=username).first_or_404()
    normal = Artifact.query.filter_by(owner=user, type="N")
    event = Artifact.query.filter_by(owner=user, type="E")
    artifactBase = ArtBase.query.all()
    waterAtk = artAtk(user, "Water")
    fireAtk = artAtk(user, "Fire")
    earthAtk = artAtk(user, "Earth")
    lightAtk = artAtk(user, "Light")
    darkAtk = artAtk(user, "Dark")
    allCrit = artCrit(user)
    allAps = artAps(user)
    waterCritDmg = artCritDmg(user, "Water")
    fireCritDmg = artCritDmg(user, "Fire")
    earthCritDmg = artCritDmg(user, "Earth")
    lightCritDmg = artCritDmg(user, "Light")
    darkCritDmg = artCritDmg(user, "Dark")


    if request.method == "GET":
        return render_template('artifacts.html', user=user, title='Artifacts', artifactBase=artifactBase, event=event,
                               normal=normal, fireAtk=fireAtk, earthAtk=earthAtk, waterAtk=waterAtk, lightAtk=lightAtk,
                               darkAtk=darkAtk, allCrit=allCrit, allAps=allAps, fireCritDmg=fireCritDmg,
                               earthCritDmg=earthCritDmg, waterCritDmg=waterCritDmg, lightCritDmg=lightCritDmg,
                               darkCritDmg=darkCritDmg)
    else:
        arts = Artifact.query.filter_by(owner=user)
        for j in arts:
            current = str(j.id)
            try:
                int(request.form.get(current + "art"))
                int(request.form.get(current + "level"))
            except:
                flash(u'Invalid input', 'error')
                return redirect(url_for('artifacts', username=current_user.username))

        # Populate dictionary with artifact base_id as key, and count as value to ensure no duplicates
        artDict = {}
        for m in arts:
            current = str(m.id)
            if request.form.get(current + "art") != "81":
                # create new key with current submitted artifacts base_id, increase its value by 1 (except 'empty')
                artDict[request.form.get(current + "art")] = artDict.get(request.form.get(current + "art"), 0) + 1
        for n in artDict.values():
            # if any artifact has a count greater than 1 we have a duplicate and generate error.
            if n > 1:
                flash(u'You may not have duplicate Artifacts', 'error')
                return redirect(url_for('artifacts', username=current_user.username))

        for i in arts:
            current = str(i.id)
            art = Artifact.query.get(i.id)
            # Bring empty artifacts back 0 if needed
            if request.form.get(current + "art") == "81":
                art.level = 0
            else:
                art.level = validateArt(art, request.form.get(current + "level"))
            art.artbase_id = request.form.get(current + "art")

        db.session.commit()
        # There's got to be a better way than running all functions and re-query the database..
        # Note to self: return redirect instead of render_template...

        flash(u'Artifacts updated successfully!', 'info')
        return redirect(url_for('artifacts', username=current_user.username))

