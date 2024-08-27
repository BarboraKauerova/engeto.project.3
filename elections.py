

'''
      elections.py: třetí projekt do Engeto Online Python Akademie
     
      author = Barbora Kauerova
      discord = barborakauerova_12439
      email = kauerova.barbora.bk@gmail.com
      '''

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd



def fetch_data(url):
    """Fetch the HTML content from the URL."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Unable to fetch data from {url}.")
        sys.exit(1)
    return response.text

def parse_data(html):
    """Parse the HTML content and extract voting data."""
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')[2:]  # Přeskočit řádky záhlaví

    results = []
    for row in rows:
        columns = row.find_all('td')
        
        # Ověření, že řádek má správný počet sloupců
        if len(columns) < 3:
            continue  # přeskočíme řádek, který nemá dostatek sloupců

        code = columns[0].text.strip()
        name = columns[1].text.strip()

        # Získej data z hlasovací schránky
        voting_url = 'https://volby.cz/pls/ps2017nss/' + columns[2].find('a')['href']
        voting_page = fetch_data(voting_url)
        voting_soup = BeautifulSoup(voting_page, 'html.parser')

        voters = voting_soup.find('td', headers='sa2')
        voters = voters.text.replace('\xa0', '') if voters else 'N/A'

        envelopes = voting_soup.find('td', headers='sa3')
        envelopes = envelopes.text.replace('\xa0', '') if envelopes else 'N/A'

        valid_votes = voting_soup.find('td', headers='sa6')
        valid_votes = valid_votes.text.replace('\xa0', '') if valid_votes else 'N/A'

        # Najdi všechny strany a jejich hlasy
        parties = voting_soup.find_all('td', headers='t1sa2 t1sb3')
        votes = voting_soup.find_all('td', headers='t2sa2 t2sb3')
        party_votes = {party.text.strip(): vote.text.replace('\xa0', '') for party, vote in zip(parties, votes)}

        results.append({
            'code': code,
            'name': name,
            'voters': voters,
            'envelopes': envelopes,
            'valid_votes': valid_votes,
            **party_votes
        })

    return results

def save_to_csv(data, filename):
    """Save the extracted data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')

def main():
    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments.")
        print("Usage: python elections.py <url> <output_file>")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2]

    if not url.startswith('http'):
        print("Error: The first argument must be a valid URL.")
        sys.exit(1)

    html = fetch_data(url)
    data = parse_data(html)
    save_to_csv(data, output_file)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
