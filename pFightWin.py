#-------------------------------------------------------------
# pFight v0.2 by JRattan
#
#
# Status: (4/19/2013)
#   -Currently only one player
#   -AI just simple random integeres
#
# Used: Python 3.3 with Pygame 1.9.1
#
# Controls:
#   x           - Attack
#   up          - Jump
#   down        - Crouch
#   left/right  - Move
#   enter       - Pause/Confirm
#   space       - Switch to Debug Mode
#   esc         - Exit game
#
# Attack Types:
#   low: attack when crouching
#      : can be blocked only when crouching
#   mid: attack when standing
#      : can be blocked
#  high: attack when on the air
#      : can be blocked only when standing
#
#
# Credits to:
#   - Chumbucket for the sprite template
#-------------------------------------------------------------


import sys, pygame, random, math, time, pygame._view
from pygame.locals import *

VERSION = 'v0.2'
FPS = 30
WINWIDTH = 540
WINHEIGHT = 420

BOTTOM = WINHEIGHT - 90 # The 'floor' of the room
COMPOS = (96, 0)        # Position of Commentary Text
LEFT = -1
RIGHT = 1
MAXROUNDS = 3

# STATUS FLAGS
IDLE = 'idle'
WALK = 'walk'
JUMP = 'jump'
CROUCH = 'crouch'
BLOCK = 'block'
ATTACK = 'attack'
HIT = 'hit'
POSE = 'pose'

# Attack Types
MID = 0
LOW = 1
HIGH = 2

GRAVITY = 1.0           # Gravity Speed

# Color            R    G    B
BLACK        =  (   0,   0,   0)
WHITE        =  ( 255, 255, 255)
GRAY         =  ( 155, 155, 155)
RED          =  ( 255,   0,   0)
GREEN        =  (   0, 255,   0)
YELLOW       =  ( 255, 255,   0)
LIGHTBLUE    =  ( 155, 155, 255)
LIGHTPURPLE  =  ( 255, 155, 255)

def main():
    global FPSCLOCK, DISPLAYSURF, FONTOBJ, FONTSM,\
           COMMENTS, COMMENTATOR, WINS, DEMO,\
           SNDPUNCH, SNDBELL, SNDHIT, SNDKO, SNDTIMEOUT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('data/michael16bit.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Practice Fighter')

    # Font Initialization
    FONTOBJ = pygame.font.Font('data/freesansbold.ttf', 32)
    FONTSM = pygame.font.Font('data/freesansbold.ttf', 16)

    # Comment Initialization
    COMMENTS = []
    COMMENTATOR = True

    # Match Rounds Initialization
    rounds = 0
    WINS = [0,0]
    DEMO = False

    #Music initialization
    pygame.mixer.init()
    pygame.mixer.music.load('data/bgm/rain.wav')

    # Sound Initialization
    SNDPUNCH = pygame.mixer.Sound('data/sound/whoosh2.wav')
    SNDHIT = pygame.mixer.Sound('data/sound/mm_hit.wav')
    SNDBELL = pygame.mixer.Sound('data/sound/bell.wav')
    SNDKO = pygame.mixer.Sound('data/sound/bash.wav')
    SNDTIMEOUT = pygame.mixer.Sound('data/sound/clock.wav')
    
    # Game Loop
    while True:
        COMMENTATOR = titleScreen()         # Title Screen

        # Game Play resets
        rounds = 0                          # Reset round number
        COMMENTS = []                       # Clear comments
        WINS = [0, 0]                       # Rest Wins
        pygame.mixer.music.play(-1, 0.0)    # Start playing music

        # Main Game Screen
        while(rounds < MAXROUNDS):
            rounds += arenaGame(rounds + 1, MAXROUNDS)

        pygame.mixer.music.stop()           # Stop music

# Game's title screen
#   - returns a boolean where pressing:
#       ENTER = False
#       SPACE = True
def titleScreen():
    global DEMO, MAXROUNDS
    
    #Title Screen Text
    titleScreen = FONTOBJ.render('Python Fighting Game', True, WHITE)
    titleScreenRect = titleScreen.get_rect()
    titleScreenRect.center = (WINWIDTH / 2, WINHEIGHT / 2 - 32)

    commentScreen = FONTSM.render('press Space to Start with Commentary', True, WHITE)
    commentRect = commentScreen.get_rect()
    commentRect.center = (WINWIDTH / 2, WINHEIGHT / 2 + 32)
    
    pressKeyScreen = FONTSM.render('press Enter to Start', True, WHITE)
    pressKeyRect = pressKeyScreen.get_rect()
    pressKeyRect.midleft = (commentRect.left, commentRect.top - 24)

    versionSurf = FONTSM.render('version %s' % VERSION, True, WHITE)
    versionRect = versionSurf.get_rect()
    versionRect.midbottom = (WINWIDTH / 2, WINHEIGHT - 4)

    demoSurf = FONTSM.render('Demo Mode', True, RED)
    demoRect = demoSurf.get_rect()
    demoRect.midbottom = (WINWIDTH / 2, WINHEIGHT - 24)

    while True:
        #Text that displays number of rounds
        roundSurf = FONTSM.render('rounds: %s (press Left/Right to change)' % MAXROUNDS, True, WHITE)
        roundRect = roundSurf.get_rect()
        roundRect.midleft = (commentRect.left, commentRect.top + 36)

        #Events
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN:
                    return False
                elif event.key == K_SPACE:
                    return True
                elif event.key == K_x:
                    DEMO = (DEMO + True) % 2
                elif event.key == K_LEFT:
                    MAXROUNDS -= 2
                    if MAXROUNDS < 1:
                        MAXROUNDS = 1
                elif event.key == K_RIGHT:
                    MAXROUNDS += 2
                    if MAXROUNDS > 9:
                        MAXROUNDS = 9

        #Backgrund
        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(titleScreen, titleScreenRect)
        DISPLAYSURF.blit(pressKeyScreen, pressKeyRect)
        DISPLAYSURF.blit(commentScreen, commentRect)
        DISPLAYSURF.blit(versionSurf, versionRect)
        DISPLAYSURF.blit(roundSurf, roundRect)
        if DEMO:
            DISPLAYSURF.blit(demoSurf, demoRect)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# Pause screen during the game
#   - Stops the current game
#   - Has two options:
#       @Continue the game
#       @Return to the title screen
#   - Accepts an array to keep track of which buttons are still pressed
#   - If COMMENTATOR = True, the game will show various texts in a random
#       interval
def pause(move1):
    # Dancing Banana
    bananaTime = time.time()
    bananaMax = 0.097
    bananaIndex = 0
    bananaSurf, bananaRect = createAnimation('data/banana/banana_frame_000', 9, True)
    for i in range(0, len(bananaSurf)):
        bananaSurf[i] = pygame.transform.scale(bananaSurf[i], (100, 103))
    bananaRect = (32, WINHEIGHT / 2 - 32, 100, 103)
    bananaRect2 = (WINWIDTH - 132, WINHEIGHT / 2- 32, 100, 103)
    
    # PAUSED text
    pauseText = FONTOBJ.render('paused', True, WHITE)
    pauseTextRect = pauseText.get_rect()
    pauseTextRect.center = (WINWIDTH / 2, WINHEIGHT / 2 - 32)

    # continue option
    resumeText = FONTSM.render('continue', True, WHITE)
    resumeTextRect = resumeText.get_rect()
    resumeTextRect.center = (WINWIDTH / 2, WINHEIGHT /2 + 18)

    # quit option
    quitText = FONTSM.render('quit', True, WHITE)
    quitTextRect = quitText.get_rect()
    quitTextRect.center = (WINWIDTH / 2, WINHEIGHT / 2 + 18 * 2)

    # continue and quit options when unselected
    resumeUnselect = FONTSM.render('continue', True, GRAY)
    quitUnselect = FONTSM.render('quit', True, GRAY)

    # handle menu items when paused
    select = 0
    maxItems = 2

    if COMMENTATOR:
        # Announcer
        commentSurf = pygame.Surface((WINWIDTH, 97))
        announcer = pygame.image.load("data/michael24bit.png")
        announcerRect = announcer.get_rect()
        announcerRect.topleft = (8, 0)
        startTime = time.time()
        waitTime = random.randint(2, 10)
        textChoices = ['I\'m waiting...',\
                       'Nice weather we\'re having...',\
                       'Can we get back to the fighting?',\
                       'Done with your bathroom break?',\
                       'Helloooooooo?',\
                       'I had dinner for breakfast at lunch.',\
                       'This game is PAUSED, do something about it!',\
                       '\"Baby don\'t hurt me, don\'t hurt me, no more...\"',\
                       '\"What is love?\"',\
                       'Let\'s get this show on the road!',\
                       'I like turtles :D',\
                       'CHARLIE BIT ME!',\
                       'I married a cake once, but it cheated on me...',\
                       'Like this song? Then don\'t condone piracy!',\
                       'LEEERRROOOOOYYY JEEENNNKIIIINNNSSS!',\
                       'Ponies!',\
                       'I KNOW EVERYTHING! I FEEL EVERYTHING!',\
                       'FUS RO DAH!',\
                       'Memes...',\
                       'Onixes and Cloysters!', \
                       '\"HEYYEYAAEYAAAEYAEYAA\"',\
                       '\"What\'s going on?\"',\
                       'Rick Roll\'d']
        textIndex = random.randint(0, len(textChoices) - 1)         
    
    # Screen Surfaces
    transSurf = pygame.Surface((WINWIDTH / 2, WINHEIGHT / 2)).convert_alpha()   # transparent box surface
    copySurf = DISPLAYSURF.copy() # surface of previous screen
    
    while True:
        if COMMENTATOR:
            if time.time() - startTime > waitTime:
                newText = textChoices[textIndex]
    
                newComment(COMMENTS, newText, COMPOS, GREEN)
                startTime = time.time()
                waitTime = random.randint(2, 10)
                textIndex = random.randint(0, len(textChoices) - 1)

            commentUpdate(COMMENTS)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                keyhandle(event, move1)
            elif event.type == KEYUP:
                keyhandle(event, move1, 1)
                if event.key == K_UP:
                    if select - 1 < 0:
                        select = maxItems - 1
                    else:
                        select -= 1
                elif event.key == K_DOWN:
                    select = (select + 1) % maxItems
                
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN:
                    return select
        
        transSurf.fill((0, 0, 0, 155))
        DISPLAYSURF.blit(copySurf, (0,0))
        DISPLAYSURF.blit(transSurf, (WINWIDTH / 4,WINHEIGHT / 4))
        DISPLAYSURF.blit(pauseText, pauseTextRect)

        #Highlights selected text
        if select == 0:
            DISPLAYSURF.blit(resumeText, resumeTextRect)
            DISPLAYSURF.blit(quitUnselect, quitTextRect)
        elif select == 1:
            DISPLAYSURF.blit(resumeUnselect, resumeTextRect)
            DISPLAYSURF.blit(quitText, quitTextRect)

        if COMMENTATOR:
            # Draw Commentator Text
            commentSurf.fill(BLACK)
            for text in COMMENTS:
                commentSurf.blit(text[0], text[1])
            commentSurf.blit(announcer, announcerRect)

            DISPLAYSURF.blit(commentSurf, (0, WINHEIGHT - 114))

        # Banana Update
        if time.time() - bananaTime > bananaMax:
            bananaIndex = (bananaIndex + 1) % len(bananaSurf)
            bananaTime = time.time()
        DISPLAYSURF.blit(bananaSurf[bananaIndex], bananaRect)
        DISPLAYSURF.blit(bananaSurf[bananaIndex], bananaRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def arenaGame(rounds, maxRounds):
    global DEMO, WINS
    
    # Load Background
    background, backgroundRect = createAnimation("data/kof/kof_frame_000", 8)
    backgroundRect.center = (WINWIDTH / 2, WINHEIGHT / 2 - 32)
    backTime = time.time()
    backMaxTime = 0.07
    backIndex = 0

    # Load Win Rounds
    p1RoundText = FONTSM.render('Wins: %s' % WINS[0], True, WHITE, BLACK)
    p1RoundRect = p1RoundText.get_rect()
    p1RoundRect.topleft = (4, 68)

    p2RoundText = FONTSM.render('Wins: %s' % WINS[1], True, WHITE, BLACK)
    p2RoundRect = p2RoundText.get_rect()
    p2RoundRect.topright = (WINWIDTH - 4, 68)
    celebrate = False

    # Timer
    lastCountTime = time.time()
    timeDiff = 0.90
    timer = 60

    # Start / End Round Time
    roundTime = time.time()
    maxTime = 2.5

    # Player 1 images
    # Each variable is a tuple that contains: image, center for hitbox, and (width and height of hitbox))
    p1ImageIdle = (pygame.image.load("data/stand2.png"), (30, 46), (40,92))
    p1ImageAttack1 = (pygame.image.load("data/punch1.png"), (30, 46), (40,98))
    p1ImageAttack2 = (pygame.image.load("data/punch2.png"), (40, 35), (40,72))
    p1ImageAttack3 = (pygame.image.load("data/punch3.png"), (34, 46), (40,92))
    p1ImageCrouch = (pygame.image.load("data/crouch1.png"), (30, 35), (40,70))
    p1ImageWalk = p1ImageIdle #placeholder
    p1ImageJump = p1ImageIdle #placeholder
    p1ImageBlock = (pygame.image.load("data/block.png"), (30, 45), (40, 90))
    p1ImageHit = (pygame.image.load("data/hit.png"), (30, 45), (40, 90))
    p1Sprites = {}
    p1Sprites[IDLE] = p1ImageIdle
    p1Sprites[WALK] = p1ImageWalk
    p1Sprites[JUMP] = p1ImageIdle
    p1Sprites[ATTACK] = [p1ImageAttack1, p1ImageAttack2, p1ImageAttack3]
    p1Sprites[CROUCH] = p1ImageCrouch
    p1Sprites[BLOCK] = p1ImageBlock
    p1Sprites[HIT] = p1ImageHit

    if COMMENTATOR:
        # Announcer
        commentSurf = pygame.Surface((WINWIDTH, 97))
    
        announcer = pygame.image.load("data/michael24bit.png")
        announcerRect = announcer.get_rect()
        announcerRect.topleft = (8, 0)

        commentReset(COMMENTS)
        newComment(COMMENTS, 'Let\'s get ready to RUMMMBBBBLLLLEEE!', COMPOS)

    # Event Flag
    eventMode = True
    winner = None
    
    # Debug mode
    debug = False
    hitBoxSurface = pygame.Surface((WINWIDTH, WINHEIGHT)).convert_alpha()

    #Creating Characters
    player1 = createPlayer(p1Sprites, (WINWIDTH // 2 - 100, BOTTOM), speed=2, name='Cleft')
    player2 = createPlayer(p1Sprites, (WINWIDTH // 2+ 100, BOTTOM), facing=LEFT, speed=2, name='Wright')
    player1['foe'] = player2
    player2['foe'] = player1

    # Character Text
    p1TextSurf = FONTSM.render('%s' % player1['id'], True, WHITE, BLACK)
    p1TextRect = p1TextSurf.get_rect()
    p1TextRect.bottomright = (WINWIDTH / 4, 28)

    # Character Text
    p2TextSurf = FONTSM.render('%s' % player2['id'], True, WHITE, BLACK)
    p2TextRect = p2TextSurf.get_rect()
    p2TextRect.bottomleft = (WINWIDTH - WINWIDTH / 4, 28)
        
    while True:
        # Update Comment Texts
        commentUpdate(COMMENTS)

        # Obtain Events
        eventList = pygame.event.get()
        
        # Able to quit anytime
        for event in eventList:
            if event.type == QUIT:
                terminate()
        
        # Checks if Characters can move or not
        if not eventMode:            
            # Endgame Check
            if (player1['health'] == 0):
                SNDKO.play()
                winner = player2['id']
                eventMode = True
                roundTime = time.time()
                WINS[1] += 1
                player1['attTime'] = 0
                continue
           
            if (player2['health'] == 0):
                SNDKO.play()
                winner = player1['id']
                eventMode = True
                roundTime = time.time()
                WINS[0] += 1
                player2['attTime'] = 0
                continue

            # Timer
            if time.time() - lastCountTime > timeDiff:
                if (timer == 0):
                    SNDTIMEOUT.play()
                    eventMode = True
                    roundTime = time.time()
                    if player1['health'] > player2['health']:
                        winner = player1['id']
                        newComment(COMMENTS, '%s wins the round!' % winner, COMPOS, YELLOW)
                        WINS[0] += 1
                    elif player2['health'] > player1['health']:
                        winner = player2['id']
                        newComment(COMMENTS, '%s wins the round!' % winner, COMPOS, YELLOW)
                        WINS[1] += 1
                    else:
                        winner = 'draw'
                        newComment(COMMENTS, 'It\'s a draw...PATHETIC!', COMPOS, YELLOW)
                    continue
                else:
                    timer -= 1
                    lastCountTime = time.time()              
                    if ((timer  % 10 == 0 and timer != 0) or timer == 15):
                        newComment(COMMENTS, '%s seconds remaining!' % timer, COMPOS, RED)
                    elif timer < 10:
                        newComment(COMMENTS, '%s...' % timer, COMPOS, RED)
                    elif playerStatus(player1) is not HIT and\
                         playerStatus(player2) is not HIT:
                        newComment(COMMENTS, '...', COMPOS)
            
            # Event handling
            for event in eventList:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        debug = (debug + 1) % 2
                    elif not DEMO:
                        keyhandle(event, player1['move'], 0)
                    
                elif event.type == KEYUP:
                    if event.key == K_RETURN:
                        if pause(player1['move']) == 1:
                            return maxRounds

                    # Event handle when key is released
                    if not DEMO:
                        keyhandle(event, player1['move'], 1)

                    if event.key == K_ESCAPE:
                        terminate()

            #AI
            if DEMO:
                aiHandle(player1)
            aiHandle(player2)

            # Handle player key events
            playerEvents(player1)
            player1['move'][4] = False
            playerEvents(player2)
            player2['move'][4] = False
            
            # Update Objects
            playerUpdate(player1)
            playerUpdate(player2)

        elif winner is None and time.time() - roundTime > maxTime:
            lastCountTime = time.time()
            eventMode = False
            commentReset(COMMENTS)
            newComment(COMMENTS, 'Fight!', COMPOS)
            SNDBELL.play()

        # Draw Objects
        DISPLAYSURF.fill(BLACK)

        #Draw Background
        if time.time() - backTime > backMaxTime:
            backIndex = (backIndex + 1) % len(background)
            backTime = time.time()
        DISPLAYSURF.blit(background[backIndex], backgroundRect)

        #Draw Players
        playerDraw(player1, DISPLAYSURF)
        playerDraw(player2, DISPLAYSURF)

        # Draw Health Meter
        #   player 1 meter
        pygame.draw.rect(DISPLAYSURF, (0, 150, 0), ((WINWIDTH / 2 - 22)- ((WINWIDTH / 2 - 22) * (player1['health']/100)), 32,\
                                                    WINWIDTH / 2 - ((WINWIDTH / 2 - 22) - ((WINWIDTH / 2 - 22)* (player1['health']/100))) - 22, 32))
        pygame.draw.rect(DISPLAYSURF, (255, 255, 255), (0, 32, WINWIDTH / 2, 32), 4)
        DISPLAYSURF.blit(p1RoundText, p1RoundRect)
        DISPLAYSURF.blit(p1TextSurf, p1TextRect)
        
        #   player 2 meter
        pygame.draw.rect(DISPLAYSURF, (0, 150, 0), (WINWIDTH / 2 + 28, 32,\
                                                    WINWIDTH / 2- ((WINWIDTH / 2 - 28)- ((WINWIDTH  / 2 - 28)* (player2['health']/100))) - 28, 32))
        pygame.draw.rect(DISPLAYSURF, (255, 255, 255), (WINWIDTH / 2, 32, WINWIDTH / 2, 32), 4)
        DISPLAYSURF.blit(p2RoundText, p2RoundRect)
        DISPLAYSURF.blit(p2TextSurf, p2TextRect)

        timerDraw(timer)

        if debug:
            # Draw HitBox (for Debug)
            hitBoxSurface.fill((0,0,0,0))
            pygame.draw.rect(hitBoxSurface, (0, 150, 0, 150), player1['hitbox'])
            pygame.draw.rect(hitBoxSurface, (0, 150, 0, 150), player2['hitbox'])

            if player1['lastAtt'] is not None:
                pygame.draw.rect(hitBoxSurface, (150, 0, 0, 150), player1['lastAtt'])
            if player2['lastAtt'] is not None:
                pygame.draw.rect(hitBoxSurface, (150, 0, 0, 150), player2['lastAtt'])
            DISPLAYSURF.blit(hitBoxSurface, (0,0))
            player1['health'] = player2['health'] = 100

        if eventMode:
            if winner is None:
                centerTextDraw(DISPLAYSURF, 'Round %s' % rounds, (WINWIDTH / 2, WINHEIGHT / 2))
            else:
                if winner is not 'draw':
                    centerTextDraw(DISPLAYSURF, '%s wins' % winner, (WINWIDTH / 2, WINHEIGHT / 2))
                else:
                    centerTextDraw(DISPLAYSURF, 'Draw', (WINWIDTH / 2, WINHEIGHT / 2))
                if time.time() - roundTime > maxTime:
                    if not celebrate:
                        maximum = math.floor(maxRounds / 2)
                        if (rounds < maxRounds) and (WINS[0] > maximum or WINS[1] > maximum):
                            SNDBELL.play()
                            celebrate = True
                            roundTime = time.time()
                            newComment(COMMENTS, '%s wins the match, congratulations!' % winner, COMPOS, YELLOW)
                            winner = player1['id'] * (WINS[0] > WINS[1]) + player2['id'] * (WINS[1] > WINS[0])
                        elif (rounds == maxRounds):
                            SNDBELL.play()
                            celebrate = True
                            roundTime = time.time()
                            if WINS[0] > WINS[1]:
                                winner = player1['id'] * (WINS[0] > WINS[1]) + player2['id'] * (WINS[1] > WINS[0])
                                newComment(COMMENTS, '%s wins the match, congratulations!' % player1['id'], COMPOS, YELLOW)
                            elif WINS[1] > WINS[0]:
                                winner = player1['id'] * (WINS[0] > WINS[1]) + player2['id'] * (WINS[1] > WINS[0])
                                newComment(COMMENTS, '%s wins the match, congratulations!' % player2['id'], COMPOS, YELLOW)
                            else:
                                newComment(COMMENTS, 'Draw...Such a shame.', COMPOS, YELLOW)
                        else:
                            return 1
                    else:
                        return maxRounds

        if COMMENTATOR:
            # Draw Commentator Text
            commentSurf.fill(BLACK)
            for text in COMMENTS:
                commentSurf.blit(text[0], text[1])
            commentSurf.blit(announcer, announcerRect)
            DISPLAYSURF.blit(commentSurf, (0, WINHEIGHT - 114))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def keyhandle(event, move, keyup=0):
    moveLeft = 0
    moveRight = 1
    moveUp = 2
    moveDown = 3
    canAttack = 4

    if keyup == 0:
        if event.key == K_LEFT:
            move[moveLeft] = True
            move[moveRight] = False
        elif event.key == K_RIGHT:
            move[moveLeft] = False
            move[moveRight] = True
        elif event.key == K_UP:
            move[moveUp] = True
            move[moveDown] = False
        elif event.key == K_DOWN:
            move[moveUp] = False
            move[moveDown] = True
        elif event.key == K_x:
            move[canAttack] = True
            
    elif keyup == 1:
        if event.key == K_LEFT:
            move[moveLeft] = False
        elif event.key == K_RIGHT:
            move[moveRight] = False
        elif event.key == K_UP:
            move[moveUp] = False
        elif event.key == K_DOWN:
            move[moveDown] = False

def aiHandle(player):
    # Syntatic sugars
    moveLeft = 0
    moveRight = 1
    moveUp = 2
    moveDown = 3
    canAttack = 4
    move = player['move']

    # Disable some movement keys
    move[moveUp] = False
    
    # AI
    chance = random.randint(0, 20)
    if chance in (0, 5, 13, 14):
        if (math.fabs(player['x'] - player['foe']['x']) > player['surface'].get_width()):
            move[moveDown] = False
            move[moveLeft] = True
            move[moveRight] = False
        else:
            move[moveLeft] = False
    elif chance in (1, 3, 11, 12):
        if (math.fabs(player['x'] - player['foe']['x']) < player['surface'].get_width() + 100):
            move[moveDown] = False
            move[moveLeft] = False
            move[moveRight] = True
        else:
            move[moveRight] = False
    if chance in (4, 12, 0) and (math.fabs(player['x'] - player['foe']['x']) < player['surface'].get_width() + 4):
        move[canAttack] = True
    if chance in (6, 7):
        move[moveLeft] = False
        move[moveRight] = False
    if chance in (8, 9):
        move[moveDown] = False
        move[moveUp] = True
    if chance in (10, 15):
        move[moveUp] = False
        move[moveDown] = True

def createPlayer(imageDict, pos, facing=RIGHT, speed=2, name='character'):
    sq = {}
    # Attributes for sprite
    sq['imgList'] = imageDict
    sq['surface'] = imageDict[IDLE][0]
    
    # Character stats
    sq['id'] = name
    sq['x'], sq['y'] = pos
    sq['dx'], sq['dy'] = (0, 0)
    sq['attDY'] = 0
    sq['speed'] = speed
    sq['facing'] = facing
    sq['damage'] = 0
    sq['health'] = 100
    sq['move'] = [False] * 5

    # Status Flags
    # Note: Idle flag is true if all flags are false.
    sq[JUMP] = False
    sq[ATTACK] = False
    sq[CROUCH] = False
    sq[BLOCK] = False
    sq[HIT] = False
    sq['attType'] = 0

    # Time Attributes
    sq['attTime'] = 0
    sq['maxTime'] = 0

    # Reference Attributes
    sq['lastHit'] = None
    sq['lastAtt'] = None
    sq['foe'] = None
    
    # Draw Rect
    width, height = imageDict[IDLE][0].get_size()
    sq['rect'] = pygame.Rect( (sq['x'] - (width / 2), sq['y'] - height,\
                               width, height))
    # HitBox Rect
    sq['boxCenter'] = imageDict[IDLE][1]
    sq['boxSize'] = imageDict[IDLE][2]
    sq['hitbox'] = pygame.Rect( (0, 0, sq['boxSize'][0], sq['boxSize'][1]))
    sq['hitbox'].center = (sq['rect'].left + sq['boxCenter'][0],\
                           sq['rect'].top + sq['boxCenter'][1])

    # Assign Image
    playerImgSet(sq, IDLE)
    return sq

def playerEvents(player):
    moveLeft = 0
    moveRight = 1
    moveUp = 2
    moveDown = 3
    attBtn = 4
    move = player['move']

    if not player[HIT]:
        #Checks if player is blocking
        if player[BLOCK] and not player['foe'][ATTACK]:
            player[BLOCK] = False
            playerImgSet(player, playerStatus(player))
        else:
            # Checks if Character is not attacking
            if not player[ATTACK]:
                # Check if Character is on the ground
                if not player[JUMP]:
                    #Check if Character is not crouching
                    if not player[CROUCH]:
                        #Crouch
                        if move[moveDown]:
                            player[CROUCH] = True
                            playerImgSet(player, CROUCH)
                        #Movements
                        else:
                            # Block if possible
                            if player['foe'][ATTACK] and\
                               ((move[moveRight] and player['facing'] == LEFT) or\
                               (move[moveLeft] and player['facing'] == RIGHT)):
                                player[BLOCK] = True
                                playerImgSet(player, BLOCK)
                            else:
                                player['dx'] = (player['speed'] * move[moveRight]) -\
                                               (player['speed'] * move[moveLeft])
                                playerImgSet(player, WALK)
                    # Checks if Character is crouching but is no longer holding the moveDown button
                    else:
                        if player['foe'][ATTACK] and\
                               ((move[moveRight] and player['facing'] == LEFT) or\
                               (move[moveLeft] and player['facing'] == RIGHT)):
                                player[BLOCK] = True
                                playerImgSet(player, BLOCK)
                        if not move[moveDown]:
                            player[CROUCH] = False
                            playerImgSet(player, IDLE)

                    # Jump
                    if move[moveUp]:
                        player['dy'] = -10
                        player[JUMP] = True
                        playerImgSet(player, JUMP)

                # Attack
                if move[attBtn]:
                    player[ATTACK] = True
                    SNDPUNCH.play()
                    playerEvents(player['foe']) # For updating block
                    
                    if player[CROUCH]:
                        player['maxTime'] = 5
                        player['damage'] = 2
                        player['attType'] = LOW
                        player['lastAtt'] = pygame.Rect(player['x'] - ((player['facing'] == LEFT) * 42), player['y'] - 24, 42, 18)
                        player['attDy'] = -8
                    elif player[JUMP]:
                        player['maxTime'] = 30
                        player['damage'] = 6
                        player['attType'] = HIGH
                        player['lastAtt'] = pygame.Rect(player['x'] - ((player['facing'] == LEFT) * 42), player['y'] - 24, 42, 42)
                        player['attDy'] = 8
                    else:
                        player['maxTime'] = 5
                        player['damage'] = 4
                        player['attType'] = MID
                        player['lastAtt'] = pygame.Rect(player['x'] - ((player['facing'] == LEFT) * 42), player['y'] - 16, 42, 18)
                        player['attDy'] = -16
                    playerImgSet(player, ATTACK, player['attType'])
            
def playerUpdate(player):
    # Moves player by dx
    if player['dx'] and isFreeX(player, player['dx']):
        move = player['dx']
        if (player['facing'] == RIGHT and move < 0) or (player['facing'] == LEFT and move > 0):
            move /= 2
        player['x'] += move
        player['hitbox'].centerx = player['x']
        if not player[JUMP] and not player[HIT]:
            player['dx'] = 0

    # Moves player when jumping
    if player[JUMP]:
        player['y'] += player['dy']
        player['hitbox'].centery = player['y']
        player['dy'] += GRAVITY
        if player['y'] > BOTTOM:
            player['y'] = BOTTOM
            player['dx'] = player['dy'] = 0
            player[JUMP] = False
            if not player[HIT]: # or not player[HIT]:
                if player[ATTACK]:
                    player[ATTACK] = False
                    player['attTime'] = 0
                    player['lastAtt'] = None
                playerImgSet(player, IDLE)

    collisionUpdate(player)

    # Plyaer gets hit
    if player[HIT]:
        player['attTime'] += 1
        if (player['attTime'] > player['maxTime']):
            player[HIT] = False
            player['attTime'] = 0
            player['dx'] = 0
            image = playerStatus(player)
            playerImgSet(player,image)
    
    # Attack
    if player[ATTACK]:
        player['attTime'] += 1
        if (player['attTime'] > player['maxTime']):
            player[ATTACK] = False
            player['attTime'] = 0
            player['lastAtt'] = None
            image = playerStatus(player)
            playerImgSet(player,image)

def collisionUpdate(player):
    # Draws Collision box        
    player['rect'].center = (player['x'], player['y'] - player['surface'].get_height())
    player['hitbox'].center = (player['rect'].left + player['boxCenter'][0],\
                               player['rect'].top + player['boxCenter'][1])
    player['hitbox'].size = player['boxSize']
    #Hit Collision
    if player['lastAtt'] is not None:
        player['lastAtt'].topleft = (player['hitbox'].centerx -\
                                     ((player['facing'] == LEFT) * 42),\
                                     player['hitbox'].centery + player['attDy'])
        
        if player['lastAtt'].colliderect(player['foe']['hitbox']) and player['foe']['lastHit'] is not player['lastAtt']:
            player['foe']['lastHit'] = player['lastAtt']
            if player['foe'][BLOCK] and ((player['foe'][CROUCH] and player['attType'] in (CROUCH, MID)) or (player['attType'] in (HIGH, MID))):
                newComment(COMMENTS, '%s blocks the attack!' % player['foe']['id'], COMPOS, LIGHTBLUE)
                return
            newComment(COMMENTS, '{} receives {} damage!'.format(player['foe']['id'], player['damage']), COMPOS, LIGHTPURPLE)
            player['foe']['health'] -= player['damage']
            SNDHIT.play()
            if player['foe']['health'] <= 0:
                player['foe']['health'] = 0
                newComment(COMMENTS, '%s K.O.' % player['foe']['id'], COMPOS, YELLOW)
            player['foe'][HIT] = True
            player['foe'][ATTACK] = False
            player['foe']['lastAtt'] = None
            player['foe']['maxTime'] = 10
            player['foe']['attTime'] = 0
            playerImgSet(player['foe'], HIT)
            player['foe']['dx'] = -2 * player['foe']['facing']
           
def playerImgSet(player, key, index=0):
    imgList = player['imgList']
    center = size = None
    if not key == ATTACK:
        player['surface'] = imgList[key][0]
        center = imgList[key][1]
        size = imgList[key][2]
    else:
        player['surface'] = imgList[key][index][0]
        center = imgList[key][index][1]
        size = imgList[key][index][2]
        
    if player['facing'] == LEFT:
        player['surface'] = pygame.transform.flip(player['surface'], True, False)
        center = (player['surface'].get_width() - center[0], center[1])
    player['boxCenter'] = center
    player['boxSize'] = size
    collisionUpdate(player)

def playerStatus(player):
    if player[HIT]:
        return HIT
#    if player[ATTACK]:
#        return ATTACK
    
    if player[JUMP]:
        return JUMP
    if player[BLOCK]:
        return BLOCK
    if player[CROUCH]:
        return CROUCH
    if player['dx']:
        return WALK
    return IDLE

def centerTextDraw(surface, text, position, depth=(1,1)):
    # Load Round Number Text
    roundText = FONTOBJ.render(text, True, WHITE)
    roundRect = roundText.get_rect()
    roundRect.center = position

    roundShadowText = FONTOBJ.render(text, True, BLACK)
    roundShadowRect = roundText.get_rect()
    roundShadowRect.center = (position[0] + depth[0], position[1] + depth[1])

    surface.blit(roundShadowText, roundShadowRect)
    surface.blit(roundText, roundRect)

def playerDraw(player, surface):
    if not player[HIT] or player['attTime'] % 2 == 0:
        surface.blit(player['surface'], player['rect'])

def timerDraw(timer):
    if timer > 9:
        timerSurf = FONTOBJ.render('%s' % timer, True, WHITE)
    else:
        timerSurf = FONTOBJ.render('0%s' % timer, True, WHITE)
    timerRect = timerSurf.get_rect()
    timerRect.topleft = (WINWIDTH / 2 - 16, 34)

    boxRect = pygame.Rect(timerRect.left - 6, timerRect.top - 4,\
                          48, 34)
    boxBack = BLACK
    if timer < 16:
        boxBack = RED
    pygame.draw.rect(DISPLAYSURF, boxBack, boxRect)
    pygame.draw.rect(DISPLAYSURF, WHITE, boxRect, 4)
    DISPLAYSURF.blit(timerSurf, timerRect)

def commentReset(strArray, length=3):
    if len(strArray) == 0:
        newComment(strArray, ' ', COMPOS)
        strArray[0][1].top = strArray[0][2]
        length -= 1
        
    for i in range(length):
        newComment(strArray, ' ', COMPOS)

def newComment(strArray, text, pos=(0,0), color=WHITE, limit=8):
    if text != ' ':
        text = 'Michael: ' + text
    adjust = 0
    if len(strArray) > 1:
        adjust = strArray[1][2] - strArray[1][1].top
    newText = FONTSM.render(text, True, color)
    newRect = newText.get_rect()
    newRect.topleft = (pos[0], pos[1] - 20 - adjust)
    
    strArray.insert(0, [newText, newRect, 0])
    if len(strArray) > limit:
        del strArray[limit]

    # Update texts
    for i in range(0, len(strArray)):
        strArray[i][2] = pos[1] + (32 * i) + 12

def commentUpdate(strArray, freq=1.5):
    if strArray == []:
        return
    if strArray[-1][1].top > 97:
        del strArray[-1]

    freq *= len(strArray)
    
    for text in strArray:
        if text[1].top + freq < text[2]:
            text[1].top += freq
        else:
            text[1].top = text[2]
            
def isFreeX(player, dx):
    tempRect = pygame.Rect.copy(player['hitbox'])
    tempRect.left += dx
    return (tempRect.left > 0) and\
           (tempRect.right < WINWIDTH) and\
           (not tempRect.colliderect(player['foe']['hitbox']))

def createAnimation(dest, length, irfanview=False, ext='png'):
    data = []
    if irfanview and length > 10:
        for i in range(1, 9):
            data.append(pygame.image.load('{}0{}.{}'.format(dest, i, ext)))
        for i in range(10, length):
            data.append(pygame.image.load('{}{}.{}'.format(dest, i, ext)))
        rect = data[0].get_rect()
        return data, rect
    else:
        for i in range(1, length):
            data.append(pygame.image.load('{}{}.{}'.format(dest, i, ext)))
        rect = data[0].get_rect()
        return data, rect

if __name__ == '__main__':
    main()
