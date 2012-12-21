# encoding: utf-8
''' Módulo responsável pela compactação de arquivos para backup

Autor: Herlon Camargo

Data: 16/10/2012
'''

import glob
import tarfile
from gera_log import gera_log
from datetime import datetime


def compacta(arquivos, local, ip):
    ''' Função que recebe uma tupla em "arquivos" com os nomes dos arquivos que
    serão compactados, compacta com bzip2, salva o arquivo compactado em
    "local", e retorna o nome do arquivo compactado.
    '''
    # Verifica se arquivos é uma tupla
    if not isinstance(arquivos, tuple):
        gera_log('Função "compacta" não recebeu tupla com nomes de aruivos')
        return 'Erro: Função deve receber uma tupla'

    # Formata o nome do arquivo de backup
    nomebackup = 'backup-{}.tar.bz2'.format(\
                                datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

    # Ajusta o caminho do diretório onde o backup será armazendado localmente,
    # completando com barra "/" no final se necessário
    if not local.find('/', -1) == len(local) - 1:
        local = '{}/'.format(local)

    # Cria o arquivo compactado
    try:
        with tarfile.open('{0}{1}'.format(local, nomebackup), 'w:bz2') as tbf:
            for i in arquivos:
                for j in glob.iglob(i):
                    tbf.add(j)
    except IOError as msgError:
        gera_log(msgError)
        return msgError

    return '{0}{1}'.format(local, nomebackup)
