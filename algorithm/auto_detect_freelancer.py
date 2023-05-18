import random

from account.models import FreelancerProfile


def get_smaller_active_work(list):
  smallest_value = list[0]
  print(smallest_value)
  print(input("--"))
  for value in list:
    if value < smallest_value:
      smallest_value = value
  return smallest_value

def get_freelancer_using_query(query):
    profiles = query.values_list('active_work', flat=True)
    random_profile = get_smaller_active_work(list(profiles))
    freelancer = FreelancerProfile.objects.get(profile__username=random_profile)
    return freelancer


def auto_detect_freelancer(query):
    freelancer = get_freelancer_using_query(query)
    print("With Condition",freelancer)
    if int(freelancer.active_work) >= 10:
        print("On Con")
        freelancer = auto_detect_freelancer(query)
        return freelancer
    print("Without Condition", freelancer)
    return freelancer