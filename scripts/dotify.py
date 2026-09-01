from PIL import Image,ImageOps
import argparse
p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('-o','--output',default='assets/portrait');p.add_argument('--cols',type=int,default=88);p.add_argument('--color',action='store_true');a=p.parse_args()
im=Image.open(a.image).convert('RGBA'); rows=max(1,int(a.cols*(im.height/im.width)*.55)); im=ImageOps.fit(im,(a.cols,rows),Image.Resampling.LANCZOS); g=ImageOps.grayscale(im); path=a.output if a.output.endswith('.svg') else a.output+'.svg'
with open(path,'w') as f:
 f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a.cols*8} {rows*8}">\n')
 for y in range(rows):
  for x in range(a.cols):
   v=g.getpixel((x,y))/255;r=.15+.72*(1-v);c=im.getpixel((x,y))[:3];fill=f'rgb{c}' if a.color else '#39D353';f.write(f'<circle cx="{x*8+4}" cy="{y*8+4}" r="{r*3:.2f}" fill="{fill}"/>')
 f.write('</svg>')
print(path)
