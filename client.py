import socket
import struct
import base64
import hashlib
import sys

CORRECT_CODE = 'ok'
TIMEOUT = 5
FORMAT = 'utf-8'
SERVER = "10.2.126.2"
PORT = 19876
ADDR = (SERVER, PORT)

ERROR_EXCEPTION = 'Lo sentimos, no fue posible establecer la conexión'
TIME_OUT_EXCEPTION = 'La conexion ha tardado demasiado en responder'
MESSAGE_EXCEPTION = 'Ha ocurrido un error recibiendo el mensaje'


def create_socket():
    # Crea conexión TCP
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_server():
    global client
    client = create_socket()
    client.settimeout(TIMEOUT)

    try:
        client.connect(ADDR)
    except socket.timeout:
        print(TIME_OUT_EXCEPTION)
        sys.exit(0)
    except Exception:
        print(ERROR_EXCEPTION)
        sys.exit(0)


def reset_socket():
    client.close()
    create_socket()
    connect_to_server()


def get_user_data():
    global CLIENT
    global UDP_PORT
    CLIENT = input('Ingrese su dirección IP : ')
    UDP_PORT = input('Ingrese el número de puerto : ')


def validate_response(message):
    if CORRECT_CODE.strip() in message.strip():
        return True
    else:
        return False


def send_msg(msg):
    message = msg.encode(FORMAT)
    client.send(message)
    client.settimeout(TIMEOUT)

    try:
        res = client.recv(1024).decode(FORMAT)
        return res
    except socket.timeout:
        print(TIME_OUT_EXCEPTION)
        sys.exit(0)
    except Exception:
        print(MESSAGE_EXCEPTION)
        sys.exit(0)


def validate_user():
    while True:
        global USERNAME
        USERNAME = input('Ingrese su nombre de usuario : ')
        res = send_msg('helloiam ' + USERNAME)
        if (validate_response(res) == False):
            print('Usuario inválido.')
            reset_socket()
        else:
            break


def create_udp_connection():
    # Crea conexión udp
    global clientUDP
    try:
        clientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientUDP.bind((CLIENT, int(UDP_PORT)))
        clientUDP.settimeout(TIMEOUT)
    except socket.timeout:
        print(TIME_OUT_EXCEPTION)
        sys.exit(0)
    except Exception as exce:
        print('Puerto o dirección Ip inválida')
        sys.exit(0)


def receive_udp_message():
    # Recibe el mensaje del puerto udp
    try:
        data, server = clientUDP.recvfrom(1024)
        return base64.b64decode(data).decode(FORMAT)
    except socket.timeout:
        print(TIME_OUT_EXCEPTION)
        sys.exit(0)
    except Exception:
        print(MESSAGE_EXCEPTION)
        sys.exit(0)


def validate_checksum(message):
    # Calcula el checksum
    m = hashlib.md5()
    m.update(message.encode(FORMAT))
    checksum_msg = m.hexdigest()
    # Envia mensaje para verificar el checksum
    message = "chkmsg " + checksum_msg
    return send_msg(message)


def comunication():
    global USERNAME
    global CLIENT
    global UDP_PORT

    # Envía mensaje autenticar usuario (nombre de usuario)
    validate_user()

    # Se obtienen los datos del usuario
    get_user_data()

    # Envía mensaje preguntando la longitud del mensaje
    send_msg('msglen')

    create_udp_connection()

    # Notifica el puerto udp
    send_msg('givememsg ' + str(UDP_PORT))

    # Se recibe y se verifica el checksum del mensaje
    finalMessage = receive_udp_message()
    checksum_res = validate_checksum(finalMessage)

    if (validate_response(checksum_res) == True):
        print('El mensaje recibido es:')
        print(finalMessage)
    else:
        print(MESSAGE_EXCEPTION)  # El checksum es inválido
        sys.exit()

    closeConnection()


def closeConnection():
    # Finalizar la conexión
    send_msg('bye')
    print('Esperamos que te haya gustado el mensaje. ¡Hasta luego!')
    client.close()
    clientUDP.close()


def main():
    connect_to_server()
    comunication()


print('Bienvenido a Mensajes UCAB')
main()
