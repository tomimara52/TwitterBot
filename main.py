import tweepy
import auth
from time import sleep
import threading


def find_user_screen_name(tw_api, id):
    user_name = tw_api.get_user(id=id)._json['screen_name']
    return user_name


def find_user_id(tw_api, id):
    try:
        user = tw_api.get_user(id=id)
        return user.id
    except:
        return False


def respond_with_info(tw_api, info, sender):
    if info == False:
        response = "I couldn't fin any tweet where the user said any of those words."
    elif isinstance(info, str):
        response = "I couldn't find the user '{}'".format(info)
    else:
        response = "The user you asked me to stalk said '{}' at {}\n" \
                   "Tweet link: https://twitter.com/{}/status/{}".format(info[0], info[1], info[2], info[3])
    tw_api.send_direct_message(recipient_id=sender, text=response)


def stalk(words, user_id, tw_api):
    print("Beginning to stalk...")
    for status in tweepy.Cursor(tw_api.user_timeline, user_id=user_id, include_rts=False).items():
        st_text = status.text.lower().replace("\n", ' ')
        for word in words:
            if (word+ ' ' in st_text) or (' '+word+' ' in st_text) or (' '+word in st_text):
                return status.text, status.created_at, find_user_screen_name(tw_api, user_id), status.id
    return False


def read_last_id(filename):
    f_read = open(filename, 'r')
    last_id = int(f_read.read().strip())
    f_read.close()
    return last_id


def write_last_id(filename, last_id):
    print("Writing new last_id...")
    f_write = open(filename, 'w')
    f_write.write(str(last_id))
    f_write.close()


def get_messages(tw_api):
    messages = tw_api.list_direct_messages()
    messages_info = []
    for message in reversed(messages):
        message_text = message._json["message_create"]['message_data']['text']
        message_id = message.id
        sender_id = message.message_create['sender_id']
        messages_info.append((int(message_id), message_text.lower(), sender_id))
    return messages_info


def process_message(tw_api, msg):
    if msg[1][:2] == '/!':
        user_name, words = msg[1][2:].split(',')
        user_id = find_user_id(tw_api, user_name)
        words = words.strip().split(" ")
        if user_id:
            info = stalk(list(map(str.lower, words)), user_id, tw_api)
        else:
            info = user_name
        respond_with_info(tw_api, info, msg[-1])


def manage_messages(tw_api, filename):
    messages = get_messages(tw_api)
    last_id = read_last_id(filename)
    for message in messages:
        if message[0] > last_id:
            process_message(tw_api, message)
    write_last_id(filename, messages[-1][0])


def print_msgs_info(tw_api):
    msgs = get_messages(tw_api)
    for msg in msgs:
        print("ID:", msg[0], "\nText:", msg[1], "\nSender ID:", msg[-1], "\n-------------------------------------------")


def main(tw_api):
    while True:
        print("Creating 'functionality_cycle'...")
        functionality_cycle = threading.Thread(target=manage_messages, args=(tw_api, "last_id.txt"))
        print("Starting 'functionality_cycle'...")
        functionality_cycle.start()
        print("Waiting for 'functionality_cycle' to finish...")
        functionality_cycle.join()
        print("'functionality_cycle' finished")
        sleep(120)


if __name__ == "__main__":
    consumer_key = auth.api_key
    consumer_secret_key = auth.api_secret_key
    access_key = auth.access_token
    access_secret_key = auth.access_token_secret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_key, access_secret_key)
    api = tweepy.API(auth)
    main(api)
