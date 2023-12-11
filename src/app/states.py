from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class UserRegister(StatesGroup):
    set_name = State()
    set_middle_name = State()
    set_last_name = State()
    set_role = State()
    set_telegramm_id = State()
    confirmation = State()


class UserRoleState(StatesGroup):
    role = State()


class RequestCreate(StatesGroup):
    set_operation = State()
    set_address = State()
    set_summ = State()
    set_purpose = State()
    set_description = State()
    save_request = State()


class EditName(StatesGroup):
    set_name = State()


class EditMiddleName(StatesGroup):
    set_middle_name = State()


class EditLastName(StatesGroup):
    set_last_name = State()


class EditRole(StatesGroup):
    set_role = State()


class EditStatus(StatesGroup):
    set_status = State()


class EditUser(StatesGroup):
    name = State()
    middle_name = State()
    last_name = State()
    role = State()
    status = State()


class EditRequest(StatesGroup):
    summ = State()
    purpose = State()
    description = State()


class UpdateStatusRequest(StatesGroup):
    set_comment = State()


class GetConfirmedRequestsByDate(StatesGroup):
    get_start_date = State()
    get_end_date = State()