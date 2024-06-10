import telebot
import requests
import urllib3
import os
from telebot import util
import time
from bs4 import BeautifulSoup
from requests import Session

session = Session()

#guarda los usuarios q iniciaron el bot
usuarios_iniciados = set()

#desactivar esa advertencia pinchila
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#FLASK
# Token del bot de Telegram
TOKEN = 'your_telegram_bot_token'
# URL de tu aplicación en Render
WEBHOOK_URL = f'https://api-ricardo-whatsapp.onrender.com/{TOKEN}'
# Puerto configurado por Render
PORT = int(os.environ.get('PORT', 3000))

# Reemplaza 'YOUR_API_KEY' con el token de tu bot
bot = telebot.TeleBot('7166794411:AAF6TQ__3eIcCRC-c5yzeroa-6KM4nmoEZU')
#FLASK
server = Flask(__name__)

# Lista blanca de usuarios autorizados para agregar búsquedas y ver la lista blanca
authorized_users = [
    6952385968,
    7178592767
]  

# Diccionario para almacenar los usuarios agregados
autorizados = {}

# Cargar las búsquedas desde el archivo
def load_autorizados():
    global autorizados
    autorizados = {}  # Limpiamos el diccionario para cargar los datos actualizados
    if os.path.exists('whitelist.txt'):
        with open('whitelist.txt', 'r') as file:
            for line in file:
                try:
                    user_id = int(line.strip())
                    autorizados[user_id] = 0  # Agregamos el ID con un contador inicial de 0
                except ValueError:
                    print(f"Error al procesar la línea: {line.strip()}")

# Cargar la whitelist al iniciar el bot
load_autorizados()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    username = user.username
    user_id = message.from_user.id
    print(f"EJECUTO /START: {user_id}")
    if username:
        bot.reply_to(
            message, f"""🌟 Bienvenido, @{username} ! 🌟

🤖 | Soy @enpunga_bot , BOT que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico !

👨🏻‍💻 | Estas Son Las Funciones que están disponibles:
› /dni [DNI] [F/M]
› /buscar [NOMBRE/RAZON SOCIAL]
› /ip [IP ADRESS] (Gasta )
› /me (ver las busquedas que te quedan)
› /id (ver tu id)
› /comprar (informacion + precios + contacto)

🔐 Para acceder a estas herramientas requiere una suscripción.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""")
    else:
        bot.reply_to(message,"""🌟 Bienvenido 🌟

🤖 | Soy @enpunga_bot , BOT que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico !

👨🏻‍💻 | Estas Son Las Funciones que están disponibles:
› /dni [DNI] [F/M]
› /buscar [NOMBRE/RAZON SOCIAL]
› /ip [IP ADRESS] (Gasta )
› /me (ver las busquedas que te quedan)
› /id (ver tu id)
› /comprar (informacion + precios + contacto)

🔐 Para acceder a estas herramientas requiere una suscripción.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""")

@bot.message_handler(commands=['dni'])
def send_dni_info(message):
    user_id = message.from_user.id
    if user_id in autorizados:
        try:
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
                    print(f"/DNI UTILIZADO POR {user_id}, DNI Buscado: {dni}")
                    if data and 'data' in data and 'sisa' in data['data']:
                        sisa_info = data['data']['sisa']

                        coverage_info = []
                        if 'cobertura' in sisa_info and sisa_info['cobertura'] is not None:
                            for coverage in sisa_info['cobertura']:
                                coverage_info.append(
                                    f"› Tipo de Cobertura: {coverage.get('tipoCobertura', 'N/A')}\n"
                                    f"  Nombre Obra Social: {coverage.get('nombreObraSocial', 'N/A')}\n"
                                    f"  RNOs: {coverage.get('rnos', 'N/A')}\n"
                                    f"  Vigencia Desde: {coverage.get('vigenciaDesde', 'N/A')}\n"
                                    f"  Fecha de Actualización: {coverage.get('fechaActualizacion', 'N/A')}\n"
                                    f"  Origen: {coverage.get('origen', 'N/A')}\n")

                        coverage_str = "\n".join(coverage_info)

                        formatted_message = (f"""```
Datos Basicos:
› Nombre: {sisa_info.get('nombre', 'N/A')}
› Apellido: {sisa_info.get('apellido', 'N/A')}
› DNI: {sisa_info.get('nroDocumento', 'N/A')}
› Sexo: {sisa_info.get('sexo', 'N/A')}
› Fecha de Nacimiento: {sisa_info.get('fechaNacimiento', 'N/A')}
› Nacionalidad: {sisa_info.get('nacionalidad', 'N/A')}
› Provincia de Nacimiento: {sisa_info.get('provinciaNacimiento', 'N/A')}
› Estado Civil: {sisa_info.get('estadoCivil', 'N/A')}
› Fallecido: {sisa_info.get('fallecido', 'N/A')}

Domicilio:
› Domicilio: {sisa_info.get('domicilio', 'N/A')}
› Localidad: {sisa_info.get('localidad', 'N/A')}
› Provincia: {sisa_info.get('provincia', 'N/A')}
› Departamento: {sisa_info.get('departamento', 'N/A')}
› Piso: {sisa_info.get('pisoDpto', 'N/A')}
› Código Postal: {sisa_info.get('codigoPostal', 'N/A')}

Información de Cobertura:
{coverage_str}
```""")
                        bot.reply_to(message, formatted_message, parse_mode='Markdown')
                    else:
                        bot.reply_to(message, "No se encontró información para el DNI y sexo proporcionados.")
                except requests.RequestException as e:
                    bot.reply_to(message, "Error al obtener información del servidor.")
                    print(f"Error al obtener información del servidor: {e}")
            else:
                bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M] y asegúrate de que el DNI tenga 8 dígitos.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M].")
    else:
        bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando @ciberforence.")


@bot.message_handler(commands=['buscar'])
def buscar_nombre(message):
    user_id = message.from_user.id
    if user_id in autorizados:  # Verifica si user_id está en el diccionario autorizados
        query = ' '.join(message.text.split(' ')[1:])
        if not query:
            bot.reply_to(message, 'Por favor, proporciona un nombre, DNI o CUIL.')
            return

        bot.reply_to(message, "🔍 Buscando...")

        # Variable para acumular los resultados
        all_results = []

        # Realizar la búsqueda en las páginas 1, 2, 3, y 4
        for pagina in range(1, 5):
            payload = {
                'nombre': query,  # Asegúrate de que este sea el nombre del campo correcto
                'page': pagina  # Si hay un parámetro para la página, agrégalo aquí
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            }

            try:
                response = requests.post('https://test.infoexperto.com.ar/buscar.php', data=payload, headers=headers, timeout=10)

                if response.status_code != 200:
                    bot.reply_to(message, f"Error interno en la API")
                    continue

                # Analizar el contenido HTML con BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table')
                if not table:
                    bot.reply_to(message, "No se encontraron resultados en esta página.")
                    continue

                # Extraer datos de la tabla
                for row in table.find_all('tr')[1:]:  # Omitir el encabezado de la tabla
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

            # Añadir un pequeño retraso entre las solicitudes
            time.sleep(5)

        # Enviar solo los primeros 55 resultados
        if all_results:
            send_long_message(message, "Resultados encontrados:", all_results[:70])
        else:
            bot.reply_to(message, "No se encontraron resultados.")

        print(f"COMANDO /BUSCAR EJECUTADO POR: {user_id}")
    else:
        bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando @ciberforence.")

def send_long_message(message, initial_text, results):
    max_message_length = 4096
    chat_id = message.chat.id
    text = initial_text + "\n"
    for result in results:
        if len(text) + len(result) + 1 > max_message_length:
            bot.send_message(chat_id, text)
            text = ""
        text += result + "\n"
    if text:
        bot.send_message(chat_id, text)


@bot.message_handler(commands=['ip'])
def ip_command(message):
    user_id = message.from_user.id
    if user_id in autorizados:
        try:
            command_params = message.text.split()
            if len(command_params) != 2:
                raise ValueError("Número incorrecto de parámetros")

            ip_address = command_params[1]

            response = requests.get(f'http://ip-api.com/json/{ip_address}')

            if response.status_code == 200:
                data = response.json()
                print(f"/IP UTILIZADO POR {user_id}")
                if data['status'] == 'fail':
                    bot.reply_to(
                        message,
                        f"No se encontró información para la IP: {ip_address}")
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
ORG: {data.get('org', 'N/A')}
AS: {data.get('as', 'N/A')}
```"""
                bot.send_message(message.chat.id,
                                 formatted_response,
                                 parse_mode="Markdown")
                bot.send_location(message.chat.id,
                                  latitude=data.get('lat', 0),
                                  longitude=data.get('lon', 0))

            elif response.status_code == 429:
                bot.send_message(
                    message.chat.id,
                    'Has excedido el límite de consultas a la API. Por favor, inténtalo más tarde.'
                )
            else:
                bot.send_message(message.chat.id, 'Error al consultar la API.')

        except ValueError as e:
            print(f"Error en formato de comando /ip: [IP]")
        except Exception as e:
            print(f"Error en comando /ip: {e}")

        finally:
            time.sleep(
                5)  # Agrega un retraso de 5 segundos después de cada consulta
    else:
        bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando @ciberforence.")
        

@bot.message_handler(commands=['id'])
def add_searches(message):
    user = message.from_user
    username = user.username
    user_id = message.from_user.id
    print(f"/ID EJECUTADO POR {user_id}")
    if username:
        bot.reply_to(message, f"{user_id}")


@bot.message_handler(commands=['comprar'])
def send_purchase_info(message):
    bot.reply_to(message, "Para comprar el bot, contacta a @Afanando o a @ciberforence")

@bot.message_handler(commands=['add'])
def add_to_whitelist(message):
    user_id = message.from_user.id
    if user_id in authorized_users:
        command_params = message.text.split()
        if len(command_params) != 2:
            bot.reply_to(message, "Formato incorrecto. Usa /add [ID].")
            return
        try:
            new_id = int(command_params[1])
            with open('whitelist.txt', 'a') as file:
                file.write(str(new_id) + '\n')
            bot.reply_to(message, f"ID {new_id} agregado a la whitelist.")
        except ValueError:
            bot.reply_to(message, "El ID debe ser un número válido.")
    else:
        bot.reply_to(
            message,
            "No tienes permiso para agregar usuarios a la whitelist."
        )

@bot.message_handler(commands=['whitelist'])
def show_whitelist(message):
    user_id = message.from_user.id
    if user_id in authorized_users:
        try:
            with open('whitelist.txt', 'r') as file:
                whitelist = file.read()
            bot.reply_to(message, "***Usuarios Autorizados:***\n" + whitelist, parse_mode="markdown")
        except FileNotFoundError:
            bot.reply_to(message, "Whitelist no encontrada.")
    else:
        bot.reply_to(
            message,
            "No tienes permiso para ver la whitelist."
        )

@bot.message_handler(commands=['me'])
def check_whitelist(message):
    user_id = message.from_user.id
    if user_id in authorized_users:
        bot.reply_to(message, "Estas autorizado.")
    else:
        bot.reply_to(message, "No estas autorizado, para comprar contacta a @afanando @ciberforence.")

def send_forwarded_message(message):
    if len(message.text.split()) > 1:
        forward_message = ' '.join(message.text.split()[1:])
        for usuario_id in usuarios_iniciados:
            bot.send_message(usuario_id, forward_message)
        print(f"Mensaje enviado a todos los usuarios iniciados")
    else:
        bot.send_message(message.chat.id,
                         "Por favor, incluye un mensaje para reenviar.")
        

@bot.message_handler(commands=['staff'])
def show_help(message):
    user_id = message.from_user.id
    print(f"el usuario {user_id} quiso ver la lista de comandos")
    if user_id not in authorized_users:
        bot.reply_to(message, "No estás autorizado para usar este comando.")
        return

    help_text = """
***🌟 Comandos Disponibles Para Admins 🌟
› /add [ID] [CANTIDAD] - Agrega búsquedas a un usuario (autorizados).
› /whitelist - Muestra la lista blanca de usuarios (autorizados).
› /staff - Muestra todos los comandos disponibles
    ***"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

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

import telebot
import requests
import urllib3
import os
from telebot import util
import time
from bs4 import BeautifulSoup
from requests import Session
from flask import Flask

session = Session()

#guarda los usuarios q iniciaron el bot
usuarios_iniciados = set()

#desactivar esa advertencia pinchila
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Reemplaza 'YOUR_API_KEY' con el token de tu bot
bot = telebot.TeleBot('7166794411:AAF6TQ__3eIcCRC-c5yzeroa-6KM4nmoEZU')

# Lista blanca de usuarios autorizados para agregar búsquedas y ver la lista blanca
authorized_users = [
    6952385968,
    7178592767
]  

# Diccionario para almacenar los usuarios agregados
autorizados = {}

# Cargar las búsquedas desde el archivo
def load_autorizados():
    global autorizados
    autorizados = {}  # Limpiamos el diccionario para cargar los datos actualizados
    if os.path.exists('whitelist.txt'):
        with open('whitelist.txt', 'r') as file:
            for line in file:
                try:
                    user_id = int(line.strip())
                    autorizados[user_id] = 0  # Agregamos el ID con un contador inicial de 0
                except ValueError:
                    print(f"Error al procesar la línea: {line.strip()}")

# Cargar la whitelist al iniciar el bot
load_autorizados()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    username = user.username
    user_id = message.from_user.id
    print(f"EJECUTO /START: {user_id}")
    if username:
        bot.reply_to(
            message, f"""🌟 Bienvenido, @{username} ! 🌟

🤖 | Soy @enpunga_bot , BOT que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico !

👨🏻‍💻 | Estas Son Las Funciones que están disponibles:
› /dni [DNI] [F/M]
› /buscar [NOMBRE/RAZON SOCIAL]
› /ip [IP ADRESS] (Gasta )
› /me (ver las busquedas que te quedan)
› /id (ver tu id)
› /comprar (informacion + precios + contacto)

🔐 Para acceder a estas herramientas requiere una suscripción.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""")
    else:
        bot.reply_to(message,"""🌟 Bienvenido 🌟

🤖 | Soy @enpunga_bot , BOT que se especializa en la búsqueda de datos de argentinos.

🔍 | Con este bot podrás tener informes de cualquier edad a un precio económico !

👨🏻‍💻 | Estas Son Las Funciones que están disponibles:
› /dni [DNI] [F/M]
› /buscar [NOMBRE/RAZON SOCIAL]
› /ip [IP ADRESS] (Gasta )
› /me (ver las busquedas que te quedan)
› /id (ver tu id)
› /comprar (informacion + precios + contacto)

🔐 Para acceder a estas herramientas requiere una suscripción.

🔗 Sigue Nuestro Canal @EnPungaUpdates Para Ver Las Novedades Del Bot!
🔋 Consulta si el bot esta apagado o esta ON: @statusenpunga""")

@bot.message_handler(commands=['dni'])
def send_dni_info(message):
    user_id = message.from_user.id
    if user_id in autorizados:
        try:
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
                    print(f"/DNI UTILIZADO POR {user_id}, DNI Buscado: {dni}")
                    if data and 'data' in data and 'sisa' in data['data']:
                        sisa_info = data['data']['sisa']

                        coverage_info = []
                        if 'cobertura' in sisa_info and sisa_info['cobertura'] is not None:
                            for coverage in sisa_info['cobertura']:
                                coverage_info.append(
                                    f"› Tipo de Cobertura: {coverage.get('tipoCobertura', 'N/A')}\n"
                                    f"  Nombre Obra Social: {coverage.get('nombreObraSocial', 'N/A')}\n"
                                    f"  RNOs: {coverage.get('rnos', 'N/A')}\n"
                                    f"  Vigencia Desde: {coverage.get('vigenciaDesde', 'N/A')}\n"
                                    f"  Fecha de Actualización: {coverage.get('fechaActualizacion', 'N/A')}\n"
                                    f"  Origen: {coverage.get('origen', 'N/A')}\n")

                        coverage_str = "\n".join(coverage_info)

                        formatted_message = (f"""```
Datos Basicos:
› Nombre: {sisa_info.get('nombre', 'N/A')}
› Apellido: {sisa_info.get('apellido', 'N/A')}
› DNI: {sisa_info.get('nroDocumento', 'N/A')}
› Sexo: {sisa_info.get('sexo', 'N/A')}
› Fecha de Nacimiento: {sisa_info.get('fechaNacimiento', 'N/A')}
› Nacionalidad: {sisa_info.get('nacionalidad', 'N/A')}
› Provincia de Nacimiento: {sisa_info.get('provinciaNacimiento', 'N/A')}
› Estado Civil: {sisa_info.get('estadoCivil', 'N/A')}
› Fallecido: {sisa_info.get('fallecido', 'N/A')}

Domicilio:
› Domicilio: {sisa_info.get('domicilio', 'N/A')}
› Localidad: {sisa_info.get('localidad', 'N/A')}
› Provincia: {sisa_info.get('provincia', 'N/A')}
› Departamento: {sisa_info.get('departamento', 'N/A')}
› Piso: {sisa_info.get('pisoDpto', 'N/A')}
› Código Postal: {sisa_info.get('codigoPostal', 'N/A')}

Información de Cobertura:
{coverage_str}
```""")
                        bot.reply_to(message, formatted_message, parse_mode='Markdown')
                    else:
                        bot.reply_to(message, "No se encontró información para el DNI y sexo proporcionados.")
                except requests.RequestException as e:
                    bot.reply_to(message, "Error al obtener información del servidor.")
                    print(f"Error al obtener información del servidor: {e}")
            else:
                bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M] y asegúrate de que el DNI tenga 8 dígitos.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Formato incorrecto. Usa /dni [DNI] [F/M].")
    else:
        bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando @ciberforence.")


@bot.message_handler(commands=['buscar'])
def buscar_nombre(message):
    user_id = message.from_user.id
    if user_id in autorizados:  # Verifica si user_id está en el diccionario autorizados
        query = ' '.join(message.text.split(' ')[1:])
        if not query:
            bot.reply_to(message, 'Por favor, proporciona un nombre, DNI o CUIL.')
            return

        bot.reply_to(message, "🔍 Buscando...")

        # Variable para acumular los resultados
        all_results = []

        # Realizar la búsqueda en las páginas 1, 2, 3, y 4
        for pagina in range(1, 5):
            payload = {
                'nombre': query,  # Asegúrate de que este sea el nombre del campo correcto
                'page': pagina  # Si hay un parámetro para la página, agrégalo aquí
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            }

            try:
                response = requests.post('https://test.infoexperto.com.ar/buscar.php', data=payload, headers=headers, timeout=10)

                if response.status_code != 200:
                    bot.reply_to(message, f"Error interno en la API")
                    continue

                # Analizar el contenido HTML con BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table')
                if not table:
                    bot.reply_to(message, "No se encontraron resultados en esta página.")
                    continue

                # Extraer datos de la tabla
                for row in table.find_all('tr')[1:]:  # Omitir el encabezado de la tabla
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

            # Añadir un pequeño retraso entre las solicitudes
            time.sleep(5)

        # Enviar solo los primeros 55 resultados
        if all_results:
            send_long_message(message, "Resultados encontrados:", all_results[:70])
        else:
            bot.reply_to(message, "No se encontraron resultados.")

        print(f"COMANDO /BUSCAR EJECUTADO POR: {user_id}")
    else:
        bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando @ciberforence.")

def send_long_message(message, initial_text, results):
    max_message_length = 4096
    chat_id = message.chat.id
    text = initial_text + "\n"
    for result in results:
        if len(text) + len(result) + 1 > max_message_length:
            bot.send_message(chat_id, text)
            text = ""
        text += result + "\n"
    if text:
        bot.send_message(chat_id, text)


@bot.message_handler(commands=['ip'])
def ip_command(message):
    user_id = message.from_user.id
    if user_id in autorizados:
        try:
            command_params = message.text.split()
            if len(command_params) != 2:
                raise ValueError("Número incorrecto de parámetros")

            ip_address = command_params[1]

            response = requests.get(f'http://ip-api.com/json/{ip_address}')

            if response.status_code == 200:
                data = response.json()
                print(f"/IP UTILIZADO POR {user_id}")
                if data['status'] == 'fail':
                    bot.reply_to(
                        message,
                        f"No se encontró información para la IP: {ip_address}")
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
ORG: {data.get('org', 'N/A')}
AS: {data.get('as', 'N/A')}
```"""
                bot.send_message(message.chat.id,
                                 formatted_response,
                                 parse_mode="Markdown")
                bot.send_location(message.chat.id,
                                  latitude=data.get('lat', 0),
                                  longitude=data.get('lon', 0))

            elif response.status_code == 429:
                bot.send_message(
                    message.chat.id,
                    'Has excedido el límite de consultas a la API. Por favor, inténtalo más tarde.'
                )
            else:
                bot.send_message(message.chat.id, 'Error al consultar la API.')

        except ValueError as e:
            print(f"Error en formato de comando /ip: [IP]")
        except Exception as e:
            print(f"Error en comando /ip: {e}")

        finally:
            time.sleep(
                5)  # Agrega un retraso de 5 segundos después de cada consulta
    else:
        bot.reply_to(message, "No estás autorizado para usar este comando, para adquirir este bot contacta a @afanando @ciberforence.")
        

@bot.message_handler(commands=['id'])
def add_searches(message):
    user = message.from_user
    username = user.username
    user_id = message.from_user.id
    print(f"/ID EJECUTADO POR {user_id}")
    if username:
        bot.reply_to(message, f"{user_id}")


@bot.message_handler(commands=['comprar'])
def send_purchase_info(message):
    bot.reply_to(message, "Para comprar el bot, contacta a @Afanando o a @ciberforence")

@bot.message_handler(commands=['add'])
def add_to_whitelist(message):
    user_id = message.from_user.id
    if user_id in authorized_users:
        command_params = message.text.split()
        if len(command_params) != 2:
            bot.reply_to(message, "Formato incorrecto. Usa /add [ID].")
            return
        try:
            new_id = int(command_params[1])
            with open('whitelist.txt', 'a') as file:
                file.write(str(new_id) + '\n')
            bot.reply_to(message, f"ID {new_id} agregado a la whitelist.")
        except ValueError:
            bot.reply_to(message, "El ID debe ser un número válido.")
    else:
        bot.reply_to(
            message,
            "No tienes permiso para agregar usuarios a la whitelist."
        )

@bot.message_handler(commands=['whitelist'])
def show_whitelist(message):
    user_id = message.from_user.id
    if user_id in authorized_users:
        try:
            with open('whitelist.txt', 'r') as file:
                whitelist = file.read()
            bot.reply_to(message, "***Usuarios Autorizados:***\n" + whitelist, parse_mode="markdown")
        except FileNotFoundError:
            bot.reply_to(message, "Whitelist no encontrada.")
    else:
        bot.reply_to(
            message,
            "No tienes permiso para ver la whitelist."
        )

@bot.message_handler(commands=['me'])
def check_whitelist(message):
    user_id = message.from_user.id
    if user_id in authorized_users:
        bot.reply_to(message, "Estas autorizado.")
    else:
        bot.reply_to(message, "No estas autorizado, para comprar contacta a @afanando @ciberforence.")

def send_forwarded_message(message):
    if len(message.text.split()) > 1:
        forward_message = ' '.join(message.text.split()[1:])
        for usuario_id in usuarios_iniciados:
            bot.send_message(usuario_id, forward_message)
        print(f"Mensaje enviado a todos los usuarios iniciados")
    else:
        bot.send_message(message.chat.id,
                         "Por favor, incluye un mensaje para reenviar.")
        

@bot.message_handler(commands=['staff'])
def show_help(message):
    user_id = message.from_user.id
    print(f"el usuario {user_id} quiso ver la lista de comandos")
    if user_id not in authorized_users:
        bot.reply_to(message, "No estás autorizado para usar este comando.")
        return

    help_text = """
***🌟 Comandos Disponibles Para Admins 🌟
› /add [ID] [CANTIDAD] - Agrega búsquedas a un usuario (autorizados).
› /whitelist - Muestra la lista blanca de usuarios (autorizados).
› /staff - Muestra todos los comandos disponibles
    ***"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

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
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Webhook set!", 200

@server.route("/status")
def status():
    return "Bot is running", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    server.run(host="0.0.0.0", port=PORT)
