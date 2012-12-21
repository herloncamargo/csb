#!/usr/bin/env python
# encoding: utf-8
''' Este script deverá ser executado na máquina que será o servidor central de
backup. Ele enviará uma requisição às máquinas remotas solicitando determinados
arquivos para serem becapeados, e os receberá num único arquivo compactado
armazenando-os num diretório previamente especificado no arquivo "settings.py".

Para saber quais arquivos serão solicitados e de quais máquinas, este script
consulta o subdiretório "hosts", que contém arquivos individuais com as
respectivas configurações referentes a cada máquina remota. Esses arquivos de
configurações individuais contém informações como o endereço ip e porta do host
alvo do backup, a senha de acesso ao serviço que receberá as solicitações no
host alvo, e a relação de arquivos para serem trazidos como backup.

As conexões entre este script e as máquinas remotas são feitas de forma
criptografada, sendo essas máquinas as possuidoras da chave e do certificado
responsáveis pela criptografia.

Não há necessidade que esse script seja executado com poderes de superusuário,
a menos que se deseje armazenar os arquivos de backup em lugares restritos ao
superusuário. Este script não necessita ser executado como um daemon e pode ser
inserido sem problemas em agendadores de tarefas como o Cron.

Toda atividade deste script é registrada no arquivo de log "backup-server.log"
localizado no mesmo diretório onde se encontra este script. Maiores
informações, bem como detalhes dos arquivos individuais de configuração dos
hosts alvos, podem ser obitdos no arquivo README.

Sua sintaxe de uso é:

    backup_server.py -h        : para exibir informações

    backup_server.py

Autor: Herlon Ayres Camargo
Data: 16/10/2012
'''

import glob
import ipaddr
import pickle
import re
import socket
import ssl
import threading
from sys import argv
from settings import *
from modules.cria_socket import cria_socket
from modules.gera_log import gera_log


def backup(ip, porta, senha, arquivos, local):
    ''' Função que solicita ao host alvo os arquivos a serem becapeados, recebe
    um arquivo compactado com os arquivos solicitados, e armazena o arquivo
    especificado num diretório passado como parâmetro. Possui como parâmetros
    de entrada o endereço "ip" do host alvo; o número da "porta" que a
    aplicação remota do host alvo utiliza para receber requisições; a "senha"
    para se contactar ao host alvo; uma tupla com a relação de "arquivos" que
    serão becapeados; e o "local" onde o arquivo compactado de backup será
    armazenado.
    '''
    # Tenta fazer conexão com host remoto
    s_ssl = cria_socket(ip, porta)

# 1a. conexão: ENVIANDO =======================================================
    # Envia senha para conexão ao host
    try:
        s_ssl.write(senha)
    except ssl.SSLError:
        gera_log('Erro ao enviar senha')
        s_ssl.close()
        exit()

# 2a. conexão: RECEBENDO ======================================================
    # Recebe status da aceitação ou não da senha
    try:
        recebido = s_ssl.read()
    except ssl.SSLError:
        gera_log('Conexão encerrada por {}'.format(ip))
        s_ssl.close()
        exit()

    if recebido == 'Senha incorreta':
        gera_log('Senha incorreta do host {}'.format(ip))
        gera_log('Encerrando conexão com {}'.format(ip))
        s_ssl.close()
        exit()

# 3a. conexão: ENVIANDO =======================================================
    # Enviando uma tupla com a relação de arquivos para backup
    try:
        s_ssl.write(pickle.dumps(arquivos))
    except:
        gera_log('Erro ao enviar relação de arquivos')
        s_ssl.close()
        exit()

# 4a. conexão: RECEBENDO ======================================================
    # Recebendo o nome do arquivo compactado
    try:
        recebido = s_ssl.read()
    except ssl.SSLError:
        gera_log('Conexão encerrada por {}'.format(ip))
        s_ssl.close()
        exit()

    name_file = recebido.split('/')[-1].strip('\n')
    name_file = '{0}-{1}-{2}'.format(name_file.split('-', 1)[0], ip,\
                                     name_file.split('-', 1)[1])

# 5a. conexão: RECEBENDO ======================================================
    # Recebendo e gravando o arquivo compactado
    if not local.find('/', -1) == len(local) - 1:
        local = '{}/'.format(local)

    while True:
        try:
            recebido = s_ssl.read()
        except ssl.SSLError:
            break

        if not recebido:
            break

        with open('{0}{1}'.format(local, name_file), 'ab') as f:
            f.write(recebido)

    gera_log('Arquivo {0} copiado de {1}'.format(name_file, ip))

    # Encerrando a conexão
    s_ssl.close()


if __name__ == '__main__':
    # Verifica se foi passado algum parâmetro
    if len(argv) != 1:
        exit('Forma de uso: ./backup_server.py')

    # RegExp para determinar o nome do arquivo com os parâmetros de um host
    p0 = re.compile(r'hosts/(.+?).py')

    # Importa as configurações de cada host alvo separadamente
    for i in glob.iglob('hosts/[!__]*.py'):
        name_file = re.search(p0, i).group(1)
        name_module = 'hosts.{}'.format(name_file)
        exec('import {}'.format(name_module))
        exec('ip = hosts.{}.IP'.format(name_file))
        exec('porta = hosts.{}.PORTA'.format(name_file))
        exec('senha = hosts.{}.SENHA'.format(name_file))
        exec('arquivos = hosts.{}.ARQUIVOS'.format(name_file))

        # Verifica se ip é válido
        try:
            ipaddr.IPv4Address(ip)
        except AddressValueError:
            gera_log('Formato de ip inválido: {}'.format(ip))

        # Cria as threads utilizadas em cada host
        t = threading.Thread(target=backup, args=(ip, porta, senha,
                                                  arquivos, LOCAL))
        t.start()

        # Limpa as variáves individuais de cada host
        del ip, porta, senha, arquivos
        exec('del {}'.format(name_module))
