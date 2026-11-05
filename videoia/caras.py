"""Mide dónde está la cara en un video 1080×1920 con YuNet. Uso: caras.py <video> <modelo.onnx>"""
import json
import statistics
import sys

import cv2


def main():
    cap = cv2.VideoCapture(sys.argv[1])
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 30)
    det = cv2.FaceDetectorYN.create(sys.argv[2], "", (w, h), 0.7)
    arriba, abajo = [], []
    muestras = 24
    for i in range(muestras):
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * dur * (i + 0.5) / muestras)
        ok, f = cap.read()
        if not ok:
            continue
        _, caras = det.detect(f)
        if caras is None:
            continue
        c = max(caras, key=lambda x: x[2] * x[3])
        arriba.append(float(c[1]))
        abajo.append(float(c[1] + c[3]))
    if not arriba:
        print(json.dumps({"encontrada": False}))
        return
    print(json.dumps({"encontrada": True, "arriba": statistics.median(arriba), "abajo": max(abajo), "muestras": len(arriba)}))


if __name__ == "__main__":
    main()
