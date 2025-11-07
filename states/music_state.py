from aiogram.fsm.state import State, StatesGroup


class MusicSearch(StatesGroup):
    active = State()
