import random
import bottle
import sys
from bottle import route, run, request, abort, redirect, static_file, template
import json

### Pickling
pname = 'data.pickle'
def getdata():
    try:
        data = json.load(open(pname,'r'))
    except IOError:
        data = {}
    return data

def setdata(data):
    json.dump(data,open(pname,'w'))
    

DINOSAURS = (
    "Tyrannosaurus",
    "Brachiosaurus",
    "Lesothosaurus",
    "Gregtrobrasaurus",
    "Nucciasaurus",
    "Graciliceratops",
    "Hadrosaurus",
    "Triceratops",
    "Stegasaurus",
    "Velociraptor",
    "Ultrasauros",
    "Pterospondylus",
    "Platyceratops",
)

class SmsSender(object):
    def __init__(self):
        self.resp = []
        
    def add(self,numbers,msg):
        if type(numbers) == str:
            numbers = [numbers]
        numbers = [number.strip('+ ') for number in numbers]
        remaining = msg
        while remaining:
            part = remaining[160:]
            for number in numbers:
                self.resp.append("""<Sms to="+%(number)s">%(part)s</Sms>""" % locals())
            remaining = remaining[:160]
        
    def __str__(self):
        return '\n'.join(["""<?xml version="1.0" encoding="UTF-8"?><Response>"""] + self.resp + ["""</Response>"""])


def redirect(url):
    return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Redirect>%(url)s</Redirect>
    </Response>""" % locals()



@get('/dinofacts')
def dinofacts():
    tokens = request.query.Body.strip().split(' '):
    frm = request.query.From
    data = getdata()
    sender = SmsSender()
    cmd = tokens[0].lower()
    
    # Control
    if cmd == 'num':
        if not data.get('nums'):
            data['nums'] = []
        try:
            data['nums'].append(tokens[1])
            setdata(data)
            sender.add(frm,"Added! Nums: %s" % data['nums'])
        except IndexError:
            sender.add(frm,"Nums: %s" % data['nums'])
        return str(sender)
            
    # Control    
    elif cmd == 'fact':
        if not data.get('facts'):
            data['facts'] = []
        data['facts'].append(' '.join(tokens[1:]))
        setdata(data)
        sender.add(frm,"Added dinofact. There are %s facts now." % len(data['facts'])
        return str(sender)
    
    # Control    
    elif cmd == 'send':
        if len(tokens) == 1:
            for num in data['nums']:
                sender.add(num,random.choice(data['facts']))
            sender.add(frm,"Random facts sent to %s numbers" % len(data['nums']))
            return str(sender)
        elif len(tokens) == 2:
            for fact in data['facts']:
                if tokens[1] in fact:
                    sender.add(data['nums'], fact)
                    sender.add(frm, "Found that fact. Sent to %s numbers." % len(data['nums']))
                    return str(sender)
            sender.add(frm,"Unable to find fact. Did not send anything.") 
            return str(sender)
        else:
            sender.add(data['nums'], ' '.join(tokens[1:]))
            sender.add(frm,"Your fact was sent to %s numbers" % len(data['nums']))
            return str(sender)
    
    # Prank
    elif cmd == 'chris' or cmd == 'wilcox':
        sender.add(frm,"Chris is the sexiest dinosaur alive. Mee-wow.")
        return str(sender)
    
    # Prank
    else:
        randino = random.choice(DINOSAUR).upper()
        sender.add(frm,"I'm sorry we don't know a fact about the dinosaur '%(cmd)s'. Did you mean %(randino)s?" % locals())
        return str(sender)
        
            
        
def getapp():
    app = bottle.default_app()
    bottle.debug(True)
    return app

application = getapp()