from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Случайное животное")],
            [KeyboardButton(text="Викторина")]
        ],
        resize_keyboard=True
    )

# Меню викторины
def quiz_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Дальше", callback_data="next")],
            [InlineKeyboardButton(text="Закончить", callback_data="stop")]
        ]
    )

# Кнопки для викторины с опцией применения винтовки
def quiz_buttons(animals, rifle_available=False, rifle_used=False):
    buttons = []
    
    # Кнопки с животными
    row = []
    for i, animal in enumerate(animals):
        row.append(InlineKeyboardButton(text=animal, callback_data=f"answer_{animal}"))
        if (i + 1) % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    # Кнопка применения винтовки (если доступна и ещё не использована)
    if rifle_available and not rifle_used:
        buttons.append([InlineKeyboardButton(text="Винтовка! 🔫", callback_data="use_rifle")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)