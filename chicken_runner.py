import pygame
import os
import json
from datetime import datetime
from random import randint
from collections import deque


class ProgramCloseError(Exception):
    pass


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
        self.__img_list = [pygame.image.load(os.path.join(image_path, f"hurdle{i + 1}.png")) for i in range(4)]
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


class RankingWindow:
    def __init__(self, score, score_list, screen, screen_width, screen_height, image_path, font_path):
        self.__screen = screen

        # 점수
        self.__score = score
        self.__score_list = score_list

        # 이미지 불러오기
        self.__score_window_img = pygame.image.load(os.path.join(image_path, "score_window.png"))
        self.__input_window_img = pygame.image.load(os.path.join(image_path, "input_window.png"))

        # 창 위치 설정
        self.__score_window_pos_x = 205
        self.__score_window_pos_y = 80
        self.__input_window_pos_x = self.__score_window_pos_x + 15
        self.__input_window_pos_y = self.__score_window_pos_y + self.__score_window_img.get_rect().size[1] - self.__input_window_img.get_rect().size[1] - 15

        self.__title_offset_y = self.__score_window_pos_y + 80

        # 제목
        self.__title_letter = pygame.font.Font(font_path, 50).render("ENTER YOUR NAME!", True, (255, 255, 0))
        self.__title_letter_rect = self.__title_letter.get_rect(center = (int(screen_width / 2), int(screen_height / 2) - 100))

        # 글자 폰트
        self.__font = pygame.font.Font(font_path, 30)

        # Ranking
        self.__rank_letter = self.__font.render("Ranking", True, (219, 68, 85))
        self.__rank_pos_x = self.__score_window_pos_x + 60
        self.__rank_letter_rect = (self.__rank_pos_x, self.__title_offset_y)

        # Score
        self.__score_letter = self.__font.render("Score", True, (219, 68, 85))
        self.__score_pos_x = self.__score_window_pos_x + 240
        self.__score_letter_rect = (self.__score_pos_x, self.__title_offset_y)

        # Name
        self.__name_letter = self.__font.render("Name", True, (219, 68, 85))
        self.__name_pos_x =self.__score_window_pos_x + 420
        self.__name_letter_rect = (self.__name_pos_x, self.__title_offset_y)

        # 입력받는 글자 폰트
        self.__name_font = pygame.font.Font(font_path, 45)

        # 입력받는 글자 설정 
        self.__user_name = ""
        self.__user_name_letter = self.__name_font.render(self.__user_name, True, (0, 0, 0))
        self.__user_name_rect = self.__user_name_letter.get_rect(topleft = (self.__input_window_pos_x + 5, self.__input_window_pos_y + 10))

        # 커서
        self.__cursor = pygame.Rect(self.__user_name_rect.topright, (3, self.__user_name_rect.height - 13))

    def Open(self):
        start_time = datetime.now()
        while (True):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    raise ProgramCloseError
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_RETURN):
                        break
                    if (event.key == pygame.K_SPACE):
                        continue
                    if (event.key == pygame.K_BACKSPACE):
                        if len(self.__user_name) > 0:
                            self.__user_name = self.__user_name[:-1]
                    elif (len(self.__user_name) < 7):
                        self.__user_name += event.unicode

                    self.__user_name_letter = self.__name_font.render(self.__user_name, True, (255, 255, 255))
                    self.__user_name_rect = self.__user_name_letter.get_rect(topleft = (self.__input_window_pos_x + 5, self.__input_window_pos_y + 10))
                    self.__cursor.topleft = self.__user_name_rect.topright
            else:
                self.__DrawImage(start_time, True)
                continue
            break
        
        if (self.__user_name != ""):
            self.__score_list[self.__user_name] = int(self.__score)

        self.__DrawImage(start_time, False)

    def __DrawImage(self, start_time, can_input_name):
        self.__screen.blit(self.__score_window_img, (self.__score_window_pos_x, self.__score_window_pos_y))
        
        self.__screen.blit(self.__title_letter, self.__title_letter_rect)
        self.__screen.blit(self.__rank_letter, self.__rank_letter_rect)
        self.__screen.blit(self.__score_letter, self.__score_letter_rect)
        self.__screen.blit(self.__name_letter, self.__name_letter_rect)

        offset_y = 40
        high_score_list = sorted(self.__score_list.items(), key = lambda x : x[1], reverse = True)[:3]
        st_nd_rd = {1 : "ST", 2 : "ND", 3 : "RD"}
        for i in range(len(high_score_list)):
            rank = self.__font.render(f"{i + 1}{st_nd_rd[i + 1] if (i + 1 <= 3) else 'TH'}", True, (0, 0, 0))
            self.__screen.blit(rank, (self.__rank_pos_x + 20, self.__title_offset_y + offset_y * (i + 1)))

            score = self.__font.render(str(high_score_list[i][1]), True, (0, 0, 0))
            self.__screen.blit(score, (self.__score_pos_x, self.__title_offset_y + offset_y * (i + 1)))

            name = self.__font.render(high_score_list[i][0], True, (0, 0, 0))
            self.__screen.blit(name, (self.__name_pos_x - 10, self.__title_offset_y + offset_y * (i + 1)))

        if (can_input_name):
            self.__screen.blit(self.__input_window_img, (self.__input_window_pos_x, self.__input_window_pos_y))
            self.__screen.blit(self.__user_name_letter, (self.__input_window_pos_x + 5, self.__input_window_pos_y))

            if ((datetime.now() - start_time).total_seconds() % 1 < 0.5):
                pygame.draw.rect(self.__screen, (255, 255, 255), self.__cursor)

        pygame.display.update()


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
        self.__twinkle_time = None
        self.__score_list = {}
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
        self.__font_path = os.path.join(self.__data_path, "Font", "game_font.ttf")

        # 폰트 설정
        self.__score_font = pygame.font.Font(self.__font_path, 35)

        # 사운드 불러오기
        pygame.mixer.music.load(os.path.join(self.__sound_path, "RustyCourier.mp3"))
        pygame.mixer.music.set_volume(0.1)
        self.__jump_sound = pygame.mixer.Sound(os.path.join(self.__sound_path, "sprites_jump.wav"))
        self.__checkPoint_sound = pygame.mixer.Sound(os.path.join(self.__sound_path, "sprites_checkPoint.wav"))
        self.__checkPoint_sound.set_volume(0.3)
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

    def __SetObject(self):
        character_pos_x = 80
        character_pos_y = self.__screen_height - self.__stage_size[1] - self.__character.size[1]
        self.__character.Reset(character_pos_x, character_pos_y)
        self.__hurdle.Reset(self.__screen_width)

    def GameStart(self):
        try:
            while (True):
                self.__GameReset()
                self.__GamePlay()
                self.__GameEnd()
        except ProgramCloseError:
            pass

    def __GamePlay(self):
        pygame.mixer.music.play(-1, 0, 0)
        while (self.__running):
            self.__clock.tick(60)
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    raise ProgramCloseError

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.__character.moving == False:
                        self.__jump_sound.play()
                        self.__character.moving = True

            self.__Action()
            self.__CollisionCheck()
            self.__DrawObject()

    def __GameEnd(self):
        pygame.mixer.music.stop()

        RankingWindow(self.__score, self.__score_list, self.__screen, self.__screen_width, self.__screen_height, self.__image_path, self.__font_path).Open()

        if (not os.path.exists(self.__save_path)):
            os.makedirs(self.__save_path)

        if (len(self.__score_list) > 0):
            with open(os.path.join(self.__save_path, "score_list.json"), "w", encoding="UTF-8") as w:
                json.dump(self.__score_list, w)

        restart_img_rect = self.__restart_img.get_rect(center = (int(self.__screen_width / 2), int(self.__screen_height / 2) + 130))
        self.__screen.blit(self.__restart_img, restart_img_rect)

        pygame.display.update()
        self.__GameWait()

    def __GameWait(self):
        while (True):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    raise ProgramCloseError
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                        break
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        break
            else:
                continue
            break
        self.__jump_sound.play()

    def __GameReset(self):
        self.__SetObject()
        self.__twinkle_time = None
        self.__score = 0
        self.__running = True

        score_path = os.path.join(self.__save_path, "score_list.json")
        if (self.__high_score == 0 and os.path.exists(score_path)):
            with open(score_path, "r", encoding="UTF-8") as r:
                self.__score_list = json.load(r)
            self.__high_score = max(self.__score_list.values())

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
        if (self.__twinkle_time == None or ((datetime.now() - self.__twinkle_time).total_seconds()) % 0.5 > 0.25):
            if (self.__twinkle_time == None):
                score_str = str(int(self.__score))

            elif (((datetime.now() - self.__twinkle_time).total_seconds()) % 0.5 > 0.25):
                score_str = str(int(self.__score / 100) * 100)

                if ((datetime.now() - self.__twinkle_time).total_seconds() > 1.98):
                    self.__twinkle_time = None

            current_score_font = self.__score_font.render(("0" * (5 - len(score_str)) + score_str), True, (0, 0, 0))
            self.__screen.blit(current_score_font, (self.__screen_width - 110, 38))

        high_score_str = str(int(self.__high_score))
        high_score_font = self.__score_font.render(("HI " + "0" * (5 - len(high_score_str)) + high_score_str), True, (128, 128, 128))
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

        if (self.__score > 1 and self.__score % 100 < 0.2):
            self.__twinkle_time = datetime.now()
            self.__checkPoint_sound.play()
 
    def __MoveStage(self):
        self.__stage_pos_x -= self.__hurdle.speed
        if (self.__stage_pos_x <= -117): # 117 은 반복되는 지형의 길이이다.
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
                self.__twinkle_time = None
                self.__running = False
                break


#---------------------------

game = GameManager.GetInstance()
game.GameStart()
pygame.quit()