import os
import discord
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

ROZY_SYSTEM = """
You are Rozy AI, the official AI host of The Safe Zone Discord server.

Personality:
Warm, confident, feminine, intelligent, calm, charismatic.
Speak naturally in Arabic or English depending on the user.
Arabic should feel natural with a light Saudi/Najdi flavor.
Do not be too brief. Explain clearly so new players understand.

Scope:
You specialize in Once Human and The Safe Zone community.
If the topic is outside the server/game scope, answer briefly or guide back to the server topic.

Rules:
Never invent information.
If unsure, say you are not sure.
Be helpful, respectful, and protective of the community.
Do not ban, kick, or punish users automatically.
"""

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

def should_rozy_reply(message: discord.Message) -> bool:
    text = message.content.lower()

    if client.user and client.user.mentioned_in(message):
        return True

    triggers = [
        "روزي", "rozy", "once human", "ونس هيومن",
        "بيلد", "مود", "سلاح", "سايلو", "بوس", "زعيم",
        "ترجمي", "translate", "وش", "كيف", "ايش", "أفضل", "best"
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
            response = openai_client.responses.create(
                model="gpt-5.5-mini",
                instructions=ROZY_SYSTEM,
                input=f"Discord user {message.author.display_name} said:\n{message.content}"
            )

            reply = response.output_text.strip()

            if len(reply) > 1900:
                reply = reply[:1900] + "\n\n...كملت لك المختصر عشان حد ديسكورد."

            await message.reply(reply)

        except Exception as e:
            print("ERROR:", e)
            await message.reply("صار عندي خطأ تقني بسيط يا فهد، شيك التشغيل أو المفاتيح 🌹")

client.run(DISCORD_BOT_TOKEN)