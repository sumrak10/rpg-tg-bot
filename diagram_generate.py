from PIL import Image, ImageDraw, ImageFont
from sys import platform


if platform == 'win32':
    oslink = 'rpg-tg-bot/'
elif platform == 'linux':
    oslink = './'
else:
    print("THIS PLATFORM DON'T SUPPORTED (diagram_generate.py)")

def generate_diagram_picture(nums, picturename):
    def mapNum(x,fromLow,fromHigh,toLow,toHigh):
        return (x - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow
    w,h = 1400,700
    fontsize = round(h / 30)
    img = Image.new('RGB', (w,h), 'white')
    try:
        font = ImageFont.truetype("arial.ttf",size=fontsize)
    except:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    nmin = min(nums)//10*10+round(min(nums)%10/10)*10
    nmax = max(nums)//10*10+round(max(nums)%10/10)*10
    workWstart = fontsize*len(str(nmax))
    workHstart = fontsize
    workWend = w-fontsize
    workHend = h-fontsize*2
    
    if nmax != nmin:
        step = round((nmax - nmin) / 10)
    else:
        step = round(nmin / 10)
        nmin -= (nmin)
        nmax += (nmax)
        
    pmin = h
    pmax = 0
    for i in range(nmin,nmax+1,step):
        mapi = mapNum(i,nmin-step,nmax+step,workHstart,workHend)
        if mapi < pmin:
            pmin = mapi
        elif mapi > pmax:
            pmax = mapi
        draw.line((workWstart,mapi,workWend,mapi),fill='green',width=1)
        if step < 10:
            strn = i / 10 + 1
        else:
            strn = round(i / 10) + 1
        draw.text((round(fontsize*0.5),workHend - mapi+round(fontsize*0.5)),str(strn),font=font,fill='black')
        
    k = 0
    last_pw = 0
    last_ph = 0
    for i in nums:
        pw = mapNum(k,0,len(nums)-1,workWstart,workWend)
        ph = mapNum(i,nmin,nmax,pmax,pmin)
        # if k % 7 == 0:
        #     draw.line((pw,workHstart,pw,workHend),fill='red',width=1)
        if last_ph != 0:
            draw.line((pw,ph,last_pw,last_ph),fill='black',width=2)
        draw.ellipse((pw-3,(ph-3),pw+3,(ph+3)),fill='black', outline='black')
        last_pw = pw
        last_ph = ph
        k+=1

    img.save(oslink+'media/img/diagrams/'+picturename+'.png')

# generate_diagram_picture([10,10,10,10,10,10],'1')