#!/usr/bin/env python
# encoding: utf-8
''' Este script deverá ser executado na máquina onde será realizado o backup.
Ele recebe uma solicitação do servidor central de backups contendo uma relação
de arquivos que deverão ser importados para o servidor, onde serão armazenados
como backup. Para o servidor de backup acessar a máquina onde este script está
sendo executado, ele necessitará informar a senha de acesso. Esta senha está
configurada no arquivo "settings.py" juntamente com as configurações do
endereço de porta utilizado por este script, a localização da chave privada e
do certificado para critografia da conexão com o servidor, e o diretório para
armazenamento local do arquivo de backup. Além de enviar uma cópia para o
servidor de backup, este script também permite que uma cópia fique armazenada
na mesma máquina onde ele está sendo executado.

Para que este script execute em toda sua plenitude, ele deverá receber
permissão de superusuário na sua execução. Com isso, ele poderá acessar todos
os arquivos na máquina onde é executado e enviar qualquer arquivo que for
solicitado pelo servidor de backup. Além disso, ele poderá salvar a cópia local
do backup em qualquer diretório.

Por ser um script que ficará rodando indefinidamente a espera de contato do
servidor de backup, ele é executado em segundo plano como um daemon. Se o
usuário achar necessário, ele poderá ser invocado já na inicialização do
sistema.

Toda a atividade deste script é registrada no arquivo de log "backup-host.log"
localizado no mesmo diretório onde se encontra este script. Maiores informações
podem ser obitdas no arquivo README.

Sua sintaxe de uso é:

    backup_host -h                    : para exibir informações

    sudo backup_host.py

Autor: Herlon Ayres Camargo
Data: 16/10/2012
'''

import daemon
import pickle
import socket
import ssl
from sys import argv
from time import sleep
from settings import *
from modules.compacta import compacta
from modules.cria_socket import cria_socket
from modules.gera_log import gera_log


def backup():
    ''' Função que recebe do servidor de backup uma relação de arquivos que
    serão becapeados e devolve a esse servidor um arquivo compactado contendo
    todos os arquivos solicitados, além de armazenar localmente uma cópia desse
    arquivo. Antes de atender a solicitação do servidor de backup, verifica se
    a senha informada está correta.
    '''
    # Cria socket
    s_ssl = cria_socket(PORTA, CHAVE_PRIVADA, CERTIFICADO)

    # Loop que permite o script ficar a espera de conexão do servidor de backup
    while True:
        # Recebe solicitação de conexão
        con, info_cliente = s_ssl.accept()
        gera_log('Conexão estabelecida por {}'.format(info_cliente))

# 1a. conexão: RECEBENDO ======================================================
        # Recebe a senha fornecida pelo servidor de backup
        try:
            dados = con.recv(128)
        except ssl.SSLError:
            gera_log('Conexão encerrada com {}'.format(info_cliente))
            con.close()
            continue

# 2a. conexão: ENVIANDO =======================================================
        # Verifica se a senha está correta
        if dados == SENHA:
            try:
                con.send('Sucesso na autenticação')
                gera_log('Sucesso na autenticação')
            except ssl.SSLError:
                gera_log('Conexão encerrada por {}'.format(info_cliente))
                con.close()
                continue
        else:
            sleep(10)
            try:
                con.send('Senha incorreta')
                gera_log('Senha incorreta')
            except ssl.SSLError:
                gera_log('Conexão encerrada por {}'.format(info_cliente))
                con.close()
                continue
            gera_log('Conexão encerrada com {}'.format(info_cliente))
            con.close()
            continue

# 3a. conexão: RECEBENDO ======================================================
        # Recebe uma tupla com a relação de arquivos a serem compactados
        try:
            dados = con.recv(1024)
        except ssl.SSLError:
            gera_log('Conexão encerrada com {}'.format(info_cliente))
            con.close()
            continue
        arquivos = pickle.loads(dados)

        # Realiza compactação dos arquivos e obtem o nome do arquivo de backup
        compactado = compacta(arquivos, LOCAL)

# 4a. conexão: ENVIANDO =======================================================
        # Informa ao servidor de backup o nome do arquivo de backup
        try:
            con.send(compactado)
        except:
            gera_log('Erro ao enviar nome de arquivo ao servidor')
            con.close()
            continue

# 5a. conexão: ENVIANDO =======================================================
        # Transfere o arquivo compactado
        try:
            with open(compactado, 'rb') as f:
                for i in f:
                    con.send(i)
        except:
            gera_log('Erro ao enviar arquivo compactado')
            con.close()
            continue

        gera_log('Arquivo {0} enviado ao servidor em {1}'
                 .format(compactado, info_cliente))

        # Encerra ciclo de conexões de uma solicitação de backup
        con.close()
        gera_log('Conexão com o servidor {} encerrada'.format(info_cliente))

    # Fecha o socket usado para transmissão
    s_ssl.close()


if __name__ == '__main__':
    # Verifica se foi passado algum parâmetro
    if len(argv) != 1:
        exit('Forma de uso: sudo ./backup_host.py')

    # Coloca este script rodando como um daemon
    with daemon.DaemonContext():
        backup()
