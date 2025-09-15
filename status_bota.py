
import time
from mcstatus import JavaServer

# --- Konfiguracja ---
# Zmień na adres IP i port swojego serwera.
# Jeśli serwer działa na tym samym komputerze, zostaw "localhost".
ADRES_SERWERA = "localhost:25565"
# Co ile sekund bot ma sprawdzać serwer?
CZAS_OCZEKIWANIA = 60

print(f"Bot statusu serwera uruchomiony.")
print(f"Sprawdzany serwer: {ADRES_SERWERA}")
print(f"Sprawdzanie co {CZAS_OCZEKIWANIA} sekund...")
print("---")

# --- Główna pętla bota ---
while True:
    try:
        # Łączenie z serwerem
        server = JavaServer.lookup(ADRES_SERWERA)
        # Sprawdzanie statusu
        status = server.status()
        
        # Jeśli się uda, wyświetl informację
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Serwer jest AKTYWNY.")
        print(f"  -> Gracze: {status.players.online}/{status.players.max}")
        print(f"  -> Ping: {status.latency:.2f} ms")

    except Exception as e:
        # Jeśli wystąpi błąd (np. serwer jest offline), wyświetl informację
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Serwer jest NIEDOSTĘPNY lub wystąpił błąd.")
        # print(f"  -> Błąd: {e}") # Odkomentuj, jeśli chcesz widzieć szczegóły błędu

    finally:
        # Poczekaj zdefiniowaną ilość czasu przed następnym sprawdzeniem
        time.sleep(CZAS_OCZEKIWANIA)
