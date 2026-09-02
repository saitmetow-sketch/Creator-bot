from aiogram.fsm.state import State, StatesGroup

class BotCreationStates(StatesGroup):
    waiting_for_token = State()
    choosing_bot_for_referral_day = State()

class AdminStates(StatesGroup):
    waiting_for_admin_id = State()
    waiting_for_mand_channel_id = State()
    waiting_for_mand_channel_link = State()
    waiting_for_mand_channel_username = State()
    waiting_for_req_channel_id = State()
    waiting_for_req_channel_link = State()
    waiting_for_broadcast_message = State()

