# Kennedy cohabitable · simulador

Simulador de 20 años de Corabastos y el Humedal La Vaca (Kennedy, Bogotá). Compara la continuidad del problema ("Situación actual") con el masterplan ("Propuesta").

## Cómo ejecutarlo
1. Descargar el repositorio.
2. Abrir `index.html` en Chrome, Edge o Firefox (no requiere instalar nada; necesita internet solo para cargar Three.js r128 desde cdnjs y las fuentes).
3. Elegir **Situación actual** o **Propuesta** en la pantalla de inicio.

## Par piloto
| Escenario | Archivo | Qué hacer | Resultado esperado |
|---|---|---|---|
| Continuidad | `escenarios/piloto_01_actual.json` | Situación actual → play | Game over en el año 11,4 |
| Propuesta | `escenarios/piloto_01_propuesta.json` | Propuesta → play hasta el año 20 | Sostenible, no alcanzado hasta el año 20 |

Las variables de cada escenario están en la pestaña **Variables** (valores base = "Restablecer valores base"). Para otros escenarios, mover las barras con los valores del archivo JSON.

- Semilla aleatoria: 7 (fija en el código, `rnd`). Los indicadores son deterministas; solo la animación de agentes usa aleatoriedad adicional.
- Horizonte: 20 años. Tic = 1 año; la regla de game over se evalúa cada 0,05 años.

## Dónde ver los indicadores y el game over
- Pestaña **Indicadores**: valor actual, trayectoria y "Cómo se calcula" con la fórmula.
- Línea de tiempo: marcas rojas = umbral cruzado; marca rosa = game over.
- Regla: game over al cruzar 3 umbrales (presión sanitaria ≥ 95 %, tinguas < 3, especulación ≥ 75, residuo sin tratar ≥ 110 t/día; en la propuesta además capital social ≤ 4,5).

## Reconstruir desde los datos
`src/index.src.html` es la plantilla; `data/data.json` los datos. Para regenerar `index.html`:
```
python3 -c "s=open('src/index.src.html').read();open('index.html','w').write(s.replace('__DATA__',open('data/data.json').read()))"
```
`src/build.py` (Python 3.11, numpy, shapely, opencv-python) genera `data.json` a partir de las capas GeoJSON del grupo (edificios, vías, parques, ríos, arbolado) y del plano del masterplan; las rutas de entrada están al inicio del archivo.

## Tráfico en tiempo real (TomTom)
Versión web: https://tatisromg36.github.io/SIMULADOR-KENNEDY/
En la leyenda, sección «Tráfico en tiempo real», pega una clave de TomTom (developer.tomtom.com) y pulsa Activar. Cada 3 minutos se consultan 14 tramos (accesos de carga y avenidas) con Flow Segment Data; la velocidad de autos y camiones, el mapa de ruido y las líneas de color sobre las vías siguen esos datos. La clave se guarda solo en el navegador de quien la escribe. Restríngela en TomTom al dominio tatisromg36.github.io.
