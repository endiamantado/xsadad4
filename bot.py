import telebot
import requests
import urllib3
import os
from telebot import util
import time
from bs4 import BeautifulSoup
from requests import Session
from flask import Flask, request

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
    if username:
        bot.reply_to(message, f"""🌟 Bienvenido, @{username} ! 🌟

🤖 | Soy @enpunga_bot , BOT que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico!

👨🏻‍💻 | Estas Son Las Funciones que están disponibles:
› /dni [DNI] [F/M]
› /buscar [NOMBRE/RAZON SOCIAL]
› /ip [IP ADRESS] (Gasta)
› /me (ver las busquedas que te quedan)
› /id (ver tu id)
› /comprar (informacion + precios + contacto)

🔐 Para acceder a estas herramientas requiere una suscripción.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""")
    else:
        bot.reply_to(message, """🌟 Bienvenido 🌟

🤖 | Soy @enpunga_bot , BOT que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico!

👨🏻‍💻 | Estas Son Las Funciones que están disponibles:
› /dni [DNI] [F/M]
› /buscar [NOMBRE/RAZON SOCIAL]
› /ip [IP ADRESS] (Gasta)
› /me (ver las busquedas que te quedan)
› /id (ver tu id)
› /comprar (informacion + precios + contacto)

🔐 Para acceder a estas herramientas requiere una suscripción.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""")

@bot.message_handler(commands=['dni'])
def send_dni_info(message):
    try:
        user_id = str(message.from_user.id)

        if user_id in authorized_users:
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
        else:
            bot.send_message(message.chat.id, 'No estás autorizado para usar este comando.')
    except (IndexError, ValueError):
        bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M].")

@bot.message_handler(commands=['buscar'])
def buscar_nombre(message):
    try:
        user_id = str(message.from_user.id)

        if user_id in authorized_users:
            command_params = message.text.split()
            if len(command_params) != 2:
                raise ValueError("Número incorrecto de parámetros")

            query = command_params[1]

            bot.reply_to(message, "🔍 Buscando...")

            all_results = []
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
                            all_results.append(f"{cuit} - {nombre}")

                except requests.exceptions.RequestException as e:
                    bot.reply_to(message, f'Error de conexión: {e}')
                    return

                time.sleep(5)

            if all_results:
                send_long_message(message, "Resultados encontrados:", all_results[:70])
            else:
                bot.reply_to(message, "No se encontraron resultados.")

            print(f"COMANDO /BUSCAR EJECUTADO POR: {user_id}")
        else:
            bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando o @ciberforence.")
    except (IndexError, ValueError) as e:
        bot.reply_to(message, str(e))

def send_long_message(message, initial_text, results):
    max_message_length = 4096
    chat_id = message.chat.id
    text = initial_text + "\n"
    for result in results:
        if len(text) + len(result) + 1 > max_message_length:
            bot.send_message(chat_id, text)
            text = ""
        text += result + "\n"
    
    # Enviar el texto restante
    if text.strip() != initial_text:
        bot.send_message(chat_id, text)

@bot.message_handler(commands=['ip'])
def ip_command(message):
    try:
        user_id = message.from_user.id

        if user_id in autorizados:
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

                formatted_response = f"""```
IP: {ip_address}
Status: {data.get('status', 'N/A')}
País: {data.get('country', 'N/A')}
Región: {data.get('regionName', 'N/A')}
Ciudad: {data.get('city', 'N/A')}
Código Postal: {data.get('zip', 'N/A')}
Latitud: {data.get('lat', 'N/A')}
Longitud: {data.get('lon', 'N/A')}
Zona Horaria: {data.get('timezone', 'N/A')}
ISP: {data.get('isp', 'N/A')}
Organización: {data.get('org', 'N/A')}
AS: {data.get('as', 'N/A')}
```"""
                bot.reply_to(message, formatted_response, parse_mode='Markdown')
            else:
                bot.reply_to(message, f"Error al consultar la información de la IP: {ip_address}")
        else:
            bot.reply_to(message, "No estás autorizado para usar este comando.")
    except (IndexError, ValueError) as e:
        bot.reply_to(message, str(e))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f'Error de conexión: {e}')

@bot.message_handler(commands=['me'])
def check_user_status(message):
    user_id = message.from_user.id
    try:
        with open('whitelist.txt', 'r') as file:
            authorized_users = file.read().splitlines()
        if str(user_id) in authorized_users:
            bot.reply_to(message, 'Estás en la whitelist.')
        else:
            bot.reply_to(message, 'No estás en la whitelist.')
    except FileNotFoundError:
        bot.reply_to(message, 'El archivo de la whitelist no se encontró.')
    except Exception as e:
        bot.reply_to(message, f'Ocurrió un error: {e}')

@bot.message_handler(commands=['id'])
def send_user_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"{user_id}")

@bot.message_handler(commands=['comprar'])
def send_purchase_info(message):
    bot.reply_to(message, "Para adquirir acceso al bot, contacta a @afanando o @ciberforence para más información y precios.")

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
            file.write(user_id + '\n')

        bot.send_message(message.chat.id, f'ID: {user_id} agregado a la lista de autorizados.')
    except ValueError:
        bot.reply_to(message, "El ID debe ser un número válido.")


@bot.message_handler(commands=['me'])
def check_user_status(message):
    user_id = message.from_user.id
    if user_id in authorizados:
        bot.reply_to(message, 'Estás Autorizado.')
    else:
        bot.reply_to(message, 'No Estás Autorizado.')
        

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
