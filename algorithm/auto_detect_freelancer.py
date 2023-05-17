import random

from account.models import FreelancerProfile


def get_freelancer_using_query(query):
    profiles = query.values_list('profile__username', flat=True)
    random_profile = random.choice(list(profiles))
    print("Inside")
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