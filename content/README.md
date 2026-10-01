# Guía para editar el contenido del sitio

`content/site.json` es la fuente editable del perfil, Inicio, Proyectos, CV y los cuatro casos. El editor local ofrece formularios para los campos habituales; el archivo JSON permanece como respaldo completo. No edites el HTML generado: el builder lo reemplaza.

## Abrir el editor

1. En Windows, ejecuta `Editar-contenido.cmd` desde el repositorio.
2. Deja abierta la ventana de consola y abre `http://127.0.0.1:8766/` en el navegador. La vista previa del sitio queda en `http://127.0.0.1:8767/`.
3. Selecciona una sección —Sitio, Inicio, Proyectos o CV y trayectoria— y edita los campos. Las áreas de texto conservan párrafos; en listas, escribe un elemento por línea.
4. En Inicio puedes seleccionar tres proyectos. En Proyectos, puedes actualizar títulos, resúmenes, resultados, temas y casos; los cuatro destinos existentes se conservan.
5. Pulsa **Guardar y reconstruir vista previa**. El editor valida el contenido y actualiza las páginas locales; si encuentra un problema, muestra el campo pendiente y restaura el JSON anterior.
6. Abre **Abrir vista previa** para revisar los cambios generados.
7. Para cerrar el editor, vuelve a la consola y pulsa `Ctrl+C`.

Guardar **no publica** el sitio. La publicación requiere revisar los archivos generados y seguir el flujo habitual del repositorio hacia GitHub Pages.

## Criterios de edición

- Escribe hechos y resultados que puedas respaldar. No agregues cifras, fechas, cargos, empresas o tecnologías sin confirmarlos.
- Mantén los identificadores de página, las rutas y los identificadores estables de proyectos.
- Cada proyecto debe conservar al menos un tema existente. Puedes agregar proyectos secundarios o quitar los que no tengan ruta ni estén seleccionados en Inicio; conserva los cuatro casos con ruta y las cuatro prioridades destacadas.
- Edita los textos del relato de Inicio aparte de los registros laborales del CV; cumplen propósitos distintos.
- El contenido son datos y texto plano, no HTML ni instrucciones de presentación. El builder se encarga de la estructura, el escape y la navegación.

## Estructura del contenido

| Campo | Qué contiene |
|---|---|
| `site` | Nombre común, URL canónica, idioma y perfiles públicos. |
| `profile` | Profesión, ubicación, presentación del CV, forma de trabajo y enlace al PDF. |
| `taxonomy.tags[]` | Temas compartidos por los proyectos; cada identificador es un slug estable. |
| `projects[]` | Registros variables con situación, tarea, contribución, resultado, evidencia, temas y prioridad; los cuatro casos existentes incluyen `caseDetails`. |
| `home` | Presentación, cinco etapas de trabajo, tres proyectos, relato profesional, notas y contacto. |
| `projectsPage`, `notFound` | Textos de la portada de Proyectos y la página 404. |
| `career[]` | Organizaciones, períodos, cargos, aportes y enlaces relacionados del CV. |
| `education`, `skills[]`, `languages[]` | Formación, capacidades, herramientas e idiomas. |
| `pages[].seo` | Título, descripción, metadatos sociales y datos estructurados para cada ruta. |
| `editorialRules[]` | Guardas editoriales para mantener contenido fiel y verificable. |

## Validación manual

Desde la raíz del repositorio, ejecuta:

```powershell
python tools/build_site.py
python tools/verify_site.py
```

El generador usa solo la biblioteca estándar de Python. La verificación revisa las rutas, el HTML, los enlaces, las imágenes, los metadatos y el inventario de proyectos.

## PDF del CV

El PDF descargable es un archivo estático. Después de modificar el CV, revisá la página `/cv/` e imprimí o exportá el documento con la acción **Imprimir** del navegador. No hay un generador de PDF automatizado configurado.
