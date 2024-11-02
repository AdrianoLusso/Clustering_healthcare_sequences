if (!requireNamespace("TraMineR", quietly = TRUE)) {
  tryCatch({
    install.packages("TraMineR", repos = "http://cran.r-project.org")
  }, error = function(e) {
    stop("Error al instalar TraMineR: ", e$message)
  })
}
