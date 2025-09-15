import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
from mcstatus import JavaServer

# --- Konfiguracja ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Adres serwera Minecraft
ADRES_SERWERA_MC = "wielkichujciwdupe.aternos.me:49760"

# ID kanału, którego TEMAT będzie automatycznie aktualizowany.
# Włącz tryb dewelopera w Discord, kliknij PPM na kanał i "Kopiuj ID kanału".
ID_KANALU_DO_AKTUALIZACJI = 1417131479992897536 # <-- WAŻNE: Wklej tutaj ID swojego kanału!

# Co ile minut aktualizować temat kanału?
MINUTY_AKTUALIZACJI = 1

# Ustawienie uprawnień bota (Intents)
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    """Wykonywane, gdy bot pomyślnie połączy się z Discordem."""
    print(f'Zalogowano jako {bot.user}')
    if ID_KANALU_DO_AKTUALIZACJI == 0:
        print("[OSTRZEŻENIE] ID_KANALU_DO_AKTUALIZACJI nie jest ustawione. Automatyczna aktualizacja tematu kanału jest wyłączona.")
    else:
        print(f"Automatyczna aktualizacja tematu kanału co {MINUTY_AKTUALIZACJI} min. na kanale o ID: {ID_KANALU_DO_AKTUALIZACJI}")
        update_channel_topic.start()
    print('---')

@bot.slash_command(name="status", description="Sprawdź status serwera Minecraft")
async def status(ctx: discord.ApplicationContext):
    """Komenda do sprawdzania statusu serwera Minecraft."""
    await ctx.defer()

    try:
        server = await JavaServer.async_lookup(ADRES_SERWERA_MC)
        status = await server.async_status()

        embed = discord.Embed(
            title="✅ Status Serwera Minecraft",
            description=f"Serwer **{ADRES_SERWERA_MC}** jest **Online**!",
            color=discord.Color.green()
        )
        embed.add_field(name="Gracze", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="Ping", value=f"{status.latency:.2f} ms", inline=True)
        embed.set_footer(text=f"Wersja: {status.version.name}")

        # --- NOWOŚĆ: Lista graczy ---
        if status.players.online > 0 and status.players.sample is not None:
            player_names = ', '.join([player.name for player in status.players.sample])
            embed.add_field(name=f"Gracze online ({status.players.online}):", value=player_names, inline=False)

        await ctx.followup.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Status Serwera Minecraft",
            description=f"Serwer **{ADRES_SERWERA_MC}** jest **Offline** lub nie odpowiada.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Upewnij się, że serwer jest włączony i adres jest poprawny.")
        print(f"[DIAGNOSTYKA] Wystąpił błąd podczas sprawdzania statusu: {e}")
        await ctx.followup.send(embed=embed)

# --- NOWOŚĆ: Pętla do automatycznej aktualizacji tematu kanału ---
@tasks.loop(minutes=MINUTY_AKTUALIZACJI)
async def update_channel_topic():
    channel = bot.get_channel(ID_KANALU_DO_AKTUALIZACJI)
    if not channel:
        print(f"[BŁĄD] Nie mogłem znaleźć kanału o ID {ID_KANALU_DO_AKTUALIZACJI}. Upewnij się, że ID jest poprawne i bot ma dostęp do tego kanału.")
        return

    try:
        server = await JavaServer.async_lookup(ADRES_SERWERA_MC)
        status = await server.async_status()
        new_topic = f"🟢 Online | Gracze: {status.players.online}/{status.players.max} | Ping: {status.latency:.0f}ms"
        await channel.edit(topic=new_topic)
    except Exception:
        new_topic = f"🔴 Offline | Ostatnie sprawdzenie: {discord.utils.utcnow().strftime('%H:%M:%S')}"
        await channel.edit(topic=new_topic)

# Uruchomienie bota
if TOKEN is None:
    print("BŁĄD: Nie znaleziono tokenu bota w pliku .env.")
else:
    bot.run(TOKEN)