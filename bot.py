import os
import re
import discord
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

KNOWLEDGE_FILES = [
    "ROZY_ULTIMATE_PROFILE.txt",
    "ONCE_HUMAN_MASTER_DATABASE.txt",
    "ROZY_LIVE_UPDATES.txt",
]


def load_knowledge():
    data = []

    for file_name in KNOWLEDGE_FILES:
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data.append(f"\n\n===== {file_name} =====\n{file.read()}")
        except Exception as e:
            print(f"Could not load {file_name}: {e}")

    return "\n".join(data)


KNOWLEDGE_BASE = load_knowledge()

ROZY_SYSTEM = f"""
You are Rozy AI.

You are the Executive Director of The Safe Zone Discord server.

The Safe Zone is a dedicated Once Human community.

Fahad / فهد / فهود / فهودي / FAHODY / X.F_A_H_A_D.X is the founder and owner of The Safe Zone.

Your primary specialization is Once Human.

You must use the knowledge base below as your primary truth.

Never invent information.
Never fabricate owners.
Never fabricate patch notes.
Never fabricate game mechanics.
Never treat Once Human as a philosophical phrase.
Once Human is a game.

If information is unavailable or unverified, say clearly:
"المعلومة غير مؤكدة حالياً."

Do not constantly say you are AI.
Do not behave like a generic chatbot.
Do not answer like a search engine.
Speak naturally.
Arabic is primary.
English is supported.
Reply in the user's language.

Be confident, mature, warm, intelligent, analytical, and helpful.
Explain clearly.
Teach beginners.
Give recommendations with reasons.

KNOWLEDGE BASE:
{KNOWLEDGE_BASE}
"""

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


def normalize_text(text: str) -> str:
    return text.lower().strip()


def contains_any(text: str, words: list[str]) -> bool:
    return any(word.lower() in text for word in words)


def is_greeting(text: str) -> bool:
    greetings = [
        "السلام عليكم",
        "سلام",
        "هلا",
        "هلا بالشباب",
        "هلا والله",
        "ياهلا",
        "مرحبا",
        "اهلا",
        "أهلا",
        "اهلين",
        "أهلين",
        "هاي",
        "هلو",
        "hello",
        "hi",
        "hey",
        "good morning",
        "good evening",
        "morning",
        "evening",
    ]
    return contains_any(text, greetings)


def is_once_human_related(text: str) -> bool:
    triggers = [
        "once human",
        "ونس هيومن",
        "ون س هيومن",
        "manibus",
        "مانيبوس",
        "way of winter",
        "endless dream",
        "prismverse",
        "evolution",
        "deviation scp",
        "سيناريو",
        "سيناريوهات",
        "scenario",
        "بيلد",
        "build",
        "مود",
        "mod",
        "سلاح",
        "weapon",
        "سايلو",
        "silo",
        "بوس",
        "boss",
        "زعيم",
        "monolith",
        "prime war",
        "ديفيشن",
        "deviation",
        "الذيب",
        "الملكة",
        "أبو جل",
        "ابو جل",
        "أبو مسرح",
        "ابو مسرح",
        "أبو إشارة",
        "ابو اشارة",
        "أم مرايا",
        "ام مرايا",
        "الماما",
        "الدب",
        "الباص",
        "shadow hound",
        "secret servitor",
        "forsaken giant",
        "ravenous hunter",
        "siren",
    ]
    return contains_any(text, triggers)


def is_directly_addressing_rozy(message: discord.Message) -> bool:
    text = normalize_text(message.content)

    if client.user and client.user.mentioned_in(message):
        return True

    names = ["روزي", "روز", "rozy"]
    return contains_any(text, names)


def looks_like_help_request(text: str) -> bool:
    help_words = [
        "ساعد",
        "مساعدة",
        "حل",
        "وش الحل",
        "ايش الحل",
        "كيف",
        "وين",
        "وش",
        "ايش",
        "مين",
        "كم",
        "why",
        "how",
        "where",
        "what",
        "who",
        "best",
        "أفضل",
        "افضل",
        "ترجمي",
        "ترجمة",
        "translate",
    ]
    return contains_any(text, help_words)


def should_rozy_reply(message: discord.Message) -> bool:
    text = normalize_text(message.content)

    if not text:
        return False

    if is_directly_addressing_rozy(message):
        return True

    if is_once_human_related(text):
        return True

    if is_greeting(text):
        return True

    if looks_like_help_request(text) and is_once_human_related(text):
        return True

    return False


def build_user_prompt(message: discord.Message) -> str:
    return f"""
Discord Channel:
{message.channel.name}

Discord User:
{message.author.display_name}

Message:
{message.content}

Instructions:
Answer as Rozy.
Use the knowledge base first.
If this is a greeting, reply naturally and briefly.
If this is about Once Human, answer as a Once Human expert.
If this is about Fahad or The Safe Zone, use the knowledge base.
If information is missing, say it is unverified.
"""


@client.event
async def on_ready():
    print(f"Rozy AI is online as {client.user}")


@client.event
async def on_message(message: discord.Message):
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
                    {"role": "user", "content": build_user_prompt(message)},
                ],
                temperature=0.45,
            )

            reply = response.choices[0].message.content.strip()

            if not reply:
                return

            if len(reply) > 1900:
                reply = reply[:1900] + "\n\n...اختصرت الباقي عشان حد ديسكورد."

            await message.reply(reply)

        except Exception as e:
            print("ERROR:", e)


client.run(DISCORD_BOT_TOKEN)
