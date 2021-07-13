from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render

def get_group_waitnumber(queue):
    qkind = [x[0] for x in queue if x[1] != 0]
#    qkind = [x[0] for x in queue]
    wait1 = qkind.count(1)
    wait2 = qkind.count(2)
    wait3 = qkind.count(3)
    return wait1, wait2, wait3

def find_lastindex(kindnumber, queue):
    qkind = [x[0] if x[1] > 0 else 0 for x in queue]
    string_list = [str(n) for n in qkind] 
    string = "".join(string_list)
    index = string.rfind(str(kindnumber))
    return index

def find_firstindex(kindnumber, queue):
    qkind = [x[0] if x[1] > 0 else 0 for x in queue]
    string_list = [str(n) for n in qkind] 
    string = "".join(string_list)
    index = string.find(str(kindnumber))
    return index


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html')


class NextView(View):
    def get(self, request, *args, **kwargs):
        processed = ProcessingView.processed
        queue = QueueView.queue
        nextnumber = processed[-1] if len(processed) else 0

        context = {"nextnumber": nextnumber, "queue": queue}
        return render(request, 'tickets/next.html', context=context)


class ProcessingView(View):
    processed = []

    def get(self, request, *args, **kwargs):
        queue = QueueView.queue
        wait1, wait2, wait3 = get_group_waitnumber(queue)
        context = {"wait1": wait1, "wait2": wait2, "wait3": wait3, "queue": queue}
        return render(request, 'tickets/processing.html', context=context)

    def post(self, request, *args, **kwargs):
        queue = QueueView.queue
        wait1, wait2, wait3 = get_group_waitnumber(queue)
        nextnumber = 0
        if wait1:
            kindnumber = 1
        elif wait2:
            kindnumber = 2
        elif wait3:
            kindnumber = 3
        else:
            kindnumber = 0

        if kindnumber:
            waittime_list = QueueView.waittime_list
            waittime = waittime_list[-1]
            if waittime:
                index = find_firstindex(kindnumber, queue)   
                nextnumber = queue[index][1]
                queue[index][1] = 0
            self.processed.append(nextnumber)

        context = {"nextnumber": nextnumber, "queue": queue}
        return render(request, 'tickets/next.html', context=context)


class QueueView(View):
    queue = []
    waittime_list = []
    
    def get(self, request, *args, **kwargs):
        kind = kwargs["kind"]           
        if kind == "change_oil":
            kindnumber = 1
        elif kind == "inflate_tires":
            kindnumber = 2
        elif kind == "diagnostic":
            kindnumber = 3

        waittime = 0
        waitnumber = 0
        if len(self.queue) == 0:
            pass
        elif len(self.queue) == 1:
            pass
        elif len(self.queue) == 2:
            if kindnumber >= self.queue[-1][0]:
                waittime = self.calc_waittime(self.queue)
            elif kindnumber >= self.queue[-2][0]:
                waittime = self.calc_waittime(self.queue[:-1])
            else:
                pass
        else:
            index = find_lastindex(kindnumber, self.queue)
            if index == -1 or index + 1 == len(self.queue):
                waittime = self.calc_waittime(self.queue)
            else:
                waittime = self.calc_waittime(self.queue[:index + 1])

        self.waittime_list.append(waittime)
        waitnumber = len(self.queue) + 1
        self.queue.append([kindnumber, waitnumber])
        self.queue.sort()
        context = {"number": waitnumber, "waittime": waittime, "queue": self.queue}
        return render(request, 'tickets/queue.html', context=context)

    def calc_waittime(self, queue):
        qkind = [x[0] for x in queue if x[1] != 0]
        waittime = 0
        for item in qkind:
            if item == 1: 
                waittime += 2
            elif item == 2:
                waittime += 5
            elif item == 3:
                waittime += 30
        return waittime