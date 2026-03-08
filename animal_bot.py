import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

from animals_data import ANIMALS, ANIMAL_CLUES
from database import UserDB
from keyboards import main_menu, quiz_menu, quiz_buttons

load_dotenv()
token = os.getenv("BOT_TOKEN")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
db = UserDB()

# Команда /start
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "🐾 <b>Добро пожаловать в мир животных!</b>\n\n"
        "Меня создал Илья, чтобы ты мог:\n"
        "Узнавать факты о животных\n"
        "Играть в викторину и зарабатывать очки\n"
        "Выбери, что хочешь делать!"
    )
    await message.answer(
        "📋 <b>Мой функционал:</b>\n"
        "Случайное животное - покажет интересный факт\n"
        "Викторина - угадывай животных по загадкам (3 попытки)\n"
        "Винтовка - открывает каждую вторую букву (1 раз за раунд)\n",
        reply_markup=main_menu()
    )

# Случайное животное
@dp.message(F.text == "Случайное животное")
async def random_animal(message: Message):
    animal = random.choice(ANIMALS)
    clues = ANIMAL_CLUES.get(animal, ["Интересный факт пока неизвестен"])
    clue = random.choice(clues)
    await message.answer(
        f"<b>{animal}</b>\n\n"
        f"<i>{clue}</i>"
    )

# Начало викторины
@dp.message(F.text == "Викторина")
async def start_quiz(message: Message):
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    if user_data["lives"] <= 0:
        db.update_user(user_id, lives=3, in_game=False)
        user_data = db.get_user(user_id)
    
    db.update_user(user_id, in_game=True)
    # Начинаем с нового животного
    await send_quiz_question(user_id, new_animal=True)

async def send_quiz_question(user_id: int, new_animal: bool = False):
    user_data = db.get_user(user_id)
    
    if user_data["lives"] <= 0:
        await bot.send_message(user_id, "У тебя закончились жизни! Начинаем заново с 3 жизнями.")
        db.update_user(user_id, lives=3, in_game=True, attempts=0)
        user_data = db.get_user(user_id)
    
    # Определяем животное для вопроса
    if new_animal or user_data["current_animal"] is None:
        # Новое животное - сбрасываем использование винтовки
        correct = random.choice(ANIMALS)
        attempts_left = 3
        db.update_user(user_id, current_animal=correct, attempts=attempts_left, rifle_used=False)
    else:
        # То же животное (после неправильного ответа)
        correct = user_data["current_animal"]
        attempts_left = user_data["attempts"]
    
    # Создаём варианты ответов (правильный + 3 случайных)
    others = random.sample([a for a in ANIMALS if a != correct], 3)
    answers = [correct] + others
    random.shuffle(answers)
    
    # Получаем загадки
    clues = ANIMAL_CLUES.get(correct, ["Угадай животное"])
    
    # Выбираем загадку в зависимости от оставшихся попыток
    if attempts_left == 3:
        clue = f"Загадка 1: {clues[0]}"
    elif attempts_left == 2:
        clue = f"Загадка 2: {clues[1]}"
    else:
        clue = f"Загадка 3: {clues[2]}"
    
    # Показываем слово в зависимости от использования винтовки
    display_word = "??? (используй загадки)"
    if user_data.get("rifle_used", False):
        # Винтовка использована - показываем буквы
        shown = []
        for i, c in enumerate(correct):
            if i % 2 == 1 or len(correct) <= 3:
                shown.append(c)
            else:
                shown.append("*")
        display_word = "Слово: " + "".join(shown)
    
    await bot.send_message(
        user_id,
        f"❤️ Жизней: {user_data['lives']} | ⭐ Очков: {user_data['score']}\n\n"
        f"{clue}\n"
        f"{display_word}\n"
        f"Попыток осталось: {attempts_left}",
        reply_markup=quiz_buttons(answers, True, user_data.get("rifle_used", False))
    )

# Применение винтовки
@dp.callback_query(F.data == "use_rifle")
async def use_rifle(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = db.get_user(user_id)
    
    if not user_data.get("rifle_used", False):
        # Активируем винтовку
        db.update_user(user_id, rifle_used=True)
        
        # Показываем слово с буквами
        correct = user_data["current_animal"]
        shown = []
        for i, c in enumerate(correct):
            if i % 2 == 1 or len(correct) <= 3:
                shown.append(c)
            else:
                shown.append("*")
        display_word = "Слово: " + "".join(shown)
        
        # Получаем текущую загадку
        attempts = user_data["attempts"]
        clues = ANIMAL_CLUES.get(correct, ["Угадай животное"])
        
        if attempts == 3:
            clue = f"Загадка 1: {clues[0]}"
        elif attempts == 2:
            clue = f"Загадка 2: {clues[1]}"
        else:
            clue = f"Загадка 3: {clues[2]}"
        
        # Создаём новые варианты ответов
        others = random.sample([a for a in ANIMALS if a != correct], 3)
        answers = [correct] + others
        random.shuffle(answers)
        
        # Обновляем сообщение (убираем кнопку винтовки)
        await callback.message.edit_text(
            f"❤️ Жизней: {user_data['lives']} | ⭐ Очков: {user_data['score']}\n\n"
            f"{clue}\n"
            f"{display_word}\n"
            f"Попыток осталось: {attempts}",
            reply_markup=quiz_buttons(answers, True, True)
        )
    
    await callback.answer("🔫 Винтовка применена!")

# Обработка ответов
@dp.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = db.get_user(user_id)
    
    if not user_data["in_game"]:
        await callback.message.edit_text("Игра не активна. Начни викторину заново.")
        return
    
    answer = callback.data.replace("answer_", "")
    correct = user_data["current_animal"]
    attempts = user_data["attempts"]
    
    if answer == correct:
        # Правильный ответ
        points = 10
        new_score = user_data["score"] + points
        db.update_user(user_id, score=new_score, current_animal=None, rifle_used=False)
        
        await callback.message.edit_text(
            f"🎉 Правильно! Это <b>{correct}</b>\n"
            f"🎉 Ты получаешь +{points} очков!\n\n"
            f"Текущий счёт: {new_score}",
            reply_markup=quiz_menu()
        )
    else:
        # Неправильный ответ
        attempts -= 1
        
        if attempts <= 0:
            # Попытки кончились - теряем жизнь
            new_lives = user_data["lives"] - 1
            db.update_user(user_id, lives=new_lives, current_animal=None, rifle_used=False)
            
            if new_lives > 0:
                await callback.message.edit_text(
                    f"Неправильно! Вот кто это был <b>{correct}</b>\n"
                    f"Теряешь одну жизнь\n\n"
                    f"Осталось жизней: {new_lives}",
                    reply_markup=quiz_menu()
                )
            else:
                await callback.message.edit_text(
                    f"Игра окончена! Это было <b>{correct}</b>\n"
                    f"У тебя не осталось жизней\n\n"
                    f"Всего очков: {user_data['score']}"
                )
                db.update_user(user_id, lives=3, in_game=False, rifle_used=False)
        else:
            # Есть ещё попытки - показываем следующую загадку
            db.update_user(user_id, attempts=attempts)
            
            # Создаём новые варианты ответов
            others = random.sample([a for a in ANIMALS if a != correct], 3)
            answers = [correct] + others
            random.shuffle(answers)
            
            # Получаем загадки
            clues = ANIMAL_CLUES.get(correct, ["Угадай животное"])
            
            # Выбираем загадку
            if attempts == 2:
                clue = f"Загадка 2: {clues[1]}"
            else:
                clue = f"Загадка 3: {clues[2]}"
            
            # Показываем слово если винтовка использована
            display_word = "??? (используй загадки)"
            if user_data.get("rifle_used", False):
                shown = []
                for i, c in enumerate(correct):
                    if i % 2 == 1 or len(correct) <= 3:
                        shown.append(c)
                    else:
                        shown.append("*")
                display_word = "Слово: " + "".join(shown)
            
            # Обновляем сообщение
            await callback.message.edit_text(
                f"❤️ Жизней: {user_data['lives']} | ⭐ Очков: {user_data['score']}\n\n"
                f"{clue}\n"
                f"{display_word}\n"
                f"Попыток осталось: {attempts}",
                reply_markup=quiz_buttons(answers, True, user_data.get("rifle_used", False))
            )
    
    await callback.answer()

# Следующий вопрос
@dp.callback_query(F.data == "next")
async def next_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.new_round(user_id)  # Сбрасываем использование винтовки
    await send_quiz_question(user_id, new_animal=True)
    await callback.message.delete()
    await callback.answer()

# Остановить игру и сбросить очки
@dp.callback_query(F.data == "stop")
async def stop_game(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Сбрасываем всё
    db.update_user(user_id, score=0, lives=3, in_game=False, 
                   current_animal=None, attempts=0, rifle_used=False)
    await callback.message.edit_text(
        "⏹Игра остановлена. Все очки сброшены!",
        reply_markup=None
    )
    await callback.answer()

# Запуск
async def main():
    print("BOT STARTED!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())