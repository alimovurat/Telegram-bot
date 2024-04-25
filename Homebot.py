import asyncio
import logging
import sys

from aiogram import Dispatcher, F, Router
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
    CallbackQuery
)
from settings import bot2

order_router = Router()


class Calculate(StatesGroup):
    house_area = State()
    rooms_number = State()
    user_choices = State()
    services = []


@order_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет {hbold(message.from_user.full_name)}!\nЯ Чат-бот!\n"
        "Для расчета стоимости приемки квартиры воспользуйтесь кнопкой меню.",
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


@order_router.message(Command("calculate"))
async def calculate(message: Message, state: FSMContext) -> None:
    await state.set_state(Calculate.house_area)
    await message.answer(
        'Для отмены набейте "cancel".\nПлощадь квартиры?',
        reply_markup=ReplyKeyboardRemove(),
    )


@order_router.message(Calculate.house_area)
async def get_house_area(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await state.update_data(house_area=message.text)
        await state.set_state(Calculate.rooms_number)
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="1"),
            KeyboardButton(text="2"),
        )
        builder.row(
            KeyboardButton(text="3"),
            KeyboardButton(text="4"),
        )
        builder.row(
            KeyboardButton(text="Студия")
        )
        await message.answer(
            'Кол-во комнат?',
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer("Введите числовое значение")


@order_router.message(Calculate.rooms_number)
async def get_rooms_number(message: Message, state: FSMContext) -> None:
    if message.text in ['1', '2', '3', '4', 'Студия']:
        await state.update_data(rooms_number=message.text)
        await state.set_state(Calculate.user_choices)
        keyboard = buttons('Проверка площади ❌', 'area_check')
        await message.answer(
                            'Выберите дополнительные услуги:\n'
                            'Замер фактической площади квартиры. Выполняется от руки на бланке компании.',
                            reply_markup=keyboard.as_markup()
                            )
        keyboard = buttons('Оценка для банка ❌', 'bank_evaluation')
        await message.answer('Оценка квартиры для банка при ипотеке. Работаем со всеми банками',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('Тепловизионный осмотр ❌', 'thermal_imaging_inspection')
        await message.answer('Проверка монтажных швов оконных блоков и фасадных стен на промерзание',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('План квартиры в AutoCAD ❌', 'apartment_plan')
        await message.answer('Подробный план квартиры с указанием размеров всех стен и высот',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('Экспертиза ремонта ❌', 'repair_examination')
        await message.answer('Строительная экспертиза качества ремонтных работ для суда. Бесплатно при заказе юридических услуг.',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('Юридическое взыскание ❌', 'legal_penalty')
        await message.answer('Взыскание компенсации с застройщика за некачественный ремонт и нарушение сроков сдачи',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('Замер радиации ❌', 'radiation_measurement')
        await message.answer('Измерение уровня радиационного фона в помещениях квартиры',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('Тепловизионный отчет ❌', 'thermal_imaging_report')
        await message.answer('Отчет с термограммами и фотографиями промерзаний с приложением сертификатов',
                            reply_markup=keyboard.as_markup())
        keyboard = buttons('Выезд специалиста НОПРИЗ или НОСТРОЙ ❌', 'specialist_visit')
        await message.answer('Приемка квартиры специалистом из реестра НОПРИЗ или НОСТРОЙ, с предоставлением застройщику документов из реестра и СРО компании.',
                            reply_markup=keyboard.as_markup())
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="продолжить"),
        )
        await message.answer('Нажмите "продолжить" для рассчета стоимости.', reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.answer("Нажмите одну из кнопок ниже.")


def buttons(button_text, button_callback_data):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=button_text, callback_data=button_callback_data))
    return keyboard


@order_router.callback_query(lambda query: query.data in ['area_check', 'bank_evaluation', 'thermal_imaging_inspection', 'apartment_plan', 'repair_examination', 'legal_penalty', 'radiation_measurement', 'thermal_imaging_report', 'specialist_visit'])
async def button_callback(query: CallbackQuery, state: FSMContext):
    button_data = query.data
    current_text = query.message.reply_markup.inline_keyboard
    for row in current_text:
        for button in row:
            if button.callback_data == button_data:
                if button.text.endswith('❌'):
                    button.text = button.text[:-1] + '✅'
                    if button.text not in Calculate.services and button.text.endswith('❌') is False:
                        Calculate.services.append(button.text)
                else:
                    if button.text in Calculate.services:
                        Calculate.services.remove(button.text)
                        button.text = button.text[:-1] + '❌'
    await query.message.edit_reply_markup(reply_markup=query.message.reply_markup)


@order_router.message(Calculate.user_choices)
async def cost_calculation(message: Message, state: FSMContext) -> None:
    if len(Calculate.services) != 0:
        await message.answer('Вы выбрали следующие услуги:')
        await message.answer('\n'.join(Calculate.services))   
    data = await state.get_data()
    house_area = int(data.get('house_area'))
    rooms_number = data.get('rooms_number')
    service_cost = await calculations(house_area, rooms_number, Calculate.services)
    await state.clear()
    Calculate.services.clear()
    await message.answer(f'Стоимость приемки квартиры составляет: {service_cost} руб.', reply_markup=ReplyKeyboardRemove())


async def calculations(house_area, rooms_number, services) -> None:
    services_cost = house_area * 80
    for service in services:
        if service == 'Проверка площади ✅':
            if rooms_number == 'Студия':
                services_cost += 200
            elif rooms_number == '1':
                services_cost += 300
            elif rooms_number == '2':
                services_cost += 400
            elif rooms_number == '3':
                services_cost += 500
            else:
                services_cost += 600
        elif service == 'Оценка для банка ✅':
            services_cost += 3500
        elif service == 'Тепловизионный осмотр ✅':
            if rooms_number == 'Студия':
                services_cost += 1000
            elif rooms_number == '1':
                services_cost += 1500
            elif rooms_number == '2':
                services_cost += 2000
            elif rooms_number == '3':
                services_cost += 2500
            else:
                services_cost += 3000
        elif service == 'План квартиры в AutoCAD ✅':
            if rooms_number == 'Студия':
                services_cost += 2500
            elif rooms_number == '1':
                services_cost += 3000
            elif rooms_number == '2':
                services_cost += 3500
            elif rooms_number == '3':
                services_cost += 4000
            else:
                services_cost += 5000
        elif service == 'Замер радиации ✅':
            services_cost += 500
        elif service == 'Тепловизионный отчет ✅':
            services_cost += 1500
        elif service == 'Выезд специалиста НОПРИЗ или НОСТРОЙ ✅':
            services_cost += 40 * house_area
    return services_cost


@order_router.message()
async def message_answer(message: Message) -> None:
    await message.reply("Чтобы произвести расчет стоимости приемки квартиры воспользуйтесь кнопкой меню.")


async def main():
    dp = Dispatcher()
    dp.include_router(order_router)
    await dp.start_polling(bot2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
