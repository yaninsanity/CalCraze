#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pygame, sys, os, json, random, time, traceback
from math import sin, cos, tan, floor, ceil, log, exp, sqrt
from googletrans import Translator

# ------------------- 常量与默认配置 -------------------
CONFIG_DIR      = "config"
ASSETS_DIR      = "assets"
HIGH_SCORE_FILE = "highscore.dat"
LOGO_FILE       = os.path.join(ASSETS_DIR, "logo.png")
BGM_FILE        = os.path.join(ASSETS_DIR, "bgm.mp3")

MENU_ANIMATION_SPEED = 15
CELL_GLOW_DURATION   = 0.3

BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
GRAY       = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
GREEN      = (0, 200, 0)
BLUE       = (100, 100, 255)
RED        = (255, 0, 0)
YELLOW     = (255, 255, 0)
DARK_GRAY  = (50, 50, 50)
BG_COLOR   = (240, 240, 240)

DEFAULT_SETTINGS = {
    "default_language": "en",
    "window_width": 600,
    "window_height": 750,
    "grid_size": 4,
    "cell_size": 100,
    "fps": 30,
    "music_on": True,
    "difficulty": {
        "beginner":      {"min": 1, "max": 9,  "rounds": 7,  "time_limit": 30},
        "intermediate":  {"min": 1, "max": 15, "rounds": 10, "time_limit": 40},
        "advanced":      {"min": 1, "max": 20, "rounds": 15, "time_limit": 50}
    },
    "current_difficulty": "beginner"
}

DEFAULT_LANGUAGES = {
    "en": {
        "title_main_menu": "CalCraze - Formula Fill",
        "menu_start": "Start Game",
        "menu_help": "Help",
        "menu_high_scores": "High Scores",
        "menu_quit": "Quit",
        "select_difficulty": "Select Difficulty",
        "difficulty_beginner": "Beginner",
        "difficulty_intermediate": "Intermediate",
        "difficulty_advanced": "Advanced",
        "press_esc_return": "(Press ESC to return)",
        "help_title": "Help - Formula Fill",
        "help_lines": [
            "A random formula skeleton with placeholders (A, B, C, ...) is provided.",
            "Select numbers from the grid to fill in the placeholders in order.",
            "The formula updates dynamically as you choose numbers.",
            "If the computed result matches the target, you score!",
            "Correct => Score up, Wrong => Penalty.",
            "Game is turn-based. Complete all rounds to finish.",
            "Press Cmd+H / Ctrl+H to toggle help."
        ],
        "score_label": "Score",
        "high_score_label": "High Score",
        "formula_label": "Formula",
        "round_label": "Round",
        "time_label": "Time",
        "game_over": "Game Over! Press Enter to return to menu.",
        "feedback_correct": "Correct!",
        "feedback_wrong": "Wrong!",
        "feedback_timeout": "Time's up!",
        "menu_new_game": "New Game",
        "menu_pause": "Pause",
        "menu_resume": "Resume",
        "menu_settings": "Settings",
        "menu_quit_game": "Quit Game",
        "language_menu_title": "Select Language",
        "language_english": "English",
        "language_chinese": "Chinese (Traditional)",
        "operator_plus": "+",
        "operator_minus": "-",
        "operator_multiply": "*",
        "operator_divide": "/",
        "settings_title": "Settings",
        "toggle_music": "Music: ",
        "change_difficulty": "Change Difficulty",
        "change_language": "Change Language",
        "language_prompt": "Select Language",
        "back": "Back",
        "paused_text": "PAUSED"
    },
    "zh": {
        "title_main_menu": "CalCraze - 填空模式",
        "menu_start": "開始遊戲",
        "menu_help": "幫助",
        "menu_high_scores": "最高分",
        "menu_quit": "離開",
        "select_difficulty": "請選擇難度",
        "difficulty_beginner": "初級",
        "difficulty_intermediate": "中級",
        "difficulty_advanced": "高級",
        "press_esc_return": "(按 ESC 返回)",
        "help_title": "幫助 - 填空模式",
        "help_lines": [
            "系統提供一個隨機公式骨架，內含 A, B, C, ... 的占位符。",
            "從棋盤中選擇數字，依序填入占位符，公式會動態更新。",
            "若計算結果與目標一致，即算成功！",
            "正確加分，錯誤扣分。",
            "遊戲為回合制，完成所有回合後結束。",
            "可按 Cmd+H / Ctrl+H 切換幫助視窗。"
        ],
        "score_label": "分數",
        "high_score_label": "最高分",
        "formula_label": "公式",
        "round_label": "回合",
        "time_label": "時間",
        "game_over": "遊戲結束！按 Enter 返回選單。",
        "feedback_correct": "正確！",
        "feedback_wrong": "錯誤！",
        "feedback_timeout": "超時！",
        "menu_new_game": "新遊戲",
        "menu_help": "幫助",
        "menu_high_scores": "最高分",
        "menu_quit": "離開",
        "menu_pause": "暫停",
        "menu_resume": "繼續",
        "menu_settings": "設定",
        "menu_quit_game": "離開遊戲",
        "language_menu_title": "選擇語言",
        "language_english": "英文",
        "language_chinese": "中文(繁體)",
        "operator_plus": "＋",
        "operator_minus": "－",
        "operator_multiply": "×",
        "operator_divide": "÷",
        "settings_title": "設定",
        "toggle_music": "音樂：",
        "change_difficulty": "更改難度",
        "change_language": "更改語言",
        "language_prompt": "選擇語言",
        "back": "返回",
        "paused_text": "暫停中"
    }
}

# ------------------- JSON 读写函数 -------------------
def load_json(path, default_data):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_data

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_settings():
    s = load_json(os.path.join(CONFIG_DIR, "settings.json"), DEFAULT_SETTINGS)
    if "music_on" not in s:
        s["music_on"] = True
    if "current_difficulty" not in s:
        s["current_difficulty"] = "beginner"
    save_json(os.path.join(CONFIG_DIR, "settings.json"), s)
    return s

def save_settings(s):
    save_json(os.path.join(CONFIG_DIR, "settings.json"), s)

def load_languages():
    return load_json(os.path.join(CONFIG_DIR, "languages.json"), DEFAULT_LANGUAGES)

def save_languages(langs):
    save_json(os.path.join(CONFIG_DIR, "languages.json"), langs)

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(v):
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
        f.write(str(v))

# ------------------- Google 翻译补齐 -------------------
def auto_translate(target_lang, src_dict):
    translator = Translator()
    new_dict = {}
    for k, v in src_dict.items():
        try:
            if isinstance(v, list):
                arr = []
                for line in v:
                    tr = translator.translate(line, dest=target_lang, src="en")
                    arr.append(tr.text)
                new_dict[k] = arr
            else:
                tr = translator.translate(v, dest=target_lang, src="en")
                new_dict[k] = tr.text
        except:
            new_dict[k] = v
    return new_dict

def ensure_language(lang_dict, lang_code):
    defaults = DEFAULT_LANGUAGES["en"].keys()
    current = lang_dict.get(lang_code, {})
    missing = [k for k in defaults if k not in current]
    if missing:
        print(f"Missing keys in {lang_code}: {missing}, auto-translating...")
        for k in missing:
            current[k] = auto_translate(lang_code, {k: DEFAULT_LANGUAGES["en"][k]})[k]
        lang_dict[lang_code] = current
        save_languages(lang_dict)
    return lang_dict.get(lang_code, DEFAULT_LANGUAGES["en"])

# ------------------- 安全运算函数 -------------------
def safe_eval(expr):
    try:
        allowed = {"__builtins__": None, "sin": sin, "cos": cos, "tan": tan,
                   "floor": floor, "ceil": ceil, "log": log, "exp": exp, "sqrt": sqrt}
        return eval(expr, allowed)
    except:
        return None

# ------------------- 系统字体函数 -------------------
def sys_font(size=36):
    try:
        return pygame.font.Font(os.path.join("assets","fonts", "jf-openhuninn-2.1.ttf"), size)
    except Exception as e:
        logging.warning(f"Failed to load custom Chinese font: {e}")
        return pygame.font.SysFont("PingFang TC", size)  # 尝试系统自带的


# ------------------- 全屏垂直选单 -------------------
def run_vertical_menu(screen, bar_height, logo_surf, font, title, items):
    clock = pygame.time.Clock()
    selected = 0
    y_offset = 0
    animation_start = time.time()
    running = True
    while running:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, screen.get_width(), bar_height))
        if logo_surf:
            lr = logo_surf.get_rect()
            lr.centerx = screen.get_width() // 2
            lr.centery = bar_height // 2
            screen.blit(logo_surf, lr)
        t_surf = font.render(title, True, BLACK)
        t_rect = t_surf.get_rect(center=(screen.get_width() // 2, bar_height+50+y_offset))
        screen.blit(t_surf, t_rect)
        start_y = bar_height + 120 + y_offset
        gap = 50
        for i, opt in enumerate(items):
            text = opt + (" ->" if i == selected else "")
            color = BLUE if i == selected else BLACK
            s = font.render(text, True, color)
            screen.blit(s, (screen.get_width() // 2 - 100, start_y + i * gap))
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return None
                elif e.key == pygame.K_UP:
                    selected = (selected - 1) % len(items)
                    y_offset = MENU_ANIMATION_SPEED
                    animation_start = time.time()
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(items)
                    y_offset = -MENU_ANIMATION_SPEED
                    animation_start = time.time()
                elif e.key == pygame.K_RETURN:
                    for i in range(5):
                        scale = 1 + 0.1 * i
                        tmp = font.render(items[selected] + " ->", True, BLUE)
                        tmp = pygame.transform.smoothscale(tmp, (int(tmp.get_width() * scale), int(tmp.get_height() * scale)))
                        screen.fill(BG_COLOR)
                        screen.blit(tmp, tmp.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
                        pygame.display.flip()
                        clock.tick(60)
                    return selected
        if time.time() - animation_start < 0.2:
            y_offset *= 0.9
        else:
            y_offset = 0

# ------------------- 弹窗菜单 -------------------
def run_popup_menu(screen, items, font, title="Menu"):
    clock = pygame.time.Clock()
    running = True
    selected = 0
    w, h = 300, 200 + len(items) * 40
    popup = pygame.Surface((w, h))
    popup_rect = popup.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    bar_height = 40

    def draw_popup():
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        popup.fill(WHITE)
        pygame.draw.rect(popup, BLACK, popup.get_rect(), 2)
        t_surf = font.render(title, True, BLACK)
        popup.blit(t_surf, (10, 10))
        for i, (key, label, _) in enumerate(items):
            clr = BLUE if i == selected else BLACK
            lbl = font.render(label + (" ->" if i == selected else ""), True, clr)
            popup.blit(lbl, (20, bar_height + 40 * i))
        screen.blit(popup, popup_rect)

    while running:
        screen.fill(BG_COLOR)
        draw_popup()
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_UP:
                    selected = (selected - 1) % len(items)
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(items)
                elif e.key == pygame.K_RETURN:
                    items[selected][2]()
                    running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not popup_rect.collidepoint(e.pos):
                    running = False
                else:
                    rel_x = e.pos[0] - popup_rect.x
                    rel_y = e.pos[1] - popup_rect.y
                    if rel_y > bar_height:
                        i = (rel_y - bar_height) // 40
                        if 0 <= i < len(items):
                            items[i][2]()
                            running = False

# ------------------- 语言切换弹窗 -------------------
def run_language_popup(screen, ld, languages, settings):
    font = sys_font(28)
    items = [
        ("en", "English", None),
        ("zh", "中文(繁體)", None)
    ]
    clock = pygame.time.Clock()
    running = True
    selected = 0
    w, h = 280, 200 + len(items) * 40
    popup = pygame.Surface((w, h))
    popup_rect = popup.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    bar_height = 40
    title = ld.get("language_prompt", "Select Language")
    def draw_popup():
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        popup.fill(WHITE)
        pygame.draw.rect(popup, BLACK, popup.get_rect(), 2)
        t_surf = font.render(title, True, BLACK)
        popup.blit(t_surf, (10, 10))
        for i, (code, label, _) in enumerate(items):
            clr = BLUE if i == selected else BLACK
            lbl = font.render(label + (" ->" if i == selected else ""), True, clr)
            popup.blit(lbl, (20, bar_height + 40 * i))
        screen.blit(popup, popup_rect)
    while running:
        screen.fill(BG_COLOR)
        draw_popup()
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_UP:
                    selected = (selected - 1) % len(items)
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(items)
                elif e.key == pygame.K_RETURN:
                    chosen = items[selected][0]
                    settings["default_language"] = chosen
                    save_settings(settings)
                    ensure_language(languages, chosen)
                    running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not popup_rect.collidepoint(e.pos):
                    running = False
                else:
                    ry = e.pos[1] - popup_rect.y
                    if ry > bar_height:
                        i = (ry - bar_height) // 40
                        if 0 <= i < len(items):
                            chosen = items[i][0]
                            settings["default_language"] = chosen
                            save_settings(settings)
                            ensure_language(languages, chosen)
                            running = False

# ------------------- 难度选单 -------------------
def run_difficulty_menu(screen, ld):
    font_big = sys_font(48)
    items = [
        ld["difficulty_beginner"],
        ld["difficulty_intermediate"],
        ld["difficulty_advanced"],
        ld["back"]
    ]
    idx = run_vertical_menu(screen, 80, None, font_big, ld["select_difficulty"], items)
    if idx is None or idx == 3:
        return None
    elif idx == 0:
        return "beginner"
    elif idx == 1:
        return "intermediate"
    elif idx == 2:
        return "advanced"

# ------------------- 生成整数公式 -------------------
SKELETONS = [
    ["A", "+", "B"],
    ["A", "-", "B", "*", "C"],
    ["(", "A", "+", "B", ")", "/", "C"],
    ["A", "*", "B", "-", "C"],
    ["(", "A", "-", "B", ")", "*", "C"],
    ["A", "+", "B", "/", "C"]
]

def generate_integer_formula(skeletons, config):
    while True:
        sk = random.choice(skeletons)
        placeholders = [s for s in sk if s in ["A", "B", "C", "D"]]
        rcount = len(placeholders)
        nums = [random.randint(config["min"], config["max"]) for _ in range(rcount)]
        expr_parts = []
        idx = 0
        for s in sk:
            if s in ["A", "B", "C", "D"]:
                expr_parts.append(str(nums[idx]))
                idx += 1
            else:
                expr_parts.append(s)
        expr = "".join(expr_parts)
        val = safe_eval(expr)
        if val is not None and abs(val - round(val)) < 1e-9:
            return sk, int(round(val))

# ------------------- Cell 类 -------------------
class Cell:
    def __init__(self, row, col, number, x, y, size):
        self.row = row
        self.col = col
        self.number = number
        self.rect = pygame.Rect(x, y, size, size)
        self.selected = False

# ------------------- 顶部菜单类（弹窗） -------------------
class TopMenu:
    def __init__(self, game, font):
        self.game = game
        self.font = font
        self.menu_bar_rect = pygame.Rect(0, 0, game.settings["window_width"], 80)
        self.menu_open = False

    def draw(self):
        pygame.draw.rect(self.game.screen, DARK_GRAY, self.menu_bar_rect)
        if self.game.logo_surf:
            lr = self.game.logo_surf.get_rect()
            lr.center = (self.menu_bar_rect.centerx, self.menu_bar_rect.centery)
            self.game.screen.blit(self.game.logo_surf, lr)
        slogan = self.font.render("calcraze -- your math tutor", True, WHITE)
        sr = slogan.get_rect(center=(self.menu_bar_rect.centerx, self.menu_bar_rect.centery+35))
        self.game.screen.blit(slogan, sr)
        txt = self.font.render("Menu", True, WHITE)
        self.game.screen.blit(txt, (10, 10))
    
    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_bar_rect.collidepoint(e.pos):
                self.show_popup_menu()

    def show_popup_menu(self):
        if self.game.paused:
            pause_label = self.game.lang_data["menu_resume"]
        else:
            pause_label = self.game.lang_data["menu_pause"]
        items = [
            ("new_game", self.game.lang_data["menu_new_game"], self.game.reset_game),
            ("pause",    pause_label, self.game.toggle_pause),
            ("settings", self.game.lang_data["menu_settings"], self.show_settings),
            ("quit_game", self.game.lang_data["menu_quit_game"], self.quit_game)
        ]
        run_popup_menu(self.game.screen, items, self.font, "Menu")

    def show_settings(self):
        show_settings_menu(self.game.screen, self.game.lang_data, self.game.settings)

    def quit_game(self):
        pygame.quit()
        sys.exit()

# ------------------- 游戏主类 -------------------
class FormulaFillGame:
    def __init__(self, screen, settings, ld, language="en"):
        self.screen = screen
        self.settings = settings
        self.lang_data = ld
        self.language = language
        self.difficulty = settings.get("current_difficulty", "beginner")
        self.config = settings["difficulty"][self.difficulty]
        self.grid_size = settings["grid_size"]
        self.cell_size = settings["cell_size"]
        self.fps = settings["fps"]
        self.font = sys_font(28)
        self.small_font = sys_font(20)
        self.large_font = sys_font(36)
        self.menu_font = sys_font(24)
        self.clock = pygame.time.Clock()
        self.score = 0
        self.high_score = load_high_score()
        self.current_round = 1
        self.total_rounds = self.config.get("rounds", 7)
        self.time_limit = self.config.get("time_limit", 30)
        self.start_time = time.time()
        self.paused = False
        self.selected_cells = []
        self.show_help = False
        self.running = True
        self.feedback_message = ""
        self.feedback_time = 0

        self.logo_surf = None
        if os.path.exists(LOGO_FILE):
            try:
                tmp = pygame.image.load(LOGO_FILE)
                self.logo_surf = pygame.transform.scale(tmp, (135, 135))
            except:
                self.logo_surf = None

        self.top_menu = TopMenu(self, self.menu_font)
        self.menu_bar_height = 80
        self.scoreboard_height = 120

        self.grid = []
        self.skeleton = []
        self.placeholder_count = 0
        self.formula_str = ""
        self.target_value = 0
        self.cell_glow_time = 0
        self.init_game()

    def init_game(self):
        self.init_grid()
        self.init_formula()
        self.start_time = time.time()

    def reset_game(self):
        self.score = 0
        self.current_round = 1
        self.running = True
        self.selected_cells = []
        self.paused = False
        self.feedback_message = ""
        self.feedback_time = 0
        self.init_game()

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.start_time = time.time()
            if self.settings["music_on"]:
                pygame.mixer.music.unpause()
        else:
            self.paused = True
            pygame.mixer.music.pause()

    def init_grid(self):
        self.grid = []
        ox = 50
        oy = self.menu_bar_height + self.scoreboard_height + 20
        for r in range(self.grid_size):
            row = []
            for c in range(self.grid_size):
                n = random.randint(self.config["min"], self.config["max"])
                x = ox + c * self.cell_size
                y = oy + r * self.cell_size
                row.append(Cell(r, c, n, x, y, self.cell_size))
            self.grid.append(row)

    def init_formula(self):
        sk, val = generate_integer_formula(SKELETONS, self.config)
        self.skeleton = sk
        self.target_value = val
        placeholders = [s for s in sk if s in ["A", "B", "C", "D"]]
        self.placeholder_count = len(placeholders)
        disp = ["?" if s in ["A", "B", "C", "D"] else s for s in sk]
        self.formula_str = " ".join(disp)

    def get_dynamic_formula(self):
        res = []
        idx = 0
        for token in self.skeleton:
            if token in ["A", "B", "C", "D"]:
                if idx < len(self.selected_cells):
                    res.append(str(self.selected_cells[idx].number))
                else:
                    res.append("?")
                idx += 1
            else:
                res.append(token)
        return " ".join(res)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.top_menu.draw()
        scoreboard_rect = pygame.Rect(0, self.menu_bar_height, self.settings["window_width"], self.scoreboard_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, scoreboard_rect)
        pygame.draw.rect(self.screen, BLACK, scoreboard_rect, 2)
        self.draw_scoreboard(scoreboard_rect)
        self.draw_grid()
        if self.paused:
            p_text = self.lang_data.get("paused_text", "PAUSED")
            p_surf = self.large_font.render(p_text, True, RED)
            self.screen.blit(p_surf, p_surf.get_rect(center=(self.settings["window_width"]//2, self.settings["window_height"]//2)))
        if self.show_help:
            self.draw_help_overlay()
        pygame.display.flip()

    def draw_scoreboard(self, rect):
        elapsed = 0 if self.paused else time.time() - self.start_time
        rem = max(0, int(self.time_limit - elapsed))
        sc_txt = f"{self.lang_data['score_label']}: {self.score}"
        hs_txt = f"{self.lang_data['high_score_label']}: {self.high_score}"
        rd_txt = f"{self.lang_data['round_label']}: {self.current_round}/{self.total_rounds}"
        tm_txt = f"{self.lang_data['time_label']}: {rem}s"
        self.screen.blit(self.font.render(sc_txt, True, BLACK), (20, rect.y + 10))
        self.screen.blit(self.font.render(hs_txt, True, BLACK), (300, rect.y + 10))
        self.screen.blit(self.font.render(rd_txt, True, BLACK), (20, rect.y + 50))
        self.screen.blit(self.font.render(tm_txt, True, BLACK), (300, rect.y + 50))
        dyn = self.get_dynamic_formula()
        formula_disp = f"{self.lang_data['formula_label']}: {dyn} = {self.target_value}"
        self.screen.blit(self.small_font.render(formula_disp, True, BLACK), (20, rect.y + 85))
        if self.feedback_message and time.time()-self.feedback_time < 1.5:
            prog = (time.time()-self.feedback_time) / 1.5
            alpha = int(255*(1-prog**2))
            scale = 1+0.2*(1-prog)
            fb_surf = self.font.render(self.feedback_message, True, YELLOW)
            fb_surf.set_alpha(alpha)
            scaled = pygame.transform.smoothscale(fb_surf, (int(fb_surf.get_width()*scale), int(fb_surf.get_height()*scale)))
            r_fb = scaled.get_rect(center=(self.settings["window_width"]//2, rect.y+100))
            self.screen.blit(scaled, r_fb)

    def draw_grid(self):
        ox = 50
        oy = self.menu_bar_height + self.scoreboard_height + 20
        gw = self.grid_size * self.cell_size
        gh = self.grid_size * self.cell_size
        pygame.draw.rect(self.screen, BLACK, (ox-5, oy-5, gw+10, gh+10), 2)
        mouse_pos = pygame.mouse.get_pos()
        hover_cell = None
        for row in self.grid:
            for c in row:
                color = GREEN if c.selected else GRAY
                pygame.draw.rect(self.screen, color, c.rect)
                pygame.draw.rect(self.screen, BLACK, c.rect, 2)
                if c.rect.collidepoint(mouse_pos):
                    hover_cell = c
                    glow_alpha = 50 + 50 * abs((pygame.time.get_ticks() % 1000)/500 - 1)
                    glow = pygame.Surface((c.rect.width+4, c.rect.height+4), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (255,255,0,int(glow_alpha)), glow.get_rect(), border_radius=5)
                    self.screen.blit(glow, (c.rect.x-2, c.rect.y-2))
                ns = self.font.render(str(c.number), True, BLACK)
                nr = ns.get_rect(center=c.rect.center)
                self.screen.blit(ns, nr)
        if self.cell_glow_time > 0 and hover_cell:
            alpha = int(255*(self.cell_glow_time/CELL_GLOW_DURATION))
            glow_circle = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_circle, (255,215,0,alpha), (self.cell_size//2, self.cell_size//2), self.cell_size//3)
            self.screen.blit(glow_circle, hover_cell.rect)
            self.cell_glow_time -= self.clock.get_time()/1000

    def draw_help_overlay(self):
        w = self.settings["window_width"] - 100
        h = self.settings["window_height"] - 200
        help_surf = pygame.Surface((w, h))
        help_surf.fill(WHITE)
        pygame.draw.rect(help_surf, BLACK, help_surf.get_rect(), 2)
        r = help_surf.get_rect(center=(self.settings["window_width"]//2, self.settings["window_height"]//2))
        t_surf = self.font.render(self.lang_data["help_title"], True, BLACK)
        help_surf.blit(t_surf, (20,20))
        y = 70
        for line in self.lang_data["help_lines"]:
            ls = self.small_font.render(line, True, BLACK)
            help_surf.blit(ls, (20,y))
            y += 30
        self.screen.blit(help_surf, r)

    def handle_click_cell(self, cell):
        if cell in self.selected_cells:
            cell.selected = False
            self.selected_cells.remove(cell)
        elif len(self.selected_cells) < self.placeholder_count:
            cell.selected = True
            self.selected_cells.append(cell)
            self.cell_glow_time = CELL_GLOW_DURATION

    def evaluate_formula(self):
        if len(self.selected_cells) < self.placeholder_count:
            return
        copy_skel = list(self.skeleton)
        idx = 0
        for i, token in enumerate(copy_skel):
            if token in ["A", "B", "C", "D"]:
                copy_skel[i] = str(self.selected_cells[idx].number)
                idx += 1
        expr = "".join(copy_skel)
        res = safe_eval(expr)
        if res is not None and abs(res - self.target_value) < 1e-9:
            self.score += 10
            self.feedback_message = self.lang_data["feedback_correct"]
        else:
            self.score -= 5
            self.feedback_message = self.lang_data["feedback_wrong"]
        self.feedback_time = time.time()
        for c in self.selected_cells:
            c.selected = False
        self.selected_cells = []
        self.current_round += 1
        if self.current_round > self.total_rounds:
            self.running = False
            self.show_game_over()
        else:
            self.init_game()

    def handle_time_over(self):
        self.score -= 5
        self.feedback_message = self.lang_data["feedback_timeout"]
        self.feedback_time = time.time()
        for c in self.selected_cells:
            c.selected = False
        self.selected_cells = []
        self.current_round += 1
        if self.current_round > self.total_rounds:
            self.running = False
            self.show_game_over()
        else:
            self.init_game()

    def show_game_over(self):
        done = True
        while done:
            self.screen.fill(BG_COLOR)
            ot = self.large_font.render(self.lang_data["game_over"], True, RED)
            st = self.large_font.render(f"{self.lang_data['score_label']}: {self.score}", True, BLACK)
            self.screen.blit(ot, ot.get_rect(center=(self.settings["window_width"]//2, 200)))
            self.screen.blit(st, st.get_rect(center=(self.settings["window_width"]//2, 300)))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        done = False
                        return

    def get_cell_by_pos(self, pos):
        for row in self.grid:
            for c in row:
                if c.rect.collidepoint(pos):
                    return c
        return None

    def update_high_score(self):
        if self.score > self.high_score:
            save_high_score(self.score)

    def run(self):
        while self.running:
            self.clock.tick(self.fps)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    pygame.quit(); sys.exit()
                self.top_menu.handle_event(e)
                if e.type == pygame.KEYDOWN:
                    if (e.mod & pygame.KMOD_META and e.key == pygame.K_h) or (e.mod & pygame.KMOD_CTRL and e.key == pygame.K_h):
                        self.show_help = not self.show_help
                    if self.show_help:
                        if e.key == pygame.K_ESCAPE:
                            self.show_help = False
                    else:
                        if e.key == pygame.K_ESCAPE:
                            pass
                        elif e.key == pygame.K_RETURN:
                            self.evaluate_formula()
                        elif e.key == pygame.K_BACKSPACE:
                            if self.selected_cells:
                                last = self.selected_cells.pop()
                                last.selected = False
                elif e.type == pygame.MOUSEBUTTONDOWN and not self.show_help and not self.paused:
                    pos = e.pos
                    cell = self.get_cell_by_pos(pos)
                    if cell:
                        self.handle_click_cell(cell)
            if not self.paused and not self.show_help:
                if time.time() - self.start_time > self.time_limit:
                    self.handle_time_over()
            self.draw()
        self.update_high_score()

# ------------------- Settings 菜单 -------------------
def show_settings_menu(screen, ld, settings):
    font_big = sys_font(36)
    while True:
        music_label = ld["toggle_music"] + ("On" if settings["music_on"] else "Off")
        items = [
            music_label,
            ld["change_difficulty"],
            ld["change_language"],
            ld["back"]
        ]
        idx = run_vertical_menu(screen, 80, None, font_big, ld["settings_title"], items)
        if idx is None:
            return
        elif idx == 0:
            settings["music_on"] = not settings["music_on"]
            save_settings(settings)
            if settings["music_on"]:
                try:
                    pygame.mixer.music.unpause()
                except:
                    pass
            else:
                pygame.mixer.music.pause()
        elif idx == 1:
            d = run_difficulty_menu(screen, ld)
            if d:
                settings["current_difficulty"] = d
                save_settings(settings)
        elif idx == 2:
            run_language_popup(screen, ld, load_languages(), settings)
            new_lang = settings.get("default_language", "en")
            ld.update(load_languages().get(new_lang, DEFAULT_LANGUAGES["en"]))
        elif idx == 3:
            return

# ------------------- 帮助、高分界面 -------------------
def show_help_menu(screen, ld):
    font_big = sys_font(36)
    font_small = sys_font(24)
    running = True
    scroll_offset = 0
    content_height = len(ld["help_lines"]) * 40 + 200
    clock = pygame.time.Clock()
    while running:
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:
                    scroll_offset = min(0, scroll_offset + 20)
                elif e.button == 5:
                    scroll_offset = max(-(content_height - screen.get_height()), scroll_offset - 20)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
            elif e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BG_COLOR)
        y = 150 + scroll_offset
        for line in ld["help_lines"]:
            ls = font_small.render(line, True, BLACK)
            screen.blit(ls, (50, y))
            y += 40
        esc = font_small.render(ld["press_esc_return"], True, BLACK)
        screen.blit(esc, (50, screen.get_height()-50))
        pygame.display.flip()
        clock.tick(60)

def show_high_score_menu(screen, ld):
    font_big = sys_font(36)
    font_small = sys_font(24)
    hs = load_high_score()
    running = True
    while running:
        screen.fill(BG_COLOR)
        txt = font_big.render(f"{ld['high_score_label']}: {hs}", True, BLACK)
        screen.blit(txt, (150, 150))
        esc = font_small.render(ld["press_esc_return"], True, BLACK)
        screen.blit(esc, (150, 250))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

# ------------------- 主菜单 -------------------
def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    settings = load_settings()
    languages = load_languages()
    default_lang = settings.get("default_language", "en")
    ensure_language(languages, default_lang)
    pygame.init()
    try:
        pygame.mixer.init()
        if os.path.exists(BGM_FILE):
            pygame.mixer.music.load(BGM_FILE)
            pygame.mixer.music.play(-1)
            if not settings["music_on"]:
                pygame.mixer.music.pause()
    except Exception as e:
        print("背景音乐加载失败：", e)
    screen = pygame.display.set_mode((settings["window_width"], settings["window_height"]))
    pygame.display.set_caption("CalCraze -- your math tutor")
    logo_surf = None
    if os.path.exists(LOGO_FILE):
        try:
            tmp = pygame.image.load(LOGO_FILE)
            logo_surf = pygame.transform.scale(tmp, (180, 180))
        except:
            logo_surf = None
    my_lang_data = languages.get(default_lang, DEFAULT_LANGUAGES["en"])
    while True:
        idx = run_vertical_menu(
            screen, 80, logo_surf, sys_font(36),
            my_lang_data["title_main_menu"],
            [
                my_lang_data["menu_start"],
                my_lang_data["menu_help"],
                my_lang_data["menu_high_scores"],
                my_lang_data["menu_quit"]
            ]
        )
        if idx is None:
            break
        elif idx == 0:
            game = FormulaFillGame(screen, settings, my_lang_data, default_lang)
            game.run()
        elif idx == 1:
            show_help_menu(screen, my_lang_data)
        elif idx == 2:
            show_high_score_menu(screen, my_lang_data)
        elif idx == 3:
            break
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        pygame.quit()
        sys.exit()
