from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.templatetags.static import static
from django import forms
import sys
import os

# Create your views here.
class InputSemester(forms.Form):
    user_semester = forms.CharField(label='Input')
    
class ClassSemester(forms.Form):
    subject_name = forms.CharField(label='Input')
    subject_code = forms.CharField(label='Input')

class Subject:
    def __init__(self, attribute_array):
        self.name = attribute_array[0]
        self.subject_code = attribute_array[1]
        self.semester = attribute_array[2]
        self.sks = int (attribute_array[3])
        self.day = attribute_array[4]
        self.start_hour = attribute_array[5]
        self.end_hour = attribute_array[6]
        self.class_name = attribute_array[7]
        self.lecturer = attribute_array[8]
        self.status = attribute_array[9]

class Backtracking:
    def __init__(self, input_file, user_semester):
        self.subject_arr = []
        self.schedule_set = set()
        self.intervals = []
        self.path = []
        self.results = []
        self.sks_total = 0

        # User inputs
        self.user_semester = user_semester

        for line in input_file:
            self.attribute_array = line.split()
            if '-' in self.attribute_array:
                continue
            self.subject = Subject(self.attribute_array)

            # Filter semester
            if int(self.user_semester) == int(self.subject.semester):
                self.subject_arr.append(self.subject)
    
    def find_combinations(self):
        self.backtrack()
        self.printResults()
        
    def add_subject(self, subject_name, subject_code):
        a = None

        for temp in self.subject_arr:
            if temp.name == subject_name and temp.subject_code == subject_code:
                a = temp

        if a is not None:
            self.path.append(a)
            self.intervals.append((a.day, a.start_hour, a.end_hour))
            self.sks_total += a.sks

    def backtrack(self):
        if self.sks_total > 18:
            if self.path:
                self.path = self.path
                self.path_res = tuple(self.path.copy())
                self.results.append(self.path_res)
            return

        for a in self.subject_arr:
            self.flag = 0

            # Memeriksa apakah mata kuliah sudah diambil atau tidak
            for subj in self.path:
                if a.name == subj.name:
                    self.flag = 1
                    break

            # Memeriksa apakah waktu sudah terpakai atau tidak
            for times in self.intervals:
                if (a.day == times[0]) and (int(a.start_hour) < int(times[2])) and (int(a.end_hour) > int(times[1])):
                    self.flag = 1
                    break

            # Memeriksa apakah kombinasinya sudah ada atau tidak
            self.temp = self.path.copy()
            self.temp.append(a)
            self.temp.sort(key= lambda x: x.name)
            self.temp = tuple(self.temp)
            if self.temp in self.schedule_set:
                self.flag = 1

            if self.flag == 1:
                continue

            self.path.append(a)
            self.intervals.append((a.day, a.start_hour, a.end_hour))
            self.sks_total += a.sks
            self.schedule_set.add(self.temp)

            self.backtrack()

            self.path.pop()
            self.intervals.pop()
            self.sks_total -= a.sks

    def printResults(self):
        for a in self.results:
            for subj in a:
                print(subj.name, subj.subject_code, subj.day, subj.start_hour, subj.end_hour)
            print("------------------------")
        print("There are", len(self.results), "combinations")

def mainpage(request):
    template = loader.get_template('index.html')
    context = {"available_subject": None, "preferred_subject": None, "isCalculating": False}
    if request.method == 'POST':
        form = InputSemester(request.POST)
        if form.is_valid():
            module_dir = os.path.dirname(__file__)
            file_path = os.path.join(module_dir, 'static/jadwal22-23.txt')
            input_file = open(file_path, 'r')
            if context["available_subject"] is None:
                user_semester = form.cleaned_data['user_semester']
                bt = Backtracking(input_file, user_semester)
                available_subject = set()
                
                for a in bt.subject_arr:
                    available_subject.add(a.name)
                context.update({"available_subject": available_subject})
                
                return HttpResponse(template.render(context, request))
            
            while not context["isCalculating"]:
                subject_name = form.cleaned_data['subject_name']
                subject_code = form.cleaned_data['subject_code']
                bt.add_subject(subject_name, subject_code)
                context.update({"preferred_subject": path})
                return HttpResponse(template.render(context, request))

            return HttpResponse(template.render(context, request))
    # else:
    #     form = MyForm()


    # print("\nAvailable subject: ")



    # while (input("\nAdd class preference? (y/n)") == "y"):
    #     subject_name = input("Enter subject name : ")
    #     subject_code = input("Enter subject code : ")
    #     bt.add_subject(subject_name, subject_code)
    

    # bt.find_combinations()


    return HttpResponse(template.render(context, request))