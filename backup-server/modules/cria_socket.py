# encoding: utf-8
''' Módulo responsável pela criação do socket que tentará estabelecer conexão
com os hosts de onde se extrairá os arquivos para backup.

Autor: Herlon Camargo

Data: 16/10/2012
'''

import socket
import ssl
from gera_log import gera_log


def cria_socket(ip, porta):
    ''' Função que cria um socket para uma conexão criptografada com SSL.
    Recebe, como parâmetros, o endereço "ip" do host alvo do backup e o número
    da "porta" que o host alvo utiliza para receber solicitações do servidor.
    Retorna um objeto que identifica o socket a ser utilizado em conexões
    criptografadas.
    '''
    # Cria  um socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        gera_log('Erro ao criar socket')

    # Acrescenta criptografia com SSL ao socket criado
    s_ssl = ssl.wrap_socket(s, suppress_ragged_eofs=False)

    # Tenta estabelecer conexão com o host alvo
    try:
        s_ssl.connect((ip, int(porta)))
    except:
        gera_log('Erro ao tentar estabelecer conexão com {}'.format(ip))

    gera_log('Conexão estabelecida com {}'.format(ip))

    return s_ssl
