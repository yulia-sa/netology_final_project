import requests
import time
import json

user_from_input = 'tim_leary'
time_delay = 0.34
separator = '.'


TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'

params_user = {
    'access_token': TOKEN,
    'user_ids': user_from_input,
    'v': '5.73'
}


def print_separator():
    return print(separator)


def get_user_id_int(user_from_input):
    if type(user_from_input) is int:
        user_id_int = user_from_input
    else:
        responce = requests.get('https://api.vk.com/method/users.get', params_user)
        user_id_int = responce.json()['response'][0]['id']
    return user_id_int

user_id_int = get_user_id_int(user_from_input)

params = {
    'access_token': TOKEN,
    'user_id': user_id_int,
    'v': '5.73'
}


def get_user_friends(user_id_int):
    print_separator()
    responce = requests.get('https://api.vk.com/method/friends.get', params)
    user_friends = responce.json()['response']['items']
    return user_friends


def get_user_groups(user_id_int):
    print_separator()
    responce = requests.get('https://api.vk.com/method/groups.get', params)
    user_groups = responce.json()['response']['items']
    user_groups = set(user_groups)
    return user_groups


def get_all_friends_groups(user_id_int):
    all_friends_groups = []
    user_friends = get_user_friends(user_id_int)
    for friend in user_friends:
        params['user_id'] = friend
        print_separator()
        requests.get('https://api.vk.com/method/groups.get', params)
        time.sleep(time_delay)
        try:
            user_groups = get_user_groups(friend)
            all_friends_groups.extend(user_groups)
        except:
            continue
    return all_friends_groups


def get_all_friends_unique_groups():
    all_friends_unique_groups_tuple = tuple(get_all_friends_groups(user_id_int))
    all_friends_unique_groups_set = set(all_friends_unique_groups_tuple)
    return all_friends_unique_groups_set


def unique_user_groups(user_from_input):
    user_groups = get_user_groups(user_id_int)
    all_friends_unique_groups = get_all_friends_unique_groups()
    unique_user_groups = user_groups.difference(all_friends_unique_groups)
    return unique_user_groups


def get_unique_user_groups_str():
    unique_user_groups_list = list(unique_user_groups(user_from_input))
    unique_user_groups_str = ','.join(map(str, unique_user_groups_list))
    return unique_user_groups_str


params_extended = {
    'access_token': TOKEN,
    'group_ids': get_unique_user_groups_str(),
    'extended': 1,
    'fields': 'members_count',
    'v': '5.73'
}


def get_extended_group_info():
    print_separator()
    time.sleep(time_delay)
    responce = requests.get('https://api.vk.com/method/groups.getById', params_extended)
    user_groups_extended = responce.json()['response']
    return user_groups_extended


def get_json_for_saving():
    raw_data = get_extended_group_info()
    data_for_saving = []
    for item in raw_data:
        group_dict = {}
        group_dict['name'] = item.get('name')
        group_dict['gid'] = item.get('screen_name')
        group_dict['members_count'] = item.get('members_count')
        data_for_saving.append(group_dict)
    return data_for_saving


def write_unique_user_groups_to_file():
    data = get_json_for_saving()
    with open('groups.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)


write_unique_user_groups_to_file()   
