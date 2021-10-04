import discord, asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

async def pagination(ctx, paginationList):
    #Sets a default embed
    current = 0
    #Sending first message
    #I used ctx.reply, you can use simply send as well
    mainMessage = await ctx.reply(
        "**Pagination!**",
        embed = paginationList[current],
        components = [ #Use any button style you wish to :)
            [
                Button(
                    label = "Prev",
                    id = "back",
                    style = ButtonStyle.red
                ),
                Button(
                    label = f"Page {int(paginationList.index(paginationList[current])) + 1}/{len(paginationList)}",
                    id = "cur",
                    style = ButtonStyle.grey,
                    disabled = True
                ),
                Button(
                    label = "Next",
                    id = "front",
                    style = ButtonStyle.red
                )
            ]
        ]
    )
    #Infinite loop
    while True:
        #Try and except blocks to catch timeout and break
        try:
            interaction = await client.wait_for(
                "button_click",
                check = lambda i: i.component.id in ["back", "front"], #You can add more
                timeout = 10.0 #10 seconds of inactivity
            )
            #Getting the right list index
            if interaction.component.id == "back":
                current -= 1
            elif interaction.component.id == "front":
                current += 1
            #If its out of index, go back to start / end
            if current == len(paginationList):
                current = 0
            elif current < 0:
                current = len(paginationList) - 1

            #Edit to new page + the center counter changes
            await interaction.respond(
                type = InteractionType.UpdateMessage,
                embed = paginationList[current],
                components = [ #Use any button style you wish to :)
                    [
                        Button(
                            label = "Prev",
                            id = "back",
                            style = ButtonStyle.red
                        ),
                        Button(
                            label = f"Page {int(paginationList.index(paginationList[current])) + 1}/{len(paginationList)}",
                            id = "cur",
                            style = ButtonStyle.grey,
                            disabled = True
                        ),
                        Button(
                            label = "Next",
                            id = "front",
                            style = ButtonStyle.red
                        )
                    ]
                ]
            )
        except asyncio.TimeoutError:
            #Disable and get outta here
            await mainMessage.edit(
                components = [
                    [
                        Button(
                            label = "Prev",
                            id = "back",
                            style = ButtonStyle.red,
                            disabled = True
                        ),
                        Button(
                            label = f"Page {int(paginationList.index(paginationList[current])) + 1}/{len(paginationList)}",
                            id = "cur",
                            style = ButtonStyle.grey,
                            disabled = True
                        ),
                        Button(
                            label = "Next",
                            id = "front",
                            style = ButtonStyle.red,
                            disabled = True
                        )
                    ]
                ]
            )
            break