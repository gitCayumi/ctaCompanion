from app import app
from flask import render_template, url_for, flash, redirect, request, send_file
from app.models import User, Hero, Artifact, export_collection
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from xlsxwriter import Workbook
import os


@app.route('/export_raid/<username>', methods=['GET'])
def export_raid(username):
    user = User.query.filter_by(username=username).first_or_404()
    normal_artifacts = Artifact.query.filter_by(owner=user, type="N").all()
    event_artifacts = Artifact.query.filter_by(owner=user, type="E").all()
    atlantus = Hero.query.filter_by(player=user, base_id=5).first_or_404()
    furiosa = Hero.query.filter_by(player=user, base_id=24).first_or_404()
    groovine = Hero.query.filter_by(player=user, base_id=29).first_or_404()
    one_eye = Hero.query.filter_by(player=user, base_id=59).first_or_404()
    sorrow = Hero.query.filter_by(player=user, base_id=77).first_or_404()
    namida = Hero.query.filter_by(player=user, base_id=54).first_or_404()
    spark = Hero.query.filter_by(player=user, base_id=78).first_or_404()
    thorn = Hero.query.filter_by(player=user, base_id=86).first_or_404()
    dark_hunter = Hero.query.filter_by(player=user, base_id=18).first_or_404()
    vlad = Hero.query.filter_by(player=user, base_id=91).first_or_404()
    kasumi = Hero.query.filter_by(player=user, base_id=39).first_or_404()
    goddess = Hero.query.filter_by(player=user, base_id=26).first_or_404()
    xak = Hero.query.filter_by(player=user, base_id=99).first_or_404()
    green_faery = Hero.query.filter_by(player=user, base_id=28).first_or_404()
    merlinus = Hero.query.filter_by(player=user, base_id=47).first_or_404()

    normal_artifacts_count = 0
    for artifact in normal_artifacts:
        if artifact.artbase_id != 81:
            normal_artifacts_count += 1

    event_artifacts_count = 0
    for artifact in event_artifacts:
        if artifact.artbase_id != 81:
            event_artifacts_count += 1

    image = Image.open(os.path.join(app.static_folder, 'ctac-export.png'))

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.join(app.static_folder, 'Roboto-Bold.ttf'), size=12)
    font_user = ImageFont.truetype(os.path.join(app.static_folder, 'Roboto-Bold.ttf'), size=24)
    font_power = ImageFont.truetype(os.path.join(app.static_folder, 'Roboto-Bold.ttf'), size=14)
    color_white = 'rgb(255, 255, 255)'
    color_dark_blue = 'rgb(18, 59, 129)'
    color_light_blue = 'rgb(37, 164, 235)'

    # Atlantus
    (x, y) = (16, 50)
    atlantus_message = str(atlantus.level)+'/'+str(atlantus.awaken)+'/'+str(atlantus.wpn)
    draw.text((x, y), atlantus_message, fill=color_white, font=font)

    # Furiosa
    (x, y) = (61, 50)
    furiosa_message = str(furiosa.level) + '/' + str(furiosa.awaken) + '/' + str(furiosa.wpn)
    draw.text((x, y), furiosa_message, fill=color_white, font=font)

    # groovine
    (x, y) = (106, 50)
    groovine_message = str(groovine.level) + '/' + str(groovine.awaken) + '/' + str(groovine.wpn)
    draw.text((x, y), groovine_message, fill=color_white, font=font)

    # One Eye
    (x, y) = (151, 50)
    one_eye_message = str(one_eye.level) + '/' + str(one_eye.awaken) + '/' + str(one_eye.wpn)
    draw.text((x, y), one_eye_message, fill=color_white, font=font)

    # Sorrow
    (x, y) = (196, 50)
    sorrow_message = str(sorrow.level) + '/' + str(sorrow.awaken) + '/' + str(sorrow.wpn)
    draw.text((x, y), sorrow_message, fill=color_white, font=font)

    # Namida
    (x, y) = (16, 110)
    namida_message = str(namida.level) + '/' + str(namida.awaken) + '/' + str(namida.wpn)
    draw.text((x, y), namida_message, fill=color_white, font=font)

    # Spark
    (x, y) = (61, 110)
    spark_message = str(spark.level) + '/' + str(spark.awaken) + '/' + str(spark.wpn)
    draw.text((x, y), spark_message, fill=color_white, font=font)

    # Thorn
    (x, y) = (106, 110)
    thorn_message = str(thorn.level) + '/' + str(thorn.awaken) + '/' + str(thorn.wpn)
    draw.text((x, y), thorn_message, fill=color_white, font=font)

    # Dark Hunter
    (x, y) = (151, 110)
    dark_hunter_message = str(dark_hunter.level) + '/' + str(dark_hunter.awaken) + '/' + str(dark_hunter.wpn)
    draw.text((x, y), dark_hunter_message, fill=color_white, font=font)

    # Vlad
    (x, y) = (196, 110)
    vlad_message = str(vlad.level) + '/' + str(vlad.awaken) + '/' + str(vlad.wpn)
    draw.text((x, y), vlad_message, fill=color_white, font=font)

    # Kasumi
    (x, y) = (241, 110)
    kasumi_message = str(kasumi.level) + '/' + str(kasumi.awaken) + '/' + str(kasumi.wpn)
    draw.text((x, y), kasumi_message, fill=color_white, font=font)

    # Goddess
    (x, y) = (16, 170)
    goddess_message = str(goddess.level) + '/' + str(goddess.awaken) + '/' + str(goddess.wpn)
    draw.text((x, y), goddess_message, fill=color_white, font=font)

    # Xak
    (x, y) = (61, 170)
    xak_message = str(xak.level) + '/' + str(xak.awaken) + '/' + str(xak.wpn)
    draw.text((x, y), xak_message, fill=color_white, font=font)

    # Green Faery
    (x, y) = (106, 170)
    green_faery_message = str(green_faery.level) + '/' + str(green_faery.awaken) + '/' + str(green_faery.wpn)
    draw.text((x, y), green_faery_message, fill=color_white, font=font)

    # Merlinus
    (x, y) = (151, 170)
    merlinus_message = str(merlinus.level) + '/' + str(merlinus.awaken) + '/' + str(merlinus.wpn)
    draw.text((x, y), merlinus_message, fill=color_white, font=font)

    # Username
    (x, y) = (320, 87)
    user_message = str(user.username)
    draw.text((x, y), user_message, fill=color_white, font=font_user)

    # Power_text
    (x, y) = (335, 120)
    power_message = 'Hero Power: '
    draw.text((x, y), power_message, fill=color_dark_blue, font=font_power)

    # Power
    (x, y) = (430, 120)
    power_message = '{:,}'.format(user.heroPower).replace(',', ' ')
    draw.text((x, y), power_message, fill=color_light_blue, font=font_power)

    # Artifacts_text
    (x, y) = (335, 140)
    artifact_message = 'Artifact Slots: '
    draw.text((x, y), artifact_message, fill=color_dark_blue, font=font_power)

    # Artifacts
    (x, y) = (430, 140)
    artifact_message = str(normal_artifacts_count) + ' + ' + str(event_artifacts_count)
    draw.text((x, y), artifact_message, fill=color_light_blue, font=font_power)

    # Days_text
    (x, y) = (335, 160)
    artifact_message = 'Days Played: '
    draw.text((x, y), artifact_message, fill=color_dark_blue, font=font_power)

    # Days_played
    (x, y) = (430, 160)
    artifact_message = str(user.daysPlayed)
    draw.text((x, y), artifact_message, fill=color_light_blue, font=font_power)

    get_date = datetime.now()
    date_tag = get_date.strftime("%Y%m%d_%H%M%S")
    image.save(os.path.join(app.static_folder + "/export_png", date_tag + '_' + user.username + '_raid_export.png'))

    user_file = date_tag + '_' + user.username + '_raid_export.png'

    flash(u'Your image was generated successfully!', 'info')
    return render_template('export_raid.html', title='Raid Export', useractive=1, user_file=user_file)


@app.route('/export_excel/<username>', methods=['GET'])
def export_excel(username):
    user = User.query.filter_by(username=username).first_or_404()
    heroes = Hero.query.filter_by(player=user).all()
    items = []

    for hero in heroes:
        info = {
            'name': hero.baseStats.name,
            'level': hero.level,
            'awaken': hero.awaken,
            'weapon': hero.wpn,
            'medals': hero.medals
        }
        items.append(info)

    headers = {
        'name': 'Hero',
        'level': 'Level',
        'awaken': 'Awaken',
        'weapon': 'Weapon',
        'medals': 'Medals'
    }

    get_date = datetime.now()
    date_tag = get_date.strftime("%Y%m%d_%H%M%S")
    export_collection(os.path.join(app.static_folder + "/export_xlsx/" + date_tag + "_{}_hero_collection.xlsx".format(user.username)), headers, items)
    return send_file(os.path.join(app.static_folder + "/export_xlsx/" + date_tag + "_{}_hero_collection.xlsx".format(user.username)), as_attachment=True)

"""
y = Hero.query.filter_by(player=user).all()
heroes = Hero.query.filter_by(player=user).filter(Hero.level > 0).options(joinedload(Hero.baseStats, innerjoin=True)).all()
"""