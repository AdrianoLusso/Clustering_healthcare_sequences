#!/bin/bash

# Directorio a buscar (puedes cambiar el directorio por defecto)
DIRECTORIO=${1:-.}

# Tamaño mínimo en MB
TAMANIO_MIN=25

find "$DIRECTORIO" -type d -name ".git" -prune -o -type f -size +${TAMANIO_MIN}M -print


# Ejecutar el comando find para buscar y eliminar archivos mayores a TAMANIO_MIN MB excluyendo el directorio .git
find "$DIRECTORIO" -type d -name ".git" -prune -o -type f -size +${TAMANIO_MIN}M -exec rm -f {} \;

echo "Archivos mayores a $TAMANIO_MIN MB eliminados en $DIRECTORIO (excluyendo .git)"