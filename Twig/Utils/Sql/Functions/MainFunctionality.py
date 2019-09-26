import aiosqlite
import time

DEFAULT_DB_FILENAME = 'twig-and-xp'


# Коннектор базы данных
async def connect_sqlite(filename):
    return await aiosqlite.connect(f'./Twig/Utils/Sql/Data/{str(filename)}.sqlite')


# Инициализатор БД
async def init_sql():
    con = await aiosqlite.connect(f'./Twig/Utils/Sql/Data/{DEFAULT_DB_FILENAME}.sqlite')

    await con.execute("CREATE TABLE IF NOT EXISTS data(guild INTEGER, user INTEGER, xp INTEGER, lastTimeEdited INTEGER)")
    await con.commit()

    await con.close()
    return print(f'[CORE:SQL] Database Twig/SQL/db/{DEFAULT_DB_FILENAME}.sqlite initialized!')


# Добавить нового пользователя в таблицу
async def add_user(guild, user):
    called_at = int(time.time() - 300)
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute("INSERT INTO data VALUES({0}, {1}, {2}, {3})".format(guild, user, 0, called_at))
    await con.commit()

    await cur.close()
    return await con.close()


# Удаляет пользователя из таблицы
async def del_user(guild, user):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute("DELETE FROM data WHERE guild={0} AND user={1}".format(guild, user))
    await con.commit()

    await cur.close()
    await con.close()
    del con, cur


# Найти данные в таблице
async def fetch_data(guild, fetch_this, where_is, where_val):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)
    cur = await con.execute(
        "SELECT {1} FROM data where guild={0} AND {2}={3}".format(guild, fetch_this, where_is, where_val)
    )
    data = await cur.fetchall()
    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data
    del new_data
    await cur.close()
    await con.close()
    del con, cur
    # Если данных не существует в БД, то возвращается None
    if len(data) <= 0:
        del data
        return None
    else:
        return data[0]


# Обновление каких-либо параметров в БД
async def update_data(guild, update_this, update_to, where_is, where_val):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)
    cur = await con.execute(
        "UPDATE data SET {1}={2} WHERE {3}={4} AND guild={0}".format(guild, update_this, update_to, where_is, where_val)
    )
    await con.commit()

    await cur.close()
    await con.close()
    del con, cur


# Получит 5 пользователей, по возрастанию по очкам опыта
# Возвращает список вида ['user.id $$$ xp-balance']...
async def fetch_top5(guild):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute('SELECT user, xp FROM data WHERE guild={0} ORDER BY xp DESC LIMIT 5'.format(guild))
    data = await cur.fetchall()

    temp_data = []

    for elem in data:
        temp_data.append(str(elem[0]) + ' $$$ ' + str(elem[1]))

    data = temp_data

    await cur.close()
    await con.close()
    del con, cur, temp_data

    return data


# Получит всех пользователей, по возрастанию по очкам опыта
# Возвращает список вида ['user.id $$$ xp-balance']...
async def fetch_table():
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute("SELECT user FROM data LIMIT 1001")
    data = await cur.fetchall()

    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data

    await cur.close()
    await con.close()
    del new_data, con, cur
    return data
