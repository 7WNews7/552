#!/usr/bin/env python3
"""Pack the finished files into dist/KRONOS_STAFF_emoji.zip (run build.py first)."""
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
OUT = os.path.join(DIST, 'KRONOS_STAFF_emoji.zip')

HOWTO = """KRONOS STAFF — 100 эмодзи для Telegram

tgs/     — анимированные эмодзи (TGS: 512x512, 60 к/с, 2–3 с, бесшовная петля)
png/     — статичные эмодзи PNG 100x100 (формат Telegram для статичных эмодзи)
png512/  — те же картинки 512x512 (например, для стикеров)
emoji_list.csv / emoji_list.md — номер, файл, какой обычный эмодзи привязать

Как загрузить анимированный набор:
 1. Откройте бота @Stickers и отправьте /newemojipack
 2. Выберите «Анимированные эмодзи» и придумайте название набора
 3. Отправьте файл из папки tgs (как файл), затем обычный эмодзи из emoji_list
 4. Повторите для остальных файлов (порядок = порядок в наборе)
 5. /publish → /skip (иконка) → короткое имя, например kronos_staff
    Ссылка на набор: t.me/addemoji/<короткое имя>

Статичный набор — то же самое, но тип «Статичные эмодзи» и файлы из папки png.
"""


def main():
    if not os.path.isdir(os.path.join(DIST, 'tgs')):
        print('run build.py first')
        return 1
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('KRONOS_STAFF_emoji/КАК_ЗАГРУЗИТЬ.txt', HOWTO)
        for sub in ('tgs', 'png', 'png512'):
            folder = os.path.join(DIST, sub)
            for fn in sorted(os.listdir(folder)):
                z.write(os.path.join(folder, fn), 'KRONOS_STAFF_emoji/%s/%s' % (sub, fn))
        for fn in ('emoji_list.csv', 'emoji_list.md'):
            p = os.path.join(DIST, fn)
            if os.path.exists(p):
                z.write(p, 'KRONOS_STAFF_emoji/' + fn)
        for fn in ('all_emoji.jpg', 'all_emoji.mp4'):
            p = os.path.join(DIST, 'preview', fn)
            if os.path.exists(p):
                z.write(p, 'KRONOS_STAFF_emoji/preview/' + fn)
    print('saved %s (%.1f MB)' % (OUT, os.path.getsize(OUT) / 1e6))
    return 0


if __name__ == '__main__':
    sys.exit(main())
