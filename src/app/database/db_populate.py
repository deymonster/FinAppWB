# # db_populate.py
#
# from app.database.models import engine, async_session
# from app.database.models import async_session, UserRole, OperationType, Address
# from config import ROLES, OPERATION_TYPE, ADDRESSES
#
#
# async def populate_tables():
#     async with engine.begin() as conn:
#         session = async_session()
#
#         for role_name in ROLES:
#             role = UserRole(name=role_name)
#             session.add(role)
#
#         for operation_name in OPERATION_TYPE:
#             operation_type = OperationType(name=operation_name)
#             session.add(operation_type)
#
#         for address in ADDRESSES:
#             address = Address(name=address)
#             session.add(address)
#
#         await session.commit()
