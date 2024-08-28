import discord
from discord.ext import commands
import json
import os

# Configurar intents necesarios para leer el contenido del mensaje
intents = discord.Intents.default()
intents.message_content = True

# Configurar el bot con el prefijo de comando
bot = commands.Bot(command_prefix="!", intents=intents)

# Ruta al archivo JSON
DATA_FILE = "user_data.json"

# Cargar datos desde el archivo JSON o inicializar un diccionario vacío
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Si el archivo JSON está corrupto o vacío, devuelve un diccionario vacío
                return {}
    else:
        # Crear el archivo JSON vacío si no existe
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}

# Guardar datos en el archivo JSON
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Inicializar datos de usuario
user_data = load_data()

@bot.event
async def on_ready():
    print(f'Bot listo y conectado como {bot.user}')

@bot.event
async def on_message(message):
    # Ignorar los mensajes del propio bot para evitar un bucle infinito
    if message.author == bot.user:
        return

    # Responder a "Hola, URUBOT"
    if message.content.lower() == 'hola, urubot':
        await message.channel.send(f'Hola, ¿cómo estás {message.author.name}?')

    # Verificar si el mensaje contiene "bump done" (confirmación de bump del bot de Disboard)
    if "bump done" in message.content.lower() and message.author.id == 735147814878969968:
        await message.channel.send("Has bumpeado el server con éxito")  # Mensaje de confirmación

        user_id = str(message.author.id)  # Convertir ID de usuario a cadena para el JSON

        if user_id not in user_data:
            user_data[user_id] = {"points": 0, "streak": 0}

        user_data[user_id]["streak"] += 1

        if user_data[user_id]["streak"] == 3:
            user_data[user_id]["points"] += 2
            user_data[user_id]["streak"] = 0
        else:
            user_data[user_id]["points"] += 1

        save_data(user_data)

        await message.channel.send(f"{message.author.mention} ha sido premiado con puntos! Puntos totales: {user_data[user_id]['points']}")

    # Procesar comandos después de manejar mensajes
    await bot.process_commands(message)

@bot.command(name='points')
async def check_points(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    if user_id in user_data:
        points = user_data[user_id]["points"]
        await ctx.send(f"{member.mention} tiene {points} puntos.")
    else:
        await ctx.send(f"{member.mention} aún no tiene puntos.")

@bot.command(name='addpoints')
async def add_points(ctx, member: discord.Member, points: int):
    user_id = str(member.id)

    if user_id not in user_data:
        user_data[user_id] = {"points": 0, "streak": 0}

    user_data[user_id]["points"] += points
    save_data(user_data)

    await ctx.send(f"{points} puntos han sido añadidos a {member.mention}. Total de puntos: {user_data[user_id]['points']}")

# Iniciar el bot con tu token
bot.run('Token_Here')