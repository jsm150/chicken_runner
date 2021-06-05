import pygame
import os
import time
from random import randint
from collections import deque


class Character:
    def __init__(self):
        # 캐릭터 설정
        self.pos_x = None
        self.pos_y = None
        self.img_list = None
        self.size = None
        self.current_img = None

        # 점프 변수
        self.moving = None
        self.__initial_speed = None
        self.__speed_weight = None
        self.__speed = None

    def Init(self, character_pos_x, character_pos_y, character_img_list, size):
        self.pos_x = character_pos_x
        self.pos_y = character_pos_y
        self.img_list = character_img_list
        self.size = size
        self.current_img = self.img_list[0]

        self.moving = False
        self.__initial_speed = 20
        self.__speed_weight = 1
        self.__speed = self.__initial_speed
        
    def JumpAction(self):
        if (not self.moving):
            return
        self.current_img = self.img_list[1]
        self.__speed -= self.__speed_weight
        self.pos_y -= self.__speed

        if (round(self.__speed, 1) <= -self.__initial_speed + self.__speed_weight):
            self.current_img = self.img_list[0]
            self.moving = False
            self.__speed = self.__initial_speed


class Hurdle:
    pass


class GameManager:
    __instance = None

    # singleton 처리
    @classmethod
    def GetInstance(cls):
        if (cls.__instance is None):
            cls.__instance = GameManager()
        return cls.__instance

    def __init__(self):
        # 기본 설정
        pygame.init()
        pygame.display.set_caption("마당을 나온 수탉")

        # FPS
        self.__clock = pygame.time.Clock()

        # 게임 진행 변수
        self.__running = True

        # 점수 설정
        self.__score = 0
        self.__high_score = 0

        # 화면 설정
        self.__screen_width = 960
        self.__screen_height = 420
        self.__screen = pygame.display.set_mode((self.__screen_width, self.__screen_height))

        # 캐릭터 설정
        self.__character = Character()

        # 파일 위치 반환
        self.__current_path = os.path.dirname(__file__)
        self.__data_path = os.path.join(self.__current_path, "Data")
        self.__image_path = os.path.join(self.__data_path, "Img")
        self.__sound_path = os.path.join(self.__data_path, "Sound")
        self.__save_path = os.path.join(self.__data_path, "Save")

        # 폰트 설정
        self.__score_font = pygame.font.Font(os.path.join(self.__data_path, "Font", "game_font.ttf"), 35)

        # 사운드 불러오기
        pygame.mixer.music.load(os.path.join(self.__sound_path, "RustyCourier.mp3"))
        pygame.mixer.music.set_volume(0.1)
        self.__jump_sound = pygame.mixer.Sound(os.path.join(self.__sound_path, "sprites_jump.wav"))
        self.__checkPoint_sound = pygame.mixer.Sound(os.path.join(self.__sound_path, "sprites_checkPoint.wav"))
        self.__die_sound = pygame.mixer.Sound(os.path.join(self.__sound_path, "sprites_die.wav"))

        # 이미지 불러오기
        self.__background_img = pygame.image.load(os.path.join(self.__image_path, "background.png"))
        self.__stage_img = pygame.image.load(os.path.join(self.__image_path, "stage.png"))
        self.__tree_img_list = [pygame.image.load(os.path.join(self.__image_path, f"tree{i}.png")) for i in range(1, 5)]

        # 이미지 사이즈
        self.__stage_size = self.__stage_img.get_rect().size
        self.__stage_pos_x = 0
        self.__tree_size_list = [t.get_rect().size for t in self.__tree_img_list]

        # 장애물 설정
        self.__tree_pos_x_list = [self.__screen_width for i in range(len(self.__tree_img_list))]
        self.__tree_pos_y_list = [self.__screen_height - self.__stage_size[1] - t[1] for t in self.__tree_size_list]
        self.__speed_weight = 8
        self.__hurdle_num_que = deque()
        self.__target_point = self.__screen_width / 2

    def CharacterAdd(self, character):
        self.__character = character
        
    def __SetCharacter(self):
        character_img_list = [ 
            pygame.image.load(os.path.join(self.__image_path, "character1.png")),
            pygame.image.load(os.path.join(self.__image_path, "character2.png"))
        ]
        size = character_img_list[0].get_rect().size
        character_pos_x = 80
        character_pos_y = self.__screen_height - self.__stage_size[1] - size[1]
        self.__character.Init(character_pos_x, character_pos_y, character_img_list, size)

    def GameStart(self):
        while (True):
            self.__GameReset()
            self.__GamePlay()
            self.__GameEnd()

    def __GamePlay(self):
        pygame.mixer.music.play(-1, 0, 0)
        while (self.__running):
            self.__clock.tick(60)
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.__character.moving == False:
                        self.__jump_sound.play()
                        self.__character.moving = True

            self.__Action()
            self.__CollisionCheck()
            self.__DrawObject()

    def __GameEnd(self):
        pygame.mixer.music.stop()
        if (not os.path.exists(self.__save_path)):
            os.makedirs(self.__save_path)

        with open(os.path.join(self.__save_path, "high_score.txt"), "w", encoding="UTF-8") as w:
            w.write(str(int(self.__high_score)))

        font = pygame.font.Font(None, 70)
        msg = font.render("Game Over", True, (255, 255, 0))
        msg_rect = msg.get_rect(center = (int(self.__screen_width / 2), int(self.__screen_height / 2)))
        self.__screen.blit(msg, msg_rect)

        pygame.display.update()
        self.__GameWait()

    def __GameWait(self):
        while (True):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        break
            else:
                continue
            break

    def __GameReset(self):
        self.__SetCharacter()
        self.__hurdle_num_que.clear()
        self.__score = 0
        self.__running = True
        self.__speed_weight = 8
        self.__target_point = self.__screen_width / 2

        score_path = os.path.join(self.__save_path, "high_score.txt")
        if (self.__high_score == 0 and os.path.exists(score_path)):
            with open(score_path, "r", encoding="UTF-8") as r:
                self.__high_score = int(r.read())

        self.__DrawObject()

    def __DrawObject(self):
        self.__screen.blit(self.__background_img, (0, 0))
        self.__screen.blit(self.__stage_img, (self.__stage_pos_x, self.__screen_height - self.__stage_size[1]))

        for hurdle in self.__hurdle_num_que:
            self.__screen.blit(hurdle["img"], (hurdle["pos_x"], hurdle["pos_y"]))

        self.__screen.blit(self.__character.current_img, (self.__character.pos_x, self.__character.pos_y))
        self.__DrawScore()

        pygame.display.update()

    def __DrawScore(self):
        score_str = str(int(self.__score))
        high_score_str = str(int(self.__high_score))
        current_score_font = self.__score_font.render(("0" * (5 - len(score_str)) + score_str), True, (0, 0, 0))
        high_score_font = self.__score_font.render(("HI " + "0" * (5 - len(high_score_str)) + high_score_str), True, (128, 128, 128))

        self.__screen.blit(current_score_font, (self.__screen_width - 110, 38))
        self.__screen.blit(high_score_font, (self.__screen_width - 240, 38))

    def __Action(self):
        self.__SetScore()
        self.__character.JumpAction()
        self.__AddHurdle()
        self.__MoveHurdle()
        self.__MoveStage()

    def __SetScore(self):
        self.__score += 0.2
        self.__high_score = max([self.__high_score, self.__score])

        if (self.__score % 50 >= 49.8):
            self.__speed_weight += 0.3

        if (self.__score % 100 >= 99.8):
            self.__checkPoint_sound.play()
 
    def __MoveStage(self):
        self.__stage_pos_x -= self.__speed_weight
        if (self.__stage_pos_x <= -117):
            self.__stage_pos_x = -(-117 - self.__stage_pos_x)
            
    def __MoveHurdle(self):
        for hurdle in list(self.__hurdle_num_que):
            hurdle["pos_x"] -= self.__speed_weight
        if (len(self.__hurdle_num_que) != 0 and self.__hurdle_num_que[0]["pos_x"] <= -self.__hurdle_num_que[0]["size"][0]):
            self.__hurdle_num_que.popleft()

    def __AddHurdle(self):
        if (self.__score <= 30):
            return
        if (len(self.__hurdle_num_que) != 0 and self.__hurdle_num_que[-1]["pos_x"] > self.__target_point):
            return
        i = randint(0, len(self.__tree_img_list) - 1)
        self.__hurdle_num_que.append({
            "img" : self.__tree_img_list[i],
            "size" : self.__tree_size_list[i], 
            "pos_x" : self.__tree_pos_x_list[i],
            "pos_y" : self.__tree_pos_y_list[i]
        })
        self.__target_point = randint(
            -self.__hurdle_num_que[0]["size"][0], 
            max([-self.__hurdle_num_que[0]["size"][0] + 1, int(self.__screen_width / 2 + 180 - (self.__speed_weight - 8) * 40)])
        )

    def __CollisionCheck(self):
        for hurdle in self.__hurdle_num_que:
            character_rect = self.__character.current_img.get_rect()
            character_rect.top = self.__character.pos_y
            character_rect.left = self.__character.pos_x

            hurdle_rect = hurdle["img"].get_rect()
            hurdle_rect.top = hurdle["pos_y"]
            hurdle_rect.left = hurdle["pos_x"]

            if (character_rect.colliderect(hurdle_rect)):
                self.__die_sound.play()
                self.__running = False
                break


#---------------------------

game = GameManager.GetInstance()
game.GameStart()
pygame.quit()