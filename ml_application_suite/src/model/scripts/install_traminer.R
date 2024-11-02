if (!requireNamespace("TraMineR", quietly = TRUE)) {
    tryCatch({
        install.packages("TraMineR")
    }, error = function(e) {
        message("Error al instalar el paquete 'TraMineR': ", e$message)
        return(e)  # Retorna el objeto de la excepción
    })
}
