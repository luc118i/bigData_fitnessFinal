import os
import glob
import pandas as pd
import re

def extract_flavor_from_name(name):
    match = re.search(r'sabor\s+(\w+(?:\s+\w+)*)', name, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return 'Sabor não disponível'

def extract_weight_from_name(name):
    match = re.search(r'(\d+\.?\d*\s*(?:kg|g))', name, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return 'Peso líquido não disponível'

def combine_csv_files(input_folder, output_file):
    all_files = glob.glob(os.path.join(input_folder, "*.csv"))
    combined_data = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
    combined_data.to_csv(output_file, index=False, encoding='utf-8')
    return combined_data

def clean_data(data):
    data['Sabor'] = data.apply(lambda row: extract_flavor_from_name(row['Name']) if row['Sabor'] == 'Sabor não disponível' else row['Sabor'], axis=1)
    data['Peso líquido'] = data.apply(lambda row: extract_weight_from_name(row['Name']) if row['Peso líquido'] == 'Peso líquido não disponível' else row['Peso líquido'], axis=1)
    cleaned_data = data[(data['Sabor'] != 'Sabor não disponível') & (data['Peso líquido'] != 'Peso líquido não disponível')]
    return cleaned_data

def main():
    input_folder = r'C:\Users\Lucas Luiz\OneDrive\Documentos\Raspagem'
    combined_file = os.path.join(input_folder, 'combined_data.csv')

    # Combinar todos os arquivos CSV em um único arquivo
    combined_data = combine_csv_files(input_folder, combined_file)
    print(f"Dados combinados salvos em {combined_file}")

    # Limpar os dados
    cleaned_data = clean_data(combined_data)
    cleaned_file = os.path.join(input_folder, 'cleaned_data.csv')
    cleaned_data.to_csv(cleaned_file, index=False, encoding='utf-8')
    print(f"Dados limpos salvos em {cleaned_file}")

if __name__ == "__main__":
    main()
