#Roast Dinner Organiser

#Imports
from tkinter import *
import yaml
from yaml import CLoader as Loader
import datetime
from PIL import ImageColor
import pygame, time

#Gets total duration of a certain constituent
def getDuration(data,constituent):
    duration=0
    for step in data[constituent]["recipe"].values():
        duration+=step[1]
    return duration

#Gets the constituent that takes the longest to prepare
def getCriticalActivity(data):
    record=0
    criticalActivity=""
    for constituent in data:
        t=getDuration(data,constituent)
        if t>record:
            criticalActivity=constituent
            record=t
    return criticalActivity,record

#Darkens color
def darken(color):
    rgb = ImageColor.getcolor(color,"RGB")
    newrgb=[int(i/1.2) for i in rgb]
    return ("#{:02X}{:02X}{:02X}".format(newrgb[0],newrgb[1],newrgb[2]))

#Gets coordinates for corner of box
def getBoxCoords(height,width,x,y):
    if height-y<180:
        if width-x<320:
            return (x-300,y-150,x,y)
        return (x,y-150,x+300,y)
    else:
        if width-x<320:
            return (x-300,y,x,y+150)
        return (x,y,x+300,y+150)
    
#Displays detailed instructions when event clicked
def clicked(event,canvas,root,boxRef):
    text=boxRef[canvas.find_closest(event.x,event.y)[0]]
    coords=getBoxCoords(canvas.winfo_height(),canvas.winfo_width(),
                       event.x,event.y)
    r=canvas.create_rectangle(coords,fill="#bbbbff")
    t=canvas.create_text(coords[0]+10,coords[1]+10,anchor=NW,
                         text=text,font="Segoe 12")
    root.after(8000,lambda:canvas.delete(r,t))
    
        
#Draws the Gantt chart
def drawGantt(data,canvas):
    y=0
    maxlength=getCriticalActivity(data)[1]
    boxRef={}
    for constituent in data:
        length=getDuration(data,constituent)
        canvas.create_text(20,y+30,anchor=W,text=constituent,
                           font="Segoe 16")
        x=250
        for step in data[constituent]["recipe"]:
            width=data[constituent]["recipe"][step][1]
            i=canvas.create_rectangle(((maxlength-length)*6+x,y+5),
                                    ((maxlength-length+width)*6+x,y+55),
                                    fill=data[constituent]["color"],
                                    activefill=darken(data[constituent]["color"]),
                                    tags="clickable")
            boxRef[i]=data[constituent]["recipe"][step][0]
            canvas.create_text((maxlength-length)*6+x+width*3,y+30,
                               text=step,font="Segoe 10")
            x+=width*6
        y+=60
    return boxRef

#Updates the Gantt chart
def update(line,canvas,root,h,alerts,plan,ends):
    x=250+((datetime.datetime.now()-ends[0]).total_seconds())/10
    canvas.delete(line)
    line=canvas.create_line(x,0,x,h,width=3,fill="#880000")
    for alert in alerts:
        alert.set("")
    a=0
    for item in plan:
        if datetime.datetime.now()>item[0] and datetime.datetime.now()<item[0]+datetime.timedelta(minutes=1) and a<3:
            alerts[a].set(item[1])
            a+=1
            if item[2]:
                pygame.mixer.music.play()
                root.update()
                time.sleep(2)
                item[2]=False
    root.after(5000,lambda:update(line,canvas,root,h,alerts,plan,ends))

#Sorting key for timeplan
def sortKey(item):
    return item[0].timestamp()

#Generates a timeplan that will be used by the update method
def timeplan(data,endtime):
    totallength=datetime.timedelta(minutes=getCriticalActivity(data)[1])
    print(totallength)
    plan=[]
    for constituent in data:
        t=0
        for step in reversed(data[constituent]["recipe"]):
            t+=data[constituent]["recipe"][step][1]
            plan.append([endtime-datetime.timedelta(minutes=t),step,True])
    plan.sort(key=sortKey)
    ends=(endtime-totallength,totallength)
    return plan,ends
    
################################################################################            

#Get endtime and chicken weight
#endtime = datetime.datetime.combine(datetime.date.today(),
#                           datetime.time(hour=19,minute=0))
endtime=datetime.datetime.now()+datetime.timedelta(minutes=10,seconds=10)
weight = 1.65

#Open database
stream = open("data.yaml","r")
data = yaml.load(stream,Loader=Loader)
stream.close()

#Updates roast chicken with calculated cooking time
data["Roast Chicken"]["recipe"]["Cook chicken"][1]=30+int(45*weight)

#Generates timeplan
plan,ends = timeplan(data,endtime)

#Creates GUI
root=Tk()
root.geometry("1250x660")
root.title("Roast Dinner Organiser")

#Creates Gantt Chart
canvas=Canvas(root,height=60*len(data))
canvas.pack(fill="both")#,expand=True)
boxRef=drawGantt(data,canvas)
canvas.tag_bind("clickable","<Button-1>",lambda x:clicked(x,canvas,root,boxRef))
#Creates Start Button
bottomframe=Frame(root)
bottomframe.pack(side=BOTTOM)
alerts=[]
startButton=Button(bottomframe,text="START",bg="#ff9999",activebackground="#99ff99",
                   font="Segoe 16",
                   command=lambda:update(1000,canvas,root,60*len(data),alerts,plan,ends),
                   relief=GROOVE)
startButton.pack(side=LEFT)

#Creates Alert Box
Label(bottomframe,text="ALERTS:",bg="#ffff77",font="Segoe 16",padx=10).pack(side=LEFT)
for n in range(0,3):
    a=StringVar(root)
    alerts.append(a)
    Label(bottomframe,textvariable=a,font="Segoe 16",padx=10,wraplength=300).pack(side=LEFT)

#Sorts sounds
pygame.init()
pygame.mixer.music.load("horn.mp3")

#Starts main loop
root.mainloop()
