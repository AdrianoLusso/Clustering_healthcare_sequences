
if (!requireNamespace("TraMineR", quietly = TRUE)) {
    tryCatch({
        .libPaths("./")

        install.packages("colorspace",lib = "./")
        install.packages("TraMineR", lib = "./")
        
        library("TraMineR")
    }, error = function(e) {
        message("Error al instalar el paquete 'TraMineR': ", e$message)
        return(e)  # Retorna el objeto de la excepción
    })
}
