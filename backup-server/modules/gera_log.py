# encoding: utf-8
''' Módulo responsável pela gravação do registro das atividades realizadas no
servidor.

Autor: Herlon Camargo

Data: 16/10/2012
'''

from datetime import datetime


def gera_log(texto):
    ''' Função que registra no servidor as atividades realizadas referentes ao
    backup. Recebe um "texto" que, junto com a data e o horário, serão escritos
    no arquivo "backup-server.log", localizado no diretório corrente onde o
    script "backup_server.py" foi executado.
    '''
    # Grava o registro das atividades
    try:
        with open('backup-server.log', 'a') as f:
            mensagem = '{0} {1}\n'.format(
                             datetime.now().strftime('%b %d %H:%M:%S'), texto)
            f.write(mensagem)
    except IOError as msgError:
        print msgError
