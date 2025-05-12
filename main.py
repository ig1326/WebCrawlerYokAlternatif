import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 5)

data = []

# 1. Üniversiteye git
driver.get("https://akademik.yok.gov.tr/AkademikArama/view/universityListview.jsp")
wait.until(EC.element_to_be_clickable((By.XPATH, "//tr[21]/td[1]/a"))).click()
#/html/body/div/div[2]/div/table/tbody/tr[21]/td[1]/a Ankara Üniversitesi
# 2. Fakülte bağlantılarını bul
wait.until(EC.presence_of_element_located((By.ID, "searchlist")))
faculty_links = driver.find_element(By.ID, "searchlist").find_elements(By.TAG_NAME, "a")

def click_award_menu():
    try:
        award_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#awardMenu > a")))
        driver.execute_script("arguments[0].click();", award_link)
        time.sleep(1)

        # Ödül elemanlarını bul
        award_items = driver.find_elements(By.CSS_SELECTOR, ".timeline > li")
        if award_items:
            for item in award_items:
                try:
                    year_elem = item.find_elements(By.CSS_SELECTOR, ".timeline-badge")
                    title_elem = item.find_elements(By.CSS_SELECTOR, ".timeline-title")
                    org_elem = item.find_elements(By.CSS_SELECTOR, ".timeline-heading small")

                    year = year_elem[0].text.strip() if year_elem else ""
                    title = title_elem[0].text.strip() if title_elem else ""
                    org = org_elem[0].text.strip() if org_elem else ""

                    data.append({
                        "Ad Soyad": current_name,
                        "Birim": current_faculty,
                        "Yıl": year,
                        "Ödül Başlığı": title if title else "Başlık bulunamadı",
                        "Kurum": org
                    })
                except Exception as e:
                    print(f"Ödül öğesi işlenemedi: {e}")
                    data.append({
                        "Ad Soyad": current_name,
                        "Birim": current_faculty,
                        "Yıl": "",
                        "Ödül Başlığı": "Hata sırasında işlenemedi",
                        "Kurum": ""
                    })
        else:
            data.append({
                "Ad Soyad": current_name,
                "Birim": current_faculty,
                "Yıl": "",
                "Ödül Başlığı": "Ödül bulunamadı",
                "Kurum": ""
            })

    except Exception as e:
        print(f"Ödül sekmesine ulaşılamadı: {e}")
        data.append({
            "Ad Soyad": current_name,
            "Birim": current_faculty,
            "Yıl": "",
            "Ödül Başlığı": "Ödül sekmesi bulunamadı",
            "Kurum": ""
        })

def handle_all_authors():
    while True:
        wait.until(EC.presence_of_element_located((By.ID, "authorlistTb")))
        author_links = driver.find_elements(By.CSS_SELECTOR, "#authorlistTb h4 > a")

        for i in range(len(author_links)):
            wait.until(EC.presence_of_element_located((By.ID, "authorlistTb")))
            author_links = driver.find_elements(By.CSS_SELECTOR, "#authorlistTb h4 > a")
            global current_name
            current_name = author_links[i].text.strip()
            print(f"Tıklanıyor: {current_name}")
            driver.execute_script("arguments[0].click();", author_links[i])
            time.sleep(1)
            click_award_menu()
            driver.back()
            driver.back()
            time.sleep(1)

        # Sonraki sayfa var mı?
        try:
            pagination = driver.find_element(By.CSS_SELECTOR, "ul.pagination")
            active_page = pagination.find_element(By.CSS_SELECTOR, "li.active")
            next_page = active_page.find_element(By.XPATH, "following-sibling::li[1]/a")
            driver.execute_script("arguments[0].click();", next_page)
            time.sleep(1)
        except:
            break

# 3. Tüm fakülteleri sırayla işle
for i in range(min(2, len(faculty_links))):
    wait.until(EC.presence_of_element_located((By.ID, "searchlist")))
    faculty_links = driver.find_element(By.ID, "searchlist").find_elements(By.TAG_NAME, "a")

    faculty_link = faculty_links[i]
    global current_faculty
    current_faculty = faculty_link.text.strip()
    print(f"\n--- {i + 1}. Fakülte: {current_faculty} ---")
    driver.execute_script("arguments[0].click();", faculty_link)
    time.sleep(1)

    handle_all_authors()

    driver.back()
    time.sleep(1)

# 4. Excel'e yaz
df = pd.DataFrame(data)
df.to_excel("tum_fakulteler_oduller.xlsx", index=False)
print("\nExcel dosyası oluşturuldu: tum_fakulteler_oduller.xlsx")

driver.quit()
