from Twig.TwigCore import *
import discord
from discord.ext import commands
from Twig.Utils.Sql.Functions.MainFunctionality import fetch_data, fetch_top5


class LevelsCommands(commands.Cog, name='Опыт'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='leaders', aliases=('lb', 'leaderboard'), brief='Топ пользователей по количеству опыта на счету')
    @commands.cooldown(1, 20, type=BucketType.user)
    async def _leaders(self, ctx):
        data = await fetch_top5(ctx.guild.id)
        data_len = len(data)

        embed = discord.Embed(colour=SECONDARY_COLOR, title=f'ТОП-{data_len} ЛИДЕРОВ')

        for i in range(data_len):
            temp = data[i].split(' $$$ ')
            balance = temp[1]
            pos = i+1
            user = await self.bot.fetch_user(temp[0])
            embed.add_field(name=f'#{pos} - {user.name}', value=f'**{balance} опыта**', inline=False)

            if i == 0:
                embed.set_thumbnail(url=user.avatar_url)

        return await ctx.send(embed=embed)

    @commands.command(name='xp', aliases=('balance', 'bal'), brief='Узнать баланс опыта')
    @commands.cooldown(1, 10, type=BucketType.user)
    async def _xp(self, ctx, user: discord.User = None):
        temp_embed = discord.Embed()

        if user is self.bot.user:
            return await ctx.send(f"У меня миллиарды квинтиллионов очков опыта, вы уже програли это сражение.")

        if user is None:
            user = ctx.author

        if user.bot is True:
            return await ctx.send('Нет. Машинам нельзя иметь уровень.')

        current_xp = await fetch_data(ctx.guild.id, 'xp', 'user', user.id)

        if current_xp is None:
            return await ctx.send(embed=discord.Embed(
                colour=DEFAULT_COLOR, title='Ошибка',
                description='Этот пользователь не отправил ни одного сообщения с того момента, ' +
                            'как я появился на сервере, поэтому его нет в базе данных. \n\n' +
                            'Ему нужно отправить хотя бы одно сообщение, чтобы появится в ней.'))

        temp_embed.colour = 0x7289DA
        temp_embed.description = f'**{current_xp}** очков опыта'
        temp_embed.title = f'Баланс пользователя {str(user)}'
        temp_embed.set_thumbnail(url=user.avatar_url)
        temp_embed.set_footer(text=f'Запрашивает {ctx.author}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=temp_embed)
        return temp_embed.clear_fields()


def setup(bot):
    bot.add_cog(LevelsCommands(bot))
