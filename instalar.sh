#!/bin/bash
# Instala VideoIA en macOS: dependencias, entorno de Python, modelo y comando.
set -euo pipefail
RAIZ="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RAIZ"

faltan=()
command -v ffmpeg >/dev/null || faltan+=(ffmpeg)
command -v node >/dev/null || faltan+=(node)
if [ ${#faltan[@]} -gt 0 ]; then
  command -v brew >/dev/null || { echo "Falta Homebrew (https://brew.sh). Instálalo y vuelve a ejecutar." >&2; exit 1; }
  echo "Instalando con Homebrew: ${faltan[*]}"
  brew install "${faltan[@]}"
fi
node -e 'if(+process.versions.node.split(".")[0]<22){console.error("HyperFrames necesita Node 22 o superior.");process.exit(1)}'
[ -d "/Applications/Google Chrome.app" ] || echo "Aviso: no encontré Google Chrome; HyperFrames intentará descargar su propio navegador."

echo "Preparando Python…"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

echo "Descargando el modelo de transcripción, si falta (unos 1,5 GB)…"
.venv/bin/python -c "from faster_whisper import download_model; download_model('medium')" 2>/dev/null

echo "Preparando HyperFrames…"
npx --yes hyperframes@0.9.14 --version >/dev/null

mkdir -p "$HOME/.local/bin"
ln -sf "$RAIZ/bin/videoia" "$HOME/.local/bin/videoia"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "Añade esto a tu ~/.zshrc y abre otra terminal:"; echo '  export PATH="$HOME/.local/bin:$PATH"' ;;
esac
command -v claude >/dev/null || echo "Aviso: sin Claude Code, VideoIA crea un plan básico sin gráficos a medida."
echo "Listo. Pon tu video en Material-Crudo/ y ejecuta: videoia"
