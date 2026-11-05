# Guía de estilo: videos verticales

Basada en los 5 videos de `Referencias/` (transcripción, frames y medición de audio y color).
**Revísala antes de cada proyecto.**

## En una frase

Fondo casi negro, persona en un panel abajo, una idea animada arriba, subtítulos blancos de pocas palabras y un solo acento rojo.

---

## 1. Lo que se repite en los referentes

| Elemento | Se repite | Dato |
|---|---|---|
| Inicio | Se habla desde el primer fotograma | 5 de 5: primera palabra en 0,00 s |
| Gancho | Promesa o pregunta directa en la primera frase | 4 de 5 (Referencia 5 es una presentación personal) |
| Título fijo arriba | Sans negrita + serif itálica para la parte clave | Referencias 1 y 2; Referencia 4 usa la misma mezcla en sus frases |
| Ritmo de voz | Rápido y casi sin aire | 186–235 palabras/min; pausa máxima 0,34–0,62 s |
| Composición | Panel de persona abajo y gráfico arriba, alternando con persona a pantalla completa | Referencias 1, 2 y 3 |
| Subtítulos | Blancos, 1–3 palabras, sin caja ni mayúsculas sostenidas | Referencias 1, 2 y 3 |
| Fondo | Casi negro | 53–67 % de píxeles oscuros en Referencias 1–4 |
| Acento | Un solo color cálido por video | Rojo en 1, 2 y 4; naranja en 3 |
| Volumen | Máster uniforme | −14,2 a −14,3 LUFS en los 5 |
| Música | Cama continua bajo la voz | Entre palabras queda sonido, unos 17 dB bajo la voz (1, 2, 3 y 5) |

**Referencia 5 es la excepción:** tiene exteriores, color pastel, texto amarillo y emoji. No marca el estilo. De ella solo tomo el número gigante como recurso.

### Por referente

| Video | Gancho | Lo que aporta |
|---|---|---|
| Referencia 1 | "There's a new type of content that is starting to crush on social media." | Panel abajo, línea de tiempo, métricas en verde, cierre con "Comment…" |
| Referencia 2 | "¿Por qué tu Claude edita como profesional, pero el audio siempre sale mal?" | Título con subrayado rojo, ondas e interfaces, conteo hasta números grandes |
| Referencia 3 | "Hoy vamos a ver cómo hacer videos explicativos como este, con un solo prompt…" | Gráfico que se transforma entre escenas |
| Referencia 4 | "How would I make a million dollars in one year from zero?" | Cifra roja gigante con brillo, cortes más rápidos (39 cambios en 39 s) |
| Referencia 5 | "Hey, this is my first reel." | Número gigante, tono personal |

---

## 2. Paleta

| Rol | Color | Uso |
|---|---|---|
| Fondo | `#050505` | Base de todo gráfico |
| Superficie | `#141416` | Tarjetas e interfaces, con borde `#2A2A2E` |
| Texto | `#FFFFFF` | Títulos y subtítulos |
| Texto secundario | `#A1A1AA` | Etiquetas y datos de apoyo |
| **Acento rojo** | `#E42430` | Palabra clave, subrayado, nodos activos, CTA |
| Rojo brillo | `#FC0000` | Solo en brillo y cifras gigantes |
| Positivo | `#22C55E` | Solo métricas o confirmaciones |

Una cuadrícula de puntos muy tenue sobre el fondo, con un resplandor rojo suave detrás del elemento activo.

---

## 3. Tipografías

Identificadas a ojo a partir de los frames; son las equivalentes gratuitas más cercanas (Google Fonts).

| Uso | Fuente | Tamaño a 1080 px |
|---|---|---|
| Títulos y subtítulos | **Inter Tight** Bold, interletraje −2 % | Subtítulo 64–72 · título 46–52 |
| Palabra clave | ***Instrument Serif* Italic** | Título 84–96 |
| Cifras gigantes | **Inter Tight** ExtraBold | 150–220 |
| Etiquetas de interfaz | **JetBrains Mono** | 22–28 |

Mayúscula inicial normal. Serif solo para la parte clave de la frase, nunca para una frase larga.

---

## 4. Reglas de edición

### Encuadre (1080×1920)
- **Modo panel:** gráfico arriba (y 280–690), persona en panel redondeado abajo (x 54–1026, y 700–1866, radio 36 px), subtítulo en y≈1120–1250.
- **Sin zoom en el panel:** la persona se ve con el plano abierto, reducida a ×0,9 sin recortar los lados. Nunca amplío el video en el panel: se pierde calidad y la cara queda demasiado cerca.
- **Modo persona:** pantalla completa a ×1,0, subtítulo a la altura del pecho, nunca sobre la cara.
- Alterno entre ambos: el gancho va en panel y la persona a pantalla completa da respiro cada 6–10 s.
- Nada importante en los primeros 140 px superiores ni en los 120 px de la derecha, donde tapa la interfaz de la app.

### Gancho (0–3 s)
- Voz desde el primer fotograma, sin saludo ni logo.
- Título fijo que resume el problema en máximo 8 palabras, con la parte clave en serif itálica.
- El título sale de lo que se dice; no promete nada que el video no diga.

### Ritmo
- Silencios recortados, dejando pausas naturales de 0,10–0,25 s. Nada de cortes dentro de palabras.
- Objetivo de voz: 190–235 palabras/min, sin acelerar más de ×1,08.
- Un cambio visual cada 2–4 s.
- Los cortes llevan un fundido de audio de 15–30 ms, y se tapan con un cambio de plano o de escena.

### Subtítulos
- 1–3 palabras a la vez, sincronizadas con la voz palabra por palabra.
- Blanco sobre fondo oscuro, contraste mínimo de 4,5:1. Si el fondo es claro, degradado oscuro debajo, no contorno.
- Entrada de 4–6 fotogramas: desenfoque y subida de 12 px. Sin rebotes.
- Palabra clave en rojo o más grande, nunca ambas.
- Corrección de texto obligatoria frente a lo que se dice; las cifras se verifican con la persona.

### Animación
- Título: palabra por palabra, con desenfoque a nítido; el subrayado rojo se dibuja de izquierda a derecha.
- Gráficos: se trazan líneas, nodos y barras al ritmo de la palabra que los nombra (±2 fotogramas).
- Curvas suaves de salida (`power3.out`), entradas de 0,25–0,5 s.
- Máximo 4 palabras por escena gráfica, sin contar subtítulos.
- Un elemento se transforma en el siguiente cuando se pueda, en vez de cortar a uno nuevo.

### Sonido
- Máster final a **−14 LUFS**, pico máximo −1 dBTP.
- Música continua, sin letra, unos 18–22 dB bajo la voz, y sube levemente en el cierre.
- Efectos solo en eventos visibles: *whoosh* en cambio de escena, *pop* o clic en elemento que aparece, impacto suave en la cifra clave.
- Entre 6 y 12 efectos por cada 30 s, siempre por debajo de la voz.

### Cierre
- Una sola llamada a la acción, tal como se dice en el audio, con palabra clave en una etiqueta roja.

---

### Anuncio en Reels de Instagram
- Todo texto, cifra y llamada a la acción va dentro de la zona segura: **x 65–1015, y 269–1248** (márgenes de 14 % arriba, 35 % abajo y 6 % a los lados, según guías que citan a Meta). Confírmala en Ads Manager.
- La cara también queda por encima de y 1248, porque debajo van el texto del anuncio y el botón de Instagram.
- No dibujo un botón abajo: lo pone la plataforma, y debe coincidir con la llamada a la acción del video.
- Toda cifra o resultado debe poder comprobarse.
- La música debe tener licencia comercial; si exige crédito, va en el texto del anuncio.
- Exporto en la calidad más alta del render: 1080×1920, H.264 y AAC.

---

## 5. Lo que no hago

- Subtítulos amarillos, con caja, contorno, sombra dura o MAYÚSCULAS todo el rato.
- Más de un color de acento, o verde y rojo como decoración.
- Emojis, stickers o memes.
- Transiciones llamativas: zoom brusco, giros, *glitch*, destellos.
- Rebotes exagerados en el texto.
- Intro con logo o saludo antes del gancho.
- Texto sobre la cara, o que tape manos y producto.
- Música con letra o más presente que la voz.
- Efectos de sonido en cada palabra.
- Cambiar el mensaje, inventar cifras o añadir promesas que la persona no dijo.
- Música o sonidos sin licencia clara.

---

## 6. Lista antes de exportar

- [ ] 1080×1920 y voz desde el primer fotograma
- [ ] Mensaje original completo, sin repeticiones ni palabras cortadas
- [ ] Subtítulos revisados contra el audio; cifras confirmadas
- [ ] Ningún texto sobre la cara ni en zonas de interfaz
- [ ] Un solo acento de color
- [ ] −14 LUFS y pico por debajo de −1 dBTP
- [ ] Créditos de música y sonidos guardados
- [ ] Vista previa aprobada
