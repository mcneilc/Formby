import datetime

from django import forms
from django.core.urlresolvers import reverse
from django.db.models.loading import cache
from django.db.models import Min, Count
from django.forms.models import ModelForm, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView

from models import Job, JobSchedule, Customer, Round


# TODO there must be an third party lib of HTML5 goodies for django
class DateInput(forms.TextInput):
    input_type = 'date'


class EmailInput(forms.TextInput):
    input_type = 'email'


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        
    email = forms.CharField(widget=EmailInput)


class JobScheduleForm(ModelForm):
    class Meta:
        model = JobSchedule
        exclude = ('customer',)

    start_date = forms.CharField(widget=DateInput)


def add_job_schedule(request):
    if request.method == 'POST':
        cust_form = CustomerForm(request.POST)
        sched_form = JobScheduleForm(request.POST)
        cv = cust_form.is_valid()
        sv = cust_form.is_valid()
        if cv and sv:
            c = cust_form.save()
            s = sched_form.save(commit=False)
            s.customer = c
            s.save()
            return HttpResponseRedirect(s.id)
    else:
        cust_form = CustomerForm()
        sched_form = JobScheduleForm()
    return render(
        request,
        'main/add_job.html',
        {
            'sched_form': sched_form,
            'cust_form': cust_form,
            'action': 'add',
            })


def edit_job_schedule(request, pk):
    schedule = get_object_or_404(JobSchedule, pk=pk)
    customer = schedule.customer
    if request.method == 'POST':
        cust_form = CustomerForm(request.POST, instance=customer)
        sched_form = JobScheduleForm(request.POST, instance=schedule)
        cv = cust_form.is_valid()
        sv = cust_form.is_valid()
        if cv and sv:
            c = cust_form.save()
            s = sched_form.save()
            return HttpResponseRedirect(c.id)
    else:
        cust_form = CustomerForm(instance=customer)
        sched_form = JobScheduleForm(instance=schedule)
    return render(
        request,
        'main/add_job.html',
        {
            'sched_form': sched_form,
            'cust_form': cust_form,
            'action': 'edit',
            })


class AnyListView(ListView):
    def get_queryset(self):
        model_name = self.args[0]
        model = cache.get_model('main', model_name)
        return model.objects.all()


class AnyDetailView(DetailView):
    def get_queryset(self):
        model_name = self.kwargs['model']
        model = cache.get_model('main', model_name)
        return model.objects.all()


class AnyCreateView(CreateView):
    def get_queryset(self):
        model_name = self.args[0]
        model = cache.get_model('main', model_name)
        return model.objects.all()

    def get_success_url(self):
        model_name = self.args[0]
        model = cache.get_model('main', model_name)
        return reverse("object_detail", args=(model_name, self.object.pk))


class ScheduleView(ListView):
    queryset = (Round.objects
                .filter(job_schedules__jobs__completed_on__isnull=True)
                .annotate(soonest=Min('job_schedules__jobs__date'),
                          count=Count('job_schedules__jobs__date'))
                .exclude(count=0)
                .order_by('soonest'))
    template_name = "main/schedule.html"

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        # TODO generalise this 'stack' GET param to something usefule
        for obj in self.object_list:
            get = self.request.GET.copy()
            if 'expand' in get:
                get.appendlist('expand', obj.pk)
            else:
                get.setlist('expand', [obj.pk])
            obj.expand_link = get.urlencode()
            get = self.request.GET.copy()
            if 'expand' in get:
                expanded = get.getlist('expand')
                if str(obj.pk) in expanded:
                    expanded.remove(str(obj.pk))
                    get.setlist('expand', expanded)
            obj.collapse_link = get.urlencode()

        context['expanded'] = [int(x) for x in self.request.GET.getlist('expand')]
        return context
    

todays_jobs = (Job.objects
                .filter(date=datetime.date.today())
                .filter(completed_on__isnull=True)
                .order_by('schedule__round'))

class WorksheetView(ListView):
    queryset = todays_jobs
    template_name= 'main/worksheet.html'


class JobForm(ModelForm):
    class Meta:
        model = Job
        exclude = ('paid_on', 'completed_on', 'date')

    completed = forms.BooleanField(required=False)
    paid = forms.BooleanField(required=False)

    def save(self, commit=True):
        job = super(JobForm, self).save(commit=False)
        completed = self.cleaned_data['completed']
        if completed:
            job.completed_on = datetime.date.today()
        if paid:
            job.paid_on = datetime.date.today()
        if commit:
            job.save()
        return job


def end_of_day(request):
    JobFormSet = modelformset_factory(Job, form=JobForm, extra=0)
    if request.method == "POST":
        formset = JobFormSet(request.POST, queryset=todays_jobs)
        if formset.is_valid():
            jobs = formset.save()
            return HttpResponseRedirect(reverse('view_schedule'))
    else:
        formset = JobFormSet(queryset=todays_jobs)
    return render(request, "main/end_of_day.html", {'jobs': formset})
