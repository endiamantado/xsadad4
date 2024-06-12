import telebot
import requests
import urllib3
import time
import os
from telebot import util
from telebot import types
from bs4 import BeautifulSoup
from requests import Session
from flask import Flask, request
from datetime import datetime, timedelta

session = Session()

# Lista blanca de usuarios ADMIN DEDL BOT
ADMINS_USERS = {
    6952385968,
    7178592767
}

# Usuarios autorizados
autorizados_file = 'whitelist.txt'

try:
    with open(autorizados_file, 'r') as file:
        authorized_users = set(map(int, file.read().splitlines()))
except FileNotFoundError:
    authorized_users = set()

# Reemplaza 'YOUR_API_KEY' con el token de tu bot
TOKEN = '7166794411:AAF6TQ__3eIcCRC-c5yzeroa-6KM4nmoEZU'
bot = telebot.TeleBot(TOKEN)

# URL del webhook
WEBHOOK_URL = "https://xsadad4.onrender.com/" + TOKEN
PORT = int(os.environ.get('PORT', 5000))

# FLASK
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    username = user.username
    user_id = user.id
    print(f"EJECUTO /START: {user_id}")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Canal", url="https://t.me/EnpungaUpdates"))
    markup.add(types.InlineKeyboardButton("Status", url="https://t.me/statusenpunga"))
    markup.add(types.InlineKeyboardButton("Referencias", url="https://t.me/enpungarefes"))
    markup.add(types.InlineKeyboardButton("Grupo", url="https://t.me/AfanandoGroup"))

    photo_path = 'renaper.jpg'  # Ruta de la foto

    if username:
        bot.send_photo(message.chat.id, open(photo_path, 'rb'), caption=f"""🌟 Bienvenido, @{username} ! 🌟

🤖 | Soy @enpunga_bot , bot que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico!

🧑🏻‍💻 | Estas Son Las Funciones que están disponibles:
➣ /dni [DNI] [F/M]
➣ /buscar [NOMBRE/RAZON SOCIAL]
➣ /ip [IP ADRESS]
➣ /me | Consultar Membresia
➣ /id | Ver tu id
➣ /comprar | Informacion Para Adquirir el bot

🔐 | Para acceder a estas herramientas requiere una membresia.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""", reply_markup=markup)


@bot.message_handler(commands=['dni'])
def send_dni_info(message):
    try:
        user_id = str(message.from_user.id)

        if user_id not in authorized_users and user_id not in ADMINS_USERS:
            bot.send_message(message.chat.id, '🚫 No tienes permiso para usar este comando, para comprar el bot /comprar')
            return

        command_params = message.text.split()
        if len(command_params) != 3:
            raise ValueError("Número incorrecto de parámetros")

        dni = command_params[1]
        sexo = command_params[2].upper()

        bot.reply_to(message, "🔍 Consultando DNI...")
        if len(dni) == 8 and dni.isdigit() and sexo in ['F', 'M']:
            url = f"https://teleconsultas-gov.onrender.com/zeakapi/{dni}/{sexo}"
            try:
                response = session.get(url, verify=False)
                response.raise_for_status()
                data = response.json()
                if data and 'data' in data and 'sisa' in data['data']:
                    sisa_info = data['data']['sisa']
                    formatted_message = """```
Datos Básicos:
› Nombre: {nombre}
› Apellido: {apellido}
› DNI: {nroDocumento}
› Sexo: {sexo}
› Fecha de Nacimiento: {fechaNacimiento}
› Nacionalidad: {nacionalidad}
› Provincia de Nacimiento: {provinciaNacimiento}
› Estado Civil: {estadoCivil}
› Fallecido: {fallecido}

Domicilio:
› Domicilio: {domicilio}
› Localidad: {localidad}
› Provincia: {provincia}
› Departamento: {departamento}
› Piso: {pisoDpto}
› Código Postal: {codigoPostal}
```""".format(**sisa_info)
                    bot.reply_to(message, formatted_message, parse_mode='Markdown')
                    print(f"/DNI UTILIZADO POR {user_id}, DNI Buscado: {dni}")
                else:
                    bot.reply_to(message, "No se encontró información para el DNI y sexo proporcionados.")
            except requests.RequestException as e:
                bot.reply_to(message, "Error al obtener información del servidor.")
                print(f"Error al obtener información del servidor: {e}")
        else:
            bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M] y asegúrate de que el DNI tenga 8 dígitos.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M].")

@bot.message_handler(commands=['buscar'])
def buscar_nombre(message):
    try:
        user_id = str(message.from_user.id)

        if user_id not in authorized_users and user_id not in ADMINS_USERS:
            bot.send_message(message.chat.id, '🚫 No tienes permiso para usar este comando, para comprar el bot /comprar.')
            return

        command_params = message.text.split(maxsplit=1)
        if len(command_params) != 2:
            raise ValueError("Número incorrecto de parámetros")

        query = command_params[1]

        bot.reply_to(message, "🔍 Buscando...")

        all_results = set()  # Utilizamos un conjunto para evitar duplicados
        for pagina in range(1, 5):
            payload = {'nombre': query, 'page': pagina}
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            }

            try:
                response = requests.post('https://test.infoexperto.com.ar/buscar.php', data=payload, headers=headers, timeout=10)
                if response.status_code != 200:
                    bot.reply_to(message, f"Error interno en la API")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table')
                if not table:
                    bot.reply_to(message, "No se encontraron resultados en esta página.")
                    continue

                for row in table.find_all('tr')[1:]:
                    columns = row.find_all('td')
                    if len(columns) == 4:
                        cuit = columns[0].text.strip()
                        dni = columns[1].text.strip()
                        nombre = columns[2].text.strip()
                        clase = columns[3].text.strip()
                        result = f"{cuit} - {nombre} - {clase}"
                        all_results.add(result)  # Agregamos el resultado al conjunto

            except requests.exceptions.RequestException as e:
                bot.reply_to(message, f'Error de conexión: {e}')
                return

            time.sleep(5)

        if all_results:
            send_long_message(message, "Resultados encontrados:", list(all_results)[:70])
        else:
            bot.reply_to(message, "No se encontraron resultados.")

        print(f"COMANDO /BUSCAR EJECUTADO POR: {user_id}")
    except (IndexError, ValueError) as e:
        bot.reply_to(message, str(e))

def send_long_message(message, header, results):
    message_text = f"{header}\n"
    for result in results:
        message_text += f"{result}\n"
    bot.send_message(message.chat.id, message_text)

@bot.message_handler(commands=['ip'])
def ip_command(message):
    try:
        user_id = message.from_user.id

        if user_id not in authorized_users and user_id not in ADMINS_USERS:
            bot.send_message(message.chat.id, '🚫 No tienes permiso para usar este comando, para comprar el bot /comprar.')
            return

        command_params = message.text.split()
        if len(command_params) != 2:
            raise ValueError("Número incorrecto de parámetros")

        ip_address = command_params[1]

        response = requests.get(f'http://ip-api.com/json/{ip_address}')

        if response.status_code == 200:
            data = response.json()
            print(f"/IP UTILIZADO POR {user_id}")
            if data['status'] == 'fail':
                bot.reply_to(message, f"No se encontró información para la IP: {ip_address}")
                return

            formatted_response = f""" ```
IP: {data['query']}
Status: {data['status']}
País: {data['country']}
Región: {data['region']}
Ciudad: {data['city']}
Código Postal: {data['zip']}
Latitud: {data['lat']}
Longitud: {data['lon']}
Zona Horaria: {data['timezone']}
ISP: {data['isp']}
ORG: {data['org']}
AS: {data['as']}
             ```"""
            bot.send_message(message.chat.id, formatted_response, parse_mode="Markdown")
            bot.send_location(message.chat.id, latitude=data['lat'], longitude=data['lon'])
        else:
            bot.reply_to(message, f"Error al consultar la información de la IP: {ip_address}")
    except (IndexError, ValueError) as e:
        bot.reply_to(message, str(e))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f'Error de conexión: {e}')

@bot.message_handler(commands=['id'])
def send_user_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"{user_id}")

@bot.message_handler(commands=['comprar'])
def send_purchase_info(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ZEAK", url="https://t.me/afanando"))
    markup.add(types.InlineKeyboardButton("Forence", url="https://t.me/ciberforence"))

    bot.reply_to(message, "Para Adquirir el Acceso al Bot Contacta a Soporte", reply_markup=markup)

@bot.message_handler(commands=['add'])
def add_user_command(message):
    if message.from_user.id not in ADMINS_USERS:
        bot.send_message(message.chat.id, 'Esta función solo puede ser utilizada por los administradores del bot.')
        return

    command_params = message.text.split()
    if len(command_params) != 2:
        bot.reply_to(message, "Formato incorrecto. Usa /add [ID].")
        return

    user_id = command_params[1]

    try:
        if user_id in authorized_users:
            bot.send_message(message.chat.id, 'Este usuario ya está autorizado.')
            return

        authorized_users.add(user_id)
        with open(autorizados_file, 'a') as file:
            file.write(f"{user_id} - {datetime.now().strftime('%Y-%m-%d')}\n")

        bot.send_message(message.chat.id, f'ID: {user_id} agregado a la lista de autorizados por 1 Mes exitosamente.')

        # Programar la eliminación del usuario después de un mes
        delete_date = datetime.now() + timedelta(days=30)
        scheduler.add_job(delete_user_from_whitelist, 'date', run_date=delete_date, args=[user_id])

    except ValueError:
        bot.reply_to(message, "El ID debe ser un número válido.")

def delete_user_from_whitelist(user_id):
    try:
        with open(autorizados_file, 'r') as file:
            lines = file.readlines()
        with open(autorizados_file, 'w') as file:
            for line in lines:
                if user_id not in line:
                    file.write(line)
    except FileNotFoundError:
        pass  # El archivo aún no existe, no se necesita hacer nada

@bot.message_handler(commands=['me'])
def check_user_status(message):
    user_id = message.from_user.id
    try:
        with open('whitelist.txt', 'r') as file:
            authorized_users = file.read().splitlines()
        if str(user_id) in authorized_users:
            bot.reply_to(message, 'Estás Autorizado.')
        else:
            bot.reply_to(message, 'No Estás Autorizado.')
    except FileNotFoundError:
        bot.reply_to(message, 'El archivo de la whitelist no se encontró culea.')
    except Exception as e:
        bot.reply_to(message, f'Ocurrió un error: {e}')
        

@bot.message_handler(commands=['staff'])
def show_help(message):
    user_id = message.from_user.id
    print(f"el usuario {user_id} quiso ver la lista de comandos")
    if user_id not in ADMINS_USERS:
        bot.reply_to(message, "No estás autorizado para usar este comando.")
        return

    help_text = """
***🌟 Comandos Disponibles Para Admins 🌟
› /add [ID] [CANTIDAD] - Agrega búsquedas a un usuario (autorizados).
› /whitelist - Muestra la lista blanca de usuarios (autorizados).
› /staff - Muestra todos los comandos disponibles
    ***"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['whitelist'])
def show_whitelist(message):
    if message.from_user.id not in ADMINS_USERS:
        bot.reply_to(message, 'Esta función solo puede ser sada por los admins.')
        return

    try:
        with open('whitelist.txt', 'r') as file:
            authorized_users = file.read().splitlines()
        if authorized_users:
            users_list = "\n".join(authorized_users)
            bot.reply_to(message, f"***Usuarios en la whitelist:***\n{users_list}", parse_mode="markdown")
        else:
            bot.reply_to(message, 'La whitelist está vacía.')
    except FileNotFoundError:
        bot.reply_to(message, 'El archivo de la whitelist no se encontró.')
    except Exception as e:
        bot.reply_to(message, f'Ocurrió un error: {e}')

@bot.message_handler(commands=['cmds'])
def show_help(message):
    user_id = message.from_user.id
    print(f"el usuario {user_id} vio la lista de comandos")
    help_text = """
***🌟 Comandos Disponibles 🌟
› /start - Inicia el bot y muestra un mensaje de bienvenida.
› /dni [DNI] [F/M] - Realiza una consulta de DNI.
› /buscar [NOMBRE/DNI/CUIL] - Realiza una busqueda de nombres.
› /ip [IP_ADRESS] - Consulta la ubicacion de una IP.
› /me - Verifica si estas autorizado.
› /id - Muestra tu ID de usuario.
› /comprar - Información sobre como adquirir el bot.***
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "¡Bot está funcionando!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "¡Webhook establecido!", 200

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    server.run(host="0.0.0.0", port=PORT)
