import requests
import json
import pandas as pd
import schedule
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials



def job():
  print("************ CONNEXION EN COURS ************")
  headers = {
      "X-Recharge-Access-Token": "73de2b55852f19424c17a24d70ff175dca5893609e480d38901bf34a",
      "Accept":"application/json",
      "Content-Type":"application/json"
  }
  url = "https://api.rechargeapps.com/subscriptions"
  params = {
      "limit": 250,
      "page": 1
  }
  request_result = requests.get(url, params=params, headers=headers)
  request_result_json = request_result.json()

  # On verifie que la communication s'effectue correctement, en HTTP le code 200 veut dire OK

  if request_result.status_code != 200:
      print("Erreur, l'URL n'a pas pu etre charge")
  else:
      print("Connexion avec le serveur: OK")

  # Le principal probleme des requetes HTTP c'est que seule une page peut etre obtenue a la fois
  # Chaque page contient seulement 250 resultats au maximum, donc pour obtenir toutes les donnees il faut
  # faire une requete pour toutes les pages, une par une, d'ou la boucle while
  # Tout a ete lu quand la page demandee affiche une liste vide []


  j = 1
  result_list = []

  while request_result_json["subscriptions"]!=[]:
      result_list.append(request_result_json["subscriptions"])
      j = j+1
      params = {
          "limit": 250,
          "page": j
      }
      request_result = requests.get(url, params=params, headers=headers)
      request_result_json = request_result.json()

  # Maintenant qu'on a la liste contenant toutes les donnees, on compte le nombre de status actifs
  # request_result est donc une liste contenant : i-1 listes de 250 elements (boucle 1)
  # + 1 liste d'un nombre d'elements < 250 (boucle 2)

  number_of_active_folks = 0

  # boucle 1
  for k in range(0,j-3):
      for l in range(0,249):
          if result_list[k][l]['status'] == 'ACTIVE':
              number_of_active_folks = number_of_active_folks + 1

  # boucle 2
  for m in range(0,len(result_list[j-2])):
      if result_list[j-2][m]['status'] == 'ACTIVE':
          number_of_active_folks = number_of_active_folks + 1

  # Le resultat
  print("Il y a aujourd'hui", number_of_active_folks, "utilisateurs actifs")

  # Remplissage du spreadsheet
  scope = ['https://spreadsheets.google.com/feeds']

  credentials = ServiceAccountCredentials.from_json_keyfile_name('API recharge-a81b60c4be53.json', scope)

  gc = gspread.authorize(credentials)

  sheet = gc.open('Joone Analytics Data').worksheet('Recharge')


  # Il faut trouver le bon index dans le tableau, c'est plus fiable qu'utiliser une variable globale a incrementer

  index = 1
  while(sheet.cell(index,1).value != ""):
      index = index + 1

  today = datetime.date.today()

  sheet.update_cell(index,1, number_of_active_folks)
  sheet.update_cell(index,2, today)


# Automatisation : le programme se lancera à 10h30 tous les jours

schedule.every().day.at("10:30").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
