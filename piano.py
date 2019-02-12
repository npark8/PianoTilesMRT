import pygame,os,random
from pygame.locals import *


#TODO - health bar should decrease in slow, continuous fashion (~2sec), make the tick smaller 
#TODO - add end screen?? (replay, scoreboard, ...)

#DONE
#TODO - lower bound for tapping zone [x]
#TODO - start screen and instructions [x]
#TODO - black tile refreshing looks weird [x] -> do not remove tiles from the list
#TODO - tile should be drawn over the horizontal line -> looks okay now
#TODO - add musics


#dimensions
wix=350
wiy=600

#create events
DRAWRECTEVENT = pygame.USEREVENT + 1 
CLEAR_TAPPING_ZONE_HIGHLIGHT_EVENT = pygame.USEREVENT + 2 
COUNTDOWN = pygame.USEREVENT + 3

def msg (screen,text,color=(55,55,55),size=36,pos=(-1,-1)):
    if pos[0] ==-1:pos=(screen.get_rect().centerx,pos[1])
    if pos[1] ==-1:pos=(pos[0],screen.get_rect().centery)
    font = pygame.font.Font(None, size)
    text = font.render(text, 1, color)
    textpos = text.get_rect()
    textpos.centerx = pos[0]
    textpos.centery= pos[1]
    screen.blit(text, textpos)
def load_sound(name):
    if not pygame.mixer or not pygame.mixer.get_init():
        pass
    return pygame.mixer.Sound(name)


class button():
    x=0
    y=-wiy//5
    h=wix//4-1
    l=wiy//5
    enclick=True
    def pos(self,n):
        self.x=n*wix//4
    def update(self,screen):              
        if self.enclick:
            pygame.draw.rect(screen,(0,0,0),[self.x,self.y,self.h,self.l])
        else:
            pygame.draw.rect(screen,(180,180,180),[self.x,self.y,self.h,self.l])            


class health_meter():
    x=wix+50
    y=0
    h=50
    l=wiy
    tick = wiy//100
    def update(self,screen,reduce):              
        if reduce:
            self.y += self.tick
            pygame.draw.rect(screen,(245,162,156),[self.x,self.y,self.h,self.l]) 
        else:
            pygame.draw.rect(screen,(245,162,156),[self.x,self.y,self.h,self.l])
        
        #terminate game if health bar reached the bottom
        if(self.y >=self.l):
            return 1
        else:
            return 0

################################################################################
## game stuff below
################################################################################
#load sounds
pygame.init()
pygame.mixer.get_init()
mutrue=load_sound(os.path.join("game_music", "hit.ogg"))
mufall=load_sound(os.path.join("game_music", "miss.ogg"))
muover=load_sound(os.path.join("game_music", "gameover.ogg"))
pygame.mixer.music.load(os.path.join("game_music", "background.ogg"))

#set other gaming context
clock=pygame.time.Clock()
screen=pygame.display.set_mode((wix+150,wiy))
tapping_zone = pygame.Surface((wix-1,120),pygame.SRCALPHA, 32)
mape=[0,0,0,0,1,1,1,2,2,2,3,3,3,1,2,3,1,0,2,3,1,0,1,2,3,0,1,2,3]
lost=0 
time=0
delt=60 #frame @ 60hz
sb=[]
speey=4
score=0
sb_index=0

#create health meter
health = health_meter() 

#drawing variables
line1_s = (wix//4-1,0)
line1_e = (wix//4-1,wiy)
line2_s = (wix//2-2,0)
line2_e = (wix//2-2,wiy)
line3_s = (3*wix//4-2,0)
line3_e = (3*wix//4-2,wiy)
line4_s = (wix-2,0)
line4_e = (wix-2,wiy)
line5_s = (0,wiy-120)
line5_e = (wix-1,wiy-120)
line_width = 1

#colors
line_color = (255,255,255)#(180,180,180) #light gray
bg_color = (224,224,255) #light blue
tapping_zone_color = (110,128,225) #(212,245,156) #light green
mis_tapping_color = (245,162,156) #light red
font_color = (110,128,225) #light purple
curr_tapping_zone_color = tapping_zone_color #set to default

#create enum-like gameplay conditions 
GAMESTART = False
REFRESH = False
MISS = True
cnth = 0

#generate start screen 
screen.fill(bg_color)
msg(screen,"MRT Sim.",color=font_color,size=100,pos=(-1,wiy//5))
msg(screen,"Piano Tiles",color=font_color,size=100,pos=(-1,wiy//5*2-30))
msg(screen,"Press [ENTER] to start",color=font_color,pos=(-1,wiy//2+40))
msg(screen,"Press [ESCAPE] to quit",color=font_color,pos=(-1,wiy//2+75))
pygame.display.update()

count_down = 3 # will count 3 second before game starts with instructions
target = 0 #tracks the closest tile to the tapping zone

while not GAMESTART:
    for event in pygame.event.get():
        if event.type == QUIT or \
           (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
        elif (event.type == KEYDOWN and (event.key == K_RETURN)):
            GAMESTART = True
            pygame.time.set_timer(COUNTDOWN, 1000) #draw count down 
            

while GAMESTART and lost == 0:
    #for i in range (10):
    for i in mape:
        if lost!=0 : break
        for j in range(wiy//(5*speey)):
            time+=1/delt
            clock.tick(delt)
            screen.fill(bg_color)
            #show instructions
            if(count_down > 0):
                msg(screen,"Press [SPACE BAR] to tap a tile",color=font_color,pos=(-1,wiy//2-80))
                msg(screen,"within the PURPLE area",color=font_color,pos=(-1,wiy//2-50))
                msg(screen,str(count_down),color=font_color,size=100,pos=(-1,-1)) 
            elif (count_down == 0):
                msg(screen,"Start!",color=font_color,size=100,pos=(-1,-1)) 
            else:
                msg(screen,"SCORE "+str(score),color=font_color,size=50,pos=(-1,30))
                tapping_zone.fill(curr_tapping_zone_color)
                screen.blit(tapping_zone, [0,wiy-120])
            if lost!=0 : break
            for k in range(len(sb)) :
                #only update incoming or tiles within the screen 
                if(k >= target - 3):
                    try:
                        #draw grid 
                        pygame.draw.line(screen, line_color,\
                                         line1_s, line1_e, line_width)
                        pygame.draw.line(screen, line_color,\
                                         line2_s, line2_e, line_width)
                        pygame.draw.line(screen, line_color, \
                                         line3_s, line3_e, line_width)
                        pygame.draw.line(screen, line_color,\
                                         line4_s, line4_e, line_width)
                        pygame.draw.line(screen, line_color,\
                                         line5_s, line5_e, line_width)                    
                        sb[k].y+=speey #move 4 down every frame
                        sb[k].update(screen)                           
                        health.update(screen,REFRESH) #refresh screen
                        REFRESH = False
                        if sb[k].y == wiy: 
                            if sb[k].enclick: #missed an enabled tile 
                                curr_tapping_zone_color = mis_tapping_color
                                lost = health.update(screen,MISS)
                                mufall.play() #play miss sound
                                pygame.time.set_timer(CLEAR_TAPPING_ZONE_HIGHLIGHT_EVENT, 250) 
                                sb[k].enclick = False
                                target += 1 #move to next target
                    except : pass
            #event handler
            for event in pygame.event.get():
                if event.type == QUIT or \
                   (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                elif (event.type == KEYDOWN and event.key == K_SPACE):
                    #handle corner cases
                    if(len(sb) <= 0): continue
                    if(target >= len(sb)): continue
                    #tile is in the tapping zone (60% of the portion or greater) 
                    # & not previously mis-tapped                     
                    in_bound = (sb[target].y + sb[target].l >= wiy - wiy//5 + wiy//5*0.6 and\
                        sb[target].y + sb[target].l <= wiy + wiy//5*0.4)
                    if (in_bound and sb[target].enclick): 
                        mutrue.play() #play hit sound
                        score+=1
                        sb[target].enclick = False # disable the tile
                        target += 1 #hit, move to next target
                    else: #for now, every miss tapping will reduce health meter
                        if(sb[target].enclick):
                            mufall.play() #play miss sound
                            curr_tapping_zone_color = mis_tapping_color
                            lost = health.update(screen, MISS)
                            pygame.time.set_timer(CLEAR_TAPPING_ZONE_HIGHLIGHT_EVENT, 250)
                            sb[target].enclick = False #disable the tile
                        target+=1 #miss, move to next target
                elif event.type == DRAWRECTEVENT:
                    sb.append(button()) #generate new tile
                    sb[-1].pos(random.randrange(4)) #set rectangle position
                elif event.type == CLEAR_TAPPING_ZONE_HIGHLIGHT_EVENT:
                    curr_tapping_zone_color = tapping_zone_color #set back to default color 
                    #disable event; should not repeat unless user misses another tile
                    pygame.time.set_timer(CLEAR_TAPPING_ZONE_HIGHLIGHT_EVENT, 0)
                elif event.type == COUNTDOWN:
                    count_down-=1
                    if(count_down == 0):
                        pygame.time.set_timer(DRAWRECTEVENT, 1000) #spawn tiles 
                    if(count_down < 0):
                        pygame.time.set_timer(COUNTDOWN, 0) #disable event 
                        pygame.mixer.music.play(-1) #play background music
                        
            pygame.display.update()
    #speey+=1
print("gameover")
muover.play() # play gameover sound
pygame.mixer.music.stop()
screen.fill(bg_color)
msg(screen,"YOU LOSE ",color=(110,128,225),size=100,pos=(-1,-1))
msg(screen,"Original Source provider: elleuch med amin",color=(110,108,225),\
    size=25,pos=(-1,wiy//2+40))

#clear timezone background
tapping_zone.fill(bg_color)
screen.blit(tapping_zone, [0,wiy-120])
pygame.display.update()
pygame.time.wait(10000)
pygame.quit()
quit()