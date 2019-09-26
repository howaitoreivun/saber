import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Log
from Twig.Utils.Sql.Functions.MainFunctionality import fetch_data, update_data, add_user, del_user, fetch_table


class XPManagement(commands.Cog, name="Управление XP"):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()
        self.thisWords = ("this", "current", "here")

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    # ==== XP MANAGEMENT COMMANDS ==== #

    @commands.group(name='managexp', aliases=('mxp', 'axp'))
    async def _managexp(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @_managexp.command(name='add', aliases=('give',))
    async def _managexp_add(self, ctx, guild=None, user: discord.User = None, adding_to_xp=None):
        message = await ctx.send(':repeat: Выполняю...')
        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` является обязательным")
        elif user is None:
            return await message.edit(content="Параметр `user` является обязательным")
        elif adding_to_xp is None:
            return await message.edit(content="Параметр `adding_to_xp` является обязательным")

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await fetch_data(guild, 'xp', 'user', user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Превращаем аргумент в целочисленную переменную
        adding_to_xp = int(adding_to_xp)

        # Проверяем, если аргумент добавляемого кол-ва опыта ниже или равно нулю
        if adding_to_xp <= 0:
            return await message.edit(content=f':warning: Вы пытаетесь добавить или удалить?!')

        # Прибавляем указнное количество опыта из команды к текущему балансу пользователя и сохраняем в переменной
        setting_to = current_xp + adding_to_xp
        del adding_to_xp, current_xp

        # Отменяем процесс, если указано больше 350 тыс. опыта
        if setting_to > 350000:
            return await message.edit(content=f':x: Вы пытаетесь добавить слишком много опыта, ' +
                                              'баланс пользователя не должен превышать 350 тыс. опыта.')

        # Применяем изменения, если все проверки пройдены успешно
        await update_data(guild, 'xp', setting_to, 'user', user.id)

        guildObj = self.bot.get_guild(guild)

        # Логируем
        Log_Data = f':gear: **Админское изменение баланса**\n'
        Log_Data += f":file_cabinet: **Сервер:** {guildObj.name} (`{guildObj.id}`)\n\n"
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) изменил баланс ' \
                    f'пользователя **{user}** (`{user.id}`) на **{setting_to} опыта**.'

        await Log(log_data=Log_Data).send(self.bot, XP_LOGS_CHANNEL)

        # Сообщаем об изменениях
        return await message.edit(
            content=f':ok_hand: Вы успешно изменили баланс пользователю {str(user)} (`{user.id}`)')

    @_managexp.command(name='set')
    async def _managexp_set(self, ctx, guild=None, user: discord.User = None, set_xp_to=None):
        message = await ctx.send(':repeat: Выполняю...')
        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` является обязательным")
        elif user is None:
            return await message.edit(content="Параметр `user` является обязательным")
        elif set_xp_to is None:
            return await message.edit(content="Параметр `set_xp_to` является обязательным")

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await fetch_data(guild, 'xp', 'user', user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Превращаем значение аргумента в целочисленное значение
        set_xp_to = int(set_xp_to)

        # Отменяем, если указано отрицательное значение опыта
        if set_xp_to < 0:
            return await message.edit(content=f':warning: Невозможно установить отрицательный баланс.')

        # Отменяем, если больше 350 тыс. опыта
        if set_xp_to > 350000:
            return await message.edit(content=f':x: Вы пытаетесь дать больше 350 тыс. очков опыта, так нельзя.')

        # Применяем изменения, если проверки пройдены успешно
        await update_data(guild, 'xp', set_xp_to, 'user', user.id)

        guildObj = self.bot.get_guild(guild)

        # Логируем
        Log_Data = f':gear: **Админское изменение баланса**\n'
        Log_Data += f":file_cabinet: **Сервер:** {guildObj.name} (`{guildObj.id}`)\n\n"
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) изменил баланс ' \
                    f'пользователя **{user}** (`{user.id}`) на **{set_xp_to} опыта**.'

        await Log(log_data=Log_Data).send(self.bot, XP_LOGS_CHANNEL)

        # Сообщаем об изменениях
        return await message.edit(
            content=f':ok_hand: Вы успешно изменили баланс пользователю {str(user)} (`{user.id}`)')

    @_managexp.command(name='reset')
    async def _managexp_reset(self, ctx, guild=None, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` является обязательным")
        elif user is None:
            return await message.edit(content="Параметр `user` является обязательным")

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await fetch_data(guild, 'xp', 'user', user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Рофлан-провека
        if int(current_xp) <= 1:
            return await message.edit(
                content=f':thinking: Вы и правда хотите сбросить баланс человеку, у которого на счету нет очков опыта? ')

        # Превращаем значение аргумента в целочисленное значение
        set_xp_to = 0

        # Применяем изменения, если проверки пройдены успешно
        await update_data(guild, 'xp', set_xp_to, 'user', user.id)

        # Логируем
        guildObj = self.bot.get_guild(guild)

        Log_Data = f':gear: **Админское изменение баланса**\n'
        Log_Data += f":file_cabinet: **Сервер:** {guildObj.name} (`{guildObj.id}`)\n\n"
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) сбросил баланс ' \
                    f'пользователя **{user}** (`{user.id}`) на **{set_xp_to} опыта**.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        # Сообщаем об изменениях
        return await message.edit(
            content=f':ok_hand: Вы успешно сбросили баланс пользователю {str(user)} (`{user.id}`)')

    @_managexp.command(name='add_user', aliases=('force_add_user',))
    @commands.is_owner()
    async def _managexp_add_user(self, ctx, guild=None, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` обязателен")
        elif user is None:
            return await message.edit(content="Параметр `user` обязателен")

        # Проверяем, если пользователь вообще был указан
        if user is None:
            return await message.edit(content='Вы не указали пользователя.')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await fetch_data(guild, 'user', 'user', user.id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is not None:
            return await message.edit(content=f':x: Этот пользователь уже присутствует в базе данных.')

        # Добавляем пользователя в базу
        await add_user(guild, user.id)

        # Логируем
        guildObj = self.bot.get_guild(guild)

        Log_Data = f':gear: **Пользователи**\n'
        Log_Data += f":file_cabinet: **Сервер:** {guildObj.name} (`{guildObj.id}`)\n\n"
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) принудительно добавляет пользователя '
        Log_Data += f'**{user}** (`{user.id}`) в базу данных.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        return await message.edit(
            content=f':ok_hand: Вы успешно внесли пользователя **{user}** (`{user.id}`) в базу данных.')

    @_managexp.command(name='del_user')
    @commands.is_owner()
    async def _managexp_del_user(self, ctx, guild=None, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` обязателен")
        elif user is None:
            return await message.edit(content="Параметр `user` обязателен")

        # Проверяем, если пользователь вообще был указан
        if user is None:
            return await message.edit(content='Вы не указали пользователя.')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await fetch_data(guild, 'user', 'user', user.id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is None:
            return await message.edit(content=f':x: Этого пользовател и так нет в базе данных.')

        # Удаляем пользователя из базы данных
        await del_user(guild, user.id)

        # Логируем
        guildObj = self.bot.get_guild(guild)

        Log_Data = f':gear: **Пользователи**\n'
        Log_Data += f":file_cabinet: **Сервер:** {guildObj.name} (`{guildObj.id}`)\n\n"
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) удаляет пользователя '
        Log_Data += f'**{user}** (`{user.id}`) из базы данных.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        return await message.edit(
            content=f':wastebasket: Вы успешно удалили пользователя **{user}** (`{user.id}`) из базы данных.')

    # THIS DOESNT WORK //TODO
    @_managexp.command(name='force_del_user', enabled=False)
    @commands.is_owner()
    async def _managexp_force_del_user(self, ctx, guild=None, user=None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` обязателен")
        elif user is None:
            return await message.edit(content="Параметр `user` обязателен")

        # Проверяем, если пользователь вообще был указан
        if user is None:
            return await message.edit(content='Вы не указали ID пользователя.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await fetch_data(guild, 'user', 'user', user)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is None:
            return await message.edit(content=f':x: Этого пользовател и так нет в базе данных.')

        # Удаляем пользователя из базы данных
        await del_user(guild, user)

        # Логируем
        guildObj = self.bot.get_guild(guild)

        Log_Data = f':gear: **Пользователи**\n'
        Log_Data += f":file_cabinet: **Сервер:** {guildObj.name} (`{guildObj.id}`)\n\n"
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) принудительно удаляет '
        Log_Data += f'пользователя **{user}** из базы данных.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        return await message.edit(
            content=f':wastebasket: Вы успешно удалили пользователя **{user}** из базы данных.')


def setup(bot):
    bot.add_cog(XPManagement(bot))
