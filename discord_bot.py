
import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
from mcstatus import JavaServer
from replit import db # <-- NOWOŚĆ: Import bazy danych Replit

# --- Konfiguracja ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- NOWOŚĆ: Dynamiczne wczytywanie adresu serwera z bazy danych ---
# Sprawdź, czy adres jest już w bazie danych, jeśli nie, użyj domyślnego
if "server_address" in db:
    ADRES_SERWERA_MC = db["server_address"]
else:
    # Domyślny adres, jeśli żaden nie został jeszcze ustawiony
    ADRES_SERWERA_MC = "wielkichujciwdupe.aternos.me:49760"
    db["server_address"] = ADRES_SERWERA_MC

ID_KANALU_DO_AKTUALIZACJI = 1234567890 # <-- Pamiętaj, aby wstawić tu poprawne ID kanału
MINUTY_AKTUALIZACJI = 5

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    print(f"Startowe monitorowanie serwera: {ADRES_SERWERA_MC}")
    if ID_KANALU_DO_AKTUALIZACJI != 0:
        update_channel_topic.start()
    print('---')

# --- NOWOŚĆ: Komenda do zmiany adresu serwera (tylko dla adminów) ---
@bot.slash_command(
    name="ustaw_serwer",
    description="Zmienia adres serwera Minecraft, który bot monitoruje.",
    default_member_permissions=discord.Permissions(administrator=True)
)
async def ustaw_serwer(ctx: discord.ApplicationContext, adres: str):
    global ADRES_SERWERA_MC
    db["server_address"] = adres
    ADRES_SERWERA_MC = adres
    await ctx.respond(f"✅ Adres serwera został pomyślnie zmieniony na: `{adres}`. Zmiany będą widoczne przy następnej aktualizacji.", ephemeral=True)

@bot.slash_command(name="status", description="Sprawdź status serwera Minecraft")
async def status(ctx: discord.ApplicationContext):
    await ctx.defer()
    try:
        server = await JavaServer.async_lookup(ADRES_SERWERA_MC)
        status = await server.async_status()
        embed = discord.Embed(title="✅ Status Serwera Minecraft", description=f"Serwer **{ADRES_SERWERA_MC}** jest **Online**!", color=discord.Color.green())
        embed.add_field(name="Gracze", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="Ping", value=f"{status.latency:.2f} ms", inline=True)
        embed.set_footer(text=f"Wersja: {status.version.name}")
        if status.players.online > 0 and status.players.sample is not None:
            player_names = ', '.join([player.name for player in status.players.sample])
            embed.add_field(name=f"Gracze online ({status.players.online}):", value=player_names, inline=False)
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="❌ Status Serwera Minecraft", description=f"Serwer **{ADRES_SERWERA_MC}** jest **Offline**.", color=discord.Color.red())
        await ctx.followup.send(embed=embed)

@tasks.loop(minutes=MINUTY_AKTUALIZACJI)
async def update_channel_topic():
    global ADRES_SERWERA_MC # Upewnij się, że pętla używa aktualnego adresu
    channel = bot.get_channel(ID_KANALU_DO_AKTUALIZACJI)
    try:
        server = await JavaServer.async_lookup(ADRES_SERWERA_MC)
        status = await server.async_status()
        # Aktualizacja tematu kanału
        if channel:
            new_topic = f"🟢 Online | Gracze: {status.players.online}/{status.players.max} | Ping: {status.latency:.0f}ms"
            await channel.edit(topic=new_topic)
        # --- NOWOŚĆ: Aktualizacja statusu bota ---
        activity = discord.Game(name=f"Minecraft z {status.players.online} graczami")
        await bot.change_presence(status=discord.Status.online, activity=activity)
    except Exception:
        # Aktualizacja tematu kanału
        if channel:
            new_topic = f"🔴 Offline | Ostatnie sprawdzenie: {discord.utils.utcnow().strftime('%H:%M:%S')}"
            await channel.edit(topic=new_topic)
        # --- NOWOŚĆ: Aktualizacja statusu bota ---
        activity = discord.Activity(type=discord.ActivityType.watching, name="serwer offline")
        await bot.change_presence(status=discord.Status.idle, activity=activity)

if TOKEN is None:
    print("BŁĄD: Nie znaleziono tokenu bota.")
else:
    bot.run(TOKEN)
