# encoding: utf-8
''' Módulo responsável pela criação do socket que ficará aguardando por uma
solicitação de conexão.

Autor: Herlon Camargo

Data: 16/10/2012
'''

import socket
import ssl
from gera_log import gera_log


def cria_socket(porta, chave_privada, certificado):
    ''' Função que cria um socket para uma conexão criptografada com SSL.
    Recebe, como parâmetros, o número da "porta" que será utilizado como
    endereço para se contactar o socket; a localização da chave privada em
    "chave_privada"; e a localização do "certificado". Retorna um objeto que
    identifica o socket a ser utilizado em conexões criptografadas.
    '''
    # Cria  um socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        s.bind(('', int(porta)))
        s.listen(1)
    except:
        gera_log('Erro ao criar socket')
        exit()

    # Acrescenta criptografia com SSL ao socket criado
    try:
        s_ssl = ssl.wrap_socket(s,
                                keyfile=chave_privada,
                                certfile=certificado,
                                server_side=True,
                                ssl_version=ssl.PROTOCOL_TLSv1,
                                suppress_ragged_eofs=False)
    except:
        gera_log('Erro ao criar conexão criptografada')
        exit()

    gera_log('Aguardando conexão...')

    return s_ssl
