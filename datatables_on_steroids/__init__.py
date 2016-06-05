import json
from django.db.models import Q
from django.http import HttpResponse


class Datatable:
    def __init__(self, request=None, model=None, fields=None, search_fields=None):
        self.fields = fields
        self.real_fields = []
        self.method_field = []
        self.model = self.model  # FIXME

    def get_response(self, request):
        start = request.GET['start']

        end = request.GET['length']
        draw = request.GET['draw']

        search = request.GET.get('search[value]', '')
        search = str(search)

        # Get only model fields.
        model_fields = [field.name for field in Client._meta.fields]

        for field in self.fields:
            if field in model_fields:
                self.real_fields.append(field)

            elif hasattr(self.model, field):
                self.method_field.append(field)

        print(self.real_fields)

        queries = [Q(**{f + '__icontains': search}) for f in self.real_fields]
        qs = reduce(lambda x, y: x | y, queries)
        order = dict(enumerate(self.real_fields))
        dirs = {'asc': '', 'desc': '-'}
        # ordering = dirs.get([request.GET['order[0][dir]']] + order[int(request.GET['order[0][column]'])])
        # ordering = dirs.get([request.GET['order[0][dir]']])
        ordering = '?'  # FIXME need to fix ordering , now set to random
        objects = self.model.objects.order_by(ordering)
        total_records = self.model.objects.count()
        ob = objects.filter(qs)
        objects = ob[start:(int(start) + int(end))]
        filtered = ob.count()

        data = []
        for object_data in objects:
            inst_dat = []
            for real_field in self.real_fields:
                inst_dat.append(str(getattr(object_data, real_field)))

            for method_field in self.method_field:
                inst_dat.append(str(getattr(object_data, method_field)()))
            data.append(inst_dat)

        return HttpResponse(json.dumps({
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": filtered,
            "data": data,
        }), content_type='application/json')
