args <- commandArgs(trailingOnly = TRUE)

input_dir <- args[1]

# Verifica si el archivo de entrada existe
if (!file.exists(input_dir)) {
  stop("El archivo de entrada no existe: ", input_dir)
}

#library("TraMineR")
current_directory <- getwd()
print(current_directory)
#source("../../traminer/seqdist.R")
#source("../../traminer/R/seqdef.R")


dataset <- read.csv(input_dir)

pattern <- "^(semester|year|month)_"  # Expresión regular
selected_cols <- grep(pattern, names(dataset), value = TRUE)
# Verificar si hay columnas de semestres
if (length(selected_cols) == 0) {
  stop("No se encontraron columnas de semestres en el dataset.")
}

#sequences_matrix <- as.matrix(dataset[, c("semester_1", "semester_2", "semester_3", "semester_4", "semester_5", "semester_6", "semester_7")])
sequences_matrix <- as.matrix(dataset[,selected_cols])

sequences <- seqdef(sequences_matrix)

om = seqdist(sequences,method="OM",indel=1,sm="TRATE")
om <- om[,-1]

write.csv(om,stdout())