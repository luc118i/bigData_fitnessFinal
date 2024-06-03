from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os
import re

def close_cookie_banner(driver):
    try:
        cookie_banner_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceitar')]")
        cookie_banner_button.click()
        time.sleep(2)
        print("Banner de cookies fechado.")
    except:
        try:
            cookie_banner_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
            cookie_banner_button.click()
            time.sleep(2)
            print("Banner de cookies fechado.")
        except:
            print("Banner de cookies não encontrado ou não foi possível fechar.")

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

def scrape_whey_data():
    url = "https://lista.mercadolivre.com.br/whey-protein"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(2)

    driver.implicitly_wait(10)
    close_cookie_banner(driver)  # Fechar o banner de cookies na página principal

    whey_data = []
    batch_size = 10
    batch_count = 1

    while True:
        products = driver.find_elements(By.CLASS_NAME, 'ui-search-layout__item')

        for index, product in enumerate(products):
            name = product.find_element(By.CLASS_NAME, 'ui-search-item__title').text.strip()
            flavor_from_name = extract_flavor_from_name(name)
            weight_from_name = extract_weight_from_name(name)

            price_element = product.find_elements(By.CLASS_NAME, 'andes-money-amount__fraction')
            price = price_element[0].text.strip() if price_element else 'Preço não disponível'

            rating_element = product.find_elements(By.CLASS_NAME, 'ui-search-reviews__rating-number')
            rating = rating_element[0].text.strip() if rating_element else 'Avaliação não disponível'

            product_link = product.find_element(By.CLASS_NAME, 'ui-search-link').get_attribute('href')
            driver.execute_script("window.open(arguments[0], '_blank');", product_link)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)

            close_cookie_banner(driver)  # Fechar o banner de cookies na página do produto

            characteristics = {
                'Marca': 'Marca não disponível',
                'Sabor': flavor_from_name,
                'Peso líquido': weight_from_name
            }

            # Clicar no botão "Ver características"
            try:
                ver_caracteristicas_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Ver características')]")
                driver.execute_script("arguments[0].scrollIntoView(true);", ver_caracteristicas_button)
                ver_caracteristicas_button.click()
                time.sleep(2)
                print(f"Clicou no botão 'Ver características' para o produto: {name}")
            except Exception as e:
                print(f"Erro ao clicar no botão 'Ver características' para o produto {name}: {e}")

            try:
                # Marca
                try:
                    marca_element = driver.find_element(By.XPATH, "//span[contains(@class, 'andes-table__column--value') and preceding-sibling::span[text()='Marca']]")
                    characteristics['Marca'] = marca_element.text.strip()
                except:
                    marca_element = driver.find_elements(By.XPATH, "//span[contains(text(),'Marca')]/following-sibling::span")
                    characteristics['Marca'] = marca_element[0].text.strip() if marca_element else 'Marca não disponível'

                # Sabor no campo Sabor
                if characteristics['Sabor'] == 'Sabor não disponível':
                    try:
                        sabor_element = driver.find_element(By.XPATH, "//span[@id='picker-label-FLAVOR']")
                        characteristics['Sabor'] = sabor_element.text.strip()
                    except Exception as e:
                        print(f"Erro ao encontrar 'Sabor' no campo Sabor para o produto {name}: {e}")

                # Peso líquido
                if characteristics['Peso líquido'] == 'Peso líquido não disponível':
                    try:
                        peso_liquido_element = driver.find_element(By.XPATH, "//span[contains(@class, 'andes-table__column--value') and preceding-sibling::span[text()='Peso líquido']]")
                        characteristics['Peso líquido'] = peso_liquido_element.text.strip()
                    except:
                        peso_liquido_element = driver.find_elements(By.XPATH, "//tr[th[contains(text(),'Peso líquido')]]/td")
                        characteristics['Peso líquido'] = peso_liquido_element[0].text.strip() if peso_liquido_element else 'Peso líquido não disponível'

                # Outra abordagem para tentar encontrar o sabor e peso líquido
                if characteristics['Sabor'] == 'Sabor não disponível':
                    try:
                        sabor_element = driver.find_element(By.XPATH, "//div[contains(@class, 'ui-pdp-specs__table__column') and text()='Sabor']/following-sibling::div")
                        characteristics['Sabor'] = sabor_element.text.strip()
                    except Exception as e:
                        print(f"Erro ao encontrar 'Sabor' na terceira tentativa para o produto {name}: {e}")

                if characteristics['Peso líquido'] == 'Peso líquido não disponível':
                    try:
                        peso_liquido_element = driver.find_element(By.XPATH, "//div[contains(@class, 'ui-pdp-specs__table__column') and text()='Peso líquido']/following-sibling::div")
                        characteristics['Peso líquido'] = peso_liquido_element.text.strip()
                    except Exception as e:
                        print(f"Erro ao encontrar 'Peso líquido' na terceira tentativa para o produto {name}: {e}")

                # Prints de depuração
                print(f"Produto: {name}")
                print(f"Marca: {characteristics['Marca']}")
                print(f"Sabor: {characteristics['Sabor']}")
                print(f"Peso líquido: {characteristics['Peso líquido']}")
                print("="*40)

            except Exception as e:
                print(f"Erro ao extrair características para o produto {name}: {e}")

            whey_data.append({
                'Name': name,
                'Price': price,
                'Rating': rating,
                **characteristics
            })

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

            # Salvar em lotes de 10 produtos
            if (index + 1) % batch_size == 0:
                save_to_csv(whey_data, f'raspagem_{batch_count}.csv')
                whey_data.clear()
                batch_count += 1

        # Verificar se há uma próxima página e clicar no botão "Seguinte"
        try:
            next_button = driver.find_element(By.XPATH, "//span[text()='Seguinte']")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            next_button.click()
            time.sleep(3)
        except:
            print("Não há mais páginas para processar.")
            break

    driver.quit()

    # Salvar o restante dos produtos se houver
    if whey_data:
        save_to_csv(whey_data, f'raspagem_{batch_count}.csv')

def save_to_csv(data, filename):
    directory = r'C:\Users\Lucas Luiz\OneDrive\Documentos\Raspagem'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Price', 'Rating', 'Marca', 'Sabor', 'Peso líquido']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    scrape_whey_data()
    print("Raspagem concluída e dados salvos.")
