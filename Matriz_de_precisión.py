import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, MultiLabelBinarizer
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, classification_report, accuracy_score, confusion_matrix
from scipy.optimize import curve_fit
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier


df = pd.read_csv("datos/datos.csv")

df_filtrado = df.drop(columns=['unreleased', 'nombre', 'appid'])

thresholds = [5, 10, 15, 20, 30, 50, 75, 100, 150, 200]

resultados= {threshold: {} for threshold in thresholds}


for threshold in thresholds: 
    # Probemos un enfoque distinto, en cambio crearemos una nueva columna con un 'threshold' de playtime y haremos clasificación.
    # Es decir, si el playtime es mayor a X horas, clase 1, sino clase 0.
    df_filtrado['high_playtime'] = (df_filtrado['average_playtime'] > threshold).astype(int)

    # Creamos también una columna que sea la razón entre rating positivos y negativos
    df_filtrado['rating_ratio'] = df_filtrado['positive_ratings'] / (df_filtrado['negative_ratings'] + 1)  # +1 para evitar división por cero

    X = df_filtrado.drop(columns=["average_playtime", "high_playtime", "median_playtime", "owners", "revenue", "positive_ratings", "negative_ratings", "copiessold"]).copy()
    y = df_filtrado["high_playtime"].copy()

    columnas_cuantitativas = ["price", "required_age", "achievements", "rating_ratio", "price", "reviewscore"]
    columnas_lista = ["platforms", "genres", "categories"]


    df_cuantitativo = X[columnas_cuantitativas].copy()
    df_lista = X[columnas_lista].copy()
    df_cualitativo = X.drop(columns=list(df_cuantitativo.columns) + list(df_lista.columns)).copy()

    df_binarizado_total = pd.DataFrame()

    for columna in columnas_lista:
        listas = df_lista[columna].fillna('').str.split(';')
        mlb = MultiLabelBinarizer()
        datos_binarizados = mlb.fit_transform(listas)
        df_temp = pd.DataFrame(datos_binarizados,
                            columns=mlb.classes_,
                            index=df_lista.index).add_prefix(f'{columna}_')
        df_binarizado_total = pd.concat([df_binarizado_total, df_temp], axis=1)

    generos_binarizados = mlb.fit_transform(df_lista)

    encoder = OneHotEncoder(
        min_frequency=100, # Agrupa categorías que aparecen menos de 100 veces
        handle_unknown='ignore',
        dtype=np.float32,
        drop="first"
    )
    result = encoder.fit_transform(df_cualitativo).toarray()

    column_names = encoder.get_feature_names_out(df_cualitativo.columns)

    data_scaled = pd.DataFrame(result, columns=column_names, index=df_cualitativo.index)
    # df_encoded = pd.concat([data_scaled, df_cuantitativo, df_binarizado_total], axis=1)
    df_encoded = pd.concat([data_scaled, df_cuantitativo], axis=1)
    df_encoded.head()

    scaler = MinMaxScaler()
    #Falta OneHotEncoder y lo que hice arriba con el multilabel (mañana lo termino antes de la reu)
    X_scaled = scaler.fit_transform(df_encoded)
    X_scaled = pd.DataFrame(X_scaled, columns=df_encoded.columns, index=df_encoded.index)


    # Empieza el testeo
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # REGRESIÓN LOGÍSTICA
    logistic_full = LogisticRegression(random_state=42, max_iter=1000)
    logistic_full.fit(X_train, y_train)
    y_pred_log = logistic_full.predict(X_test)

    # Resultados
    report = classification_report(y_test, y_pred_log, output_dict=True)
    resultados[threshold]['logistic_regression'] = (report['1']['precision'], report['1']['recall'])

    # RANDOM FOREST
    rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    max_features='sqrt',
    oob_score=True,
    random_state=42
    )
    rf.fit(X_train, y_train)
    yhat_rf_test = rf.predict(X_test)

    # Resultados
    report = classification_report(y_test, yhat_rf_test, output_dict=True)
    resultados[threshold]['random_forest'] = (report['1']['precision'], report['1']['recall'])

    # KNN
    k_values = range(1, 21, 2)
    scores = []
    for k in k_values:
        knn = KNeighborsClassifier(n_neighbors=k)
        cv_score = cross_val_score(knn, X_train, y_train, cv=5, scoring="f1_macro").mean()
        scores.append(cv_score)

    best_k = k_values[np.argmax(scores)]
    knn = KNeighborsClassifier(n_neighbors=best_k)
    knn.fit(X_train, y_train)
    y_pred_knn = knn.predict(X_test)

    # Resultados
    report = classification_report(y_test, y_pred_knn, output_dict=True)
    resultados[threshold]['knn'] = (report['1']['precision'], report['1']['recall'])

    print(f"Threshold {threshold}: {resultados[threshold]}")