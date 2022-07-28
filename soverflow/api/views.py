from django.shortcuts import render
import requests
import json
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.cache import cache

def get_stackexchange_data(param):
	STACKOVERFLOW_URL = 'https://api.stackexchange.com/2.3/{}'
	try:
		response = requests.get(STACKOVERFLOW_URL.format('questions'), params=param)
		json_response = response.json()
		return response.json()
	except Exception as e:
		print(f'Exception occured - {STACKOVERFLOW_URL}: {e}')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class QuestionsView(TemplateView):
	template_name = "index.html"
	def get_context_data(self, **kwargs):
		curr_ip = get_client_ip(self.request)
		context = super(QuestionsView, self).get_context_data(**kwargs)
		if cache.get(f"search_limit_day{curr_ip}"):
			total_search_day = cache.get(f"search_limit_day{curr_ip}")
			if total_search_day > 100:
				context['cdata'] = {}
				return context
			else:
				if cache.get(f"search_limit_min{curr_ip}"):
					total_search = cache.get(f"search_limit_min{curr_ip}")
					if total_search > 5:
						context['cdata'] = {}
						return context
					else:
						cache.set(f"search_limit_min{curr_ip}", total_search + 1, 5*60)
				else:
					cache.set(f"search_limit_min{curr_ip}", 1, 5*60)
		else:
			cache.set(f"search_limit_day{curr_ip}", 1, 86400)
        
		page = self.request.GET.get("page")
		pg_page = self.request.GET.get("pg_page")
		pagesize = self.request.GET.get("pagesize")
		fromdate = self.request.GET.get("fromdate")
		todate = self.request.GET.get("todate")
		order = self.request.GET.get("order")
		sort = self.request.GET.get("sort")
		maxm = self.request.GET.get("max")
		minm = self.request.GET.get("min")
		tagged = self.request.GET.get("tagged")

		param = {
			"page": page,
			"pagesize": pagesize,
			"order": order,
			"sort" : sort,
			"site" : "stackoverflow"
		}
		resp_data = get_stackexchange_data(param)
		resp_data = resp_data.get("items")
		p = Paginator(resp_data, 10)
		context['cdata'] = p.get_page(pg_page)
		return context