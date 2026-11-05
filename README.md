# VideoIA

Del video crudo al anuncio vertical para Reels con un solo comando.

```bash
videoia
```

Pone subtítulos sincronizados, gráficos animados, música y efectos, y deja el video a 1080×1920 y −14 LUFS, con textos dentro de la zona segura de anuncios.

## Instalación (macOS)

```bash
git clone https://github.com/xJeffx23/VideoIA.git
```

```bash
cd VideoIA && ./instalar.sh
```

El instalador usa Homebrew para ffmpeg y Node si faltan, crea el entorno de Python, descarga el modelo de transcripción (unos 1,5 GB) y deja disponible el comando `videoia`.

Necesitas [Claude Code](https://claude.com/claude-code) con sesión iniciada para que el plan de escenas se haga a medida. Sin él, `videoia` crea un plan básico solo con títulos y cifras. También necesitas Google Chrome para el render.

## Uso

1. Pon tu video en `Material-Crudo/`.
2. Ejecuta `videoia`.
3. Revisa la vista previa y el plan que se abren, y responde `s` para exportar.

Los archivos quedan en `Resultados/`:

| Archivo | Contenido |
|---|---|
| `<video>-plan.md` | Plan de edición y textos por confirmar |
| `<video>-vista-previa.mp4` | Video para revisar |
| `<video>-final.mp4` | Versión final aprobada |
| `<video>-creditos.md` | Créditos que debes conservar |

### Opciones

| Comando | Qué hace |
|---|---|
| `videoia --video clip.mov` | Edita un video concreto de `Material-Crudo/` |
| `videoia --replan` | Rehace el plan de escenas |
| `videoia --final` | Exporta la última vista previa |
| `videoia --si` | Exporta sin preguntar |
| `videoia --sin-ia` | Usa el plan básico |
| `videoia estilo` | Rehace la guía con los videos de `Referencias/` |

Para ajustar textos o escenas, edita `.videoia/<video>/plan.json` y vuelve a ejecutar `videoia`.

## Carpetas

| Carpeta | Contenido | ¿Se sube a GitHub? |
|---|---|---|
| `Material-Crudo/` | Tu video y, si quieres, tu propia música | No |
| `Referencias/` | Videos de inspiración para `videoia estilo` | No |
| `Editor IA/` | `Guia-de-estilo.md` y `estilo.json` (paleta) | Sí |
| `Resultados/` | Lo que genera VideoIA | No |

## Qué hace el comando

1. **Transcribe** en local; el video no sale del equipo. Claude solo recibe el texto.
2. **Planea** escenas, correcciones y repeticiones según tu guía de estilo.
3. **Corta** silencios y repeticiones por el audio, con IT Reelsmaker.
4. **Encuadra** midiendo la cara, para colocar el panel sin ampliar el video.
5. **Renderiza** gráficos y subtítulos palabra por palabra con HyperFrames.
6. **Mezcla** voz, música y efectos a −14 LUFS.
7. **Muestra** la vista previa y exporta solo si la apruebas.

## Antes de publicar

- Confirma lo que aparece en "Por confirmar" del plan: la transcripción puede fallar, sobre todo en cifras.
- La música incluida es CC BY: da el crédito indicado en [CREDITOS.md](CREDITOS.md) o pon tu propio audio en `Material-Crudo/`.
- Comprueba la zona segura con la guía de Ads Manager.

## Skills para Claude Code

Al abrir esta carpeta en Claude Code tienes `/videoia`, además de las skills incluidas: `it-reelsmaker`, `hyperframes`, `hyperframes-cli` y `media-use`. Sus licencias están en cada carpeta y en [CREDITOS.md](CREDITOS.md).
