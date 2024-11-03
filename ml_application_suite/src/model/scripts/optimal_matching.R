args <- commandArgs(trailingOnly = TRUE)

input_dir <- args[1]

tryCatch(
{
    # Verifica si el archivo de entrada existe
    if (!file.exists(input_dir)) {
      stop("El archivo de entrada no existe: ", input_dir)
    }

    # importar traminer
    .libPaths("./")
    library("TraMineR")

    dataset <- read.csv(input_dir)

    # seleccionar columnas que representen timeframes
    pattern <- "^(semester|year|month)_"  # Expresión regular
    selected_cols <- grep(pattern, names(dataset), value = TRUE)

    # Verificar si hay columnas de timeframes
    if (length(selected_cols) == 0) {
      stop("No se encontraron columnas de timeframes en el dataset.")
    }

    sequences_matrix <- as.matrix(dataset[,selected_cols])
    sequences <- seqdef(sequences_matrix)

    om = seqdist(sequences,method="OM",indel=1,sm="TRATE")
    om <- om[,-1]

    write.csv(om,stdout())
}
,error = function(e) {
        message("Error': ", e$message)
        return(e)  # Retorna el objeto de la excepción
    }
)