# Sleep & Tech: Analiza zależności między czasem ekranowym, jakością snu i zmęczeniem


## O projekcie

Projekt analizuje zależności między wieczornymi nawykami cyfrowymi, jakością snu i zmęczeniem odczuwanym następnego dnia. Wykorzystując Python do analizy danych i modelowania predykcyjnego oraz Power BI do wizualizacji, zbadałam, jak czas spędzany przed ekranem, rodzaj używanych aplikacji i inne czynniki związane ze stylem życia wiążą się z parametrami snu i poziomem zmęczenia.

Celem projektu było przećwiczenie całego procesu analizy danych — od przygotowania i eksploracji zbioru, przez modelowanie predykcyjne, aż po stworzenie interaktywnego raportu.

## Zbiór danych

* **Źródło:** Kaggle – The Bedtime Addiction: Sleep Debt & Screen Time
* **Liczba obserwacji:** 8 500
* **Rodzaj danych:** dane symulowane

**Ważne:** Zbiór danych został wygenerowany symulacyjnie. Wyniki należy zatem interpretować jako zależności występujące w wygenerowanych danych, a nie jako dowód rzeczywistych zależności przyczynowo-skutkowych.

## Wykorzystane narzędzia

* **Python:** Pandas, NumPy, Scikit-learn, XGBoost
* **Power BI:** wizualizacja danych i interaktywny raport
* **GitHub:** dokumentacja projektu i przechowywanie kodu


## Najważniejsze wyniki

* Czas korzystania z telefonu wykazał dodatnią korelację ze zmęczeniem następnego dnia (**r = 0,71**).
* Całkowity czas snu wykazał silną ujemną korelację ze zmęczeniem (**r = -0,88**).
* Latencja snu była dodatnio skorelowana ze zmęczeniem (**r = 0,74**).
* Grupa korzystająca z TikToka/Reels osiągnęła średni poziom zmęczenia **4,16**, w porównaniu z **3,33** w grupie News/Reading.
* Czas korzystania z telefonu wykazał niemal zerową korelację liniową z długością fazy REM (**r = -0,009**). Pokazuje to, jak ważne jest analizowanie różnych parametrów snu oddzielnie.

Wyniki opisują zależności w symulowanym zbiorze danych i nie stanowią dowodu na istnienie zależności przyczynowo-skutkowych.

## Modelowanie predykcyjne

Wytrenowałam dwa modele regresyjne służące do przewidywania poziomu zmęczenia następnego dnia:

| Model         |  MAE |   R² |
| ------------- | ---: | ---: |
| XGBoost       | 0,87 | 0,82 |
| Random Forest | 0,90 | 0,81 |

Oba modele osiągnęły zbliżone wyniki. XGBoost uzyskał nieco niższy błąd predykcji i minimalnie wyższy współczynnik R².

Dodatkowo przeanalizowałam ważność cech, aby sprawdzić, które zmienne miały największy wpływ na predykcje modeli.

## Struktura projektu

```text
Sleep-and-Tech-Analysis/
│
├── python/
    ├── analiza_sleep.py
├── power bi/
    ├── Sleep&Tech.pbix
├── README.md
├──data/
    ├── predykcje_xgboost.csv
    ├── waznosc_zmiennych_csv
    ├── wyniki_modele.csv
    ├── bedtime_screentime_sleep_debt.csv

```

## Czego się nauczyłam?

Podczas realizacji projektu rozwijałam umiejętności w zakresie:

* czyszczenia danych i eksploracyjnej analizy danych (EDA),
* analizy korelacji i wizualizacji danych,
* budowania modeli regresyjnych z wykorzystaniem Scikit-learn i XGBoost,
* oceny jakości modeli za pomocą MAE i R²,
* tworzenia interaktywnych raportów w Power BI,
* prezentowania wyników analizy wraz z ich ograniczeniami.

## Podsumowanie

Projekt pozwolił mi połączyć analizę danych w Pythonie z raportowaniem w Power BI oraz lepiej zrozumieć cały proces pracy analityka danych — od surowego zbioru po czytelną prezentację wyników.

