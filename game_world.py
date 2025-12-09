world = [[] for _ in range(4)]

def add_object(o, depth = 0):
    world[depth].append(o)

def add_objects(ol, depth = 0):
    world[depth] += ol

def update():
    for layer in world:
        for o in layer:
            o.update()

def render():
    for layer in world:
        for o in layer:
            o.draw()

def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)
    pass

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            remove_collision_object(o)
            return

    raise ValueError('Cannot delete non existing object')

def clear():
    global world

    for layer in world:
        layer.clear()

def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True # 충돌 발생

collision_pairs = {}

def add_collision_pair(group, a, b):
    if group not in collision_pairs: # 처음 등록되는 그룹이면
        collision_pairs[group] = ([], []) # 충돌 객체 리스트 쌍 생성
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def handle_collisions():
    for group, pairs in collision_pairs.items():
        for a in pairs[0]:
            for b in pairs[1]:
                if group == 'attack:slime':
                    attack_bb = a.get_attack_bb()
                    if attack_bb:
                        attack_left, attack_bottom, attack_right, attack_top = attack_bb
                        slime_left, slime_bottom, slime_right, slime_top = b.get_bb()

                        if not (attack_right < slime_left or attack_left > slime_right or
                        attack_top < slime_bottom or attack_bottom > slime_top):
                            a.handle_collision(group, b)
                            b.handle_collision(group, a)
                elif group == 'attack:boss':
                    attack_bb = a.get_attack_bb()
                    if attack_bb:
                        attack_left, attack_bottom, attack_right, attack_top = attack_bb
                        boss_left, boss_bottom, boss_right, boss_top = b.get_bb()

                        if not (attack_right < boss_left or attack_left > boss_right or
                        attack_top < boss_bottom or attack_bottom > boss_top):
                            a.handle_collision(group, b)
                            b.handle_collision(group, a)
                elif group == 'slime_attack:character':
                    slime_attack_bb = a.get_attack_bb()
                    if slime_attack_bb:
                        slime_left, slime_bottom, slime_right, slime_top = slime_attack_bb
                        char_left, char_bottom, char_right, char_top = b.get_bb()

                        if not (slime_right < char_left or slime_left > char_right or
                        slime_top < char_bottom or slime_bottom > char_top):
                            a.handle_collision(group, b)
                            b.handle_collision(group, a)
                else:
                    if collide(a, b):
                        a.handle_collision(group, b)
                        b.handle_collision(group, a)