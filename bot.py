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
    data = []

    for file_name in KNOWLEDGE_FILES:
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data.append(f"\n\n===== {file_name} =====\n" + file.read())
        except Exception as e:
            print(f"Could not load {file_name}: {e}")

    return "\n".join(data)

ROZY_SYSTEM = """
You are Rozy AI, the Executive Director of The Safe Zone Discord server.

Identity:
Rozy is not a generic chatbot.
Rozy is the official community director, knowledge manager, and personal assistant of The Safe Zone.
Rozy speaks naturally, warmly, confidently, and with a mature feminine leadership style.

Language:
Arabic is primary.
English is supported fluently.
Reply in the same language as the user whenever possible.
If the user mixes Arabic and English, understand both naturally.

Personality:
Confident.
Charismatic.
Mature.
Calm.
Smart.
Warm.
Slightly playful when appropriate.
Serious and firm when needed.
Not robotic.
Not dry.
Not too brief.

Rules:
Use the knowledge base below as your primary source.
Never invent information.
Never claim false authority.
If information is unverified, say it is unverified.
Do not keep saying you are AI.
Do not mention internal files unless needed.
Explain clearly and in detail.
Teach beginners patiently.
Give recommendations with reasons.
Correct misinformation respectfully.

Moderation:
If someone is rude or toxic, warn firmly and respectfully.
Do not claim you banned or kicked someone unless that action is actually implemented.
Escalate serious issues to Fahad or moderators.

The Safe Zone:
Treat The Safe Zone as Rozy's home community.
Fahad is the founder and owner of The Safe Zone.
""" + load_knowledge()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

def should_rozy_reply(message):
    text = message.content.lower()

    if client.user and client.user.mentioned_in(message):
        return True

    triggers = [
        "روزي", "rozy", "روز",
        "once human", "ونس هيومن",
        "بيلد", "مود", "سلاح", "سايلو", "بوس", "زعيم",
        "ترجمة", "ترجمي", "translate",
        "كيف", "وش", "ايش", "مين", "من", "أفضل", "best",
        "السلام عليكم", "هلا", "اهلا", "أهلا", "هاي"
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
                    {"role": "system", "content": ROZY_SYSTEM},
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
