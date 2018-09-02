# encoding: utf-8
import requests

class LongPoll(object):
    def __init__(self, vk, wait=25, use_ssl=True, mode=34):
        self.vk = vk
        self.wait = wait
        self.use_ssl = use_ssl
        self.mode = mode
        self.get_longpoll_server()
        self.url = 'https' if use_ssl else 'http'
        self.url += '://' + self.server

    def get_longpoll_server(self, update_ts=True):
        values = {
            'use_ssl': '1' if self.use_ssl else '0',
            'need_pts': '1'
        }
        response = self.vk.messages.getLongPollServer(**values)
        self.key = response['key']
        self.server = response['server']
        if update_ts:
            self.ts = response['ts']
            self.pts = response['pts']

    def check(self):
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
            'mode': self.mode
        }
        response = requests.get(self.url, params=values,
                                 timeout=self.wait + 10).json()
        events = []

        if 'failed' not in response:
            self.ts = response['ts']
            self.pts = response['pts']

            for raw_event in response['updates']:
                events.append(Event(raw_event))
            # http://vk.com/dev/using_longpoll
        else:
            self.get_longpoll_server(update_ts=False)

        return events


CHAT_START_ID = int(2E9)

EVENT_TYPES = {
    0: 'message_delete',
    1: 'message_flags_replace',
    2: 'message_flags_put',
    3: 'message_flags_reset',
    4: 'message_new',

    8: 'user_online',
    9: 'user_offline',

    51: 'chat_new',
    61: 'user_typing',
    62: 'user_typing_in_chat',

    70: 'user_call',
    }

ASSOCIATIVES = {
    0: ['message_id'],
    1: ['message_id', 'flags'],
    2: ['message_id', 'mask', 'user_id'],
    3: ['message_id', 'mask', 'user_id', 'timestamp', 'subject',
        'text', 'attachments'],
    4: ['message_id', 'flags', 'from_id', 'timestamp', 'subject',
        'text', 'attachments'],

    8: ['user_id', 'flags'],
    9: ['user_id', 'flags'],

    51: ['chat_id', 'byself'],
    61: ['user_id', 'flags'],
    62: ['user_id', 'chat_id'],

    70: ['user_id', 'call_id'],
}

MESSAGE_FLAGS = [
    'unread', 'outbox', 'replied', 'important', 'chat', 'friends', 'spam',
    'deleted', 'fixed', 'media'
]


class Event(object):
    def __init__(self, raw):
        self.raw = raw

        self.message_id = None
        self.flags = None
        self.mask = None
        self.user_id = None
        self.from_id = None
        self.timestamp = None
        self.subject = None
        self.text = None
        self.attachments = None
        self.call_id = None
        self.chat_id = None
        self.byself = None

        cmd = raw[0]

        self.message_flags = {}
        self.type = EVENT_TYPES.get(cmd)
        self._list_to_attr(raw[1:], ASSOCIATIVES.get(cmd))

        if cmd == 4:
            self._parse_message_flags()
            self.text = self.text.replace('<br>', '\n')

            if self.from_id > CHAT_START_ID:
                self.chat_id = self.from_id - CHAT_START_ID
                self.from_id = self.attachments['from']
        elif cmd in [2, 3]:
            if self.user_id > CHAT_START_ID:
                self.chat_id = self.user_id - CHAT_START_ID
                self.user_id = None
        elif cmd in [8, 9]:
            self.user_id = abs(self.user_id)

    def _parse_message_flags(self):
        x = 1
        for i in MESSAGE_FLAGS:

            if self.flags & x:
                self.message_flags.update({i: True})

            x *= 2

    def _list_to_attr(self, l, associative):
        if not associative:
            return

        for i in range(len(l)):
            try:
                name = associative[i]
            except IndexError:
                return True

            value = l[i]
            self.__setattr__(name, value)
