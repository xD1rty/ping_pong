import os
import random
import time
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db.models import Users, Game
from keyboards.inline import game_menu, get_opponent_menu, complexity_ai_menu

BALL = "🍐"
CLOUD = "🌫"
PLAYER = "☄"
OPPONENT = "🌏"

game_router = Router()

# Начальная карта

map_list = {}
game_state = {}


def create_new_map(user_id, opponent_id):
    game_state[user_id] = {
        'map': [
            [CLOUD, CLOUD, OPPONENT, CLOUD, CLOUD, CLOUD, CLOUD],
            [BALL, CLOUD, CLOUD, CLOUD, CLOUD, CLOUD, CLOUD],
            [CLOUD, CLOUD, CLOUD, CLOUD, CLOUD, CLOUD, CLOUD],
            [CLOUD, CLOUD, CLOUD, CLOUD, CLOUD, CLOUD, CLOUD],
            [CLOUD, CLOUD, PLAYER, CLOUD, CLOUD, CLOUD, CLOUD]
        ],
        'ball_pos': (1, 0),
        'ball_dir_x': 1,
        'ball_dir_y': 1,
        'stopped': False,
        'opponent_id': opponent_id
    }


def find_position(game_map, value):
    for i, row in enumerate(game_map):
        for j, cell in enumerate(row):
            if cell == value:
                return i, j
    return None


def display_map(game_map):
    s = ""
    for row in game_map:
        s += "".join(row) + "\n"
    return s


def move_player(game_map, direction):
    player_pos = find_position(game_map, PLAYER)
    if player_pos:
        x, y = player_pos
        new_y = y + direction
        if 0 <= new_y < len(game_map[0]):
            game_map[x][y], game_map[x][new_y] = CLOUD, PLAYER


def move_opponent(game_map, direction):
    player_pos = find_position(game_map, OPPONENT)
    if player_pos:
        x, y = player_pos
        new_y = y + direction
        if 0 <= new_y < len(game_map[0]):
            game_map[x][y], game_map[x][new_y] = CLOUD, OPPONENT


async def find_or_create_game(user: Users):
    # Попробуем найти игру, ожидающую второго игрока
    game = await Game.filter(status='waiting').first()

    if game:
        # Присоединяем пользователя к игре как player2
        game.player2 = user
        game.status = 'ongoing'
        await game.save()
    else:
        # Создаем новую игру, где user будет player1
        game = await Game.create(player1=user)
        await game.save()

    return game


def move_ball(game_map, ball_pos, ball_dir_x, ball_dir_y):
    x, y = ball_pos
    new_x = x + ball_dir_y
    new_y = y + ball_dir_x
    print(new_x, new_y)
    print(find_position(game_map, PLAYER))

    player_pos = find_position(game_map, PLAYER)

    if (new_x, new_y) == player_pos or (new_x == player_pos[0] and new_y-1 == player_pos[0]):
        print(">")
        ball_dir_x = -ball_dir_x
        ball_dir_y = -ball_dir_y
        new_x = x + ball_dir_x
        new_y = y + ball_dir_y

    opponent_pos = find_position(game_map, OPPONENT)

    if (new_x, new_y) == opponent_pos or (new_x == opponent_pos[0] and new_y-1 == opponent_pos[0]):
        print("<")
        ball_dir_x = -ball_dir_x
        ball_dir_y = -ball_dir_y
        new_x = x + ball_dir_x
        new_y = y + ball_dir_y

    # Проверка столкновений с краями
    if new_x == 0:
        return "player"
    if new_x >= len(game_map) - 1:
        return "opponent"
    if new_y < 0 or new_y >= len(game_map[0]):
        ball_dir_x = -ball_dir_x
        new_y = y + ball_dir_x

    # Проверка наличия игрока вокруг мяча

    # Проверка границ перед присвоением
    if 0 <= new_x < len(game_map) and 0 <= new_y < len(game_map[0]):
        game_map[x][y], game_map[new_x][new_y] = CLOUD, BALL

    return (new_x, new_y), ball_dir_x, ball_dir_y


async def game_loop_for_2players(message: Message, message_1: Message, user_id, game_id):
    while not game_state[user_id]['stopped']:
        result = move_ball(game_state[user_id]['map'], game_state[user_id]['ball_pos'],
                           game_state[user_id]['ball_dir_x'], game_state[user_id]['ball_dir_y'])

        if result == "player":
            game_obj = await Game.filter(id=game_id).first()
            await game_obj.delete()
            await message.answer("Ты проиграл!")
            await message_1.answer("Ты выиграл!")
            winner = await Users.filter(id=message_1.from_user.id).first()
            winner.wins = winner.wins + 1
            if winner.rating == 0:
                winner.rating = float(winner.wins)
            else:
                winner.rating = float(winner.wins / winner.losses)
            await winner.save()

            losser = await Users.filter(id=message.from_user.id).first()
            losser.losses = losser.losses + 1
            losser.rating = float(losser.wins / losser.losses)
            await losser.save()
            return
        elif result == "opponent":
            game_obj = await Game.filter(id=game_id).first()
            await game_obj.delete()
            await message.answer("Ты выиграл!")

            await message_1.answer("Ты проиграл!")

            winner = await Users.filter(id=message.from_user.id).first()
            winner.wins = winner.wins + 1
            if winner.rating == 0:
                winner.rating = float(winner.wins)
            else:
                winner.rating = float(winner.wins / winner.losses)
            await winner.save()

            losser = await Users.filter(id=message_1.from_user.id).first()
            losser.losses = losser.losses + 1
            losser.rating = float(losser.wins / losser.losses)
            return
        else:
            game_state[user_id]['ball_pos'], game_state[user_id]['ball_dir_x'], game_state[user_id][
                'ball_dir_y'] = result

        await message.edit_text(display_map(game_state[user_id]['map']), reply_markup=game_menu)
        await message_1.edit_text(display_map(game_state[user_id]['map']), reply_markup=game_menu)
        await asyncio.sleep(1)

async def game_loop_easy(message: Message, user_id, user):
    while not game_state[user_id]["stopped"]:
        result = move_ball(game_state[user_id]['map'], game_state[user_id]['ball_pos'],
                           game_state[user_id]['ball_dir_x'], game_state[user_id]['ball_dir_y'])
        if result == "player":
            await message.edit_text("Вы выиграли")

            user.wins = user.wins + 1
            if user.rating == 0:
                user.rating = float(user.wins)
            else:
                user.rating = float(user.wins / user.losses)
            await user.save()
            return
        if result == "opponent":
            await message.edit_text("Вы проиграли")

            print(user)
            user.losses = user.losses + 1
            user.rating = float(user.wins / user.losses)
            await user.save()
            return
        else:
            game_state[user_id]['ball_pos'], game_state[user_id]['ball_dir_x'], game_state[user_id][
                'ball_dir_y'] = result
            move_opponent(game_state[user_id]["map"], random.choice([1, -1]))
            await message.edit_text(display_map(game_state[user_id]["map"]), reply_markup=game_menu)
        await asyncio.sleep(0.5)

async def game_loop_middle(message: Message, user_id, user):
    while not game_state[user_id]["stopped"]:
        result = move_ball(game_state[user_id]['map'], game_state[user_id]['ball_pos'],
                           game_state[user_id]['ball_dir_x'], game_state[user_id]['ball_dir_y'])
        if result == "player":
            await message.edit_text("Вы выиграли")

            user.wins = user.wins + 1
            if user.rating == 0:
                user.rating = float(user.wins)
            else:
                user.rating = float(user.wins / user.losses)
            await user.save()
            return
        if result == "opponent":
            await message.edit_text("Вы проиграли")

            print(user)
            user.losses = user.losses + 1
            user.rating = float(user.wins / user.losses)
            await user.save()
            return
        else:
            game_state[user_id]['ball_pos'], game_state[user_id]['ball_dir_x'], game_state[user_id][
                'ball_dir_y'] = result
            x, y = find_position(game_state[user_id]["map"], PLAYER)
            my_x, my_y = find_position(game_state[user_id]["map"], OPPONENT)
            move_opponent(game_state[user_id]["map"], y-my_y if y<my_y else my_y-y)
            await message.edit_text(display_map(game_state[user_id]["map"]), reply_markup=game_menu)

        await asyncio.sleep(0.5)

async def game_loop_hard(message: Message, user_id, user):
    while not game_state[user_id]["stopped"]:
        result = move_ball(game_state[user_id]['map'], game_state[user_id]['ball_pos'],
                           game_state[user_id]['ball_dir_x'], game_state[user_id]['ball_dir_y'])
        if result == "player":
            await message.edit_text("Вы выиграли")

            user.wins = user.wins + 1
            if user.rating == 0:
                user.rating = float(user.wins)
            else:
                user.rating = float(user.wins / user.losses)
            await user.save()
            return
        if result == "opponent":
            await message.edit_text("Вы проиграли")

            print(user)
            user.losses = user.losses + 1
            user.rating = float(user.wins / user.losses)
            await user.save()
            return
        else:
            game_state[user_id]['ball_pos'], game_state[user_id]['ball_dir_x'], game_state[user_id][
                'ball_dir_y'] = result
            x, y = find_position(game_state[user_id]["map"], BALL)
            my_x, my_y = find_position(game_state[user_id]["map"], OPPONENT)
            move_opponent(game_state[user_id]["map"], y-my_y if y<my_y else my_y-y)
            await message.edit_text(display_map(game_state[user_id]["map"]), reply_markup=game_menu)

        await asyncio.sleep(0.5)


@game_router.message(F.text == "Играть")
async def send_profile(message: Message, user: Users):
    await message.answer("Тебе следует выбрать с кем играть!", reply_markup=get_opponent_menu)


@game_router.callback_query(F.data == "game_with_ai")
async def play_with_ai_complexity_handler(query: CallbackQuery, user: Users):
    await query.message.edit_text("Ага! Значит ты решил поиграть сразу!", reply_markup=complexity_ai_menu)


@game_router.callback_query(F.data == "game_with_people")
async def search_game_with_people(query: CallbackQuery, user: Users):
    print(user)
    search_game = await find_or_create_game(user)
    print(search_game.player1)
    print(search_game.player2)
    if search_game.player2:
        msg_for_creator = await query.bot.send_message(search_game.player1_id,
                                                       f"К вам подсоединился игрок {search_game.player2.username.replace('_', '\\_')}")
        msg_for_opponent = await query.message.answer(f"Игра началась! Игровой идентификатор: {search_game.id}")
        create_new_map(search_game.player1_id, query.from_user.id)
        map = display_map(game_state[search_game.player1_id]["map"])
        msg1 = await query.message.answer(map, reply_markup=game_menu)
        msg2 = await query.bot.send_message(search_game.player1_id, map, reply_markup=game_menu)
        await asyncio.create_task(game_loop_for_2players(msg1, msg2, search_game.player1_id, search_game.id))
    else:
        await query.message.answer("Ждем другого пользователя, чтобы начать игру.")

@game_router.callback_query(F.data == "easy")
async def easy_game(query: CallbackQuery, user: Users):
    print(user)
    create_new_map(query.from_user.id, "bot")
    map = display_map(game_state[query.from_user.id]["map"])
    msg = await query.message.answer(map, reply_markup=game_menu)
    await asyncio.create_task(game_loop_easy(msg, query.from_user.id, user))

@game_router.callback_query(F.data == "middle")
async def easy_game(query: CallbackQuery, user: Users):
    print(user)
    create_new_map(query.from_user.id, "bot")
    map = display_map(game_state[query.from_user.id]["map"])
    msg = await query.message.answer(map, reply_markup=game_menu)
    await asyncio.create_task(game_loop_middle(msg, query.from_user.id, user))

@game_router.callback_query(F.data == "hard")
async def easy_game(query: CallbackQuery, user: Users):
    print(user)
    create_new_map(query.from_user.id, "bot")
    map = display_map(game_state[query.from_user.id]["map"])
    msg = await query.message.answer(map, reply_markup=game_menu)
    await asyncio.create_task(game_loop_hard(msg, query.from_user.id, user))

@game_router.callback_query(F.data == "left")
async def move_left(query: CallbackQuery):
    user_id = query.from_user.id
    if user_id in game_state:
        move_player(game_state[user_id]['map'], -1)
        await query.message.edit_text(display_map(game_state[user_id]['map']), reply_markup=game_menu)
        await query.answer()
    else:
        search_game = await Game.filter(player2_id=user_id, status="ongoing").first()
        print(search_game)
        move_opponent(game_state[search_game.player1_id]['map'], -1)
        await query.message.edit_text(display_map(game_state[search_game.player1_id]['map']), reply_markup=game_menu)
        await query.answer()


@game_router.callback_query(F.data == "right")
async def move_right(query: CallbackQuery):
    user_id = query.from_user.id
    if user_id in game_state:
        move_player(game_state[user_id]['map'], 1)
        await query.message.edit_text(display_map(game_state[user_id]['map']), reply_markup=game_menu)
        await query.answer()
    else:
        search_game = await Game.filter(player2_id=user_id, status="ongoing").first()
        print(search_game)
        move_opponent(game_state[search_game.player1_id]['map'], 1)
        await query.message.edit_text(display_map(game_state[search_game.player1_id]['map']), reply_markup=game_menu)
        await query.answer()

@game_router.callback_query(F.data == "stop")
async def stop_game(query: CallbackQuery):
    user_id = query.from_user.id
    if user_id in game_state:
        game_state[user_id]['ball'] = True
        await query.message.edit_text("Игра остановлена по вашему решению", reply_markup=game_menu)
        await query.answer()
    else:
        search_game = await Game.filter(player2_id=user_id, status="ongoing").first()
        print(search_game)
        game_state[search_game.player1_id]['ball'] = True
        await query.message.edit_text("Игра остановлена", reply_markup=game_menu)
        await query.bot.send_message(search_game.player1_id ,"Игра остановлена")
        await query.answer()
