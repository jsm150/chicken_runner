import pygame
import os
import time
from random import randint
from collections import deque


class Character:
    def __init__(self, image_path):
        # 캐릭터 설정
        self.img_list = [pygame.image.load(os.path.join(image_path, f"character{i + 1}.png")) for i in range(2)]
        self.size = self.img_list[0].get_rect().size
        self.current_img = None
        self.pos_x = None
        self.pos_y = None

        # 점프 변수
        self.__initial_speed = 20
        self.__speed_weight = 1
        self.__speed = None
        self.moving = None

    def Reset(self, character_pos_x, character_pos_y):
        self.current_img = self.img_list[0]
        self.pos_x = character_pos_x
        self.pos_y = character_pos_y

        self.__speed = self.__initial_speed
        self.moving = False
        
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
    # 장애물 설정
    def __init__(self, image_path, screen_width, screen_height, stage_height):
        self.hurdle_queue = deque()
        self.__img_list = [pygame.image.load(os.path.join(image_path, f"tree{i + 1}.png")) for i in range(4)]
        self.__size_list = [t.get_rect().size for t in self.__img_list]
        self.__pos_x_list = [screen_width for i in range(len(self.__img_list))]
        self.__pos_y_list = [screen_height - stage_height - t[1] for t in self.__size_list]

        self.__initial_speed = 8
        self.__speed_weight = 0.3
        self.__target_point = None
        self.speed = None

    def Reset(self, screen_width):
        self.__target_point = screen_width / 2
        self.speed = self.__initial_speed
        self.hurdle_queue.clear()

    def SpeedUp(self):
        self.speed += self.__speed_weight

    def MoveHurdle(self):
        for hurdle in list(self.hurdle_queue):
            hurdle["pos_x"] -= self.speed
        if (len(self.hurdle_queue) != 0 and self.hurdle_queue[0]["pos_x"] <= -self.hurdle_queue[0]["size"][0]):
            self.hurdle_queue.popleft()

    def AddHurdle(self, score, screen_width):
        if (score <= 30):
            return
        if (len(self.hurdle_queue) != 0 and self.hurdle_queue[-1]["pos_x"] > self.__target_point):
            return

        i = randint(0, len(self.__img_list) - 1)

        self.hurdle_queue.append({
            "img" : self.__img_list[i],
            "size" : self.__size_list[i], 
            "pos_x" : self.__pos_x_list[i],
            "pos_y" : self.__pos_y_list[i]
        })

        self.__target_point = randint(
            -self.hurdle_queue[0]["size"][0], 
            max([-self.hurdle_queue[0]["size"][0] + 1, int(screen_width / 2 + 180 - (self.speed - 8) * 40)])
        )


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
        self.__restart_img = pygame.image.load(os.path.join(self.__image_path, "replay_button.png"))

        # 이미지 사이즈
        self.__stage_size = self.__stage_img.get_rect().size
        self.__stage_pos_x = 0

        # 오브젝트 설정
        self.__character = Character(self.__image_path)
        self.__hurdle = Hurdle(self.__image_path, self.__screen_width, self.__screen_height, self.__stage_size[1])

    def CharacterAdd(self, character):
        self.__character = character
        
    def __SetObject(self):
        character_pos_x = 80
        character_pos_y = self.__screen_height - self.__stage_size[1] - self.__character.size[1]
        self.__character.Reset(character_pos_x, character_pos_y)
        self.__hurdle.Reset(self.__screen_width)

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
        msg = font.render("G a m e   O v e r", True, (255, 255, 0))
        msg_rect = msg.get_rect(center = (int(self.__screen_width / 2), int(self.__screen_height / 2) - 70))
        self.__screen.blit(msg, msg_rect)

        restart_img_rect = self.__restart_img.get_rect(center = (int(self.__screen_width / 2), int(self.__screen_height / 2) + 20))
        self.__screen.blit(self.__restart_img, restart_img_rect)

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
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        break
            else:
                continue
            break

    def __GameReset(self):
        self.__SetObject()
        self.__score = 0
        self.__running = True

        score_path = os.path.join(self.__save_path, "high_score.txt")
        if (self.__high_score == 0 and os.path.exists(score_path)):
            with open(score_path, "r", encoding="UTF-8") as r:
                self.__high_score = int(r.read())

        self.__DrawObject()

    def __DrawObject(self):
        self.__screen.blit(self.__background_img, (0, 0))
        self.__screen.blit(self.__stage_img, (self.__stage_pos_x, self.__screen_height - self.__stage_size[1]))

        for hurdle in self.__hurdle.hurdle_queue:
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
        self.__hurdle.AddHurdle(self.__score, self.__screen_width)
        self.__hurdle.MoveHurdle()
        self.__MoveStage()

    def __SetScore(self):
        self.__score += 0.2
        self.__high_score = max([self.__high_score, self.__score])

        if (self.__score % 50 >= 49.8):
            self.__hurdle.SpeedUp()

        if (self.__score % 100 >= 99.8):
            self.__checkPoint_sound.play()
 
    def __MoveStage(self):
        self.__stage_pos_x -= self.__hurdle.speed
        if (self.__stage_pos_x <= -117): # 117 은 반복되는 지형의 넓이이다.
            self.__stage_pos_x = -(-117 - self.__stage_pos_x)

    def __CollisionCheck(self):
        for hurdle in self.__hurdle.hurdle_queue:
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