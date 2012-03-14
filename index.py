import random
import bottle
import sys
from bottle import route, get, post, run, request, abort, redirect, static_file, template
import json

### Pickling
pname = 'dinofacts.json'
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
    def __init__(self,this_num):
        self.resp = []
        self.this_num = this_num
        
    def add(self,numbers,msg):
        if isinstance(numbers,basestring):
            numbers = [numbers]
        numbers = [number.strip('+ ') for number in numbers]
        remaining = msg
        while remaining:
            part = remaining[:160]
            for number in numbers:
                self.resp.append("""<Sms to="+%(number)s">%(part)s</Sms>""" % locals())
            remaining = remaining[160:]
            print "Remaining: %s" % remaining
        
    def add_fact(self,numbers,fact):
        this_num = self.this_num
        fact = fact.strip('. ')
        self.add(numbers,"%(fact)s. Reply 'STOP' or 'MORE'." % locals())
        
    def __str__(self):
        return '\n'.join(["""<?xml version="1.0" encoding="UTF-8"?><Response>"""] + self.resp + ["""</Response>"""])


def redirect(url):
    return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Redirect>%(url)s</Redirect>
    </Response>""" % locals()


@get('/')
def dinofacts():
    tokens = request.query.Body.strip().split(' ')
    frm = request.query.From
    data = getdata()
    sender = SmsSender(this_num=request.query.To)
    cmd = tokens[0].lower()
    

    # Control
    if cmd == 'num':
        if not data.get('nums'):
            data['nums'] = []
        if len(tokens) == 1: 
            sender.add(frm,"Nums: %s" % ','.join(data['nums']))
        else: 
            try:
                num = str(int(tokens[1].replace('+','').replace('-','').replace('(','').replace(')','')))
            except ValueError:
                sender.add(frm,"%s is not a valid number" % tokens[1])
                return str(sender)
            if num in data['nums']:
                sender.add(frm,"Already exists! Nums: %s" % ','.join(data['nums']))
            else:
                data['nums'].append(num)
                sender.add(frm,"Added! Nums: %s" % ','.join(data['nums']))
                
        setdata(data)
        return str(sender)
            
            
    # Control    
    elif cmd == 'fact':
        if len(tokens) == 1:
            sender.add(frm,"There are %s facts in the fact db" % len(data['facts']))
        elif len(tokens) == 2:
            for fact in data['facts']:
                if tokens[1] in fact.lower():
                    sender.add_fact(frm, fact)
                    return str(sender)
            sender.add(frm,"Unable to find that fact.")
        else:
            if not data.get('facts'):
                data['facts'] = []
            data['facts'].append(' '.join(tokens[1:]))
            setdata(data)
            sender.add(frm,"Added dinofact. There are %s facts now." % len(data['facts']))
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
                if tokens[1] in fact.lower():
                    sender.add_fact(data['nums'], fact)
                    sender.add(frm, "Found that fact. Sent to %s numbers." % len(data['nums']))
                    return str(sender)
            sender.add(frm,"Unable to find fact. Did not send anything.") 
            return str(sender)
        else:
            sender.add_fact(data['nums'], ' '.join(tokens[1:]))
            sender.add(frm,"Your fact was sent to %s numbers" % len(data['nums']))
            return str(sender)
    
    # Prank
    elif cmd == 'chris' or cmd == 'wilcox':
        sender.add(frm,"Chris is the sexiest dinosaur alive. Mee-wow.")
        return str(sender)
    
    # Nothing
    elif cmd == 'more':
        sender.add_fact(frm, random.choice(data['facts']))
        return str(sender)
    
    
    # Nothing
    elif cmd == '':
        return str(sender)
    
    # Prank
    else:
        randino = random.choice(DINOSAURS).upper()
        _cmd = cmd.upper()
        sender.add(frm,"I'm sorry we don't know a fact about the dinosaur '%(_cmd)s'. Did you mean %(randino)s?" % locals())
        return str(sender)
        
            
        
def getapp():
    app = bottle.default_app()
    bottle.debug(True)
    return app

application = getapp()