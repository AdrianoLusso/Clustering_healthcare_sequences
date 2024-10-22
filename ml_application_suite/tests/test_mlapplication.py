from src.model.mlApplication.MLApplication import MLApplication
import traceback
from io import StringIO
import os

def get_object(directory):
    with open(directory,'r',encoding='utf-8') as f:
        content = f.read()
    return StringIO(content)

def save_result(case,et,afs,ase,md,c):
    output_directory = 'dataset/'+str(case)+'/results/'
    with open(os.path.join(output_directory, 'estados_timeframes.csv'), 'w') as f:
        f.write(et.getvalue())  # Assuming it's in CSV format

    with open(os.path.join(output_directory, 'afiliados_secuencias.csv'), 'w') as f:
        f.write(afs.getvalue())  # Assuming it's in CSV format

    with open(os.path.join(output_directory, 'afiliados_secuencias_etiquetadas.csv'), 'w') as f:
        f.write(ase.getvalue())  # Assuming it's in CSV format

    with open(os.path.join(output_directory, 'matriz_disimilitud.csv'), 'w') as f:
        f.write(md.getvalue())  # Assuming it's in CSV format

    with open(os.path.join(output_directory, 'clustering.json'), 'w') as f:
        f.write(c.getvalue())  # Assuming it's in CSV format


def test_workflow(not_to_run:list[int] = [],show_traceback:bool = False):
    cases = [
        # 0
        {
            "debug": True,

            "afiliados_practicas": get_object('dataset/raw/affiliate_practice.csv'),

            "practicas_interes": {
                "diabetes": get_object("dataset/raw/diabetes_practices.csv")
            },

            "unidad_timeframe": 'semestre',
            "numero_timeframes": 7,
            "fecha_superior_ultimo_timeframe": "2024-07-1",

            "matriz_disimilitud_precomputada": False,

            "n_grupos": "optimizado",
            "umbral_de_filtrado_de_grupos": None
        },
        # 1
        {
            "debug": True,

            "afiliados_monodrogas": 'dataset/raw/affiliate_monodrug.csv',

            "monodrogas_interes": {
                "diabetes": "dataset/raw/diabetes_monodrug.csv"
            },
            "estados_timeframes": 'dataset/1/preprocessed/dataframes_states_dataset.csv',
            "afiliados_secuencias": 'dataset/1/preprocessed/sequences_dataset.csv',
            "afiliados_secuencias_etiquetadas": 'dataset/1/preprocessed/labeled_sequences_dataset.csv',

            "unidad_timeframe": 'semestre',
            "numero_timeframes": 7,
            "fecha_superior_ultimo_timeframe": "2024-07-1",

            "matriz_disimilitud_precomputada": True,
            "matriz_disimilitud": "dataset/1/preprocessed/dissimilarity_matrix.csv",

            "n_grupos": "optimizado",
            "umbral_de_filtrado_de_grupos": None,

            "agrupamientoSecuencias": "dataset/1/results/clustering.json"
        },
        # 2
        {
            "debug": True,

            "afiliados_practicas": 'dataset/raw/affiliate_practice.csv',

            "practicas_interes": {
                "diabetes": "dataset/raw/diabetes_practices.csv"
            },
            "estados_timeframes": 'dataset/2/preprocessed/dataframes_states_dataset.csv',
            "afiliados_secuencias": 'dataset/2/preprocessed/sequences_dataset.csv',
            "afiliados_secuencias_etiquetadas": 'dataset/2/preprocessed/labeled_sequences_dataset.csv',

            "unidad_timeframe": 'semestre',
            "numero_timeframes": 7,
            "fecha_superior_ultimo_timeframe": "2024-07-1",

            "matriz_disimilitud_precomputada": False,
            "matriz_disimilitud": "dataset/2/preprocessed/dissimilarity_matrix.csv",

            "n_grupos": "optimizado",
            "umbral_de_filtrado_de_grupos": None,

            "agrupamientoSecuencias": "dataset/2/results/clustering.json"
        },
        # 3
        {
            "debug": True,

            "afiliados_practicas": 'dataset/raw/affiliate_practice.csv',

            "practicas_interes": {
                "diabetes": "dataset/raw/diabetes_practices.csv"
            },
            "estados_timeframes": 'dataset/3/preprocessed/dataframes_states_dataset.csv',
            "afiliados_secuencias": 'dataset/3/preprocessed/sequences_dataset.csv',
            "afiliados_secuencias_etiquetadas": 'dataset/3/preprocessed/labeled_sequences_dataset.csv',

            "unidad_timeframe": 'mes',
            "numero_timeframes": 13,
            "fecha_superior_ultimo_timeframe": "2023-05-1",

            "matriz_disimilitud_precomputada": False,
            "matriz_disimilitud": "dataset/3/preprocessed/dissimilarity_matrix.csv",

            "n_grupos": "optimizado",
            "umbral_de_filtrado_de_grupos": None,

            "agrupamientoSecuencias": "dataset/3/results/clustering.json"
        },
        # 4
        {
            "debug": True,

            "afiliados_practicas": 'dataset/raw/affiliate_practice.csv',

            "practicas_interes": {
                "diabetes": "dataset/raw/diabetes_practices.csv"
            },
            "estados_timeframes": 'dataset/4/preprocessed/dataframes_states_dataset.csv',
            "afiliados_secuencias": 'dataset/4/preprocessed/sequences_dataset.csv',
            "afiliados_secuencias_etiquetadas": 'dataset/4/preprocessed/labeled_sequences_dataset.csv',

            "unidad_timeframe": 'anio',
            "numero_timeframes": 3,
            "fecha_superior_ultimo_timeframe": "2022-02-1",

            "matriz_disimilitud_precomputada": False,
            "matriz_disimilitud": "dataset/4/preprocessed/dissimilarity_matrix.csv",

            "n_grupos": "3",
            "umbral_de_filtrado_de_grupos": None,

            "agrupamientoSecuencias": "dataset/4/results/clustering.csv"
        },
    ]

    app = MLApplication()
    for itr,case in enumerate(cases):
        if itr in not_to_run:
            continue

        print('Running case', itr)
        try:
            (estados_timeframes,
             afiliados_secuencias,
             afiliados_secuencias_etiquetadas,
             matriz_disimilitud,
             clustering) =  app.run_affiliatesHealthcarePathways_clustering(case)
            save_result(itr,
                        estados_timeframes,
                        afiliados_secuencias,
                        afiliados_secuencias_etiquetadas,
                        matriz_disimilitud,
                        clustering)

            print('Succeed!')
        except Exception as e:
            print('ERROR IN CASE', itr)
            if show_traceback:
                traceback.print_exc()
        finally:
            print('\n')




if __name__ == '__main__':
    test_workflow(not_to_run=[],show_traceback=True)

