import os
import requests
from bs4 import BeautifulSoup
import zipfile

def get_weather_data_links():
    url = "https://portal.inmet.gov.br/dadoshistoricos"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_='post-preview')
        
        weather_links = []
        for article in articles:
            links = article.find_all('a', href=True)
            zip_links = [link['href'] for link in links if link['href'].endswith('.zip')]
            weather_links.extend(zip_links)
            
        return weather_links
    else:
        print("Falha ao acessar o site.")
        return None

def download_weather_data(link, directory):
    filename = link.split('/')[-1]
    file_path = os.path.join(directory, filename)

    # Criar o diretório se ele não existir
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(file_path):
        print(f'Baixando {filename}...')
        file_response = requests.get(link)
        with open(file_path, 'wb') as f:
            f.write(file_response.content)
        print(f'{filename} baixado com sucesso.')

        # Extrair o arquivo zip
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(directory)
        
        # Excluir o arquivo zip após a extração
        os.remove(file_path)

        print(f'{filename} extraído e excluído.')
    else:
        print(f'{filename} já foi baixado e extraído.')
        
def list_city_names(directory):
    city_names = []
    # Verificar se o diretório existe
    if os.path.exists(directory):
        # Iterar sobre os arquivos no diretório
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            # Verificar se é um arquivo
            if os.path.isfile(file_path):
                # Adicionar o nome do arquivo à lista
                city_names.append(file_name)
    return city_names

# Chamando a função principal para baixar os dados meteorológicos
if __name__ == "__main__":
    directory = "dados_meteorologicos"  # Definindo o nome do diretório
    weather_links = get_weather_data_links()
    for link in weather_links:
        download_weather_data(link, directory)
