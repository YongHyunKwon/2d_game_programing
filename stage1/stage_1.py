import random
import time
import datetime
import os

from pico2d import *

#***************************************
# 스테이지 1
#***************************************
# 기본 인자 초기화
#***************************************
running     = None
character   = None
obstacle    = None
clear_time  = None

#***************************************
# Background
# 게임의 배경을 담당하는 클래스
#***************************************
class Background:
    def __init__(self):
        self.image = load_image('stage_1.png')

    def draw(self):
        self.image.draw(250, 200)

#***************************************
# Obstacle
# 게임내 장애물을 담당하는 클래스
#***************************************
class Obstacle:
    image = None

    def __init__(self):
        self.make()

        if Obstacle.image == None:
            Obstacle.image = load_image('stage_1_stone.png')

    #***************************************
    # make
    # 장애물 재생성 함수
    # x: 20~480, y: 400, 속도: 5~10
    #***************************************
    def make(self):
        self.x, self.y  = random.randint(20, 480), 400
        self.speed      = random.randint(5, 10)

    def update(self):
        #***************************************
        # y 값은 속도 값에 비례하게 하강
        # 땅 밑으로 장애물이 사라지면 make 호출
        #***************************************
        self.y -= self.speed

        if(self.y < -20):
            self.make()

    def getcollisionbox(self):
        return self.x - 40, self.y + 10, self.x - 10, self.y + 40

    def draw(self):
        self.image.draw(self.x, self.y)

    #########################################
    # 충돌 박스 테스트 코드
    ########################################
    def drawcollision(self):
        draw_rectangle(*self.getcollisionbox())

#***************************************
# Character
# 캐릭터를 담당하는 클래스
#***************************************
class Character:

    # ***************************************
    # 캐릭터의 방향 및 시트 값
    # ***************************************
    LEFT_RUN, RIGHT_RUN, LEFT_STAND, RIGHT_STAND = 5, 4, 1, 0

    def __init__(self):
        self.x, self.y  = 250, 40
        self.speed      = 10
        self.frame      = random.randint(0, 7)
        self.state      = self.RIGHT_STAND
        self.image      = load_image('stage_1_cha.png')
        self.effect     = load_image('effect.png')
        # ***************************************
        # 최초 생명력은 3
        # ***************************************
        self.life_cnt   = 3
        self.life_image = load_image('heart.png')

    def handle_event(self, event):
        # ***************************************
        # ->,<- 키 입력시 캐릭터 이동
        # ***************************************
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.state = self.LEFT_RUN
            elif event.key == SDLK_RIGHT:
                self.state = self.RIGHT_RUN

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                self.state = self.LEFT_STAND
            elif event.key == SDLK_RIGHT:
                self.state = self.RIGHT_STAND

    def update(self):
        self.frame = (self.frame + 1) % 8
        # ***************************************
        # 화면을 벗어나지 않게 x 값을 조정
        # 스테이지1 에서는 x 값을 10 씩 이동
        # ***************************************
        if self.state == self.RIGHT_RUN:
            self.x = min(500, self.x + self.speed)
        elif self.state == self.LEFT_RUN:
            self.x = max(0, self.x - self.speed)

        if(self.life_cnt <= 0):
            return False

    # ***************************************
    # damage
    # 장애물과 충돌시 생명력 1 감소
    # ***************************************
    def damage(self):
        self.life_cnt = self.life_cnt - 1
        self.effect.draw(self.x, self.y)


    def getcollisionbox(self):
        return self.x - 15, self.y -30, self.x + 10, self.y + 25

    def draw(self):
        self.image.clip_draw(self.frame * 70, self.state * 70, 70, 70, self.x, self.y)
        # ***************************************
        # life_cnt 에 맞게 생명력 이미지를 draw
        # ***************************************
        for i in range(0, self.life_cnt):
            image_range = 30 * (i + 1)
            self.life_image.draw(image_range,375)

    #########################################
    # 충돌 박스 테스트 코드
    #########################################
    def drawcollision(self):
        draw_rectangle(*self.getcollisionbox())

def handle_events():
    global running
    global character

    events = get_events()
    # ***************************************
    # 종료키를 누르지 않는다면 캐릭터 이벤트 갱신
    # ***************************************
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            character.handle_event(event)

#***************************************
# lifetime
# 클리어 타임을 출력해주고 0 초에 도달하면
# 스테이지 완료를 해주는 함수
#***************************************
def lifetime():
    global running
    global clear_time
    # ***************************************
    # 클리어 시간과 현재 시간과의 차이를 구함
    # ***************************************
    life_time   = clear_time - time.time()
    str_time    = datetime.datetime.fromtimestamp(life_time).strftime('%S')

    font        = load_font('HMKMRHD.TTF', 20)
    font.draw(240, 380, str_time)

    # ***************************************
    # 스테이지 1 의 클리어시간을 버티면 게임 종료
    # ***************************************
    if(int(str_time) <= 0 ):
        clear_font = load_font('HMKMRHD.TTF', 50)
        clear_font.draw(70, 200, 'Stage Clear')
        update_canvas()
        delay(3)
        running = False

#***************************************
# stagefail
# 생명력이 0 이 돼 스테이지를 실패한 상태
#***************************************
def stagefail():
    global running

    clear_font = load_font('HMKMRHD.TTF', 50)
    clear_font.draw(90, 200, 'Stage Fail')
    update_canvas()
    delay(3)
    running = False

def collide(chr, obs):
    left_chr, bottom_chr, right_chr, top_chr = chr.getcollisionbox()
    left_obs, bottom_obs, right_obs, top_obs = obs.getcollisionbox()

    if left_chr < right_obs and right_chr > left_obs and top_chr > bottom_obs:
        return False

    return True

def main():
    open_canvas(500, 400)

    global running
    global character
    global obstacle
    global clear_time

    back_ground = Background()
    character   = Character()
    #***************************************
    # 스테이지 1 에서 장애물은 10개
    # 클리어 시간은 10초
    #***************************************
    obstacle    = [Obstacle() for i in range(10)]
    #########################################
    # 현재는 테스트용으로 시간을 20 초만 줌
    #########################################
    clear_time  = time.time() + 20
    running     = True

    while running:
        handle_events()

        clear_canvas()

        back_ground.draw()
        character.draw()
        character.drawcollision()

        for stone in obstacle:
            stone.draw()
            stone.drawcollision()
            stone.update()

        lifetime()

        if(character.update() == False):
            stagefail()

        # ***************************************
        # 장애물이 케릭터와 충돌하면 make 함수를
        # 호출해 다시 재생성 후 케릭터 생명력 1 감소
        # ***************************************
        for stone in obstacle:
            if collide(character, stone) == False:
                stone.make()
                character.damage()

        update_canvas()

        delay(0.05)

    close_canvas()

if __name__ == '__main__':
    main()



