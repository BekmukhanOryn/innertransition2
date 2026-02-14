import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

import os
TOKEN = os.getenv("8323313698:AAHGpCJr_oc-fkMU4sYHd5tKM31VrjE0-AE")                                               # вставляй свой токен

class TestState(StatesGroup):
    question = State()

questions = [
    "1️⃣ Ваш внутренний мир — это:",
    "2️⃣ Когда вы сталкиваетесь с повторяющимся поведением в отношениях:",
    "3️⃣ Сны и случайные образы:",
    "4️⃣ Внутренний критик:",
    "5️⃣ Если внутри поднимается сил"
    ""
    "ьная эмоция:",
    "6️⃣ Когда что-то вызывает раздражение:",
    "7️⃣ Ваши сильные стороны:",
    "8️⃣ При внутреннем конфликте:",
    "9️⃣ Повторяющиеся сценарии:",
    "🔟 Если бы психика могла говорить:"
]

answers = [
    ["a) Хаос", "b) Теряюсь в деталях", "c) Лабиринт паттернов"],
    ["a) Не повезло", "b) Обвиняю других", "c) Замечаю сценарии"],
    ["a) Просто картинки", "b) Иногда интересуюсь", "c) Подсказки психики"],
    ["a) Руководит мной", "b) Трудно отделить", "c) Наблюдаю"],
    ["a) Заглушаю", "b) Проигрываю", "c) Ищу корень"],
    ["a) Автоматически", "b) Не понимаю силу", "c) Эхо Тени"],
    ["a) Не вижу", "b) Иногда использую", "c) Интегрирую"],
    ["a) Перетерпеть", "b) Импульсивно", "c) Анализирую"],
    ["a) Так сложилось", "b) Редко меняю", "c) Корректирую"],
    ["a) Не готов", "b) Ты застрял", "c) Вот паттерны"]
]

def get_inline_keyboard(q_index):
    """Клавиатура с вариантами ответа для вопроса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=answers[q_index][0], callback_data="a")],
        [InlineKeyboardButton(text=answers[q_index][1], callback_data="b")],
        [InlineKeyboardButton(text=answers[q_index][2], callback_data="c")]
    ])

def get_start_keyboard():
    """Кнопка Start снизу, всегда видна"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="▶️ Start")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Стартовое сообщение с кнопкой Start
    @dp.message(CommandStart())
    async def send_welcome(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "🧠 *Тест: Что скрывает ваша психика?*\n\n"
            "Нажмите кнопку Start ниже, чтобы начать тест.",
            reply_markup=get_start_keyboard(),
            parse_mode="Markdown"
        )
        # Сбрасываем счётчики и историю
        await state.update_data(a=0, b=0, c=0, q=0, history=[])

    # Нажатие кнопки Start
    @dp.message(F.text == "▶️ Start")
    async def begin(message: Message, state: FSMContext):
        await state.clear()
        await state.update_data(a=0, b=0, c=0, q=0, history=[])
        await state.set_state(TestState.question)
        await message.answer(questions[0], reply_markup=get_inline_keyboard(0))

    # Обработка ответов
    @dp.callback_query(TestState.question, F.data.in_(["a", "b", "c"]))
    async def process_answer(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()

        data[callback.data] += 1
        data["q"] += 1

        # Добавляем в историю выбранный вариант
        q_index = data["q"] - 1
        data.setdefault("history", []).append(f"{questions[q_index]} {answers[q_index]['abc'.index(callback.data)]}")
        await state.update_data(**data)

        # Отправляем выбранный ответ в чате
        await callback.message.answer(f"{questions[q_index]}\nВы выбрали: {answers[q_index]['abc'.index(callback.data)]}")

        # Следующий вопрос или результат
        if data["q"] < len(questions):
            await callback.message.answer(questions[data["q"]], reply_markup=get_inline_keyboard(data["q"]))
        else:
            a, b, c = data["a"], data["b"], data["c"]
            if a >= b and a >= c:
                result_text = ("🟢 *Консультация*\n\n"
                               "Вы начинаете замечать себя, но психика управляет вами. "
                               "Консультация поможет увидеть слепые зоны и даст конкретные шаги для изменений.")
            elif b >= a and b >= c:
                result_text = ("🟡 *Игра Лила*\n\n"
                               "Вы видите свои паттерны, но ещё не интегрировали их. "
                               "Игра Лила через символы и архетипы поможет глубже понять себя и свои сценарии.")
            else:
                result_text = ("🔵 *Психоаналитическая терапия*\n\n"
                               "Вы умеете наблюдать себя, распознавать бессознательные сценарии и символы. "
                               "Психоаналитическая терапия позволяет глубоко проработать структуру личности и Тень.")

            history_text = "\n\n*Ваша история ответов:*\n" + "\n".join(data["history"])

            await callback.message.answer(result_text + "\n\n" + history_text,
                                          reply_markup=get_start_keyboard(),
                                          parse_mode="Markdown")
            await state.clear()

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
