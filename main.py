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

    # Verificar si el mensaje proviene del bot específico y contiene "Thx for bumping our Server!"
    if message.author.id == 1277645160376963167:  # ID del bot de Disboard u otro bot que utilices
        if "Thx for bumping our Server!" in message.content:
            # Extraer la primera mención en el mensaje
            if len(message.mentions) > 0:
                bump_user = message.mentions[0]  # Obtener el primer usuario mencionado
                user_id = str(bump_user.id)  # Convertir ID de usuario a cadena para el JSON

                # Inicializar puntos y racha si el usuario no está en los datos
                if user_id not in user_data:
                    user_data[user_id] = {"points": 0, "streak": 0}

                # Incrementar el streak del usuario que hizo el bump
                user_data[user_id]["streak"] += 1

                # Restablecer el streak de todos los demás usuarios
                for other_user_id in user_data.keys():
                    if str(other_user_id) != str(user_id):
                        user_data[other_user_id]["streak"] = 0

                # Verificar si el usuario alcanza 3 de streak
                if user_data[user_id]["streak"] == 3:
                    user_data[user_id]["points"] += 2
                    user_data[user_id]["streak"] = 0  # Restablecer el streak después de alcanzar 3
                    message_to_send = f"{bump_user.mention} ha sido premiado con puntos adicionales por alcanzar una racha de 3! Puntos totales: {user_data[user_id]['points']}"
                else:
                    user_data[user_id]["points"] += 1
                    if user_data[user_id]["streak"] == 2:
                        message_to_send = f"{bump_user.mention} estás en una racha de 2! Puntos totales: {user_data[user_id]['points']}"
                    else:
                        message_to_send = f"{bump_user.mention} ha sido premiado! Puntos totales: {user_data[user_id]['points']}"

                # Guardar los datos actualizados
                save_data(user_data)

                # Enviar mensaje de confirmación con los puntos del usuario
                await message.channel.send(message_to_send)
            else:
                await message.channel.send("No se encontró ninguna mención en el mensaje.")

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

bot.run('TOKEN_HERE')