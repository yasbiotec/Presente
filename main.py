# CÓDIGO FINAL CORRIGIDO E ORGANIZADO (PRONTO PARA WEB)
import pygame
import sys
import random
import textwrap
import json
import os
import asyncio

# =============================================================================
# --- CONSTANTES E CONFIGURAÇÕES DO JOGO ---
# =============================================================================
# Janela
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 500
GAME_TITLE = "Maya - A raposinha"
FPS = 60
SAVE_FILE = "savegame.json"

# Cores
COLORS = {
    "white": (255, 255, 255), "black": (0, 0, 0), "text": (80, 80, 80),
    "green": (40, 180, 99), "green_hover": (50, 200, 110),
    "red": (231, 76, 60),
    "blue": (52, 152, 219), "blue_hover": (72, 172, 239),
    "purple": (142, 68, 173), "purple_hover": (162, 88, 193),
    "xp_color": (250, 215, 70), "background": (253, 226, 232),
    "bubble_bg": (255, 255, 255), "bubble_border": (180, 180, 180),
    "final_message_bg": (220, 20, 60), "correct_answer": (46, 204, 113), "incorrect_answer": (192, 57, 43)
}

# Configurações do Pet e do Jogo
PET_ANIMATION_SPEED = 200
STAT_DECAY_INTERVAL = 7000
PHRASE_INTERVAL = 5000
XP_PER_LEVEL = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
PHRASES = [
    "Foi amor ao primeiro grito?",
    "Estou com um pouquinho de fome...", "Vamos no café do harry potter denovo...",
    "Quero um café das Letras!!", "Zzz... que soninho bom...", "Por que você não deixa a Yas te morder ?",
    "Qual a sua cor favorita?", "Corte o bolo de casamento com uma espada!",
    "Ela ama seus presentes, de a ela um labubu!", "Me dê presentes! muitos!!!"
]
QUIZ_DATA = [
    {"pergunta": "Onde foi o primeiro encontro de vocês?",
     "opcoes": ["Café das Letras", "Festa de Haloween", "Parque", "Café do Harry Potter"], "correta": 3},
    {"pergunta": "Qual o nome do primeiro filho que vocês tiveram ?",
     "opcoes": ["Galactos", "Squirtle", "Maya", "Hermes"], "correta": 2},
    {"pergunta": "Qual a comida favorita da Yas para pedir no delivery?",
     "opcoes": ["Pizza", "Hambúrguer", "Sushi", "Comida Mexicana", "Xis"], "correta": 1},
    {"pergunta": "Qual foi o primeiro apelido que ela deu para você",
     "opcoes": ["Squirtle", "Vida", "Mari", "Cacau Show"], "correta": 0},
    {"pergunta": "Qual foi o primeiro presente que você deu a ela ? ",
     "opcoes": ["Bottom Harry Potter", "Café das Letras", "Chocolate", "Bumbum"], "correta": 0}
]

# =============================================================================
# --- FUNÇÕES AUXILIARES ---
# =============================================================================
def draw_heart_shape(screen, color, pos, size):
    s = size
    pygame.draw.circle(screen, color, (pos[0] - s // 2, pos[1]), s // 2)
    pygame.draw.circle(screen, color, (pos[0] + s // 2, pos[1]), s // 2)
    pygame.draw.polygon(screen, color, [(pos[0] - s, pos[1]), (pos[0] + s, pos[1]), (pos[0], pos[1] + s)])

# =============================================================================
# --- GERENCIADOR DE RECURSOS (ASSET MANAGER) ---
# =============================================================================
class AssetManager:
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.load_assets()

    def load_assets(self):
        try:
            self.fonts['medium'] = pygame.font.Font('assets/font/font.ttf', 22)
            self.fonts['large'] = pygame.font.Font('assets/font/font.ttf', 30)
            self.fonts['popup'] = pygame.font.Font('assets/font/font.ttf', 72)
        except pygame.error:
            print("Aviso: Fonte personalizada não encontrada. Usando fontes padrão.")
            self.fonts['medium'] = pygame.font.Font(None, 28)
            self.fonts['large'] = pygame.font.Font(None, 36)
            self.fonts['popup'] = pygame.font.Font(None, 80)

        try:
            self.images['spritesheet'] = pygame.image.load('assets/images/265627.png').convert_alpha()
            self.images['background'] = pygame.image.load('assets/images/background.png').convert()
            self.images['background'] = pygame.transform.scale(self.images['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.images['final_photo'] = pygame.image.load('assets/images/nossa_foto.png').convert()
            self.images['final_photo'] = pygame.transform.scale(self.images['final_photo'],
                                                                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.images['food_spritesheet'] = pygame.image.load('assets/images/comidas.png').convert_alpha()
        except pygame.error as e:
            print(f"Erro ao carregar imagem: {e}. Verifique se os arquivos estão na pasta 'assets/images'.")
            sys.exit()

        try:
            self.sounds['click'] = pygame.mixer.Sound('assets/sfx/click.wav')
            self.sounds['interact'] = pygame.mixer.Sound('assets/sfx/interact.wav')
            self.sounds['correct'] = pygame.mixer.Sound('assets/sfx/correct.wav')
            self.sounds['wrong'] = pygame.mixer.Sound('assets/sfx/wrong.wav')
            self.sounds['level_up'] = pygame.mixer.Sound('assets/sfx/level_up.wav')
        except pygame.error as e:
            print(f"Aviso: Não foi possível carregar alguns sons. O jogo funcionará sem eles. Erro: {e}")
    def load_audio(self):
        pass
# =============================================================================
# --- CLASSES DO JOGO ---
# =============================================================================
class SpriteSheet:
    def __init__(self, sheet, grid_width, grid_height):
        self.sheet = sheet
        self.grid_width = grid_width
        self.grid_height = grid_height

    def get_sprite(self, row, col, scale=3):
        image = pygame.Surface((self.grid_width, self.grid_height), pygame.SRCALPHA)
        source_rect = (col * self.grid_width, row * self.grid_height, self.grid_width, self.grid_height)
        image.blit(self.sheet, (0, 0), source_rect)
        image = pygame.transform.scale(image, (int(self.grid_width * scale), int(self.grid_height * scale)))
        return image


class Raposinha(pygame.sprite.Sprite):
    def __init__(self, assets):
        super().__init__()
        self.assets = assets
        self.pet_sheet_handler = SpriteSheet(self.assets.images['spritesheet'], 51, 53)
        self.food_sheet_handler = SpriteSheet(self.assets.images['food_spritesheet'], 16, 16)

        self.animation = [self.pet_sheet_handler.get_sprite(6, col) for col in [0, 1, 2, 3, 4, 5]]
        self.happy_animation = [self.pet_sheet_handler.get_sprite(7, col) for col in [0, 1]]
        self.food_icons = self.load_food_icons()
        self.eating_food = None
        self.eating_timer = 0
        self.level, self.xp, self.xp_to_next_level = 1, 0, XP_PER_LEVEL[0]
        self.fome, self.felicidade = 10, 10
        self.current_frame, self.image = 0, self.animation[0]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.particles = []
        self.current_phrase, self.phrase_start_time = None, 0
        self.last_update, self.stat_decay_time = pygame.time.get_ticks(), pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > PET_ANIMATION_SPEED:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            self.image = self.animation[self.current_frame]
        if now - self.stat_decay_time > STAT_DECAY_INTERVAL:
            self.stat_decay_time = now
            self.fome = max(0, self.fome - 1)
            self.felicidade = max(0, self.felicidade - 1)
        if self.current_phrase is None and now - self.phrase_start_time > PHRASE_INTERVAL:
            self.show_new_phrase()
        elif self.current_phrase and now - self.phrase_start_time > 5000:
            self.current_phrase = None
            self.phrase_start_time = now
        self.update_eating_animation()

    def load_food_icons(self):
        icons = []
        sheet_width_in_icons = self.food_sheet_handler.sheet.get_width() // self.food_sheet_handler.grid_width
        sheet_height_in_icons = self.food_sheet_handler.sheet.get_height() // self.food_sheet_handler.grid_height
        for row in range(sheet_height_in_icons):
            for col in range(sheet_width_in_icons):
                icons.append(self.food_sheet_handler.get_sprite(row, col, scale=2))
        return icons

    def update_eating_animation(self):
        if self.eating_food and pygame.time.get_ticks() - self.eating_timer > 1500:
            self.eating_food = None

    def draw_eating_animation(self, screen):
        if self.eating_food:
            food_rect = self.eating_food.get_rect(center=(self.rect.centerx - 40, self.rect.centery))
            screen.blit(self.eating_food, food_rect)

    def start_eating(self):
        if self.fome < 10:
            if self.food_icons:
                self.eating_food = random.choice(self.food_icons)
                self.eating_timer = pygame.time.get_ticks()
            return self.alimentar()
        return None

    def show_new_phrase(self):
        self.current_phrase = random.choice(PHRASES)
        self.phrase_start_time = pygame.time.get_ticks()

    def add_xp(self, amount):
        if self.level > len(XP_PER_LEVEL): return None
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            return self.level_up()

    def level_up(self):
        if 'level_up' in self.assets.sounds: self.assets.sounds['level_up'].play()
        self.level += 1
        if self.level > len(XP_PER_LEVEL):
            return "VICTORY"
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = XP_PER_LEVEL[self.level - 1]
        self.fome, self.felicidade = 10, 10
        return "LEVEL_UP"

    def emit_particles(self):
        for _ in range(15): self.particles.append(Particle(self.rect.centerx, self.rect.centery))

    def alimentar(self):
        self.fome = min(10, self.fome + 3)
        if 'interact' in self.assets.sounds: self.assets.sounds['interact'].play()
        self.emit_particles()
        return self.add_xp(15)

    def fazer_carinho(self):
        self.felicidade = min(10, self.felicidade + 1)
        if 'interact' in self.assets.sounds: self.assets.sounds['interact'].play()
        self.emit_particles()
        return self.add_xp(5)

    def get_save_data(self):
        return {'level': self.level, 'xp': self.xp, 'fome': self.fome, 'felicidade': self.felicidade}

    def load_save_data(self, data):
        self.level = data.get('level', 1)
        self.xp = data.get('xp', 0)
        self.fome = data.get('fome', 10)
        self.felicidade = data.get('felicidade', 10)
        if self.level > len(XP_PER_LEVEL): return
        self.xp_to_next_level = XP_PER_LEVEL[self.level - 1]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, assets):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.assets = assets
        self.text_surf = self.assets.fonts['medium'].render(self.text, True, COLORS['white'])
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)
        screen.blit(self.text_surf, self.text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if 'click' in self.assets.sounds: self.assets.sounds['click'].play()
            return True
        return False

class Particle:
    def __init__(self, x, y):
        self.x = x + random.randint(-20, 20)
        self.y = y + random.randint(-20, 20)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-3, -1)
        self.lifespan = 255
        self.color = random.choice([(255, 105, 180), (255, 182, 193)])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 5
        return self.lifespan > 0

    def draw(self, screen):
        size = int(10 * (self.lifespan / 255))
        if size < 2: return
        draw_heart_shape(screen, self.color, (self.x, self.y), size)

class Heart:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, 0)
        self.speed = random.randint(2, 5)
        self.size = random.randint(10, 25)
        self.color = random.choice([(255, 105, 180), (255, 182, 193), (220, 20, 60)])

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT + self.size:
            self.y = random.randint(-100, -self.size)
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        draw_heart_shape(screen, self.color, (self.x, self.y), self.size)

# =============================================================================
# --- MÁQUINA DE ESTADOS DO JOGO (STATE MACHINE) ---
# =============================================================================
class GameState:
    def __init__(self, game): self.game = game
    def handle_events(self, events): pass
    def update(self): pass
    def draw(self, screen): pass

class IntroState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.text_alpha = 0
        self.fade_in = True
        self.title_surf = self.game.assets.fonts['large'].render("Maya, a Raposinha", True, COLORS['text'])
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.prompt_surf = self.game.assets.fonts['medium'].render("Clique para começar", True, COLORS['text'])
        self.prompt_rect = self.prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                self.game.change_state(PlayingState)
    def update(self):
        if self.fade_in:
            self.text_alpha = min(255, self.text_alpha + 3)
            if self.text_alpha == 255: self.fade_in = False
        else:
            self.text_alpha = max(100, self.text_alpha - 3)
            if self.text_alpha == 100: self.fade_in = True

    def draw(self, screen):
        screen.blit(self.game.assets.images['background'], (0, 0))
        screen.blit(self.title_surf, self.title_rect)
        self.prompt_surf.set_alpha(self.text_alpha)
        screen.blit(self.prompt_surf, self.prompt_rect)

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.maya = self.game.maya
        self.buttons = [
            Button(20, SCREEN_HEIGHT - 70, 140, 50, "Carinho", COLORS['purple'], COLORS['purple_hover'],
                   self.game.assets),
            Button(180, SCREEN_HEIGHT - 70, 140, 50, "Quiz", COLORS['blue'], COLORS['blue_hover'], self.game.assets),
            Button(340, SCREEN_HEIGHT - 70, 140, 50, "Alimentar", COLORS['green'], COLORS['green_hover'],
                   self.game.assets)
        ]
        self.popup_message = None
        self.label_fome = self.game.assets.fonts['medium'].render("Fome:", True, COLORS['text'])
        self.label_felicidade = self.game.assets.fonts['medium'].render("Felicidade:", True, COLORS['text'])
        self.label_xp = self.game.assets.fonts['medium'].render("XP:", True, COLORS['text'])
        self.level_surf = None
        self.update_level_text()

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                if button.is_clicked(event):
                    result = None
                    if button.text == "Alimentar":
                        result = self.maya.start_eating()
                    elif button.text == "Carinho":
                        result = self.maya.fazer_carinho()
                    elif button.text == "Quiz":
                        self.game.change_state(QuizState)
                    self.handle_action_result(result)

    def handle_action_result(self, result):
        if result == "VICTORY":
            self.game.change_state(AnniversaryState)
        elif result == "LEVEL_UP":
            self.show_popup(f"Nível {self.maya.level}!")
            self.update_level_text()

    def update(self):
        self.maya.update()
        for button in self.buttons: button.check_hover(pygame.mouse.get_pos())
        self.maya.particles = [p for p in self.maya.particles if p.update()]
        if self.popup_message and pygame.time.get_ticks() > self.popup_message['end_time']:
            self.popup_message = None

    def draw(self, screen):
        screen.blit(self.game.assets.images['background'], (0, 0))
        screen.blit(self.maya.image, self.maya.rect)
        self.maya.draw_eating_animation(screen)
        for particle in self.maya.particles: particle.draw(screen)
        if self.maya.current_phrase:
            self.draw_speech_bubble(screen, self.maya.current_phrase, (self.maya.rect.centerx, self.maya.rect.top - 40))
        self.draw_ui(screen)
        if self.popup_message:
            screen.blit(self.popup_surf, self.popup_rect)

    def update_level_text(self):
        level_text = f"Nível: {self.maya.level}"
        self.level_surf = self.game.assets.fonts['medium'].render(level_text, True, COLORS['text'])

    def show_popup(self, text, duration=2000):
        self.popup_message = {'text': text, 'end_time': pygame.time.get_ticks() + duration}
        popup_surf = self.game.assets.fonts['popup'].render(text, True, COLORS['xp_color'])
        self.popup_surf = popup_surf
        self.popup_rect = popup_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def draw_ui(self, screen):
        self.draw_status_bar(screen, 10, 10, self.label_fome, self.maya.fome, 10, COLORS['red'])
        self.draw_status_bar(screen, 10, 50, self.label_felicidade, self.maya.felicidade, 10, COLORS['blue'])
        self.draw_status_bar(screen, 10, 90, self.label_xp, self.maya.xp, self.maya.xp_to_next_level,
                             COLORS['xp_color'])
        screen.blit(self.level_surf, (SCREEN_WIDTH - self.level_surf.get_width() - 20, 20))
        for button in self.buttons: button.draw(screen)

    def draw_status_bar(self, screen, x, y, label_surf, value, max_value, color):
        screen.blit(label_surf, (x, y))
        bar_x, bar_width, bar_height = x + 120, 200, 25
        percent = value / max_value if max_value > 0 else 0
        border_rect = pygame.Rect(bar_x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, y, bar_width * percent, bar_height)
        pygame.draw.rect(screen, COLORS['white'], border_rect, border_radius=5)
        if fill_rect.width > 0:
            pygame.draw.rect(screen, color, fill_rect, border_radius=5)
        pygame.draw.rect(screen, COLORS['black'], border_rect, 2, border_radius=5)

    def draw_speech_bubble(self, screen, text, pos):
        text_surf = self.game.assets.fonts['medium'].render(text, True, COLORS['text'])
        padding = 10
        bubble_rect = text_surf.get_rect(center=pos).inflate(padding * 2, padding * 2)
        pygame.draw.rect(screen, COLORS['bubble_bg'], bubble_rect, border_radius=15)
        pygame.draw.rect(screen, COLORS['bubble_border'], bubble_rect, 2, border_radius=15)
        screen.blit(text_surf, text_surf.get_rect(center=pos))
        tip = (pos[0], pos[1] + bubble_rect.height // 2)
        points = [tip, (tip[0] - 10, tip[1] + 10), (tip[0] + 10, tip[1] + 10)]
        pygame.draw.polygon(screen, COLORS['bubble_bg'], points)
        pygame.draw.polygon(screen, COLORS['bubble_border'], points, 2)

class QuizState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.maya = self.game.maya
        self.question_data = random.choice(QUIZ_DATA)
        self.question_text = self.question_data["pergunta"]
        self.options = self.question_data["opcoes"]
        self.correct_idx = self.question_data["correta"]
        self.feedback, self.feedback_timer = None, 0
        self.buttons = []
        self.setup_buttons()

    def handle_events(self, events):
        if self.feedback: return
        for event in events:
            for i, button in enumerate(self.buttons):
                if button.is_clicked(event):
                    self.process_answer(i)
                    return

    def update(self):
        if not self.feedback:
            for button in self.buttons: button.check_hover(pygame.mouse.get_pos())
        elif pygame.time.get_ticks() - self.feedback_timer > 2000:
            self.game.change_state(PlayingState)

    def draw(self, screen):
        screen.blit(self.game.assets.images['background'], (0, 0))
        screen.blit(self.maya.image, self.maya.rect)
        wrapped_text = textwrap.wrap(self.question_text, width=35)
        y = 80
        for line in wrapped_text:
            text_surf = self.game.assets.fonts['medium'].render(line, True, COLORS['text'])
            screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += 40
        for button in self.buttons: button.draw(screen)

    def setup_buttons(self):
        btn_w, btn_h, pad = 350, 50, 15
        start_y = (SCREEN_HEIGHT - (btn_h + pad) * len(self.options)) // 2 + 50
        for i, opt in enumerate(self.options):
            y = start_y + i * (btn_h + pad)
            self.buttons.append(
                Button(SCREEN_WIDTH // 2 - btn_w // 2, y, btn_w, btn_h, opt, COLORS['blue'], COLORS['purple'],
                       self.game.assets))

    def process_answer(self, chosen_index):
        self.feedback_timer = pygame.time.get_ticks()
        result = None
        if chosen_index == self.correct_idx:
            self.feedback = "CORRECT"
            self.buttons[chosen_index].color = COLORS['correct_answer']
            if 'correct' in self.game.assets.sounds: self.game.assets.sounds['correct'].play()
            self.maya.felicidade = min(10, self.maya.felicidade + 5)
            result = self.maya.add_xp(50)
        else:
            self.feedback = "INCORRECT"
            self.buttons[chosen_index].color = COLORS['incorrect_answer']
            self.buttons[self.correct_idx].color = COLORS['correct_answer']
            if 'wrong' in self.game.assets.sounds: self.game.assets.sounds['wrong'].play()
            self.maya.felicidade = max(0, self.maya.felicidade - 3)
            result = self.maya.add_xp(5)
        if result:
            self.game.change_state(PlayingState, action_result=result)

class AnniversaryState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.hearts = [Heart() for _ in range(100)]
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
        self.happy_frames = self.game.maya.happy_animation
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = PET_ANIMATION_SPEED

    def update(self):
        for heart in self.hearts: heart.update()
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.happy_frames)

    def draw(self, screen):
        screen.blit(self.game.assets.images['final_photo'], (0, 0))
        for heart in self.hearts: heart.draw(screen)
        current_happy_image = self.happy_frames[self.current_frame]
        happy_rect = current_happy_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
        screen.blit(current_happy_image, happy_rect)
        self.draw_final_message(screen, "Feliz aniversário de namoro", SCREEN_HEIGHT // 2 - 50)
        self.draw_final_message(screen, "Meu Squirtle!", SCREEN_HEIGHT // 2 + 40, font_key='medium')

    def draw_final_message(self, screen, text, y_pos, font_key='large'):
        font = self.game.assets.fonts[font_key]
        text_surf = font.render(text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        bg_rect = text_rect.inflate(20, 20)
        pygame.draw.rect(screen, COLORS['final_message_bg'], bg_rect, border_radius=15)
        screen.blit(text_surf, text_rect)

# =============================================================================
# --- CLASSE PRINCIPAL DO JOGO ---
# =============================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self.maya = Raposinha(self.assets)
        self.load_game()
        self.state_manager = IntroState(self)
        # <-- MUDANÇA: ADICIONE ESTAS DUAS LINHAS AQUI
        try:
            icon_surface = pygame.image.load("icon.png")
            pygame.display.set_icon(icon_surface)
        except pygame.error as e:
            print(f"Não foi possível carregar o ícone: {e}")

    def change_state(self, new_state_class, **kwargs):
        new_state = new_state_class(self)
        self.state_manager = new_state
        action_result = kwargs.get('action_result')
        if isinstance(new_state, PlayingState) and action_result:
            new_state.handle_action_result(action_result)

    def save_game(self):
        with open(SAVE_FILE, 'w') as f: json.dump(self.maya.get_save_data(), f)
        print("Jogo salvo!")

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.maya.load_save_data(data)
                print("Progresso carregado!")
            except (json.JSONDecodeError, KeyError):
                print("Arquivo de save corrompido. Começando um novo jogo.")

    def run(self):
        is_running = True
        while is_running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.save_game()
                    is_running = False
            self.state_manager.handle_events(events)
            self.state_manager.update()
            self.state_manager.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# =============================================================================
# --- PONTO DE ENTRADA ---
# =============================================================================
async def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    asyncio.run(main())
