import json

from django.contrib.auth.decorators import user_passes_test
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from gui.models.history import History


@user_passes_test(lambda u: u.is_superuser)
def history(request):
    if not request.is_ajax():
        return render(request, 'history.html')

    order_dir = {
        'asc': "-",
        'desc': ""
    }

    draw = request.GET.get('draw')
    start = request.GET.get("start")
    length = request.GET.get('length', 10)
    columns = json.loads(request.GET['columns'])
    order_0_dir = request.GET.get('order[0][dir]')
    order_0_col = request.GET.get('order[0][column]')

    order = f"{order_dir[order_0_dir]}{columns[int(order_0_col)]}"

    nb_data = History.objects.all().count()
    data = [model_to_dict(f) for f in History.objects.all().order_by(order)[int(start): int(length) + int(start)]]

    return JsonResponse({
        'draw': draw,
        'recordsTotal': nb_data,
        'recordsFiltered': nb_data,
        'data': data
    })
