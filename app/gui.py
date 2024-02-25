import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import shutil
import matplotlib.pyplot as plt
from app.app_logic import get_weather_data_links, download_weather_data, list_city_names

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x300")
        self.root.title("Análise de Dados Meteorológicos INMET")
        
        # Estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#e1d8b2')
        self.style.configure('TButton', background='#d9d0ac')
        self.style.configure('TLabel', background='#e1d8b2')
        self.style.configure('TCombobox', background='#ffffff')
        
        self.create_widgets()

    def create_widgets(self):
        # Frames
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        self.left_frame = ttk.Frame(self.bottom_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = ttk.Frame(self.bottom_frame)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Widgets
        self.year_label = ttk.Label(self.top_frame, text="Selecione o ano:", font=('Arial', 10, 'bold'))
        self.year_label.grid(row=0, column=0, padx=10, pady=10)

        self.year_combobox = ttk.Combobox(self.top_frame, state="readonly", width=10, font=('Arial', 10))
        self.year_combobox.grid(row=0, column=1, padx=10, pady=10)
        
        self.download_button = ttk.Button(self.top_frame, text="Baixar Dados", command=self.download_data)
        self.download_button.grid(row=0, column=2, padx=10, pady=10)

        self.city_label = ttk.Label(self.left_frame, text="Selecione a cidade:", font=('Arial', 10, 'bold'))
        self.city_label.grid(row=0, column=0, padx=10, pady=10)

        self.city_combobox = ttk.Combobox(self.left_frame, state="readonly", width=25, font=('Arial', 10))
        self.city_combobox.grid(row=0, column=1, padx=10, pady=10)
        
        
        self.plot_button = ttk.Button(self.left_frame, text="Gerar Gráficos", command=self.plot_data)
        self.plot_button.grid(row=1, columnspan=2, padx=10, pady=10)

        self.close_button = ttk.Button(self.left_frame, text="Fechar Aplicação", command=self.close_application)
        self.close_button.grid(row=2, columnspan=2, padx=10, pady=10)

        # Preencher a combobox com os anos disponíveis
        self.populate_year_combobox()

    def populate_year_combobox(self):
        # Obtém os links dos dados meteorológicos
        weather_links = get_weather_data_links()

        # Verifica se a lista de links não é None antes de prosseguir
        if weather_links is not None:
            # Extrai os anos dos links e adiciona à combobox
            years = [link.split("/")[-1].split(".")[0] for link in weather_links]
            self.year_combobox["values"] = years
        else:
            print("Não foi possível obter os links dos dados meteorológicos. Verifique sua conexão com a internet ou tente novamente mais tarde.")

    def download_data(self):
        selected_year = self.year_combobox.get()
        directory = "dados_meteorologicos"  # Diretório onde os dados serão salvos
        weather_links = get_weather_data_links()
        for link in weather_links:
            if selected_year in link:
                download_weather_data(link, directory)
        # Atualiza a lista de anos na combobox após o download
        self.populate_year_combobox()
        # Atualiza a lista de cidades na combobox após o download
        cities_directory = os.path.join(directory, selected_year)  # Diretório onde os dados foram extraídos
        cities = list_city_names(cities_directory)
        self.city_combobox["values"] = cities
        
    def plot_data(self):
        selected_city_file = self.city_combobox.get()
        selected_year = self.year_combobox.get()
        directory = os.path.join("dados_meteorologicos", selected_year)

        # Verificar se o diretório existe
        if os.path.exists(directory) and os.path.isdir(directory):
            file_path = os.path.join(directory, selected_city_file)
            
            # Verificar se o arquivo existe
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Ler o arquivo CSV
                data = pd.read_csv(file_path, sep=';', encoding='ISO-8859-1', skiprows=8)
                
                # Extrair mês e ano da coluna de data
                data['Data'] = pd.to_datetime(data['DATA (YYYY-MM-DD)'], format='%Y-%m-%d')
                data['Mês'] = data['Data'].dt.month
                data['Ano'] = data['Data'].dt.year
                
                # Calcular a média da temperatura máxima por mês
                max_temp_monthly = data.groupby(['Ano', 'Mês'])['TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)'].max()
                
                # Calcular a máxima das precipitações por mês
                max_precip_monthly = data.groupby(['Ano', 'Mês'])['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].max()
                
                # Resetar o índice para tornar os índices de Ano e Mês em colunas
                max_temp_monthly_reset = max_temp_monthly.reset_index()
                max_precip_monthly_reset = max_precip_monthly.reset_index()
                
                # Converter os índices em uma coluna 'Data' formatada como 'YYYY-MM'
                max_temp_monthly_reset['Data'] = max_temp_monthly_reset['Ano'].astype(str) + '-' + max_temp_monthly_reset['Mês'].astype(str).str.zfill(2)
                max_precip_monthly_reset['Data'] = max_precip_monthly_reset['Ano'].astype(str) + '-' + max_precip_monthly_reset['Mês'].astype(str).str.zfill(2)
                
                # Criar figuras e eixos para os gráficos
                fig, axs = plt.subplots(2, 1, figsize=(10, 8))
                
                # Gráfico da temperatura máxima por mês
                axs[0].plot(max_temp_monthly_reset['Data'], max_temp_monthly_reset['TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)'], marker='o', linestyle='-')
                axs[0].set_title('Temperatura Máxima por Mês')
                axs[0].set_xlabel('Data')
                axs[0].set_ylabel('Temperatura Máxima (°C)')

                # Gráfico da máxima das precipitações por mês
                axs[1].plot(max_precip_monthly_reset['Data'], max_precip_monthly_reset['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], marker='o', linestyle='-')
                axs[1].set_title('Máxima Precipitação por Mês')
                axs[1].set_xlabel('Data')
                axs[1].set_ylabel('Máxima Precipitação (mm)')

                
                # Ajustar layout
                plt.tight_layout()
                
                # Exibir os gráficos
                plt.show()
            else:
                print(f"O arquivo {selected_city_file} não existe no diretório.")
        else:
            print("O diretório especificado não existe.")

    def close_application(self):
        # Fechar a aplicação
        self.root.destroy()
        
        # Excluir os arquivos baixados
        directory = "dados_meteorologicos"
        if os.path.exists(directory):
            shutil.rmtree(directory)

    def run(self):
        self.root.mainloop()

# Exemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    app.run()
