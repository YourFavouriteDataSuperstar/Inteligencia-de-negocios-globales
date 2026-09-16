# Cómo publicar el sitio web de su proyecto final

**Inteligencia en Negocios Globales · Universidad EAN · 2026**

Su proyecto final ya está convertido en un sitio web. En la carpeta `sitio/` de su
grupo encuentran el archivo **`index.html`**: ese único archivo es el sitio completo.
Las gráficas, las tablas y los estilos están adentro, así que no necesitan nada más.

Para verlo en su computador basta con hacerle doble clic. Para que quede en internet
con un enlace propio, sigan estos pasos. **No hay que programar nada.**

---

## Lo que van a lograr

Una dirección pública como `https://suusuario.github.io/proyecto-ing/` que pueden
poner en la hoja de vida, compartir con una empresa o enviar por WhatsApp. El sitio
queda en **su** cuenta, no en la de la profesora, y es gratis para siempre.

---

## Paso 1. Crear la cuenta (una sola persona del equipo)

1. Entren a [github.com](https://github.com) y hagan clic en **Sign up**.
2. Registren un correo, una contraseña y un nombre de usuario.
   El nombre de usuario aparecerá en la dirección del sitio, así que elijan algo
   presentable: `laura-barbosa` sirve, `xXpapi_2005Xx` no tanto.
3. Confirmen el correo que les llega.

> Si alguien del equipo ya tiene cuenta de GitHub, úsenla y sáltense este paso.

---

## Paso 2. Crear el repositorio

1. Arriba a la derecha, clic en **+** y luego en **New repository**.
2. En **Repository name** escriban un nombre sin espacios ni tildes, por ejemplo
   `proyecto-inteligencia-negocios`.
3. **Marquen la opción `Public`.** Esto es obligatorio: en las cuentas gratuitas de
   GitHub, la publicación de sitios solo funciona con repositorios públicos.
4. Marquen **Add a README file**.
5. Clic en **Create repository**.

---

## Paso 3. Subir el archivo del sitio

1. Dentro del repositorio, clic en **Add file** y luego en **Upload files**.
2. Arrastren el archivo **`index.html`** a la zona punteada, o búsquenlo con
   **choose your files**.
3. Abajo, clic en el botón verde **Commit changes**.

El archivo pesa unos 3 MB, así que la subida tarda unos segundos. Cuando termine,
debe aparecer `index.html` en la lista de archivos del repositorio.

---

## Paso 4. Encender la publicación

1. En la barra superior del repositorio, clic en **Settings**.
2. En el menú de la izquierda, clic en **Pages**.
3. En **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` y la carpeta `/ (root)`
4. Clic en **Save**.

---

## Paso 5. Esperar y copiar el enlace

Esperen entre uno y tres minutos y recarguen esa misma página de **Settings → Pages**.
Aparecerá un recuadro que dice:

> **Your site is live at** `https://suusuario.github.io/proyecto-inteligencia-negocios/`

Ese es el enlace del sitio. Ábranlo, revisen que todo se vea bien y compártanlo.

---

## Cómo actualizar el sitio después

Si necesitan corregir algo y reciben un `index.html` nuevo:

1. Entren al repositorio.
2. **Add file → Upload files**, arrastren el archivo nuevo (debe llamarse igual,
   `index.html`) y **Commit changes**.
3. En uno o dos minutos la dirección ya muestra la versión corregida.

---

## Si algo sale mal

| Lo que ven | Qué pasó | Cómo se arregla |
|---|---|---|
| Error **404** al abrir el enlace | El sitio todavía no termina de publicarse, o el archivo no está en la raíz | Esperen dos minutos más y recarguen. Verifiquen que el archivo se llame exactamente `index.html` y esté al mismo nivel que el README |
| En **Settings** no aparece la opción **Pages** | El repositorio quedó privado | Settings → abajo del todo → **Change repository visibility** → `Make public` |
| La página abre pero sin gráficas ni colores | Subieron otro archivo, no el `index.html` de la carpeta `sitio/` | Vuelvan al Paso 3 con el archivo correcto |
| La subida se queda pegada | Conexión lenta con un archivo de 3 MB | Intenten de nuevo desde otra red |

---

## Alternativa rápida, sin crear cuenta

Si solo quieren mostrar el sitio en una sustentación y no les interesa que quede
permanente: entren a [app.netlify.com/drop](https://app.netlify.com/drop) y arrastren
ahí el archivo `index.html`. En segundos les dan un enlace público. Ojo: si nadie
reclama ese sitio con una cuenta, desaparece a los pocos días.

---

## Para quien quiera ir más allá

En la carpeta `sitio/` también está `index.ipynb` (el cuaderno con la configuración
del sitio) y `ean.scss` (los colores institucionales). Con
[Quarto](https://quarto.org) instalado, el sitio se vuelve a generar con un comando:

```bash
quarto render index.ipynb
```
