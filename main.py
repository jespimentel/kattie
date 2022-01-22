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
  print('Objeto soup criado.\nCódigo:', doe.status_code)

# Texto e estrutura do DOE
texto_doe = soup.find(class_='mpsp-daily-official').getText()
texto_doe = trata_palavras(texto_doe)
lista_doe = texto_doe.split('\n') # Gera a lista com o conteúdo do DOE
estrutura = soup.find_all('h1') # Gera a lista com a estrutura do DOE

# Pesquisa individualizada
for nome in good_guys:
  email = good_guys[nome]['email']
  data = today.replace('_', '/')
  assunto = f"Leitura automatizada do Diário Oficial de {data} para {nome}"
  content = f"""Prezado(a) {nome},\n\nSegue o resultado da leitura automatizada do Diário Oficial de {data}, obtido pelo link: {url}\n\n*********************************\n"""
  content += 'ESTRUTURA DO DOE:\n\n'
  for i in estrutura:
    if i.get_text() != 'Navegação':
      content += i.get_text()+'\n'
  content += '\n*********************************\n'
  content += 'PESQUISA NOMINAL:\n\n'
  resultados, n_corrrespondencias = encontra_correspondencias(good_guys[nome]['aliases'], lista_doe)
  content += f'Nº de ocorrências com o seu nome: {n_corrrespondencias}\n\n'
  for r in resultados:
    content += r + '\n\n'
  content += '\n*********************************\n'
  content +='PESQUISA POR PALAVRAS-CHAVE: '
  palavras_chave = good_guys[nome]['pesquisa']
  for palavra in palavras_chave:
    if palavra == palavras_chave[-1]:
      content += palavra
    else:
      content += palavra + ' - '
  content +=  '\n\n'
  resultados, n_corrrespondencias = encontra_correspondencias(good_guys[nome]['pesquisa'], lista_doe)
  content += f'Nº de ocorrências com a(s) palavra(s)-chave fornecida(s): {n_corrrespondencias}\n\n'
  for r in resultados:
    content += r + '\n\n'
  content += '\n_________________________________\n\n'
  content += 'Programa experimental da Promotoria de Piracicaba/SP. Algumas publicações podem não estar completas.\n'
  content += 'Responda ao e-mail se quiser cancelar o "serviço" ou acrescentar palavras-chave à sua pesquisa individualizada.\n'
  content += 'Conheça: github.com/jespimentel\n\n\n'
  # Testes
  print(f'\n\ne-mail para {email}')
  print ('_'*40 + '\n')
  print (content)
  envia_email(email,assunto, content)
