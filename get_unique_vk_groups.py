import requests
import time
import json
import sys

CONFIG = 'config.json'
SEPARATOR = '.'
TIME_DELAY = 0.7

API_VK_VERSION = '5.73'
API_VK_USERS_URL = 'https://api.vk.com/method/users.get'
API_VK_FRIENDS_URL = 'https://api.vk.com/method/friends.get'
API_VK_GROUPS_URL = 'https://api.vk.com/method/groups.get'
API_VK_GROUPS_BY_ID_URL = 'https://api.vk.com/method/groups.getById'

UNKNOWN_ERROR_OCCURRED = 1
TOO_MANY_REQUESTS_PER_SECOND = 6
PERMISSION_TO_PERFORM_THIS_ACTION_IS_DENIED = 7
FLOOD_CONTROL = 9
INTERNAL_SERVER_ERROR = 10
USER_WAS_DELETED_OR_BANNED = 18
ONE_OF_THE_PARAMETERS_SPECIFIED_WAS_MISSING_OR_INVALID = 100
INVALID_USER_ID = 113

user_from_input = sys.argv[1]


def get_token_from_config():
    with open(CONFIG, encoding="utf-8") as f:
        config = json.load(f)
        token = config[0]['token']
    return token


def print_separator():
    return print(SEPARATOR, end='', flush=True)


def do_request(url, params):
    base_params = {
        'access_token': token,
        'v': API_VK_VERSION   
    }
    base_params.update(params)
    params = base_params
    while True:
        print_separator()
        response = requests.get(url, params)
        status_code = response.status_code
        if status_code == requests.codes.ok:
            if 'error' in response.json():
                if response.json()['error']['error_code'] in (TOO_MANY_REQUESTS_PER_SECOND, 
                                                              FLOOD_CONTROL):
                    time.sleep(TIME_DELAY)
                    continue
                elif response.json()['error']['error_code'] in (ONE_OF_THE_PARAMETERS_SPECIFIED_WAS_MISSING_OR_INVALID, 
                                                                USER_WAS_DELETED_OR_BANNED, 
                                                                PERMISSION_TO_PERFORM_THIS_ACTION_IS_DENIED):
                    return {}
                elif response.json()['error']['error_code'] in (UNKNOWN_ERROR_OCCURRED, 
                                                                INTERNAL_SERVER_ERROR):
                    return print('Server error')
                elif response.json()['error']['error_code'] == INVALID_USER_ID:
                    return print('Invalid user id')
                else:
                    return {}         
            else:
                return response
        else:
            return print('Server error')    


def get_user_id_int():
    params = {
        'user_ids': user_from_input
    }
    if user_from_input.isdigit():
        return user_from_input
    else:
        response = do_request(API_VK_USERS_URL, params).json()
        user_id_int = response['response'][0]['id']
        return user_id_int


def get_user_friends():
    params = {
        'user_id': user_id_int
    }
    response = do_request(API_VK_FRIENDS_URL, params)
    try:
        user_friends = response.json()['response']['items']
    except (AttributeError, TypeError, KeyError):
        return []
    return user_friends


def get_user_groups():
    params = {
        'user_id': user_id_int
    }
    response = do_request(API_VK_GROUPS_URL, params)
    try:
        user_groups = response.json()['response']['items']
        user_groups = set(user_groups)
    except (AttributeError, TypeError, KeyError):
        return set()
    return user_groups


def get_all_friends_groups():
    all_friends_groups = []
    user_friends = get_user_friends()
    for friend in user_friends:
        params = {
            'user_id': friend
        }
        response = do_request(API_VK_GROUPS_URL, params)
        try:
            user_groups = response.json()['response']['items']
        except (TypeError, AttributeError, KeyError):
            user_groups = []
        all_friends_groups.extend(user_groups)
    return all_friends_groups


def get_all_friends_unique_groups():
    all_friends_unique_groups_set = set(get_all_friends_groups())
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
    params = {
        'group_ids': get_unique_user_groups_str(),
        'extended': 1,
        'fields': 'members_count',
    }
    response = do_request(API_VK_GROUPS_BY_ID_URL, params)
    try:
        user_groups_extended = response.json()['response']
    except (AttributeError, TypeError, KeyError):
        return {}
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
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=False)


def main():
    write_unique_user_groups_to_file()


if __name__ == '__main__':
    token = get_token_from_config()
    user_id_int = get_user_id_int()
    main()
