import random

from account.models import FreelancerProfile


def get_smaller_active_work(list):
  smallest_value = list[0]
  for value in list:
    if value < smallest_value:
      smallest_value = value
  return smallest_value

def get_freelancer_using_query(profiles):
    print(profiles)
    random_profile = get_smaller_active_work(list(profiles))
    freelancer = FreelancerProfile.objects.filter(active_work=random_profile)
    return freelancer[0]


def auto_detect_freelancer(query):
    total_query = 3
    profiles = query.values_list('active_work', flat=True)
    if any(value < total_query for value in list(profiles)):
      freelancer = get_freelancer_using_query(profiles)
      if int(freelancer.active_work) >= total_query:
        freelancer = auto_detect_freelancer(query)
        return freelancer
      return freelancer
    return None
