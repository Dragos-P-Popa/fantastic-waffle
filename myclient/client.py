import requests
import sys
import dill as pickle
import json
from datetime import datetime

session = requests.Session()
url = str()

try:
    with open('session_data.pkl', 'rb') as inp:
        pickleData = pickle.load(inp)
        url = pickleData['url']
        session = pickleData['session']
except FileNotFoundError:
    print("No session data found")
    pass # not logged in

def login():
    try:
        url = sys.argv[2]
    except IndexError:
        print("No URL provided")
        return

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    data = {
        'username': username,
        'password': password
    }

    csrftoken = session.cookies['csrftoken']

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrftoken
    }

    response = session.post(url + "/api/login", data=data, headers=headers)

    if response.status_code == 200:
        print("Logged into %s" % url)

        # save session data
        with open('session_data.pkl', 'wb') as outp:
            pickle.dump({'session': session, 'url': url}, outp, pickle.HIGHEST_PROTOCOL)
    else:
        print("Failed to log into %s" % url)
        print(response.text)

def logout():
    csrftoken = session.cookies['csrftoken']

    headers = {
        'X-CSRFToken': csrftoken
    }

    response = session.post(url + "/api/logout", headers=headers)

    if response.status_code == 200:
        print("Logged out of %s" % url)
        with open('session_data.pkl', 'wb') as outp:
            pickle.dump({'session': '', 'url': ''}, outp, pickle.HIGHEST_PROTOCOL)
    else:
        print(response.text)
        print("Failed to logout of %s" % url)

def news():
    id = "*"
    cat = "*"
    reg = "*"
    date = "*"
    global url

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if "=" in arg:
            key, value = arg.split("=", 1)  # Split on the first "="
            value = value.strip('"')  # Remove quotes from value

            if key == "-id":
                id = value
            elif key == "-cat":
                cat = value
            elif key == "-reg":
                reg = value
            elif key == "-date":
                date = value

    # Validate date format if it's not "*"
    if date != "*":
        try:
            datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            print("Incorrect date format, should be DD/MM/YYYY")
            return

    #url based on given news agency id
    agencies = listAgencies(verbose=False)

    if id == "*":
        if len(agencies) >= 20:
            agencies = agencies[:20]

        for agency in agencies:
            article = session.get(agency['url'] + "/api/stories", params={
                "story_cat": cat,
                "story_region": reg,
                "story_date": date
            })

            if article.status_code == 200:
                print(json.dumps(article.json(), indent=4))
            else:
                print("Failed to get articles from %s" % article.url)
    else:
        url = ''
        for agency in agencies:
            if agency['agency_code'] == id:
                url = agency['url']
                break

        if url == '':
            print("Invalid news agency id")
            return

        articles = session.get(url + "/api/stories", params={
            "story_cat": cat,
            "story_region": reg,
            "story_date": date
        })

        if articles.status_code == 200:
            print(articles.json())
        elif articles.status_code == 404:
            print(articles.text)
        else:
            print("Failed to get articles")
            

def post():
    headline = input("Enter the story's headline: ")
    category = input("Enter the story's category: ")
    region = input("Enter the story's region: ")
    details = input("Enter the story's details: ")

    csrftoken = session.cookies['csrftoken']

    headers = {
        'X-CSRFToken': csrftoken
    }

    newStory = session.post(url + "api/stories", headers=headers, json={
        "headline": headline,
        "category": category,
        "region": region,
        "details": details
    })

    if newStory.status_code == 201:
        print("Story posted")
    else:
        print("Failed to post story")
        print(newStory.text)

def listAgencies(verbose=True):
    response = session.get("http://newssites.pythonanywhere.com/api/directory/")

    if verbose == True:
        for agency in response.json():
            print(agency['agency_code'], agency['agency_name'], agency['url'])
              
    return response.json()

def delete():
    csrftoken = session.cookies['csrftoken']

    headers = {
        'X-CSRFToken': csrftoken
    }

    response = session.delete(url + "api/stories/" + sys.argv[2], headers=headers)

    if response.status_code == 200:
        print("Story deleted")
    else:
        print("Failed to delete story")
        print(response.text)

if sys.argv[1] == "login":
    login()
elif sys.argv[1] == "logout":
    logout()
elif sys.argv[1] == "news":
    news()
elif sys.argv[1] == "list":
    listAgencies()
elif sys.argv[1] == "post":
    post()
elif sys.argv[1] == "delete":
    delete()