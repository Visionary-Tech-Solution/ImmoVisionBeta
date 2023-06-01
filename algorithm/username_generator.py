def auto_user(set_email):
    special_characters = "!@#$%^&*()_+{}[]|:;<>,.?/~"
    provider = set_email.split("@")[1]
    usernames = {
        "gmail.com": "",
        "yahoo.com": "2",
        "hotmail.com": "3",
        "aol.com": "4",
        "outlook.com": "5",
        "icloud.com": "6",
        "protonmail.com": "7",
        "zoho.com": "8",
        "mail.com": "9",
        "gmx.com": "10",
    }
    import random
    # Generate the unique username based on the email provider
    if provider in usernames:
        username = f"imo{random.choice(special_characters)}" + str(random.randint(11,99)) + set_email.split("@")[0] + usernames[provider]
        username += str(random.randint(11,99)) + username[-1] + username[1] + str(random.randint(11,99))
    else:
        username = f"imo{random.choice(special_characters)}" + set_email.split("@")[0]
        username += str(random.randint(11,99)) + username[-1] + username[1] + str(random.randint(11,99))
    return username