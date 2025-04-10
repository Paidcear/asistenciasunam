import streamlit as st
import pandas as pd
import json
from datetime import date
import random

# Archivo JSON para almacenar los datos
data_file = "asistencias.json"

# Función para cargar los datos del archivo JSON
def load_data():
    try:
        with open(data_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Función para guardar los datos en el archivo JSON
def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

# Función para reasignar IDs
def reassign_ids(data):
    for index, record in enumerate(data):
        record["id"] = index + 1
    return data

# Cargar datos iniciales
data = load_data()

# Panel lateral
st.sidebar.title("Gestión de Asistencias")
menu = st.sidebar.selectbox(
    "Opciones:",
    [
        "Registrar Asistencia",
        "Registrar Alumno",
        "Consultar Alumno",
        "Modificar Alumno",
        "Eliminar Alumno",
        "Mostrar Todos los Registros",
        "Importar desde CSV"
    ],
    index=0
)

# Registrar Asistencia
if menu == "Registrar Asistencia":
    st.title("Registrar Asistencias")
    asistencia_id = st.number_input("Ingresa el ID del Alumno:", min_value=1, step=1, format="%d")
    tipo = st.selectbox("Selecciona el tipo de registro:", ["Asistencia", "Retardo"], key="tipo_asistencia")
    fecha = st.date_input("Selecciona la fecha:", value=date.today(), key="fecha_asistencia")

    if st.button("Registrar", key="registrar_asistencia_action_button"):
        alumno = next((item for item in data if item["id"] == asistencia_id), None)
        if alumno:
            fecha_str = fecha.isoformat()
            if "registros" not in alumno:
                alumno["registros"] = {}
            if fecha_str not in alumno["registros"]:
                alumno["registros"][fecha_str] = {"asistencias": 0, "retardos": 0}
            if tipo == "Asistencia":
                alumno["registros"][fecha_str]["asistencias"] += 1
                st.success(f"Asistencia registrada para el alumno {alumno['nombre']} el {fecha_str}.")
            elif tipo == "Retardo":
                alumno["registros"][fecha_str]["retardos"] += 1
                st.success(f"Retardo registrado para el alumno {alumno['nombre']} el {fecha_str}.")
            save_data(data)
        else:
            st.error("No se encontró ningún alumno con ese ID.")

# Registrar Alumno
elif menu == "Registrar Alumno":
    st.title("Registrar Nuevo Alumno")

    apellido_paterno = st.text_input("Apellido Paterno:")
    apellido_materno = st.text_input("Apellido Materno:")
    nombre = st.text_input("Nombre(s):")
    matricula = st.text_input("Matrícula:")
    nivel = st.text_input("Licenciatura:")
    materia = st.text_input("Materia:")

    if st.button("Registrar", key="registrar_alumno_button"):
        if all([apellido_paterno.strip(), apellido_materno.strip(), nombre.strip(), matricula.strip()]):
            new_id = len(data) + 1
            data.append({
                "id": new_id,
                "apellido_paterno": apellido_paterno,
                "apellido_materno": apellido_materno,
                "nombre": nombre,
                "matricula": matricula,
                "licenciatura": nivel,
                "materia": materia,
                "registros": {}
            })
            save_data(data)
            st.success(f"Alumno '{nombre}' registrado con éxito.")
        else:
            st.error("Por favor, completa todos los campos.")

# Consultar Alumno
elif menu == "Consultar Alumno":
    st.title("Consultar Alumno")
    consulta_id = st.number_input("Ingresa el ID del Alumno:", min_value=1, step=1, format="%d")

    if st.button("Buscar", key="consultar_alumno_button"):
        alumno = next((item for item in data if item["id"] == consulta_id), None)
        if alumno:
            st.write(f"**ID:** {alumno['id']}")
            st.write(f"**Nombre:** {alumno['nombre']} {alumno['apellido_paterno']} {alumno['apellido_materno']}")
            st.write(f"**Matrícula:** {alumno['matricula']}")
            st.write(f"**Licenciatura:** {alumno['nivel']}")
            st.write(f"**Materia:** {alumno['materia']}")
            #st.write(f"**Asistencias:** {alumno['asistencia']}")
            #st.write(f"**Retardos:** {alumno['retardo']}")

        else:
            st.error("No se encontró ningún alumno con ese ID.")

    if st.checkbox("Detalle de asistencias"):
        ids = [item["id"] for item in data]
        selected_id = st.selectbox("Selecciona el ID del alumno:", ids)
        alumno = next((item for item in data if item["id"] == selected_id), None)
        if alumno:
            registros = alumno.get("registros", {})
            export_data = []
            for fecha, detalles in registros.items():
                export_data.append({
                    "Fecha": fecha,
                    "Asistencia": detalles["asistencias"],
                    "Retardo": detalles["retardos"]
                })
            df_export = pd.DataFrame(export_data)
            st.dataframe(df_export)
            csv = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"asistencias_alumno_{selected_id}.csv",
                mime="text/csv"
            )

# Modificar Alumno
elif menu == "Modificar Alumno":
    st.title("Modificar Alumno")

    # Obtener niveles de la tabla de todos los registros
    niveles = list(set(record["nivel"] for record in data))
    materias = list(set(record["materia"] for record in data))

    modificar_id = st.number_input("Ingresa el ID del Alumno a Modificar:", min_value=1, step=1, format="%d")

    alumno = next((item for item in data if item["id"] == modificar_id), None)
    if alumno:
        nuevo_apellido_paterno = st.text_input("Apellido Paterno:", alumno["apellido_paterno"])
        nuevo_apellido_materno = st.text_input("Apellido Materno:", alumno["apellido_materno"])
        nuevo_nombre = st.text_input("Nombre(s):", alumno["nombre"])
        nueva_matricula = st.text_input("Matrícula:", alumno["matricula"])
        nuevo_nivel = st.selectbox("Licenciatura:", niveles)
        nuevo_materia = st.selectbox("Materia:", materias)
        #nuevo_materia = st.text_input("Materia:", alumno["materia"])

        if st.button("Guardar Cambios", key="modificar_alumno_button"):
            alumno["apellido_paterno"] = nuevo_apellido_paterno
            alumno["apellido_materno"] = nuevo_apellido_materno
            alumno["nombre"] = nuevo_nombre
            alumno["matricula"] = nueva_matricula
            alumno["nivel"] = nuevo_nivel
            alumno["materia"] = nuevo_materia
            save_data(data)
            st.success("Datos del alumno actualizados correctamente.")
    else:
        st.error("No se encontró ningún alumno con ese ID.")

# Eliminar Alumno
elif menu == "Eliminar Alumno":
    st.title("Eliminar Alumno")
    eliminar_id = st.number_input("Ingresa el ID del Alumno a Eliminar:", min_value=1, step=1, format="%d")

    if st.button("Eliminar", key="eliminar_alumno_button"):
        alumno = next((item for item in data if item["id"] == eliminar_id), None)
        if alumno:
            data.remove(alumno)
            data = reassign_ids(data)
            save_data(data)
            st.success(f"Alumno {alumno['nombre']} eliminado correctamente. ID reasignado.")
        else:
            st.error("No se encontró ningún alumno con ese ID.")

# Mostrar Todos los Registros
elif menu == "Mostrar Todos los Registros":
    st.title("Registros")
    if data:
        formatted_data = []
        for record in data:
            total_asistencias = sum(day["asistencias"] for day in record.get("registros", {}).values())
            total_retardos = sum(day["retardos"] for day in record.get("registros", {}).values())
            formatted_data.append({
                "ID": record["id"],
                "Apellido Paterno": record["apellido_paterno"],
                "Apellido Materno": record["apellido_materno"],
                "Nombre": record["nombre"],
                "Matrícula": record["matricula"],
                "Licenciatura": record["nivel"],
                "Total Asistencias": total_asistencias,
                "Total Retardos": total_retardos
            })

        df = pd.DataFrame(formatted_data)
        df.set_index('ID', inplace=True)
        st.dataframe(df, use_container_width=True)


    # Generar equipos
    generar_equipos = st.checkbox("Generar Equipos")
    
    if generar_equipos:
        # Extraer las materias y niveles disponibles en los registros
        materias = list(set(record["materia"] for record in data))
        niveles = list(set(record["nivel"] for record in data))
        
        materia = st.selectbox("Selecciona la Materia", materias)
        #nivel = st.selectbox("Selecciona el Nivel", niveles)
        cantidad_de_equipos = st.number_input("Cantidad de equipos", min_value=1, step=1)
        
        if st.button("Generar Equipos"):
            # Filtrar alumnos por materia y nivel
            alumnos_filtrados = [record for record in data if record["materia"] == materia]
            if not alumnos_filtrados:
                st.warning("No hay estudiantes registrados con esa materia y nivel.")
            else:
                total_alumnos = len(alumnos_filtrados)
                if total_alumnos < cantidad_de_equipos:
                    st.warning("No hay suficientes alumnos para formar esa cantidad de equipos.")
                else:
                    # Calcular cuántos estudiantes deben ir en cada equipo
                    estudiantes_por_equipo = total_alumnos // cantidad_de_equipos
                    estudiantes_extra = total_alumnos % cantidad_de_equipos

                    random.shuffle(alumnos_filtrados)  # Mezclar aleatoriamente
                    
                    equipos = []
                    start_idx = 0
                    for i in range(cantidad_de_equipos):
                        # Asignar el número de estudiantes extra a los primeros equipos
                        end_idx = start_idx + estudiantes_por_equipo + (1 if i < estudiantes_extra else 0)
                        equipo = alumnos_filtrados[start_idx:end_idx]
                        equipos.append({"Equipo": len(equipos) + 1, "Integrantes": [alumno["nombre"] + " " + alumno["apellido_paterno"] for alumno in equipo]})
                        start_idx = end_idx


                    # Mostrar los equipos generados con el índice en "Equipo"
                    st.write("Equipos:") 
                    equipos_df = pd.DataFrame(equipos)
                    equipos_df.set_index("Equipo", inplace=True)  # Convertir "Equipo" en el índice
                    st.dataframe(equipos_df)


# Importar desde CSV
elif menu == "Importar desde CSV":
    st.title("Importar Alumnos desde CSV")
    archivo_csv = st.file_uploader("Sube un archivo CSV", type=["csv"])

    if archivo_csv is not None:
        try:
            df = pd.read_csv(archivo_csv, encoding="latin-1")
            for _, row in df.iterrows():
                new_id = len(data) + 1
                data.append({
                    "id": new_id,
                    "apellido_paterno": row["apellido_paterno"],
                    "apellido_materno": row["apellido_materno"],
                    "nombre": row["nombre"],
                    "matricula": row["matricula"],
                    "Licenciatura": row["nivel"],
                    "materia": row["materia"],
                    "registros": {}
                })
            save_data(data)
            st.success("Datos importados correctamente desde el archivo CSV.")
        except Exception as e:
            st.error(f"Error al importar el archivo CSV: {e}")
#Terminado!