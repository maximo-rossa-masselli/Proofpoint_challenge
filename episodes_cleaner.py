def main():
    #Contadores para el Report
    total_input = 0
    discarded = 0
    duplicated = 0
    corrected_entries = 0
    
    with open ("episodes.csv", "r", encoding="utf-8") as file:
        #Aquí voy a guardar los episodios
        catalog = {}

        header = next(file)
        for linea in file:

            datos = linea.strip().split(",")
            if len(datos) < 5: 
                continue
            total_input += 1
            
            #Proceso los datos
            series_name = process_series_name(datos[0])
            season_number = process_number(datos[1])
            episode_number = process_number(datos[2])
            episode_title = process_episode_title(datos[3])
            air_date = process_air_date(datos[4])

            #Checkeo si los datos fueron corregidos
            is_corrected = False
            if datos[0] != series_name or datos[3] != episode_title: 
                is_corrected = True

            #Si no tiene num de episodio, titulo de episodio y fecha de emisión, lo omito
            if (episode_number == 0 and episode_title == "Untitled episode" and air_date == "Unknown") or not series_name:
                discarded +=1
                continue

            if is_corrected: 
                corrected_entries += 1

            #Establecí un sistema de puntos para ver que episodio me conviene
            current_points = calcular_puntos(season_number, episode_number, episode_title, air_date)
            
            #Los episodios se consideran duplicados cuando refieren a la misma:
            #Nombre de la serie, numero de temporada, numero de episodio
            #o nombre de la serie, temporada desconocida, numero de episodio, titulo episodio
            #o nombre de la serie, numero de temporada, numero episodio desconocido, titulo episodio
            
            #Osea que tengo un episodio repetido puede aparecer de esas 3 formas.
            #Para poder acceder al episodio en el catalogo creo 3 key siguiendo esos patrones, 
            #que apunten al mismo objeto en memoria
            serie_norm = series_name.lower()
            episode_title_norm = episode_title.lower()

            id1 = f"{serie_norm}|{season_number}|{episode_number}"
            id2 = f"{serie_norm}|0|{episode_number}|{episode_title_norm}"
            id3 = f"{serie_norm}|{season_number}|0|{episode_title_norm}"
            ids = [id1, id2, id3]
           
            #Verifico si ya procese ese episodio bajo alguna de las tres formas de accederlo
            found = None
            for id in ids:
                if id in catalog:
                    found = id
                    break
            
            #Si todavía no procese ese episodio, lo agrego al catálogo y hago que los 3 id
            #apunten al mismo objeto new_registry
            if found is None:
                new_registry = {
                    "data":[series_name, season_number, episode_number, episode_title, air_date],
                    "points": current_points}

                for id in ids:
                    catalog[id] = new_registry

            #Si encuentro que el episodio está duplicado, evalúo utilizando el sistemas de puntos
            #si es un mejor registro que el existente. Si lo es, actualizo los datos
            else:
                duplicated += 1 
                if current_points > catalog[found]["points"]:
                    catalog[found]["data"] = [series_name, season_number, episode_number, episode_title, air_date]
                    catalog[found]["points"] = current_points
                    #No uso un new_registry pq estaría cambiando el objeto al que hace referencia en memoria ese id

        #Elimino los duplicados
        episodes = set()
        for registry in catalog.values():
            data_tuple = tuple(registry["data"])
            episodes.add(data_tuple)

        #Ordeno los registros
        sorted_episodes = list(episodes)
        sorted_episodes.sort(key=lambda x: (x[0].lower(), x[1], x[2]))
        total_output = len(sorted_episodes)

        #Escribo el nuevo archivo
        with open ("episodes_clean.csv", "w", encoding="utf-8") as new:
            new.write("SeriesName,SeasonNumber,EpisodeNumber,EpisodeTitle,AirDate\n")
            for episode in sorted_episodes:
                line = ",".join(str(campo) for campo in episode) + "\n"
                new.write(line)

        #Escribo el reporte
        with open("report.md", "w", encoding="utf-8") as report:
            report.write("# Data Quality Report\n\n")
            report.write("## Summary Statistics\n")
            report.write(f"- **Total input records:** {total_input}\n")
            report.write(f"- **Total output records:** {total_output}\n")
            report.write(f"- **Number of discarded entries:** {discarded}\n")
            report.write(f"- **Number of corrected entries:** {corrected_entries}\n")
            report.write(f"- **Number of duplicates detected:** {duplicated}\n\n")
            
            report.write("## Deduplication Strategy\n")
            report.write("The strategy uses a **3-Key Identity System** to catch duplicates even with missing data:\n")
            report.write("1. `Series|Season|Episode`: Standard identity.\n")
            report.write("2. `Series|0|Episode|Title`: Identifies duplicates when the Season is missing.\n")
            report.write("3. `Series|Season|0|Title`: Identifies duplicates when the Episode number is missing.\n\n")
            report.write("When a duplicate is found, a **Point-Based Priority System** selects the best record:\n")
            report.write("- Valid Air Date: +3 points\n")
            report.write("- Known Episode Title: +2 points\n")
            report.write("- Valid Season/Episode numbers: +1 point each.\n")


#Funciones

def process_series_name(series_name):
    #Elimino los espacios
    name = " ".join(series_name.split())
    
    if not name:
        return False
    return name


def process_number(num):
    number = num.strip()
    try:
        number = int(number)
        if number <= 0:
            return 0
        else: 
            return number
    except: 
        return 0 
        

def process_episode_title(episode_title):
    title = " ".join(episode_title.split())

    if not title:
        return "Untitled episode"
    return title
    

def process_air_date(air_date):
    try:
        date = air_date.strip()
        date_splitted= date.split("-")
        year = int(date_splitted[0])
        month = int(date_splitted[1])
        day = int(date_splitted[2])
        
        if day > 31 or month > 12 or year < 1900:
            return "Unknown"
        else:
            return date 

    except:
        return "Unknown"


def calcular_puntos(season_number, episode_number, episode_title, air_date):
    puntaje = 0
    #Los puntos se suman según la prioridad establecida en la consigna
    if air_date != "Unknown":
        puntaje += 3
    if episode_title != "Untitled episode":
        puntaje +=2
    if season_number != 0:
        puntaje += 1
    if episode_number != 0:
        puntaje += 1
    return puntaje


if __name__ == "__main__":
    main()