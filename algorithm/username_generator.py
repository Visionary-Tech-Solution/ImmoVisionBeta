def auto_user(set_email):
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

    # Generate the unique username based on the email provider
    if provider in usernames:
        username = set_email.split("@")[0] + usernames[provider]
    else:
        username = set_email.split("@")[0]

    return username