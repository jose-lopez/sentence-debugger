Sobre el propósito de este programa:

El presente programa desarrollado en Python, denominado debugger, recibe una colección de archivos en griego antiguo cuyas oraciones han sido en buena medida recuperadas, o etiquetadas como ruidosas (que tienen lagunas). Ya sea que se trate de palabras/frases recuperadas o ruidosas, las oraciones del caso incluyen dobles corchetes en los lugares correspondientes. A continuación un ejemplo:

⸤Κλ⸥υτοφόρμιγγες Δ[ιὸς ὑ-] ⸤ψιμέδοντος πα[ρθέ]νοι,⸥ [–⏑⏑ Πι]ερίδες [–] [–]ενυφαι[⏑⏑––] [–⏑⏑]ο?υς, ἵνα κ[––] [–⏑]γαίας Ἰσθμί[ας] [––⏑]ν, εὐβούλου ν?[⏑–] [–⏑ γαμ]βρὸν Νηρέ[ος] [⏑⏑–] νάσοιό τ' ἐϋ[⏑ ⏑ ]αν, ἔνθ?[–⏑–] –⏑⏑–⏑⏑–– –⏑⏑–⏑⏑–– ⸤ὦ Πέλοπος λιπαρᾶς νάσου θεόδματοι πύλαι⸥

El objetivo aqui es procesar la totalidad de los archivos suministrados y generar como salida cuatro colecciones de archivos; cada una de ellas vinculada a versiones de cada archivo original. Las cuatro colecciones corresponden a oraciones: limpias, ruidosas, extrañas y recuperadas. Cada colección de archivos se guarda en carpetas con el mismo nombre, accesibles en ./ancient_greek_test/.

Oraciones limpias: Corresponden éstas tanto a las oraciones completas sin restauración como a aquellas que han sido restauradas. 

Oraciones ruidosas: Son oraciones cuyas lagunas han sido demarcadas en dobles corchetes. Para propósito de la programación se ha asumido que el marcado mencionado define el modo correcto de identificar las regiones ruidosas en una oración.

Oraciones extrañas: Corresponden éstas oraciones a aquellos casos en los que una oración ruidosa no sigue el estándar de representación.

Oraciones curadas (restauradas): Se listan en estos archivos solo oraciones restauradas, libres en su totalidad de fragmentos ruidos.

Además de lo anterior, el script genera un par de indicadores, relacionados con el nivel de ruido de los archivos presentes en el corpus suministrado. Tales indicadores son:

Tasa de ruido: Refiere este indicador la proporción de oraciones ruidosas en un archivo, respecto de la totalidad de las mismas. En este caso han sido consideradas tanto las oraciones ruidosas que siguen el estándar como las que no.

Tasa de ruido = (cant. oraciones ruidosas estándares + cant. oraciones ruidosas no estándares)/total cant. oraciones

Índice de ruido: En este caso se procura medir el ruido en un archivo considerando la cantidad de fragmentos ruidosos presentes en sus oraciones. El indicador también es proporcional a la cantidad de oraciones ruidosas que no siguen el estándar. En el futuro, si la aplicación lo requiere, la cantidad de fragmentos no estándares serán debidamente medidos y el indicador debidamente modificado.

Índice de ruido = (cant. fragmentos ruidosos estándares + cant. oraciones ruidosas no estándares)/total cant. oraciones

Los indicadores recién descritos permiten generar reportes sobre los archivos del corpus, ordenados según el grado de ruido que presenten.  Los reportes pueden accederse en ./ancient_greek_test/report.

Para ejecutar el script: 

1. Clone el repo:
	
	$ git clone https://github.com/jose-lopez/sentence-debugger

2. Cambie el directorio:

	$ cd sentence-debugger

3. Ejecute el script:

	$ python3.9 ./src/utilities/debugger.py
