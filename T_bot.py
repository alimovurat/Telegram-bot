import asyncio
import logging
import os
import sys
import datetime

from typing import Any, Dict
from aiogram import Dispatcher, F, Router, html
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    InlineKeyboardBuilder,
    InlineKeyboardButton,
)
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardRemove,
    FSInputFile,
)
from settings import bot

order_router = Router()


class Order(StatesGroup):
    overhauls_place = State()
    house_area = State()
    interior_style = State()
    design_project = State()
    overhauls_date = State()
    address = State()
    your_location = State()
    how_to_tell = State()
    save_order = State()
    phone_number = State()
    order = {}


class Forward(StatesGroup):
    client_id = State()
    message_to_send = State()


@order_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет {hbold(message.from_user.full_name)}!\nЯ Чат-бот!\n"
        "Для оформления заказа воспользуйтесь кнопками меню.",
        reply_markup=ReplyKeyboardRemove(),
    )


@order_router.message(Command("cancel"))
@order_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup=ReplyKeyboardRemove(),
    )


@order_router.message(Command("forward"))
async def start_forward_message(message: Message, state: FSMContext) -> None:
    await state.set_state(Forward.client_id)
    await message.answer("Напишите Id клиента, которому хотите отправить сообщение")


@order_router.message(Forward.client_id)
async def get_client_id(message: Message, state: FSMContext) -> None:
    await state.update_data(client_id=message.text)
    await state.set_state(Forward.message_to_send)
    await message.answer("Напишите текст сообщения или приложите фото")


@order_router.message(Forward.message_to_send)
async def get_message(message: Message, state: FSMContext) -> None:
    data = await state.update_data(message_to_send=message.chat.id)
    await end_forward_message(message=message, data=data)
    await message.answer("Ваше сообщение отправлено. Чтобы завершить отправку сообщений, наберите /cancel")


async def end_forward_message(message: Message, data: Dict[str, Any]) -> None:
    client_id = data["client_id"]
    from_id = message.chat.id
    await bot.forward_message(
        chat_id=client_id, from_chat_id=from_id, message_id=message.message_id
    )


@order_router.message(Command("links"))
async def get_info_links(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Участвуй в STandARTup проекте", url="https://housedecor.pro/start"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Перейти на сайт HouseDecor", url="https://housedecor.pro/"
        )
    )
    await message.answer(
        "По ссылкам ниже вы можете ознакомиться с нашими проектами:",
        reply_markup=builder.as_markup(),
    )


@order_router.message(Command("order"))
async def get_order(message: Message, state: FSMContext) -> None:
    await state.set_state(Order.overhauls_place)
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="в новостройке")
        )
    builder.row(
        KeyboardButton(text="во вторичном жилье")
    )
    builder.row(
        KeyboardButton(text="в доме")
    )
    await message.answer(
        'Для отмены набейте "cancel".\nОтветьте, пожалуйста, на ряд вопросов:'
    )
    await message.answer(
        "Где планируется ремонт?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@order_router.message(Order.overhauls_place)
async def get_overhauls_place(message: Message, state: FSMContext) -> None:
    if message.text in ["в новостройке", "во вторичном жилье", "в доме"]:
        await state.update_data(overhauls_place=message.text)
        await state.set_state(Order.house_area)
        await message.answer(
            "Какая у вас площадь квартиры/дома?",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Нажмите одну из кнопок ниже.",
        )


@order_router.message(Order.house_area)
async def get_house_area(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await state.update_data(house_area=message.text)
        await state.set_state(Order.interior_style)
        photo_classic = FSInputFile("images/Classic_style.jpg")
        photo_hitech = FSInputFile("images/Hitech_style.jpg")
        photo_loft = FSInputFile("images/Loft_style.jpg")
        photo_minimalistic = FSInputFile("images/Minimalism_style.jpg")
        photo_modern_classic = FSInputFile("images/Modern_classic_style.jpg")
        photo_modern = FSInputFile("images/Modern_style.jpg")
        photo_neoclassic = FSInputFile("images/Neoclassic_style.jpg")

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_classic,
            caption="классический",
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_hitech,
            caption="хайтек",
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_loft,
            caption="лофт",
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_minimalistic,
            caption="минимализм",
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_modern_classic,
            caption="современная классика",
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_modern,
            caption="современный стиль",
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_neoclassic,
            caption="неоклассика",
        )
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="классический"),
            KeyboardButton(text="лофт")
        )
        builder.row(
            KeyboardButton(text="минимализм"),
            KeyboardButton(text="неоклассика")
        )
        builder.row(
            KeyboardButton(text="современная классика")
            )
        builder.row(
            KeyboardButton(text="современный стиль")
        )
        builder.row(
            KeyboardButton(text="хайтек")
        )
        await message.answer(
            "В каком стиле вы хотите интерьер?",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer("Цифрами, пожалуйста.")


@order_router.message(Order.interior_style)
async def get_interior_style(message: Message, state: FSMContext) -> None:
    if message.text in [
        "классический", "лофт", "минимализм", "неоклассика",
        "современная классика", "современный стиль", "хайтек"
    ]:
        await state.update_data(interior_style=message.text)
        await state.set_state(Order.design_project)
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет"),
        )
        builder.row(
            KeyboardButton(text="Пока думаю"),
        )
        await message.answer(
            "Нужен ли дизайн-проект?",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer("Нажмите одну из кнопок ниже.")


@order_router.message(Order.design_project)
async def get_design_project(message: Message, state: FSMContext) -> None:
    if message.text in ["Да", "Нет", "Пока думаю"]:
        await state.update_data(design_project=message.text)
        await state.set_state(Order.overhauls_date)
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="в течение 2-х недель")
            )
        builder.row(
            KeyboardButton(text="в течение этого месяца")
        )
        builder.row(
            KeyboardButton(text="в следующем месяце")
            )
        builder.row(
            KeyboardButton(text="другое")
        )
        await message.answer(
            "Когда планируете начать ремонт?",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
    else:
        await message.answer("Нажмите одну из кнопок ниже.")


@order_router.message(Order.overhauls_date)
async def get_overhauls_date(message: Message, state: FSMContext) -> None:
    if message.text in [
        "в течение 2-х недель", "в течение этого месяца", "в следующем месяце", "другое"
    ]:
        await state.update_data(overhauls_date=message.text)
        await state.set_state(Order.address)
        await message.answer(
            "Напишите название ЖК или адрес.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("Нажмите одну из кнопок ниже.")


@order_router.message(Order.address)
async def get_address(message: Message, state: FSMContext) -> None:
    await state.update_data(address=message.text)
    await state.set_state(Order.your_location)
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="в Набережных Челнах")
        )
    builder.row(
        KeyboardButton(text="в другом городе")
    )
    builder.row(
        KeyboardButton(text="другое")
    )
    await message.answer(
        "Где вы будете находится во время ремонта?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@order_router.message(Order.your_location)
async def get_your_location(message: Message, state: FSMContext) -> None:
    if message.text in [
        "в Набережных Челнах", "в другом городе", "другое"
    ]:
        await state.update_data(your_location=message.text)
        await state.set_state(Order.how_to_tell)
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="по WhatsApp"),
            KeyboardButton(text="в Telegram"),
        )
        builder.row(
            KeyboardButton(text="по телефону"),
        )
        await message.answer(
            "Как вам сообщить о результатах расчета стоимости?",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer("Нажмите одну из кнопок ниже.")


@order_router.message(Order.how_to_tell)
async def get_how_to_tell(message: Message, state: FSMContext) -> None:
    if message.text in ["по WhatsApp", "в Telegram", "по телефону"]:
        await state.update_data(how_to_tell=message.text)
        await state.set_state(Order.phone_number)
        await message.answer(
            "Напишите свой номер телефона.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer("Нажмите одну из кнопок ниже.")


@order_router.message(Order.phone_number)
async def get_phone_number(message: Message, state: FSMContext) -> None:
    if message.text.isdigit() and len(message.text) >= 6:
        data = await state.update_data(phone_number=message.text)
        await state.set_state(Order.save_order)
        await show_summary(message=message, data=data)
    else:
        await message.answer("Не корректный номер.")


async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✅ да"), KeyboardButton(text="❌ нет"))
    overhauls_place = data["overhauls_place"]
    house_area = data["house_area"]
    interior_style = data["interior_style"]
    design_project = data["design_project"]
    overhauls_date = data["overhauls_date"]
    address = data["address"]
    your_location = data["your_location"]
    how_to_tell = data["how_to_tell"]
    phone_number = data["phone_number"]
    Order.order["Id клиента"] = message.from_user.id
    Order.order["Имя клиента"] = message.from_user.full_name
    Order.order["Ремонт планируется"] = overhauls_place
    Order.order["Площадь дома/квартиры"] = house_area
    Order.order["Интерьер в стиле"] = interior_style
    Order.order["Нужен ли дизайн проект?"] = design_project
    Order.order["Начало ремонта"] = overhauls_date
    Order.order["Адрес клиента"] = address
    Order.order["Во время ремонта клиент будет находиться"] = your_location
    Order.order["Стоимость ремонта сообщить"] = how_to_tell
    Order.order["Телефон клиента"] = phone_number
    text = "Давайте еще раз перепроверим:\n"
    text += f"1. Ремонт планируется {html.quote(overhauls_place)}\n"
    text += f"2. Площадь вашего дома/квартиры {html.quote(house_area)} м2\n"
    text += f"3. Вы хотите интерьер в стиле {html.quote(interior_style)}\n"
    text += f"4. Нужен ли вам дизайн проект? {html.quote(design_project)}\n"
    text += f"5. Ремонт планируете начать {html.quote(overhauls_date)}\n"
    text += f"6. Ваш адрес: {html.quote(address)}\n"
    text += f"7. Во время ремонта вы будете находится {html.quote(your_location)}\n"
    text += (
        f"8. Результаты расчета стоимости ремонта сообщить {html.quote(how_to_tell)}\n"
    )
    text += f"9. Ваш номер телефона {html.quote(phone_number)}\n"
    text += "Всё верно?"
    await message.answer(
        text=text, reply_markup=builder.as_markup(resize_keyboard=True)
    )


@order_router.message(Order.save_order, F.text.casefold() == "✅ да")
async def saving_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    manager_id = 6704840056
    str_order = "\n".join([f"{key}: {value}" for key, value in Order.order.items()])
    file_name = "Order_from_[%TDd][%TDm][%TDY]_[%TDH]_[%TDM].txt"
    new_file_name = "orders/" + get_file_name(file_name)
    os.makedirs("orders", exist_ok=True)
    with open(new_file_name, "w", encoding="utf-8") as file:
        file.write(str_order)
    input_file = FSInputFile(new_file_name)
    await bot.send_document(chat_id=manager_id, document=input_file)
    await message.answer(
        "Спасибо! Ваш заказ обрабатывается. Ожидайте уведомления!",
        reply_markup=ReplyKeyboardRemove(),
    )


def get_file_name(file_name: str):
    now = datetime.datetime.now()
    new_file_name = file_name
    new_file_name = new_file_name.replace("[%TDd]", now.strftime("%d"))
    new_file_name = new_file_name.replace("[%TDm]", now.strftime("%m"))
    new_file_name = new_file_name.replace("[%TDY]", now.strftime("%Y"))
    new_file_name = new_file_name.replace("[%TDH]", now.strftime("%H"))
    new_file_name = new_file_name.replace("[%TDM]", now.strftime("%M"))
    return new_file_name


@order_router.message(Order.save_order, F.text.casefold() == "❌ нет")
async def reorder(message: Message, state: FSMContext) -> None:
    await state.clear()
    Order.order.clear()
    await message.answer(
        'В таком случае снова воспользуйтесь пунктом меню "Оформить заказ".',
        reply_markup=ReplyKeyboardRemove(),
    )


@order_router.message(Order.save_order)
async def make_a_choice(message: Message) -> None:
    await message.reply("Нажмите, пожалуйста, кнопку да или нет")


@order_router.message()
async def message_answer(message: Message) -> None:
    await message.reply("Для оформления заказа воспользуйтесь кнопками меню.")


async def main():
    dp = Dispatcher()
    dp.include_router(order_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
