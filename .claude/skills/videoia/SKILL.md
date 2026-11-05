---
name: videoia
description: Edita un video crudo de Material-Crudo/ y lo convierte en un anuncio vertical para Reels con el comando videoia, o rehace la guía de estilo con Referencias/. Usar cuando pidan editar un video, hacer un reel o anuncio, ajustar un plan de escenas o actualizar la guía de estilo en este proyecto.
---

# VideoIA

1. Lee `Editor IA/Guia-de-estilo.md`.
2. Comprueba que haya un video en `Material-Crudo/`; si falta, pídelo.
3. Si `.venv` no existe, indica a la persona que ejecute `./instalar.sh` y pide su visto bueno antes de ejecutarlo tú.
4. Ejecuta `bin/videoia --no-abrir` en segundo plano. Sin terminal interactiva, se detiene en la vista previa sin exportar.
5. Enseña `Resultados/<video>-plan.md` y la vista previa, y señala lo que haya en "Por confirmar".
6. Para cambios, edita `.videoia/<video>/plan.json` y vuelve a ejecutar. El formato está en `videoia/prompt_plan.md`.
7. Exporta con `bin/videoia --final --video <archivo>` solo cuando la persona apruebe.

Para actualizar la guía: `bin/videoia estilo` (guarda una copia de la anterior).

No cambies el mensaje ni inventes cifras. No subas medios de `Material-Crudo/`, `Referencias/` ni `Resultados/`.

Si usas las skills `hyperframes` o `media-use`, omite su aviso de uso y mantén `HYPERFRAMES_NO_TELEMETRY=1`.
