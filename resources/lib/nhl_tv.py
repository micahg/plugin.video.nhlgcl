
from resources.lib.globals import *


def categories():
    addDir('Today\'s Games','/live',100,ICON,FANART)
    addDir('Yesterday\'s Games','/live',105,ICON,FANART)
    if FAV_TEAM != 'None' and FAV_TEAM != '':
        #'https://www.nhl.com/site-core/images/team/logo/current/'+FAV_TEAM_ID+'_light.svg'
        #http://nhl.bamcontent.com/images/logos/600x600/pit.png
        addFavToday(FAV_TEAM+'\'s Game Today', 'Today\'s ' +  FAV_TEAM + ' Game', FAV_TEAM_LOGO, FANART)
        addDir(FAV_TEAM+'\'s Recent Games','favteam',500, FAV_TEAM_LOGO,FANART)
    addDir('Goto Date','/date',200,ICON,FANART)
    addDir('Featured Videos','/qp',300,ICON,FANART)


def todaysGames(game_day):
    if game_day == None:
        game_day = localToEastern()

    xbmc.log("GAME DAY = " + str(game_day))
    settings.setSetting(id='stream_date', value=game_day)

    display_day = stringToDate(game_day, "%Y-%m-%d")
    prev_day = display_day - timedelta(days=1)

    addDir('[B]<< Previous Day[/B]','/live',101,PREV_ICON,FANART,prev_day.strftime("%Y-%m-%d"))

    date_display = '[B][I]'+ colorString(display_day.strftime("%A, %m/%d/%Y"),GAMETIME_COLOR)+'[/I][/B]'
    addPlaylist(date_display,display_day,'/playhighlights',900,ICON,FANART)

    url = API_URL+'schedule?expand=schedule.teams,schedule.linescore,schedule.scoringplays,schedule.game.content.media.epg&date='+game_day+'&site=en_nhl&platform='+PLATFORM

    headers = {'User-Agent': UA_IPHONE,
               'Connection': 'close'
    }

    r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
    json_source = r.json()

    global RECAP_PLAYLIST
    global EXTENDED_PLAYLIST
    RECAP_PLAYLIST.clear()
    EXTENDED_PLAYLIST.clear()
    try:
        for game in json_source['dates'][0]['games']:
            createGameListItem(game, game_day)

    except:
        pass

    next_day = display_day + timedelta(days=1)
    addDir('[B]Next Day >>[/B]','/live',101,NEXT_ICON,FANART,next_day.strftime("%Y-%m-%d"))


def createGameListItem(game, game_day):
    away = game['teams']['away']['team']
    home = game['teams']['home']['team']
    #http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/NJD_at_BOS.jpg
    #icon = 'http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/'+away['abbreviation']+'_at_'+home['abbreviation']+'.jpg'
    #icon = 'http://raw.githubusercontent.com/eracknaphobia/game_images/master/square_black/'+away['abbreviation']+'vs'+home['abbreviation']+'.png'
    icon = getGameIcon(home['abbreviation'],away['abbreviation'])


    if TEAM_NAMES == "1":
        away_team = away['teamName']
        home_team = home['teamName']
    elif TEAM_NAMES == "2":
        away_team = away['name']
        home_team = home['name']
    elif TEAM_NAMES == "3":
        away_team = away['abbreviation']
        home_team = home['abbreviation']
    else:
        away_team = away['locationName']
        home_team = home['locationName']


    if away_team == "New York":
        away_team = away['name']

    if home_team == "New York":
        home_team = home['name']


    fav_game = False
    if FAV_TEAM_ID == str(away['id']):
        fav_game = True
        away_team = colorString(away_team,FAV_TEAM_COLOR)

    if FAV_TEAM_ID == str(home['id']):
        fav_game = True
        home_team = colorString(home_team,FAV_TEAM_COLOR)


    game_time = ''
    if game['status']['detailedState'] == 'Scheduled':
        game_time = game['gameDate']
        game_time = stringToDate(game_time, "%Y-%m-%dT%H:%M:%SZ")
        game_time = UTCToLocal(game_time)

        if TIME_FORMAT == '0':
             game_time = game_time.strftime('%I:%M %p').lstrip('0')
        else:
             game_time = game_time.strftime('%H:%M')

        game_time = colorString(game_time,UPCOMING)

    else:
        game_time = game['status']['detailedState']

        if game_time == 'Final':
            #if (NO_SPOILERS == '1' and game_time[:5] == "Final") or (NO_SPOILERS == '2' and game_time[:5] == "Final" and fav_game):
            #game_time = game_time[:5]
            game_time = colorString(game_time,FINAL)
        elif 'In Progress' in game_time:
            color = LIVE
            if 'Critical' in game_time:
                color = CRITICAL
            game_time = game['linescore']['currentPeriodTimeRemaining']+' '+game['linescore']['currentPeriodOrdinal']
            game_time = colorString(game_time,color)
        else:
            game_time = colorString(game_time,LIVE)


    game_id = str(game['gamePk'])

    #live_video = game['gameLiveVideo']
    epg = ''
    try:
        epg = json.dumps(game['content']['media']['epg'])
    except:
        pass
    live_feeds = 0
    archive_feeds = 0
    teams_stream = away['abbreviation'] + home['abbreviation']
    stream_date = str(game['gameDate'])


    desc = ''
    hide_spoilers = 0
    if NO_SPOILERS == '1' or (NO_SPOILERS == '2' and fav_game) or (NO_SPOILERS == '3' and game_day == localToEastern()) or (NO_SPOILERS == '4' and game_day < localToEastern()) or game['status']['detailedState'] == 'Scheduled':
        name = game_time + ' ' + away_team + ' at ' + home_team
        hide_spoilers = 1
    else:
        name = game_time + ' ' + away_team + ' ' + colorString(str(game['teams']['away']['score']),SCORE_COLOR) + ' at ' + home_team + ' ' + colorString(str(game['teams']['home']['score']),SCORE_COLOR)


    #fanart = None
    fanart = 'http://nhl.bamcontent.com/images/arena/default/'+str(home['id'])+'@2x.jpg'
    try:
        if game_day < localToEastern():
            #fanart = str(game['content']['media']['epg'][3]['items'][0]['image']['cuts']['1136x640']['src'])
            if hide_spoilers == 0:
                #soup = BeautifulSoup(str(game['content']['editorial']['recap']['items'][0]['preview']))
                #desc = soup.get_text()
                desc = str(game['content']['media']['epg'][3]['items'][0]['description'])
        else:

            if PREVIEW_INFO == 'true':
                url = API_URL+'game/'+str(game['gamePk'])+'/content?site=en_nhl'
                headers = {'User-Agent': UA_IPHONE,
                            'Connection': 'close'
                }

                r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
                json_source = r.json()
                fanart = str(json_source['editorial']['preview']['items'][0]['media']['image']['cuts']['1284x722']['src'])
                soup = BeautifulSoup(str(json_source['editorial']['preview']['items'][0]['preview']))
                desc = soup.get_text()
            elif hide_spoilers == 0:
                for play in game['scoringPlays']:
                    scorer = play['result']['description']
                    scorer = scorer[0:scorer.find(",")]
                    when = play['about']['periodTime'] + ' ' +play['about']['ordinalNum']
                    game_score = '('+str(play['about']['goals']['away'])+' - '+str(play['about']['goals']['home'])+')'
                    desc +=  colorString(when,LIVE) + ' ' + scorer + ' ' + game_score + '\n'
    except:
        pass

    name = name.encode('utf-8')
    if fav_game:
        name = '[B]'+name+'[/B]'

    title = away_team + ' at ' + home_team
    title = title.encode('utf-8')

    #Label free game of the day
    try:
        if bool(game['content']['media']['epg'][0]['items'][0]['freeGame']):
            name = colorString(name,FREE)
    except:
        pass

    #Set audio/video info based on stream quality setting
    audio_info, video_info = getAudioVideoInfo()
    #'duration':length
    info = {'plot':desc,'tvshowtitle':'NHL','title':title,'originaltitle':title,'aired':game_day,'genre':'Sports'}

    #Create Playlist for all highlights
    try:
        global RECAP_PLAYLIST
        temp_recap_stream_url = createHighlightStream(game['content']['media']['epg'][3]['items'][0]['playbacks'][3]['url'])
        listitem = xbmcgui.ListItem(title, thumbnailImage=icon)
        listitem.setInfo( type="Video", infoLabels={ "Title": title })
        RECAP_PLAYLIST.add(temp_recap_stream_url, listitem)

        global EXTENDED_PLAYLIST
        temp_extended_stream_url = createHighlightStream(game['content']['media']['epg'][2]['items'][0]['playbacks'][3]['url'])
        listitem = xbmcgui.ListItem(title, thumbnailImage=icon)
        listitem.setInfo( type="Video", infoLabels={ "Title": title } )
        EXTENDED_PLAYLIST.add(temp_extended_stream_url, listitem)
    except:
        pass


    addStream(name,'',title,game_id,epg,icon,fanart,info,video_info,audio_info,teams_stream,stream_date)



def streamSelect(game_id, epg, teams_stream, stream_date):
    #print epg
    #0 = NHLTV
    #1 = Audio
    #2 = Extended Highlights
    #3 = Recap

    try:
        epg = json.loads(epg)
    except:
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Streams Not Found', msg)
        sys.exit()

    full_game_items = epg[0]['items']
    audio_items = epg[1]['items']
    highlight_items = epg[2]['items']
    recap_items = epg[3]['items']

    stream_title = []
    content_id = []
    event_id = []
    free_game = []
    media_state = []
    archive_type = ['Recap','Extended Highlights','Full Game']

    multi_angle = 0
    multi_cam = 0
    if len(full_game_items) > 0:
        for item in full_game_items:
            media_state.append(item['mediaState'])

            if item['mediaFeedType'].encode('utf-8') == "COMPOSITE":
                multi_cam += 1
                stream_title.append("Multi-Cam " + str(multi_cam))
            elif item['mediaFeedType'].encode('utf-8') == "ISO":
                multi_angle += 1
                stream_title.append("Multi-Angle " + str(multi_angle))
            else:
                temp_item = item['mediaFeedType'].encode('utf-8').title()
                if item['callLetters'].encode('utf-8') != '':
                    temp_item = temp_item+' ('+item['callLetters'].encode('utf-8')+')'

                stream_title.append(temp_item)

            content_id.append(item['mediaPlaybackId'])
            event_id.append(item['eventId'])
            free_game.append(item['freeGame'])
    else:
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Streams Not Found', msg)
        sys.exit()

    #Reverse Order for display purposes
    #stream_title.reverse()
    #ft.reverse()

    stream_url = ''
    media_auth = ''

    if media_state[0] == 'MEDIA_ARCHIVE':
        dialog = xbmcgui.Dialog()
        a = dialog.select('Choose Archive', archive_type)
        if a < 2:
            if a == 0:
                #Recap
                try:
                    url = recap_items[0]['playbacks'][2]['url']
                    #Overwrite url if preferable scenario found
                    for item in recap_items[0]['playbacks']:
                        if item['name'] == PLAYBACK_SCENARIO:
                            url = item['url']
                            break

                    stream_url = createHighlightStream(url)
                except:
                    pass
            elif a == 1:
                #Extended Highlights
                try:
                    url = highlight_items[0]['playbacks'][2]['url']
                    #Overwrite url if preferable scenario found
                    for item in highlight_items[0]['playbacks']:
                        if item['name'] == PLAYBACK_SCENARIO:
                            url = item['url']
                            break

                    stream_url = createHighlightStream(url)
                except:
                    pass
        elif a == 2:
            dialog = xbmcgui.Dialog()
            n = dialog.select('Choose Stream', stream_title)
            if n > -1:
                stream_url, media_auth = fetchStream(game_id, content_id[n],event_id[n])
                xbmc.log(stream_url)
                stream_url = createFullGameStream(stream_url,media_auth,media_state[n])
    else:
        dialog = xbmcgui.Dialog()
        n = dialog.select('Choose Stream', stream_title)
        if n > -1:
            stream_url, media_auth = fetchStream(game_id, content_id[n],event_id[n])
            stream_url = createFullGameStream(stream_url,media_auth,media_state[n])


    listitem = xbmcgui.ListItem(path=stream_url)
    listitem.setMimeType("application/x-mpegURL")


    if stream_url != '':
        #listitem.setMimeType("application/x-mpegURL")
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, listitem)


def playAllHighlights():
    stream_title = ['Recap','Extended Highlights']
    dialog = xbmcgui.Dialog()
    n = dialog.select('View All', stream_title)

    if n == 0:
        xbmc.Player().play(RECAP_PLAYLIST)
    elif n == 1:
        xbmc.Player().play(EXTENDED_PLAYLIST)


def createHighlightStream(stream_url):
    bandwidth = ''
    bandwidth = find(QUALITY,'(',' kbps)')
    #Switch to ipad master file
    '''
    if QUALITY.upper() == 'ALWAYS ASK':
        #stream_url = selectStreamQualty(stream_url)
        bandwidth = getStreamQuality(stream_url)
    '''
    if bandwidth != '':
        stream_url = stream_url.replace(stream_url.rsplit('/', 1)[-1], 'asset_'+bandwidth+'k.m3u8')

    stream_url = stream_url + '|User-Agent='+UA_IPHONE

    xbmc.log(stream_url)
    return stream_url


def createFullGameStream(stream_url, media_auth, media_state):
    bandwidth = ''
    bandwidth = find(QUALITY,'(',' kbps)')

    #Only set bandwidth if it's explicitly set in add-on settings
    if QUALITY.upper() == 'ALWAYS ASK':
        #stream_url = selectStreamQualty(stream_url)
        bandwidth = getStreamQuality(stream_url)

    if bandwidth != '':
        #Reduce convert bandwidth if composite video selected
        if ('COMPOSITE' in stream_url or 'ISO' in stream_url) :
            if int(bandwidth) >= 3500:
                bandwidth = '3500'
            elif int(bandwidth) == 1200:
                bandwidth = '1500'

        playlist = getPlaylist(stream_url,media_auth)

        for line in playlist:
            if bandwidth in line and '#EXT' not in line:
                if 'http' in line:
                    stream_url = line
                else:
                    stream_url = stream_url.replace(stream_url.rsplit('/', 1)[-1], line)


    cj = load_cookies()

    cookies = ''
    for cookie in cj:
        if cookie.name == "Authorization":
            cookies = cookies + cookie.name + "=" + cookie.value + "; "
    #stream_url = stream_url + '|User-Agent='+UA_PS4+'&Cookie='+cookies+media_auth
    stream_url += '|User-Agent='+UA_IPHONE+'&Cookie='+cookies+media_auth

    xbmc.log("STREAM URL: "+stream_url)
    return stream_url




def getPlaylist(stream_url, media_auth):
    headers = { "Accept": "*/*",
                "Accept-Encoding": "identity",
                "Accept-Language": "en-US,en;q=0.8",
                "Connection": "keep-alive",
                "User-Agent": UA_NHL,
                "Cookie": media_auth
    }

    r = requests.get(stream_url, headers=headers, cookies=load_cookies(), verify=VERIFY)
    playlist = r.text


    return playlist.splitlines()


def fetchStream(game_id, content_id,event_id):
    stream_url = ''
    media_auth = ''

    authorization = getAuthCookie()

    if authorization == '':
        login()
        authorization = getAuthCookie()
        if authorization == '':
            return stream_url, media_auth

    session_key = getSessionKey(game_id,event_id,content_id,authorization)
    if session_key == '':
        return stream_url, media_auth
    elif session_key == 'blackout':
        msg = "The game you are trying to access is not currently available due to local or national blackout restrictions.\n Full game archives will be available 48 hours after completion of this game."
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Game Blacked Out', msg)
        return stream_url, media_auth

    url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream'
    url += '?contentId=' + content_id
    url += '&playbackScenario=' + PLAYBACK_SCENARIO
    url += '&platform=' + PLATFORM
    url += '&sessionKey=' + urllib.quote_plus(session_key)

    #Get user set CDN
    if CDN == 'Akamai':
        url +='&cdnName=MED2_AKAMAI_SECURE'
    elif CDN == 'Level 3':
        url +='&cdnName=MED2_LEVEL3_SECURE'

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
        "Authorization": authorization,
        "User-Agent": UA_NHL,
        "Proxy-Connection": "keep-alive"
    }

    r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
    json_source = r.json()

    if json_source['status_code'] == 1:
        if json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']['status'] == 'BlackedOutStatus':
            msg = "The game you are trying to access is not currently available due to local or national blackout restrictions.\n Full game archives will be available 48 hours after completion of this game."
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Game Blacked Out', msg)
            sys.exit()
        elif json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['auth_status'] == 'NotAuthorizedStatus':
            msg = "You do not have an active NHL.TV subscription. To access this content please purchase at www.NHL.TV or call customer support at 800-559-2333"
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Account Not Authorized', msg)
            sys.exit()
        else:
            stream_url = json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['url']
            media_auth = str(json_source['session_info']['sessionAttributes'][0]['attributeName']) + "=" + str(json_source['session_info']['sessionAttributes'][0]['attributeValue'])
            session_key = json_source['session_key']
            settings.setSetting(id='media_auth', value=media_auth)
            #Update Session Key
            settings.setSetting(id='session_key', value=session_key)
    else:
        msg = json_source['status_message']
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Error Fetching Stream', msg)
        sys.exit()

    return stream_url, media_auth



def getSessionKey(game_id,event_id,content_id,authorization):
    #session_key = ''
    session_key = str(settings.getSetting(id="session_key"))

    if session_key == '':
        epoch_time_now = str(int(round(time.time()*1000)))

        url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?eventId='+event_id+'&format=json&platform='+PLATFORM+'&subject=NHLTV&_='+epoch_time_now
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
            "Authorization": authorization,
            "User-Agent": UA_PC,
            "Origin": "https://www.nhl.com",
            "Referer": "https://www.nhl.com/tv/"+game_id+"/"+event_id+"/"+content_id
        }

        r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
        json_source = r.json()

        xbmc.log("REQUESTED SESSION KEY")
        if json_source['status_code'] == 1:
            if json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']['status'] == 'BlackedOutStatus':
                msg = "The game you are trying to access is not currently available due to local or national blackout restrictions.\n Full game archives will be available 48 hours after completion of this game."
                session_key = 'blackout'
            else:
                session_key = str(json_source['session_key'])
                settings.setSetting(id='session_key', value=session_key)
        else:
            msg = json_source['status_message']
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Error Fetching Stream', msg)

    return session_key


def login():
    #Check if username and password are provided
    global USERNAME
    if USERNAME == '""':
        dialog = xbmcgui.Dialog()
        USERNAME = dialog.input('Please enter your username', type=xbmcgui.INPUT_ALPHANUM)
        settings.setSetting(id='username', value=USERNAME)
        USERNAME = json.dumps(USERNAME)
        sys.exit()

    global PASSWORD
    if PASSWORD == '""':
        dialog = xbmcgui.Dialog()
        PASSWORD = dialog.input('Please enter your password', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        settings.setSetting(id='password', value=PASSWORD)
        PASSWORD = json.dumps(PASSWORD)
        sys.exit()

    if USERNAME != '""' and PASSWORD != '""':
        url = 'https://user.svc.nhl.com/oauth/token?grant_type=client_credentials'
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Accept-Language": "en-US,en;q=0.8",
            "User-Agent": UA_PC,
            "Origin": "https://www.nhl.com",
            "Authorization": "Basic d2ViX25obC12MS4wLjA6MmQxZDg0NmVhM2IxOTRhMThlZjQwYWM5ZmJjZTk3ZTM=",
        }

        r = requests.post(url, headers=headers, data='', cookies=load_cookies(), verify=VERIFY)
        if r.status_code >= 400:
            msg = "Authorization Cookie couldn't be downloaded."
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Authorization Not Found', msg)
            sys.exit()

        json_source = r.json()

        authorization = getAuthCookie()
        if authorization == '':
            authorization = json_source['access_token']


        if ROGERS_SUBSCRIBER == 'true':
            url = 'https://activation-rogers.svc.nhl.com/ws/subscription/flow/rogers.login'
            login_data = '{"rogerCredentials":{"email":'+USERNAME+',"password":'+PASSWORD+'}}'
            #referer = "https://www.nhl.com/login/rogers"
        else:
            url = 'https://user.svc.nhl.com/v2/user/identity'
            login_data = '{"email":{"address":'+USERNAME+'},"type":"email-password","password":{"value":'+PASSWORD+'}}'

        headers = {
             "Accept": "*/*",
             "Accept-Encoding": "identity",
             "Accept-Language": "en-US,en;q=0.8",
             "Content-Type": "application/json",
             "Authorization": authorization,
             "Connection": "keep-alive",
             "User-Agent": UA_PC
         }

        r = requests.post(url, headers=headers, data=login_data, cookies=load_cookies(), verify=VERIFY)

        if r.status_code >= 400:
            try:
                json_source = r.json()
                msg = json_source['message']
            except:
                msg = "Please check that your username and password are correct"
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Login Error', msg)
            sys.exit()

        save_cookies(r.cookies)


def logout(display_msg=None):
    url = 'https://account.nhl.com/ui/rest/logout'
    headers={
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Accept-Language": "en-US,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://account.nhl.com/ui/SignOut?lang=en",
        "Connection": "close",
        "User-Agent": UA_PC
    }

    r = requests.post(url, headers=headers, data='', cookies=load_cookies(), verify=VERIFY)
    if r.status_code >= 400:
        xbmc.log('The server couldn\'t fulfill the request.')
        xbmc.log('Error code: ', e.code)
        xbmc.log(url)


    #Delete cookie file
    try: os.remove(ADDON_PATH_PROFILE+'cookies.lwp')
    except: pass

    if display_msg == 'true':
        settings.setSetting(id='session_key', value='')
        dialog = xbmcgui.Dialog()
        title = "Logout Successful"
        dialog.notification(title, 'Logout completed successfully', ICON, 5000, False)


def myTeamsGames():
    if FAV_TEAM != 'None':
        end_day = localToEastern()
        end_date = stringToDate(end_day, "%Y-%m-%d")
        start_date = end_date - timedelta(days=30)
        start_day = start_date.strftime("%Y-%m-%d")


        url = API_URL+'schedule?teamId='+FAV_TEAM_ID+'&startDate='+start_day+'&endDate='+end_day+'&expand=schedule.teams,schedule.linescore,schedule.scoringplays,schedule.game.content.media.epg'
        headers = {'User-Agent': UA_IPHONE}
        r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
        json_source = r.json()

        for date in reversed(json_source['dates']):
            #temp_date = stringToDate(date['date'], "%Y-%m-%d")
            #date_display = '[B][I]'+ colorString(temp_date.strftime("%A, %m/%d/%Y"),GAMETIME_COLOR)+'[/I][/B]'
            #addDir(date_display,'/nothing',999,ICON,FANART)
            for game in date['games']:
                createGameListItem(game, date['date'])


    else:
        msg = "Please select your favorite team from the addon settings"
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Favorite Team Not Set', msg)


def playTodaysFavoriteTeam():

    if FAV_TEAM != 'None':
        end_day = localToEastern()
        start_day = end_day

        url = API_URL+'schedule?teamId='+FAV_TEAM_ID+'&startDate='+start_day+'&endDate='+end_day+'&expand=schedule.game.content.media.epg,schedule.teams'
        headers = {'User-Agent': UA_IPHONE}

        r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
        json_source = r.json()

        stream_url = ''
        if json_source['dates']:
            todays_game = json_source['dates'][0]['games'][0]

            # Determine if favorite team is home or away
            fav_team_homeaway = ''

            away = todays_game['teams']['away']['team']
            home = todays_game['teams']['home']['team']

            if FAV_TEAM_ID == str(away['id']):
                fav_team_homeaway = 'AWAY'

            if FAV_TEAM_ID == str(home['id']):
                fav_team_homeaway = 'HOME'


            # Grab the correct feed (home/away/national)
            epg = todays_game['content']['media']['epg']
            streams = epg[0]['items']
            local_stream = {}
            natl_stream = {}
            for stream in streams:
                feedType = stream['mediaFeedType']
                if feedType == fav_team_homeaway:
                    local_stream = stream
                    break
                elif feedType == 'NATIONAL':
                    natl_stream = stream
            if not local_stream:
                local_stream = natl_stream

            game_id = str(todays_game['gamePk'])

            # Create the stream url
            stream_url, media_auth = fetchStream(str(game_id), local_stream['mediaPlaybackId'], local_stream['eventId'])
            stream_url = createFullGameStream(stream_url, media_auth, local_stream['mediaState'])

        else:
            dialog = xbmcgui.Dialog()
            dialog.ok('No Game Today', FAV_TEAM + " doesn't play today")

        listitem = xbmcgui.ListItem(path=stream_url)
        if stream_url != '':
            listitem.setMimeType("application/x-mpegURL")
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        else:
            xbmcplugin.setResolvedUrl(addon_handle, False, listitem)


    else:
        msg = "Please select your favorite team from the addon settings"
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Favorite Team Not Set', msg)


def gotoDate():
    #Goto Date
    search_txt = ''
    dialog = xbmcgui.Dialog()
    #game_day = dialog.input('Enter date (yyyy-mm-dd)', type=xbmcgui.INPUT_ALPHANUM)
    game_day = ''

    #Year
    year_list = []
    #year_item = datetime.now().year
    year_item = 2015
    while year_item <= datetime.now().year:
        year_list.insert(0,str(year_item))
        year_item = year_item + 1

    ret = dialog.select('Choose Year', year_list)

    if ret > -1:
        year = year_list[ret]

        #Month
        #mnth_name = ['September','October','November','December','Janurary','February','March','April','May','June']
        #mnth_num = ['9','10','11','12','1','2','3','4','5','6']

        mnth_name = ['Janurary','February','March','April','May','June','September','October','November','December']
        mnth_num = ['1','2','3','4','5','6','9','10','11','12']

        ret = dialog.select('Choose Month', mnth_name)

        if ret > -1:
            mnth = mnth_num[ret]

            #Day
            day_list = []
            day_item = 1
            last_day = calendar.monthrange(int(year), int(mnth))[1]
            while day_item <= last_day:
                day_list.append(str(day_item))
                day_item = day_item + 1

            ret = dialog.select('Choose Day', day_list)

            if ret > -1:
                day = day_list[ret]
                game_day = year+'-'+mnth.zfill(2)+'-'+day.zfill(2)


    if game_day != '':
        todaysGames(game_day)
    else:
        sys.exit()

def nhlVideos(selected_topic=None):
    #url = 'http://nhl.bamcontent.com/nhl/en/section/v1/video/nhl/ios-tablet-v1.json'
    url = 'http://nhl.bamcontent.com/nhl/en/nav/v1/video/connectedDevices/nhl/playstation-v1.json'

    headers = {'User-Agent': UA_PS4,
    }

    r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
    json_source = r.json()

    if selected_topic == None or 'topic=' not in selected_topic:
        for topic in json_source['topics']:
            addDir(topic['title'],'/topic='+topic['title']+'&',300,ICON,FANART)
    else:
        topic = find(selected_topic,'topic=','&')

        for main_topic in json_source['topics']:
            if topic == main_topic['title']:
                for video in main_topic['list']:
                    title = video['title']
                    name = title
                    icon = video['image']['cuts']['1136x640']['src']
                    url = video['playbacks'][4]['url']
                    desc = video['description']
                    release_date = video['date'][0:10]
                    duration = video['duration']

                    bandwidth = find(QUALITY,'(',' kbps)')
                    if bandwidth != '':
                        url = url.replace('master_wired60.m3u8', 'asset_'+bandwidth+'k.m3u8')
                    url = url + '|User-Agent='+UA_PS4

                    audio_info, video_info = getAudioVideoInfo()
                    info = {'plot':desc,'tvshowtitle':'NHL','title':name,'originaltitle':name,'duration':'','aired':release_date}
                    addLink(name,url,title,icon,info,video_info,audio_info,icon)
