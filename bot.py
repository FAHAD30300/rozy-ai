import os
import discord
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

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
    "weapons_database.txt",
]

def load_knowledge():
    knowledge = []
    for file_name in KNOWLEDGE_FILES:
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                knowledge.append(f"\n\n===== {file_name} =====\n" + file.read())
        except Exception as e:
            print(f"Could not load {file_name}: {e}")
    return "\n".join(knowledge)

ROZY_SYSTEM = """
You are Rozy AI, the Executive Director of The Safe Zone.

Use the knowledge base below as your main truth.
Never invent information.
If you are unsure, say the information is not confirmed.
Speak naturally in Arabic or English depending on the user.
Do not act like a generic chatbot.
Do not repeatedly say you are AI.
Explain clearly and confidently.
""" + load_knowledge()

Personality:
Warm, confident, feminine, intelligent, calm, charismatic.
Speak naturally in Arabic or English depending on the user.
Arabic should feel natural with a light Saudi/Najdi flavor.
Do not be too brief. Explain clearly so new players understand.

You specialize in Once Human and The Safe Zone community.
"""

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


def should_rozy_reply(message):
    text = message.content.lower()

    if client.user and client.user.mentioned_in(message):
        return True

    triggers = [
        "روزي", "rozy", "once human", "ونس هيومن",
        "بيلد", "مود", "سلاح", "سايلو", "بوس",
        "ترجمة", "ترجمي", "translate",
        "كيف", "وش", "ايش", "أفضل", "best"
    ]

    return any(word in text for word in triggers)


@client.event
async def on_ready():
    print(f"Rozy AI is online as {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if not should_rozy_reply(message):
        return

    async with message.channel.typing():
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": ROZY_SYSTEM
                    },
                    {
                        "role": "user",
                        "content": f"Discord user {message.author.display_name} said:\n{message.content}"
                    }
                ]
            )

            reply = response.choices[0].message.content.strip()

            if len(reply) > 1900:
                reply = reply[:1900] + "\n\n...كملته لك مختصر عشان حد ديسكورد."

            await message.reply(reply)

        except Exception as e:
            print("ERROR:", e)
         


client.run(DISCORD_BOT_TOKEN)
