import random
from pico2d import *

import game_framework
import game_world
import common
from character import Character
from slime import spawn_slimes
from background import Background
from wall import Wall
from portal import Portal

startscreen = None
show_startscreen = True
show_help = False  # 게임 설명 화면 표시 여부
help_image = None  # 게임 설명 이미지
character = None
background = None
slimes = []
walls = []
portal = None
current_stage = 1

# 사운드 변수
lobby_music = None
stage1_music = None
stage2_music = None
stage3_music = None
attack_sound = None
levelup_sound = None
slimeattack_sound = None
current_music = None
complete_image = None
complete_music = None
show_complete = False

# 버튼 영역 정의 (x, y, width, height)
START_BUTTON = {'x': 1250, 'y': 340, 'width': 260, 'height': 100}
HELP_BUTTON = {'x': 1250, 'y': 200, 'width': 300, 'height': 100}
EXIT_BUTTON = {'x': 1250, 'y': 70, 'width': 240, 'height': 100}
BACK_BUTTON = {'x': 150, 'y': 930, 'width': 260, 'height': 90}  # 게임 설명 화면에서 돌아가기

def is_inside_button(mx, my, button):
    """마우스 좌표가 버튼 영역 안에 있는지 확인"""
    left = button['x'] - button['width'] // 2
    right = button['x'] + button['width'] // 2
    bottom = button['y'] - button['height'] // 2
    top = button['y'] + button['height'] // 2
    return left <= mx <= right and bottom <= my <= top


def draw_button(button):
    """버튼 바운딩박스 그리기"""
    left = button['x'] - button['width'] // 2
    right = button['x'] + button['width'] // 2
    bottom = button['y'] - button['height'] // 2
    top = button['y'] + button['height'] // 2

    # 바운딩박스만 그리기
    draw_rectangle(left, bottom, right, top)

def play_music(music):
    global current_music
    if current_music:
        current_music.stop()
    current_music = music
    if music:
        music.repeat_play()


def handle_events():
    global show_startscreen, show_help
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif show_complete:
            # 완료 화면에서는 아무 키나 누르면 종료
            if event.type == SDL_KEYDOWN or event.key == SDLK_ESCAPE:
                game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_1:
            if not show_startscreen:
                init_stage_1()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_2:
            if not show_startscreen:
                init_stage_2()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_3:
            if not show_startscreen:
                init_stage_3()
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = event.x, 1000 - event.y

            if show_startscreen and not show_help:
                if is_inside_button(mx, my, START_BUTTON):
                    init_stage_1()
                    show_startscreen = False
                elif is_inside_button(mx, my, HELP_BUTTON):
                    show_help = True
                elif is_inside_button(mx, my, EXIT_BUTTON):
                    game_framework.quit()
            elif show_help:
                if is_inside_button(mx, my, BACK_BUTTON):
                    show_help = False
        elif not show_startscreen:
            common.character.handle_event(event)

def check_attack_collision():
    if isinstance(common.character.state_machine.cur_state, common.character.ATTACK.__class__):
        attack_state = common.character.state_machine.cur_state
        if attack_state.attack_bb:
            attack_left, attack_bottom, attack_right, attack_top = attack_state.attack_bb
            for slime in slimes:
                slime_left, slime_bottom, slime_right, slime_top = slime.get_bb()

                # 바운딩박스 충돌 검사
                if not (attack_right < slime_left or attack_left > slime_right or
                        attack_top < slime_bottom or attack_bottom > slime_top):
                    # 충돌 발생 - 슬라임을 death 상태로 변경
                    slime.state_machine.handle_state_event(('DEATH', None))
def add_background():
    global background
    if background is None:
        background = Background()
        game_world.add_object(background, 0)


def add_walls():
    global walls
    # 벽 추가 - 여기에 원하는 만큼 벽을 추가
    walls.append(Wall(80, 700, 22, 750))


    for wall in walls:
        game_world.add_object(wall, 1)
        game_world.add_collision_pair('character:wall', common.character, wall)
        for slime in slimes:
            game_world.add_collision_pair('slime:wall', slime, wall)


def init_stage_1():
    global background, slimes, walls, portal, current_stage
    current_stage = 1

    # 1스테이지 음악 재생
    play_music(stage1_music)

    if background is None:
        background = Background()
        game_world.add_object(background, 0)
    else:
        background.image = load_image('./Resource/map/map1.png')

    for slime in slimes:
        game_world.remove_object(slime)
    slimes.clear()

    for wall in walls:
        game_world.remove_object(wall)
    walls.clear()

    walls.append(Wall(80, 700, 22, 750))
    walls.append(Wall(1520, 700, 22, 750))
    walls.append(Wall(350, 360, 560, 50))
    walls.append(Wall(1240, 360, 560, 50))
    walls.append(Wall(430, 630, 400, 50))
    walls.append(Wall(240, 800, 22, 350))
    walls.append(Wall(1160, 630, 400, 50))
    walls.append(Wall(1360, 800, 22, 350))
    walls.append(Wall(570, 830, 240, 50))
    walls.append(Wall(450, 900, 22, 170))
    walls.append(Wall(1030, 830, 240, 50))
    walls.append(Wall(1150, 900, 22, 170))

    for wall in walls:
        game_world.add_object(wall, 1)

    avoid = [common.character] + walls if common.character else walls
    slimes = spawn_slimes(5, depth=1, avoid_objects=avoid)

    if portal is None:
        portal = Portal(800, 950, 100, 100)
        game_world.add_object(portal, 1)

    setup_collisions()


def init_stage_2():
    global background, slimes, walls, portal, current_stage
    current_stage = 2

    # 2스테이지 음악 재생
    play_music(stage2_music)

    background.image = load_image('./Resource/map/map2.png')

    for slime in slimes:
        game_world.remove_object(slime)
    slimes.clear()

    for wall in walls:
        game_world.remove_object(wall)
    walls.clear()

    if portal:
        game_world.remove_object(portal)
        portal = None

    # 스테이지 2용 포탈 생성 (처음엔 비활성화)
    portal = Portal(800, 950, 100, 100)
    game_world.add_object(portal, 1)

    for wall in walls:
        game_world.add_object(wall, 1)

    avoid = [common.character] + walls if common.character else walls
    slimes = spawn_slimes(7, depth=1, avoid_objects=avoid)

    common.character.x = 200
    common.character.y = 200

    setup_collisions()


def init_stage_3():
    global background, slimes, walls, portal, current_stage
    current_stage = 3

    # 3스테이지 음악 재생
    play_music(stage3_music)

    background.image = load_image('./Resource/map/map3.png')

    # 기존 슬라임 제거
    for slime in slimes:
        game_world.remove_object(slime)
    slimes.clear()

    # 기존 벽 제거
    for wall in walls:
        game_world.remove_object(wall)
    walls.clear()

    # 포탈 제거
    if portal:
        game_world.remove_object(portal)
        portal = None

    # 캐릭터 위치 설정
    common.character.x = 200
    common.character.y = 200

    # 보스 생성
    from boss import Boss
    boss = Boss(1200, 500)
    game_world.add_object(boss, 1)

    # 충돌 설정
    setup_collisions()
    game_world.add_collision_pair('character:boss', common.character, boss)
    game_world.add_collision_pair('attack:boss', common.character, boss)
    game_world.add_collision_pair('boss_ball:character', None, common.character)

def setup_collisions():
    # 기존 충돌 쌍 초기화
    game_world.collision_pairs.clear()

    # 캐릭터 관련 충돌
    game_world.add_collision_pair('character:slime', common.character, None)
    game_world.add_collision_pair('attack:slime', common.character, None)
    game_world.add_collision_pair('slime_attack:character', None, common.character)
    game_world.add_collision_pair('character:wall', common.character, None)
    game_world.add_collision_pair('slime:wall', None, None)

    # 포탈 충돌 (스테이지 1, 2)
    if portal:
        game_world.add_collision_pair('character:portal', common.character, portal)

    # 슬라임 충돌 등록
    for slime in slimes:
        game_world.add_collision_pair('character:slime', None, slime)
        game_world.add_collision_pair('attack:slime', None, slime)
        game_world.add_collision_pair('slime_attack:character', slime, None)
        game_world.add_collision_pair('slime:wall', slime, None)

    # 벽 충돌 등록
    for wall in walls:
        game_world.add_collision_pair('character:wall', None, wall)
        for slime in slimes:
            game_world.add_collision_pair('slime:wall', None, wall)


def init():
    global startscreen, help_image, complete_image
    global lobby_music, stage1_music, stage2_music, stage3_music
    global attack_sound, levelup_sound, slimeattack_sound, complete_music

    startscreen = load_image('./Resource/map/startscreen.png')
    help_image = load_image('./Resource/map/help.png')
    complete_image = load_image('./Resource/map/complete.png')

    # 음악 로드
    lobby_music = load_music('./Resource/sound/lobby.mp3')
    stage1_music = load_music('./Resource/sound/stage1.mp3')
    stage2_music = load_music('./Resource/sound/stage2.mp3')
    stage3_music = load_music('./Resource/sound/stage3.mp3')
    complete_music = load_music('./Resource/sound/complete.mp3')

    # 효과음 로드
    attack_sound = load_wav('./Resource/sound/attack.mp3')
    levelup_sound = load_wav('./Resource/sound/levelup.mp3')
    slimeattack_sound = load_wav('./Resource/sound/slimeattack.mp3')

    # 볼륨 설정
    lobby_music.set_volume(32)
    stage1_music.set_volume(32)
    stage2_music.set_volume(32)
    stage3_music.set_volume(32)
    complete_music.set_volume(32)
    attack_sound.set_volume(64)
    levelup_sound.set_volume(64)
    slimeattack_sound.set_volume(40)

    play_music(lobby_music)

    common.character = Character()
    game_world.add_object(common.character, 2)


def update():
    if not show_startscreen:
        # 이전 레벨 저장
        prev_level = common.character.level

        game_world.update()
        game_world.handle_collisions()

        # 레벨업 체크
        if common.character.level > prev_level:
            levelup_sound.play()

        # 스테이지별 포탈 활성화 조건
        if current_stage == 1 and portal and common.character.level >= 2:
            portal.activate()
        elif current_stage == 2 and portal and common.character.level >= 3:
            portal.activate()

        # 포탈 트리거 체크
        if hasattr(common.character, 'portal_triggered') and common.character.portal_triggered:
            delattr(common.character, 'portal_triggered')
            if current_stage == 1:
                init_stage_2()
            elif current_stage == 2:
                init_stage_3()

def show_complete_screen():
    global show_complete
    show_complete = True
    play_music(complete_music)

def draw():
    clear_canvas()
    if show_complete:
        complete_image.draw_to_origin(0, 0, 1600, 1000)
    elif show_startscreen:
        if show_help:
            help_image.draw_to_origin(0, 0, 1600, 1000)
            draw_button(BACK_BUTTON)
        else:
            startscreen.draw_to_origin(0, 0, 1600, 1000)
            draw_button(START_BUTTON)
            draw_button(HELP_BUTTON)
            draw_button(EXIT_BUTTON)
    else:
        game_world.render()
    update_canvas()

def finish():
    game_world.clear()
    if current_music:
        current_music.stop()

def pause():
    if current_music:
        current_music.pause()
def resume():
    if current_music:
        current_music.resume()