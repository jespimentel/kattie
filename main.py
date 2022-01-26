#!.\env\Scripts\python.exe

import requests
from bs4 import BeautifulSoup
from datetime import date
import urllib3
import yagmail
import unidecode
from dados import good_guys, usuario, senha 

def trata_palavras (texto):
  """Tira os acentos, caracteres º e ª e converte o texto em letras maiúsculas"""
  texto = texto.replace('º', '')
  texto = texto.replace('ª', '')
  texto = texto.replace('    ', ' ') # 4
  texto = texto.replace('   ', ' ') # 3
  texto = texto.replace('  ', ' ') # 2
  return unidecode.unidecode(texto).upper()

def encontra_correspondencias(lista_alias, lista_doe):
  """Encontra a correspondência entre os textos contidos em lista e as publicações do DOE e o número de ocorrências"""
  resultados=[]
  n_correspondencias = 0
  for publicacao in lista_doe:
      for nome in lista_alias:
          if trata_palavras(nome) in publicacao:
              resultados.append(publicacao)
              n_correspondencias += 1
  return (resultados, n_correspondencias)

def envia_email (destinatario, assunto, corpo_email):
  """Envia e-mail a partir do destinatário e corpo de mensagem informados"""
  try:
    yag = yagmail.SMTP(usuario,senha)
    yag.send(destinatario, assunto, corpo_email)
    print('e-mail enviado para '+ destinatario)
  except:
    print('e-mail não enviado para '+ destinatario)

# Cria a url de hoje:
today = date.today().strftime('%d_%m_%Y')
url_base = 'https://www.mpsp.mp.br/w/do_'
url = url_base + today

# Para testes:
# url = 'https://www.mpsp.mp.br/w/do_22_01_2022'

# Faz o request
urllib3.disable_warnings()
doe = requests.get(url, verify=False)
if doe.status_code != 200:
  print (f'Url gerada: {url}')
  print ('DOE não encontrado. Código:', doe.status_code)
  print ('Tente outra vez mais tarde.')
  quit()
else:
  soup = BeautifulSoup(doe.text, 'html.parser')
  print(f'Objeto soup criado.\nCódigo: {doe.status_code}\n')

# Texto e estrutura do DOE
texto_doe = soup.find(class_='mpsp-daily-official').getText()
texto_doe = texto_doe.replace ('\n\n', '\n')
texto_tratado = trata_palavras(texto_doe)
lista_doe = texto_tratado.split('\n') # Gera a lista com o conteúdo do DOE
estrutura = soup.find_all('h1') # Gera a lista com a estrutura do DOE

# Pesquisa individualizada
for nome in good_guys:
  email = good_guys[nome]['email']
  data = today.replace('_', '/')
  assunto = f"Pesquisa automatizada do Diário Oficial de {data} para {nome}"
  content = f"""Prezado {nome},\n\nSegue o resultado da pesquisa automatizada do Diário Oficial de {data}, obtido pelo link: {url} \n\n***********************************\n"""
  content += 'PESQUISA NOMINAL\n\n'
  resultados, n_corrrespondencias = encontra_correspondencias(good_guys[nome]['aliases'], lista_doe)
  content += f'Nº de ocorrências com o seu nome: {n_corrrespondencias}\n'
  if n_corrrespondencias != 0:
    n=0
    for r in resultados:
      content += '\n'
      n +=1
      content += str(n) + ') '+ r + '\n'
  content += '\n\n***********************************\n'
  content +='PESQUISA POR PALAVRAS-CHAVE/FRASES\n\n'
  palavras_chave = good_guys[nome]['pesquisa']
  for palavra in palavras_chave:
    content += '* ' + palavra + f': {texto_tratado.count(trata_palavras(palavra))}\n'
  content += '\n***********************************\n'
  content += 'ESTRUTURA DO DOE\n\n'
  for i in estrutura:
    if i.get_text() != 'Navegação':
      content += '* ' + i.get_text()+'\n'
  content += '\n***********************************\n'
  content += f'Programa experimental da Promotoria de Justiça de Piracicaba/SP (Usuários ativos: {len(good_guys)}).\n'
  content += 'Responda ao e-mail se quiser cancelar o "serviço" ou alterar/acrescentar alíases, palavras-chave ou frases para a pesquisa individualizada.\n'
  content += 'Conheça: github.com/jespimentel\n\n'
  content += '\n_________________________________\n\n'
  content += 'Texto do Diário Oficial. Use "Ctr-F" para localizar as publicações de seu interesse.\n'
  content += texto_doe
  
  # Printa ou envia o e-mail
  """ print ('\n' + email)
  print ('\n' + content)
  print ('\n' + '='* 40) """
  envia_email(email,assunto, content)
