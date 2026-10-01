# %% Import bibliotek
import pandas as pd

# %% Wczytanie danych
df = pd.read_csv("bedtime_screentime_sleep_debt.csv")

# %% Podstawowe informacje o danych
print(df.shape)

# %% Nazwy kolumn
print(df.columns)

# %% Podgląd danych
df.head()

# %% Typy danych
print(df.dtypes)

# %% Sprawdzenie brakujących wartości
print(df.isnull().sum())

# %% Wartości w zmiennej gender
print(df["gender"].value_counts())

# %% Wartości w zmiennej chronotype
print(df["chronotype"].value_counts())

# %% Wartości w zmiennej primary_bedtime_app
print(df["primary_bedtime_app"].value_counts())

# %% Wartości w zmiennej sleep_debt_category
print(df["sleep_debt_category"].value_counts())

# %% Statystyki zmiennych liczbowych
df.describe()

# %% Sprawdzenie duplikatów
print(df.duplicated().sum())

# %% Sprawdzenie unikalności użytkowników
print(df["user_id"].duplicated().sum())

# %% Sprawdzenie wartości filtra światła niebieskiego
print(df["blue_light_filter_active"].value_counts())
#-------------------------------------------------------------------------------------------
#Krok 1 analizy: jak wygląda poziom zmęczenia?
# %% Rozkład zmęczenia następnego dnia
print(df["next_day_fatigue_score"].describe())

# %% Zmęczenie według kategorii niedoboru snu
print(
    df.groupby("sleep_debt_category")["next_day_fatigue_score"]
      .agg(["count", "mean", "median"])
      .sort_values("mean")
)
# %% Udział kategorii długu snu
print(
    df["sleep_debt_category"]
      .value_counts(normalize=True)
      .mul(100)
      .round(1)
)

#-------------------------------------------
# %% Czas korzystania z telefonu przed snem
print(df["bedtime_phone_minutes"].describe())

# %% Podział użytkowników według czasu korzystania z telefonu
df["phone_time_group"] = pd.qcut(
    df["bedtime_phone_minutes"],
    q=4
)
print(df["phone_time_group"].value_counts().sort_index())

# %% Zmęczenie według czasu korzystania z telefonu
print(
    df.groupby("phone_time_group", observed=True)["next_day_fatigue_score"]
      .agg(["count", "mean", "median"])
)

# %% Czas snu według czasu korzystania z telefonu
print(
    df.groupby("phone_time_group", observed=True)["total_sleep_hours"]
      .agg(["count", "mean", "median"])
)
#---------------------------------------------------------------------------------
# %% REM według czasu korzystania z telefonu
print(
    df.groupby("phone_time_group", observed=True)["rem_sleep_pct"]
      .agg(["count", "mean", "median"])
)
# Wniosek:
# Średni udział REM jest bardzo podobny we wszystkich grupach
# czasu korzystania z telefonu. W analizowanym zbiorze nie widać
# wyraźnej zależności między czasem korzystania z telefonu przed snem
# a udziałem snu REM.

# %% Sen głęboki według czasu korzystania z telefonu
print(
    df.groupby("phone_time_group", observed=True)["deep_sleep_pct"]
      .agg(["count", "mean", "median"])
)
# Wniosek:
# W analizowanym zbiorze wraz ze wzrostem czasu korzystania z telefonu
# przed snem obserwujemy spadek średniego udziału snu głębokiego.
# Różnica między grupą 1–31 min a grupą 80–180 min wynosi około
# 2,02 punktu procentowego.

# %% Czas zasypiania według czasu korzystania z telefonu
print(
    df.groupby("phone_time_group", observed=True)["sleep_latency_min"]
      .agg(["count", "mean", "median"])
)
# Wniosek:
# W analizowanym zbiorze wraz ze wzrostem czasu korzystania z telefonu
# przed snem rośnie również średni czas potrzebny na zaśnięcie.
# Różnica między grupą 1–31 min a grupą 80–180 min wynosi około
# 36,6 minuty.

# %% Zależność między czasem korzystania z telefonu a snem REM
korelacja_rem = df["bedtime_phone_minutes"].corr(df["rem_sleep_pct"])
print(f"Korelacja między czasem korzystania z telefonu a REM: {korelacja_rem:.3f}")
# Wniosek:
# Współczynnik korelacji wynosi -0,009, co wskazuje na praktycznie
# brak liniowej zależności między czasem korzystania z telefonu
# przed snem a udziałem snu REM w analizowanym zbiorze.
# W analizowanym zbiorze nie obserwujemy wyraźnej zależności
# między czasem korzystania z telefonu przed snem a udziałem snu REM.
# Średni udział REM pozostaje na podobnym poziomie we wszystkich
# grupach czasu korzystania, a współczynnik korelacji wynosi -0,009.

#-----------------------------------------------------------------------------
# %% Filtr światła niebieskiego a zmęczenie
print(
    df.groupby("blue_light_filter_active")["next_day_fatigue_score"]
      .agg(["count", "mean", "median"])
)
# %% Poziom jasności ekranu
print(df["screen_brightness_pct"].describe())
# %% Jasność ekranu a zmęczenie
# %% Podział jasności ekranu na grupy
df["brightness_group"] = pd.qcut(
    df["screen_brightness_pct"],
    q=4
)
print(df["brightness_group"].value_counts().sort_index())

# %% Zmęczenie według jasności ekranu
print(
    df.groupby("brightness_group", observed=True)["next_day_fatigue_score"]
      .agg(["count", "mean", "median"])
)
# Wniosek:
# W analizowanym zbiorze wraz ze wzrostem jasności ekranu
# obserwujemy wzrost średniego poziomu zmęczenia następnego dnia.
# Różnica między grupą najniższej i najwyższej jasności wynosi
# około 0,61 punktu.
#
# Jest to zależność obserwowana w danych i nie oznacza jeszcze,
# że wyższa jasność ekranu powoduje większe zmęczenie.

# %% Jasność ekranu i filtr a zmęczenie
print(
    df.groupby(
        ["brightness_group", "blue_light_filter_active"],
        observed=True
    )["next_day_fatigue_score"]
    .agg(["count", "mean", "median"])
)
# Wniosek:
# We wszystkich analizowanych grupach jasności osoby korzystające
# z filtra światła niebieskiego mają niższy średni poziom zmęczenia
# niż osoby bez aktywnego filtra.
#
# Różnica jest największa w grupie najwyższej jasności ekranu
# i wynosi około 0,63 punktu.
#
# Wynik wskazuje na zależność między aktywnym filtrem a niższym
# poziomem zmęczenia, ale nie pozwala stwierdzić zależności przyczynowej.

#--------------------------Aplikacje-----------------------------------
# %% Rodzaj aplikacji a zmęczenie
print(
    df.groupby("primary_bedtime_app")["next_day_fatigue_score"]
      .agg(["count", "mean", "median"])
      .sort_values("mean")
)

# Wniosek:
# W analizowanym zbiorze obserwujemy różnice w średnim poziomie
# zmęczenia w zależności od rodzaju aplikacji używanej przed snem.
# Najniższa średnia występuje dla News / Reading (3,33),
# a najwyższa dla TikTok / Reels (4,16).
#
# Różnica między tymi grupami wynosi około 0,84 punktu.
# Jest to zależność obserwowana w danych i nie oznacza,
# że konkretny rodzaj aplikacji powoduje wyższe zmęczenie.

# %% Czas korzystania z telefonu według aplikacji
print(
    df.groupby("primary_bedtime_app")["bedtime_phone_minutes"]
      .agg(["count", "mean", "median"])
      .sort_values("mean")
)
# Wniosek:
# Średni czas korzystania z telefonu przed snem jest podobny
# dla wszystkich analizowanych rodzajów aplikacji.
# Różnica między grupą o najniższej i najwyższej średniej
# wynosi około 3,7 minuty.
#
# Oznacza to, że zaobserwowane różnice w poziomie zmęczenia
# między aplikacjami nie wynikają po prostu z dużych różnic
# w średnim czasie korzystania z telefonu.

#-------------------------Kofeina---------------------------
# %% Kofeina spożywana po 17:00
print(df["caffeine_post_5pm_mg"].describe())
# %% Czy użytkownicy spożywają kofeinę po 17:00?
print(
    df["caffeine_post_5pm_mg"]
    .gt(0)
    .value_counts()
)

# %% Rozkład ilości kofeiny wśród osób, które ją spożywały
print(
    df.loc[df["caffeine_post_5pm_mg"] > 0, "caffeine_post_5pm_mg"]
      .describe()
)

# %% Podział użytkowników według ilości kofeiny po 17:00
df["caffeine_group"] = "0 mg"
df.loc[df["caffeine_post_5pm_mg"] > 0, "caffeine_group"] = pd.qcut(
    df.loc[df["caffeine_post_5pm_mg"] > 0, "caffeine_post_5pm_mg"],
    q=4,
    labels=["Niska", "Umiarkowana", "Wyższa", "Wysoka"]
)
print(df["caffeine_group"].value_counts())

# %% Kofeina po 17:00 a zmęczenie
print(
    df.groupby("caffeine_group", observed=True)["next_day_fatigue_score"]
      .agg(["count", "mean", "median"])
)
# Wniosek:
# W analizowanym zbiorze osoby spożywające większe ilości kofeiny
# po 17:00 mają na ogół wyższy średni poziom zmęczenia następnego dnia.
# Średnie zmęczenie wzrasta od 3,49 punktu w grupie 0 mg
# do 4,92 punktu w grupie wysokiego spożycia.
# Jest to zależność obserwowana w danych i nie oznacza,
# że kofeina po 17:00 jest bezpośrednią przyczyną wyższego zmęczenia.

#-----------------------------------Model do przewidywania --------------------------------------
# %% Wybór zmiennych do modelu

features = [
    "age",
    "gender",
    "occupation_type",
    "chronotype",
    "bedtime_phone_minutes",
    "primary_bedtime_app",
    "screen_brightness_pct",
    "blue_light_filter_active",
    "caffeine_post_5pm_mg",
    "physical_activity_min"
]

target = "next_day_fatigue_score"

print("Zmienne wejściowe:")
print(features)

print("\nZmienna docelowa:")
print(target)

# %% Przygotowanie danych wejściowych i zmiennej docelowej
X = df[features]
y = df[target]
print("Rozmiar danych wejściowych X:", X.shape)
print("Rozmiar zmiennej docelowej y:", y.shape)

# %% Podział danych na zbiór treningowy i testowy
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)
print("Dane treningowe:", X_train.shape)
print("Dane testowe:", X_test.shape)

# %% Podział zmiennych na tekstowe i liczbowe

kolumny_tekstowe = [
    "gender",
    "occupation_type",
    "chronotype",
    "primary_bedtime_app"
]

kolumny_liczbowe = [
    "age",
    "bedtime_phone_minutes",
    "screen_brightness_pct",
    "blue_light_filter_active",
    "caffeine_post_5pm_mg",
    "physical_activity_min"
]

print("Zmienne tekstowe:", kolumny_tekstowe)
print("Zmienne liczbowe:", kolumny_liczbowe)

# %% Przygotowanie kodowania zmiennych tekstowych
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

preprocessor = ColumnTransformer(
    transformers=[
        (
            "tekstowe",
            OneHotEncoder(handle_unknown="ignore"),
            kolumny_tekstowe
        )
    ],
    remainder="passthrough"
)
# %% Kodowanie danych treningowych i testowych

X_train_encoded = preprocessor.fit_transform(X_train)
X_test_encoded = preprocessor.transform(X_test)

print("Rozmiar danych treningowych po kodowaniu:", X_train_encoded.shape)
print("Rozmiar danych testowych po kodowaniu:", X_test_encoded.shape)

# %% Utworzenie modelu Random Forest
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)
print("Model Random Forest został utworzony.")

# %% Trenowanie modelu
model.fit(X_train_encoded, y_train)

print("Model został wytrenowany.")

# %% Przewidywanie wyniku dla danych testowych

y_pred = model.predict(X_test_encoded)
print("Liczba przewidywań:", len(y_pred))
print("Pierwsze 10 przewidywań:")
print(y_pred[:10])

# %% Porównanie przewidywań z rzeczywistymi wartościami
porownanie = pd.DataFrame({
    "Rzeczywiste zmęczenie": y_test.values[:10],
    "Przewidywane zmęczenie": y_pred[:10]
})
print(porownanie)

# %% Ocena modelu - MAE

from sklearn.metrics import mean_absolute_error
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE modelu: {mae:.2f}")
# %% Ocena modelu - R²

from sklearn.metrics import r2_score
r2 = r2_score(y_test, y_pred)
print(f"R² modelu: {r2:.2f}")
# Wniosek:
# Model Random Forest osiągnął MAE = 0,90, co oznacza,
# że średni błąd przewidywania poziomu zmęczenia wynosi około
# 0,90 punktu.
#
# Wartość R² = 0,81 oznacza, że model wyjaśnia około 81%
# zróżnicowania poziomu zmęczenia następnego dnia w zbiorze testowym.
#
# Model został zbudowany wyłącznie na podstawie zmiennych
# behawioralnych i demograficznych, bez wykorzystania
# bezpośrednich parametrów fizjologicznych snu.
# %% Wykres: wartości rzeczywiste a przewidywane

import matplotlib.pyplot as plt

plt.scatter(y_test, y_pred)

plt.xlabel("Rzeczywisty poziom zmęczenia")
plt.ylabel("Przewidywany poziom zmęczenia")
plt.title("Rzeczywiste a przewidywane zmęczenie")

plt.show()
# Wniosek:
# Na wykresie większość obserwacji układa się wzdłuż rosnącej zależności
# między rzeczywistym a przewidywanym poziomem zmęczenia.
# Oznacza to, że model poprawnie odwzorowuje ogólny kierunek zmian
# poziomu zmęczenia.
#
# Jednocześnie widoczne jest rozproszenie punktów, co oznacza,
# że przewidywania modelu nie są idealne i dla części obserwacji
# występują większe różnice między wartością rzeczywistą a przewidywaną.
#
# Wynik jest zgodny z wartościami MAE = 0,90 oraz R² = 0,81.

# %% Ważność zmiennych w modelu
nazwy_zmiennych = preprocessor.get_feature_names_out()

print("Liczba zmiennych po kodowaniu:", len(nazwy_zmiennych))
print(nazwy_zmiennych)
# %% Obliczenie ważności zmiennych

waznosc = pd.DataFrame({
    "zmienna": nazwy_zmiennych,
    "waznosc": model.feature_importances_
})

waznosc = waznosc.sort_values(
    "waznosc",
    ascending=False
)

print(waznosc)
# Wniosek:
# W modelu Random Forest największą względną ważność spośród
# analizowanych zmiennych ma czas korzystania z telefonu przed snem
# (bedtime_phone_minutes) – 0,551.
#
# Kolejne zmienne pod względem ważności to chronotyp Night Owl (0,150),
# ilość kofeiny po godzinie 17:00 (0,052) oraz praca zmianowa
# w sektorze ochrony zdrowia (0,052).
#
# Wynik jest spójny z wcześniejszą analizą opisową, w której wraz
# ze wzrostem czasu korzystania z telefonu obserwowaliśmy wyższy
# poziom zmęczenia następnego dnia.
#
# Ważność zmiennej w modelu nie oznacza jednak zależności przyczynowej
# ani nie oznacza, że dana zmienna odpowiada za określony procent
# poziomu zmęczenia.

# %% Grupowanie ważności do pierwotnych zmiennych
waznosc["zmienna_glowna"] = waznosc["zmienna"].str.split("__").str[-1].str.split("_").str[0]

waznosc_grupowa = (
    waznosc.groupby("zmienna_glowna")["waznosc"]
    .sum()
    .sort_values(ascending=False)
)

print(waznosc_grupowa)
# %% Przygotowanie nazw głównych zmiennych

mapowanie = {
    "bedtime_phone_minutes": "Czas korzystania z telefonu",
    "chronotype": "Chronotyp",
    "occupation_type": "Typ pracy",
    "caffeine_post_5pm_mg": "Kofeina po 17:00",
    "screen_brightness_pct": "Jasność ekranu",
    "physical_activity_min": "Aktywność fizyczna",
    "age": "Wiek",
    "primary_bedtime_app": "Aplikacja przed snem",
    "gender": "Płeć",
    "blue_light_filter_active": "Filtr światła niebieskiego"
}

print(mapowanie)

# %% Grupowanie ważności do 10 głównych zmiennych

waznosc["zmienna_glowna"] = None

for zmienna in mapowanie:
    maska = waznosc["zmienna"].str.contains(zmienna)
    waznosc.loc[maska, "zmienna_glowna"] = mapowanie[zmienna]

waznosc_grupowa = (
    waznosc.groupby("zmienna_glowna")["waznosc"]
    .sum()
    .sort_values(ascending=False)
)

print(waznosc_grupowa)
# Wniosek:
# W modelu Random Forest największą względną ważność ma czas
# korzystania z telefonu przed snem (55,1%).
# Drugą najważniejszą zmienną jest chronotyp (18,2%).
#
# Kolejne zmienne mają wyraźnie mniejszą względną ważność:
# typ pracy (6,5%), ilość kofeiny po 17:00 (5,2%)
# oraz jasność ekranu (4,5%).
#
# Wynik wskazuje, że w tym modelu czas korzystania z telefonu
# przed snem ma największe znaczenie dla przewidywania
# poziomu zmęczenia następnego dnia.
#
# Jest to ważność zmiennych w modelu, a nie zależność przyczynowa.
# Nie oznacza również, że czas korzystania z telefonu odpowiada
# za 55,1% poziomu zmęczenia.

# %% Wykres ważności zmiennych

waznosc_grupowa.sort_values().plot(
    kind="barh",
    figsize=(8, 6)
)

plt.xlabel("Względna ważność")
plt.ylabel("Zmienna")
plt.title("Ważność zmiennych w modelu Random Forest")

plt.show()

# %% Model XGBoost

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Utworzenie modelu XGBoost
xgb_model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    random_state=42
)

# Trenowanie modelu
xgb_model.fit(X_train_encoded, y_train)

# Przewidywanie dla danych testowych
y_pred_xgb = xgb_model.predict(X_test_encoded)

# Ocena modelu
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
r2_xgb = r2_score(y_test, y_pred_xgb)

print("\n--- XGBoost ---")
print(f"MAE modelu: {mae_xgb:.2f}")
print(f"R² modelu: {r2_xgb:.2f}")


# %% Porównanie modeli

porownanie_modeli = pd.DataFrame({
    "Model": ["Random Forest", "XGBoost"],
    "MAE": [mae, mae_xgb],
    "R²": [r2, r2_xgb]
})

print("\nPorównanie modeli:")
print(porownanie_modeli)


# %% Ważność zmiennych - XGBoost

waznosc_xgb = pd.DataFrame({
    "zmienna": nazwy_zmiennych,
    "waznosc": xgb_model.feature_importances_
})

waznosc_xgb = waznosc_xgb.sort_values(
    "waznosc",
    ascending=False
)

print("\nWażność zmiennych - XGBoost:")
print(waznosc_xgb)


# %% Grupowanie ważności XGBoost do głównych zmiennych
waznosc_xgb["zmienna_glowna"] = None
for zmienna in mapowanie:
    maska = waznosc_xgb["zmienna"].str.contains(zmienna)
    waznosc_xgb.loc[maska, "zmienna_glowna"] = mapowanie[zmienna]

waznosc_xgb_grupowa = (
    waznosc_xgb.groupby("zmienna_glowna")["waznosc"]
    .sum()
    .sort_values(ascending=False)
)
print("\nWażność głównych zmiennych - XGBoost:")
print(waznosc_xgb_grupowa)

# %% Wykres ważności zmiennych - XGBoost
waznosc_xgb_grupowa.sort_values().plot(
    kind="barh",
    figsize=(8, 6)
)

plt.xlabel("Względna ważność")
plt.ylabel("Zmienna")
plt.title("Ważność zmiennych w modelu XGBoost")

plt.show()

# Wniosek:
# XGBoost osiągnął nieco lepsze wyniki predykcyjne niż Random Forest.
# Dla XGBoost uzyskano MAE = 0,87 oraz R² = 0,82,
# podczas gdy Random Forest osiągnął MAE = 0,90 oraz R² = 0,81.
#
# Oznacza to, że XGBoost uzyskał na zbiorze testowym nieco mniejszy
# błąd przewidywania oraz nieco lepiej wyjaśniał zróżnicowanie
# poziomu zmęczenia.
#
# Oba modele wskazują na znaczenie czasu korzystania z telefonu,
# chronotypu, typu pracy i kofeiny, jednak przypisują im różną
# względną ważność.
#
# Różnice w ważności zmiennych pokazują, że ważność cechy zależy
# od zastosowanego modelu i nie powinna być interpretowana jako
# bezpośredni wpływ przyczynowy.

# %% Eksport wyników modeli do Power BI

# Tworzymy tabelę z wynikami obu modeli
wyniki_modele = pd.DataFrame({
    "Model": ["Random Forest", "XGBoost"],
    "MAE": [mae, mae_xgb],
    "R2": [r2, r2_xgb]
})

# Zapisujemy wyniki do pliku CSV
wyniki_modele.to_csv(
    "wyniki_modele.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nWyniki modeli zapisane do: wyniki_modele.csv")
print(wyniki_modele)

# %% Eksport predykcji XGBoost do Power BI

# Tworzymy tabelę zawierającą rzeczywiste i przewidywane wartości
predykcje_xgboost = pd.DataFrame({
    "Rzeczywiste_zmeczenie": y_test.values,
    "Przewidywane_zmeczenie": y_pred_xgb
})

# Zapisujemy dane do pliku CSV
predykcje_xgboost.to_csv(
    "predykcje_xgboost.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nPredykcje XGBoost zapisane do: predykcje_xgboost.csv")
print(predykcje_xgboost.head()) 

# %% Eksport ważności zmiennych do Power BI

# Tworzymy tabelę porównującą ważność zmiennych
waznosc_zmiennych = pd.DataFrame({
    "Zmienna": waznosc_grupowa.index,
    "Random Forest": waznosc_grupowa.values,
    "XGBoost": waznosc_xgb_grupowa.reindex(
        waznosc_grupowa.index
    ).values
})

# Zapisujemy tabelę do pliku CSV
waznosc_zmiennych.to_csv(
    "waznosc_zmiennych.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nWażność zmiennych zapisana do: waznosc_zmiennych.csv")
print(waznosc_zmiennych)