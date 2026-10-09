#!/bin/sh
# Вырезает предмет с бумаги: предмет непрозрачный, бумага вокруг прозрачная.
# usage: cutout.sh in.png out.png '#paper' islands [x,y ...]
#   '#paper'  — цвет бумаги ассета (медиана по углам);
#   islands   — отдельные куски предмета меньше этой площади (px) считаются соринками-волокнами:
#               материалы 20000, эмблемы с брызгами и листьями 400;
#   x,y ...   — точки внутри замкнутых участков бумаги, которые тоже должны стать прозрачными
#               (кольцо связки ключей, ручка подсвечника, просвет между цепями вывески).
# Замкнутые участки бумаги не меньше N px сделать прозрачными сами: AUTOHOLES=N (листы иконок;
# после этого смотреть результат на цветном фоне — светлую заливку можно принять за бумагу).
# Без обрезки по содержимому: NOTRIM=1 (кадры анимации режутся потом одним общим прямоугольником).
# Светлые заливки внутри предмета (воск, пергамент, светлый камень) не трогаются: прозрачной
# становится только бумага, связанная с краем картинки, и участки с указанными точками.
# Все маски — одноканальные серые без альфы: иначе ImageMagick 7 берёт для CopyOpacity не тот канал.
set -e
in=$1; out=$2; paper=$3; islands=$4; shift 4
t=$(mktemp -d)
gray="-alpha off -colorspace Gray -type Grayscale"
# бумага — белым: всё, что почти совпадает с цветом бумаги
magick "$in" -strip -alpha off \( +clone -fill "$paper" -colorize 100 \) -compose difference -composite \
  -channel RGB -separate -evaluate-sequence max -blur 0x2 -threshold 8% -morphology Close Disk:5 \
  -negate $gray "$t/paper.png"
# предмет = всё, кроме бумаги, связанной с краем
magick "$t/paper.png" -fill gray50 -draw 'color 0,0 floodfill' -fill white +opaque gray50 -fill black -opaque gray50 \
  $gray "$t/obj0.png"
# соринки меньше islands убрать
magick "$t/obj0.png" -define connected-components:area-threshold="$islands" \
  -define connected-components:mean-color=true -connected-components 8 $gray "$t/obj.png"
# дыры — участки бумаги с указанными точками, из предмета вычесть
fills=""
for p in "$@"; do fills="$fills -draw 'color $p floodfill'"; done
if [ -n "$fills" ]; then
  eval magick "$t/paper.png" -fill gray50 $fills -fill black +opaque gray50 -fill white -opaque gray50 $gray "$t/holes.png"
  magick "$t/obj.png" "$t/holes.png" -compose minus_src -composite $gray "$t/obj.png"
fi
if [ -n "$AUTOHOLES" ]; then
  magick "$t/paper.png" -fill gray50 -draw 'color 0,0 floodfill' -fill black +opaque gray50 -fill white -opaque gray50 $gray "$t/outside.png"
  magick "$t/paper.png" "$t/outside.png" -compose minus_src -composite $gray \
    -define connected-components:area-threshold="$AUTOHOLES" -define connected-components:mean-color=true \
    -connected-components 8 $gray "$t/auto.png"
  magick "$t/obj.png" "$t/auto.png" -compose minus_src -composite $gray "$t/obj.png"
fi
magick "$t/obj.png" -morphology Erode Disk:2 -blur 0x1.2 $gray "$t/alpha.png"
if [ -n "$NOTRIM" ]; then trim=""; else trim="-trim +repage"; fi
magick "$in" -strip -alpha off "$t/alpha.png" -compose CopyOpacity -composite $trim "$out"
rm -r "$t"
