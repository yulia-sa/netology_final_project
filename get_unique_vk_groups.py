import requests
import time
import json
import sys

CONFIG = 'config.json'
SEPARATOR = '.'
TIME_DELAY = 0.34

API_VK_USERS_URL = 'https://api.vk.com/method/users.get'
API_VK_FRIENDS_URL = 'https://api.vk.com/method/friends.get'
API_VK_GROUPS_URL = 'https://api.vk.com/method/groups.get'
API_VK_GROUPS_BY_ID_URL = 'https://api.vk.com/method/groups.getById'

user_from_input = sys.argv[1]


def get_token_from_config():
    with open(CONFIG, encoding="utf-8") as f:
        config = json.load(f)
        token = config[0]['token']
    return token


def print_separator():
    return print(SEPARATOR, end='', flush=True)


def get_user_id_int():
    params_user = {
        'access_token': get_token_from_config(),
        'user_ids': user_from_input,
        'v': '5.73'
    }
    if user_from_input.isdigit():
        user_id_int = user_from_input
        return user_id_int
    else:
        r = requests.get(API_VK_USERS_URL, params_user)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            print_separator()
            responce = requests.get(API_VK_USERS_URL, params_user)
            user_id_int = responce.json()['response'][0]['id']
            return user_id_int
        else:
            return print('server error')


params = {
    'access_token': get_token_from_config(),
    'user_id': get_user_id_int(),
    'v': '5.73'
}     


def do_request(url, params):
    while True:
        r = requests.get(url, params)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            try:
                print_separator()
                responce = requests.get(url, params).json() 
                if 'error' in responce:
                    if responce['error']['error_code'] == 6:
                        time.sleep(TIME_DELAY)
                        pass
                    elif responce['error']['error_code'] == 18:
                        break
                    elif responce['error']['error_code'] == 7:
                        break
            except AttributeError:
                return {}
            except KeyError:
                return {}
            else: 
                return responce
        else:
            return print('server error')


def get_user_friends():
    responce = do_request(API_VK_FRIENDS_URL, params)
    user_friends = responce['response']['items']
    return user_friends


def get_user_groups():
    try:
        responce = do_request(API_VK_GROUPS_URL, params)
        user_groups = responce['response']['items']
        user_groups = set(user_groups)
    except TypeError:
        return {}
    except KeyError:
        return {}  # случай, когда групп у пользователя нет
    return user_groups


def get_all_friends_groups():
    all_friends_groups = []
    user_friends = get_user_friends()
    for friend in user_friends:
        params['user_id'] = friend
        user_groups = get_user_groups()
        all_friends_groups.extend(user_groups)
    return all_friends_groups


def get_all_friends_unique_groups():
    all_friends_unique_groups_tuple = tuple(get_all_friends_groups())
    all_friends_unique_groups_set = set(all_friends_unique_groups_tuple)
    return all_friends_unique_groups_set


def unique_user_groups():
    user_groups = get_user_groups()
    all_friends_unique_groups = get_all_friends_unique_groups()
    unique_user_groups = user_groups.difference(all_friends_unique_groups)
    return unique_user_groups


def get_unique_user_groups_str():
    unique_user_groups_list = list(unique_user_groups())
    unique_user_groups_str = ','.join(map(str, unique_user_groups_list))
    return unique_user_groups_str


def get_extended_group_info():
    params_extended = {
        'access_token': get_token_from_config(),
        'group_ids': get_unique_user_groups_str(),
        'extended': 1,
        'fields': 'members_count',
        'v': '5.73'
    }
    responce = do_request(API_VK_GROUPS_BY_ID_URL, params_extended)
    try:
        user_groups_extended = responce['response']
    except KeyError:
        return {}  # случай, когда уникальных групп у пользователя нет
    return user_groups_extended


def get_json_for_saving():
    raw_data = get_extended_group_info()
    data_for_saving = []
    try:
        for item in raw_data:
            group_dict = {}
            group_dict['name'] = item.get('name')
            group_dict['gid'] = item.get('screen_name')
            group_dict['members_count'] = item.get('members_count')
            data_for_saving.append(group_dict)
        return data_for_saving
    except KeyError:
        return {}  # случай, когда уникальных групп у пользователя нет  


def write_unique_user_groups_to_file():
    data = get_json_for_saving()
    with open('groups.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=False)


def main():
    get_user_id_int()
    write_unique_user_groups_to_file()


if __name__ == '__main__':
    main()
