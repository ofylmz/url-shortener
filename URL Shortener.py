import sqlite3
import hashlib
import requests
import random
import webbrowser
import pyperclip

conn = sqlite3.connect('url_database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS url_mapping(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        shortened_url TEXT NOT NULL)
    ''')


SHORT_DOMAIN = 'kisalt.io/'


def generate_hash(original_url):
    encoded_url = original_url.encode()
    hash_object = hashlib.sha256(encoded_url)
    hashed_url = hash_object.hexdigest()
    return hashed_url[:8]


def shorten_url(original_url, cursor, conn):
    shortened_url = SHORT_DOMAIN + generate_hash(original_url)

    while True:
        cursor.execute('SELECT id FROM url_mapping WHERE shortened_url = ?', (shortened_url,))
        existing_record = cursor.fetchone()

        if existing_record:
            original_url += str(random.randint(0, 9))
            shortened_url = SHORT_DOMAIN + generate_hash(original_url)
        else:
            cursor.execute('INSERT INTO url_mapping (original_url, shortened_url) VALUES (?, ?)',
                           (original_url, shortened_url))
            conn.commit()
            break

    return shortened_url


def retrieve_url(short_url):
    cursor.execute('SELECT original_url FROM url_mapping WHERE shortened_url = ?', (short_url,))
    result = cursor.fetchone()

    if result:
        original_url = result[0]
        return original_url
    else:
        return None


def redirect(short_url):
    original_url = retrieve_url(short_url)

    if original_url is not None:
        response = requests.get(original_url)

        if response.status_code == 200:
            try:
                webbrowser.open(original_url)
            except webbrowser.Error as err:
                print(f'Error: {err}')
        elif response.status_code == 404:
            print('404 Not Found')
        else:
            print(f'Failed, status code: {response.status_code}')

    else:
        print('URL not found in the database')
        
while True:
    print('Welcome to the nim URL shortening service')
    print('Options:')
    print(' - Shorten URL [s]')
    print(' - Access Website [a]')
    print(' - Retrieve Original URL [r]')
    print(' - Exit [e]')
    
    choice = input()
        
    if choice.lower() == 's':
        original_url = input('Enter the URL to be shortened: ')
        shortened_url = shorten_url(original_url, cursor, conn)
        pyperclip.copy(shortened_url)    
        print(f'Shortened URL: {shortened_url}')
        print('Copied to clipboard')
    
    elif choice.lower() == 'a':
        short_url = input('Enter the shortened URL: ')
        redirect(short_url)
    
    elif choice.lower() == 'r':
        short_url = input('Enter the shortened URL: ')
        original_url = retrieve_url(short_url)
        if original_url is not None:
            pyperclip.copy(original_url)
            print(f'Original URL: {original_url}')
            print('Copied to clipboard')
        else:
            print('Failed to retrieve the original URL')
            
    elif choice.lower() == 'e':
        print('Thanks for using the kisalt URL shortening service')
        break
    
    else:
        print('Please pick a valid option')