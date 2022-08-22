import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import selectorlib
from selectorlib import Extractor

# Iniciamos el Selenium
options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--mute-audio")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(
    executable_path=r"chromedriver.exe",
    options=options)
driver.get("https://web.facebook.com/")
time.sleep(5)

# Inicio de sesion para entrar a Facebook
driver.find_element(By.XPATH, "//input[contains(@id,'email')]").send_keys("veronicalizeth3@gmail.com")
driver.find_element(By.XPATH, "//input[contains(@id,'pass')]").send_keys("zafiritob16")
driver.find_element(By.XPATH, "//button[contains(@name,'login')]").click()
time.sleep(10)

# Con las credenciales ya listas, entremos a un perfil
driver.get("https://web.facebook.com/RicardoSalinasPliego")
time.sleep(10)
bajar = "window.scrollTo(0," + str(100) + ")"  # para que cargue un poco la página
driver.execute_script(bajar)
time.sleep(10)

df_n = []  # lista para guardar todos los df con distintas publicaciones
comentarios = []  # Lista donde guardaremos los comentarios en formato dict
posts = []
links = []

# Recorremos las publicaciones que queremos scrapear
for i in range(1, 5):  # solo queremos las primeras 5
    try:
        element = driver.find_element(By.XPATH,
                                      "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div["
                                      "4]/div[2]/div/div[2]/div[2]/div[{0}]/div/div/div/div/div/div/div/div/div/div/div["
                                      "8]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]".format(str(i)))
        element.click()
        time.sleep(5)

        # Volvemos al inicio de la publicacion para evitar problemas
        driver.execute_script("scroll(0,0);")

        # Obtenemos el link de la publicacion para usarlo como id
        try:
            link_root = driver.find_element(By.XPATH,
                                            "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div["
                                            "1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div["
                                            "2]/div/div[2]/div/div[2]/span/span/span[2]/span/a")
        except Exception as e:
            print(e)
            print('Exception por publicacion con video')
            link_root = driver.find_element(By.XPATH,
                                            "/html/body/div[1]/div/div[1]/div/div[4]/div/div[3]/div[1]/div/div["
                                            "3]/div[2]/div/div/div[2]/div[1]/div/div[1]/div/div/div[1]/div[1]/div["
                                            "2]/div/div[2]/span/span/span[2]/span/a")

        print(link_root.get_attribute(("href")))
        links.append(link_root.get_attribute("href"))
        time.sleep(5)

        # Obtenemos el texto de la publicacion
        texto = driver.find_element(By.XPATH, "//div[contains(@data-ad-preview,'message')]")
        posts.append(texto.text)

        # Obtener los datos de cada comentario
        # Obtenemos el HTML del driver, extraemos la informacion con SelectorLib Extractor.
        raw_html = driver.page_source  # HTML de la pag
        extracted_text = Extractor.from_yaml_file('selectorlib/post_salinas.yml')  # Extraccion de la info
        raw_data = extracted_text.extract(raw_html)  # Datos en crudo
        data = raw_data['coments']  # Guardamos la informacion de los comentarios
        comentarios.append(data)

        # Volvemos a la publicacion original para ir al segundo post
        driver.get("https://web.facebook.com/RicardoSalinasPliego")
        time.sleep(5)

        if i == (2, 3):
            # Cargamos mas la pagina para los posts mas viejos, bajando y subiendo un poco
            bajar = "window.scrollTo(0," + str(1000) + ")"  # para que cargue un poco la página
            driver.execute_script(bajar)
            time.sleep((5))
            bajar = "window.scrollTo(0," + str(950) + ")"  # para que cargue un poco la página
            driver.execute_script(bajar)
        elif i == (4, 5):
            bajar = "window.scrollTo(0," + str(1000) + ")"  # para que cargue un poco la página
            driver.execute_script(bajar)
            time.sleep((5))
            bajar = "window.scrollTo(0," + str(950) + ")"  # para que cargue un poco la página
            driver.execute_script(bajar)
            bajar = "window.scrollTo(0," + str(2000) + ")"  # para que cargue un poco la página
            driver.execute_script(bajar)
            bajar = "window.scrollTo(0," + str(1950) + ")"  # para que cargue un poco la página
            driver.execute_script(bajar)
    except Exception as e:
        # Nos devuelve el error y continua a la siguiente publicacion
        print("Fallo por publicacion especial")
        print(e)
        continue

# Lista donde se guardaran todos los Df con la informacion
comentarios_n = []

# Recorremos todos los dict y los transformamos en df
for j in range(len(comentarios)):
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in comentarios[j].items()]))
    df["post"] = posts[j]
    df["id"] = links[j]
    comentarios_n.append(df)

# Union de todos los df de cada publicacion
df = pd.concat(comentarios_n)  # Union de todos los df

# Limpiamos el df para evitar errores de formato
df.replace('\n',
           '',
           regex=True,
           inplace=True)

# Exportamos el df a formato csv para su analisis
df.to_csv('bases/richi.csv', sep='|',
          encoding='utf-16',
          na_rep='Na',
          index=False)
