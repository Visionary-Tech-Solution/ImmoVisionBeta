import random

from account.models import FreelancerProfile
from order.models import MaxOrder


def get_smaller_active_work(list):
  smallest_value = list[0]
  for value in list:
    if value < smallest_value:
      smallest_value = value
  return smallest_value

def get_freelancer_using_query(profiles, query):
    random_profile = get_smaller_active_work(list(profiles))
    freelancer = query.filter(active_work=random_profile)
    return freelancer[0]


def auto_detect_freelancer(query):
    # print(query[0].profile)
    get_max_order = MaxOrder.objects.latest('id')
    max_order = int(get_max_order.max_order)
    profiles = query.values_list('active_work', flat=True)
    # print(profiles)
    if any(value < max_order for value in list(profiles)):
      freelancer = get_freelancer_using_query(profiles, query)
      if int(freelancer.active_work) >= max_order:
        freelancer = auto_detect_freelancer(query)
        return freelancer
      return freelancer
    return None
