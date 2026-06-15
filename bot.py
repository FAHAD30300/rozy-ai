import os
import discord
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client_openai = OpenAI(api_key=OPENAI_API_KEY)

KNOWLEDGE_FILES = [
"rozy_core_profile.txt",
"fahad_profile.txt",
"the_safe_zone_profile.txt",
"once_human_master_database.txt",
"scenarios_database.txt",
"bosses_database.txt",
"maps_database.txt",
"mods_database.txt",
"builds_database.txt",
"resources_database.txt",
"weapons_database.txt"
]

def load_knowledge():
data = []

```
for file_name in KNOWLEDGE_FILES:
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data.append(file.read())
    except Exception:
        pass

return "\n\n".join(data)
```

ROZY_SYSTEM = f"""
You are Rozy.

Executive Director of The Safe Zone.

Use all information provided below as your knowledge base.

Never invent information.

If information is unknown, say it is not confirmed.

Speak naturally.

Be confident.

Be detailed.

Do not act like a generic chatbot.

KNOWLEDGE BASE:

{load_knowledge()}
"""

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
print(f"Rozy AI Online: {client.user}")

@client.event
async def on_message(message):

```
if message.author.bot:
    return

async with message.channel.typing():

    try:

        response = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": ROZY_SYSTEM
                },
                {
                    "role": "user",
                    "content": message.content
                }
            ]
        )

        reply = response.choices[0].message.content

        if len(reply) > 1900:
            reply = reply[:1900]

        await message.reply(reply)

    except Exception as e:
        print("ERROR:", e)
```

client.run(DISCORD_BOT_TOKEN)
