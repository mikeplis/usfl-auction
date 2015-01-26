from bs4 import BeautifulSoup
import re
import sys
sys.path.append('/Users/mplis/personal/workspace/dlf_rankings_scrape')
import nfdl_keepers
sys.path.append('/Users/mplis/personal/workspace/python-mfl/mfl')
import api as mfl_api
import csv
from sets import Set


def get_all_bids():
  api = mfl_api.Api(2014)
  api.login(51974, '0015', sys.argv[1])

  current_bids_page = api.opener.open('http://football.myfantasyleague.com/2014/options?L=51974&O=43')
  soup = BeautifulSoup(current_bids_page.read())
  auction_table = soup.find_all('table')[1]
  current_bids = auction_table.find_all('tr')[1:]

  finished_bids_page = api.opener.open('http://football.myfantasyleague.com/2014/options?L=51974&O=102')
  soup2 = BeautifulSoup(finished_bids_page.read())
  auction_table = soup2.find_all('table')[1]
  finished_bids = auction_table.find_all('tr')[1:]

  return (current_bids, finished_bids)

def extract_bids():
  bids = get_all_bids()
  current_bids = bids[0]
  finished_bids = bids[1]
  rankings = nfdl_keepers.dlf_rankings()
  bidding_opened_on = Set()
  with open('usfl_auction.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter = ',')
    x = ['Name', 'Salary', 'Owner', 'ADP', 'Rank', 'Age', 'Position', 'Bidding Order']
    writer.writerow(x)

    for i, bid in enumerate(current_bids):
      d = bid.find_all('td')
      player_info = re.split('[ ,]+', d[0].text.strip())
      salary = re.search('^(\$[\d,]+).*', d[1].text).group(1)
      owner = re.search('(<font.*>)?([\w \.]+)(</font>)?', d[2].img['alt']).group(2)
      if len(player_info) == 5 and player_info[4] != '(R)':
        last_name = ' '.join(player_info[0:2])
        first_name = player_info[2]
      elif player_info[0] != '*':
        last_name = player_info[0]
        first_name = player_info[1]
      else:
        first_name = ' '.join(player_info[2:5])
        last_name = ''
      key = nfdl_keepers.normalize_name('{}, {}'.format(last_name, first_name))
      bidding_opened_on.add(key)
      try:
        ranking = rankings[key]
        x = [ranking['player'], salary, owner, ranking['adp'], ranking['rank'], ranking['age'], ranking['position'], i]
        writer.writerow(x)
      except:
        x = ['{} {}'.format(first_name, last_name), salary, owner, '', '', '', '', i]
        writer.writerow(x)

    for bid in finished_bids:
      # mostly duplicate code from above; only difference is no bidding order
      d = bid.find_all('td')
      player_info = re.split('[ ,]+', d[0].text.strip())
      salary = re.search('^(\$[\d,]+).*', d[1].text).group(1)
      owner = re.search('(<font.*>)?([\w \.]+)(</font>)?', d[2].img['alt']).group(2)
      if len(player_info) == 5 and player_info[4] != '(R)':
        last_name = ' '.join(player_info[0:2])
        first_name = player_info[2]
      elif player_info[0] != '*':
        last_name = player_info[0]
        first_name = player_info[1]
      else:
        first_name = ' '.join(player_info[2:5])
        last_name = ''
      key = nfdl_keepers.normalize_name('{}, {}'.format(last_name, first_name))
      bidding_opened_on.add(key)
      try:
        ranking = rankings[key]
        x = [ranking['player'], salary, owner, ranking['adp'], ranking['rank'], ranking['age'], ranking['position'], '']
        writer.writerow(x)
      except:
        x = ['{} {}'.format(first_name, last_name), salary, owner, '', '', '', '', '']
        writer.writerow(x)


    for k, ranking in rankings.iteritems():
      if k not in bidding_opened_on:
        x = [ranking['player'], '', '', ranking['adp'], ranking['rank'], ranking['age'], ranking['position']]
        writer.writerow(x)

extract_bids()





