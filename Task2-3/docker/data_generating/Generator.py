import random
import uuid
from datetime import timedelta
from random import randint, choices, sample, choice, randrange
from faker import Faker

Faker.seed(42)
random.seed(42)

VISIT_LOG = 'LOG: first visit'
REGISTRATION_LOG = 'LOG: User {} registered'
LOGIN_LOG = 'LOG:  User {} is log in'
LOGOUT_LOG = 'LOG: User {} is log out'
CREATE_TOPIC_LOG = 'LOG: Topic {} was created'
ENTRY_TOPIC_LOG = 'LOG: Topic {} viewed'
DELETE_TOPIC_LOG = 'LOG: Topic {} was deleted'
WRITE_MESSAGE_LOG = 'LOG: Message {} was send'

REGISTRATION_ERROR = 'ERROR: Еmail already in use'
CREATE_TOPIC_ERROR = 'ERROR: Only authorized users can create topics'
LOGIN_ERROR = 'ERROR: Wrong login or password'
SERVER_ERROR = 'ERROR: Server Error'


class Topic:
    def __init__(self, user_guid, date_created):
        self.user_guid = user_guid
        self.date_created = date_created
        self.msg = []


class Message:
    def __init__(self, user_guid, topic_guid, date_created):
        self.user_guid = user_guid
        self.topic_guid = topic_guid
        self.date_created = date_created


class Generator:
    # Log events
    event_name = [
        'first visited',
        'registration',
        'login',
        'logout',
        'create topic',
        'entry topic',
        'delete topic',
        'write message',
    ]
    log_events = {k: uuid.uuid4() for k in event_name}
    fake = Faker()

    def __init__(self, start, end):
        ## Entities

        # Users
        self.users = []
        self.user_joined = []
        self.username = []
        self.user_email = []

        # Topics
        self.topics = {}
        self.topic_title = []
        self.topic_content = []

        # Messages
        self.messages = {}
        self.message_body = []

        # Logs
        self.log_guid = []
        self.log_date = []
        self.user_guid = []
        self.server_response = []
        self.log_event_guid = []
        self.log_message = []
        self.message_guid = []
        self.topic_guid = []

        # Start date, objects cnt
        self.start = start
        self.end = end
        self.log_cnt = 0
        self.user_cnt = 0
        self.topic_cnt = 0
        self.msg_cnt = 0


    def random_date(self, log_date):
        end = self.start + timedelta(hours=23, minutes=59)
        start = self.start if self.start >= log_date else log_date
        delta = (end - start).seconds
        random_second = randint(0, delta)
        return start + timedelta(seconds=random_second)

    def gen_logs(self, n, key):
        self.log_cnt += n
        self.log_guid += [uuid.uuid4() for _ in range(n)]
        self.log_event_guid += [self.log_events[key]] * n

    def registration(self):
        n = randint(5, 30)
        errors = randint(2, 5)
        success = n - errors

        self.user_cnt += success
        self.gen_logs(n, 'registration')
        self.log_date += [self.random_date(self.start) for _ in range(n)]
        self.server_response += [0] * errors + [1] * success

        user_ref = [uuid.uuid4() for _ in range(success)]
        self.user_guid += [None] * errors + user_ref
        self.log_message += [REGISTRATION_ERROR] * errors + [REGISTRATION_LOG.format(i) for i in user_ref]

        self.users += user_ref
        self.user_joined += self.log_date[self.log_cnt - success: self.log_cnt]
        self.message_guid += [None] * n
        self.topic_guid += [None] * n

    def first_visited(self):
        n = randint(5, 60)
        errors = randint(2, 5)
        success = n - errors

        self.gen_logs(n, 'first visited')
        self.log_date += [self.random_date(self.start) for _ in range(n)]
        self.server_response += [0] * errors + [1] * success
        self.log_message += [SERVER_ERROR] * errors + [VISIT_LOG] * success
        self.message_guid += [None] * n
        self.topic_guid += [None] * n
        self.user_guid += [None] * n

    def login(self):
        n = randint(5, max(10, self.user_cnt))

        self.gen_logs(n, 'login')
        errors = randint(2, n - 1)
        success = n - errors
        self.server_response += [0] * errors + [1] * success
        self.log_message += choices([LOGIN_ERROR, SERVER_ERROR], k=errors, weights=[1, 1])
        self.user_guid += [None] * errors
        self.log_date += [self.random_date(self.start) for _ in range(errors)]

        user_ref = choices(range(self.user_cnt), k=success)
        self.log_date += [self.random_date(self.user_joined[i]) for i in user_ref]
        self.log_message += [LOGIN_LOG.format(self.users[i]) for i in user_ref]
        self.user_guid += [self.users[i] for i in user_ref]

        self.message_guid += [None] * n
        self.topic_guid += [None] * n

    def logout(self):
        n = randint(5, max(10, self.user_cnt))

        self.gen_logs(n, 'logout')
        user_ref = choices(range(self.user_cnt), k=n)
        self.log_date += [self.random_date(self.user_joined[i]) for i in range(n)]

        self.user_guid += [self.users[i] for i in user_ref]
        self.log_message += [LOGOUT_LOG.format(self.users[i]) for i in user_ref]
        self.server_response += [1] * n
        self.topic_guid += [None] * n
        self.message_guid += [None] * n

    def topic_creation(self):
        n = randint(5, max(10, self.user_cnt))
        errors = randint(2, n - 1)
        success = n - errors
        self.topic_cnt += success

        self.gen_logs(n, 'create topic')
        self.log_date += [self.random_date(self.start) for _ in range(errors)]
        self.server_response += [0] * errors + [1] * success
        self.log_message += [CREATE_TOPIC_ERROR] * errors
        self.user_guid += [None] * errors
        self.message_guid += [None] * n
        self.topic_guid += [None] * errors

        user_ref = choices(range(self.user_cnt), k=success)
        self.log_date += [self.random_date(self.user_joined[i]) for i in user_ref]
        for k, i in enumerate(user_ref):
            ref = uuid.uuid4()
            self.topics[ref] = Topic(self.users[i], self.log_date[self.log_cnt - success + k])
            self.user_guid.append(self.users[i])
            self.log_message.append(CREATE_TOPIC_LOG.format(ref))
            self.topic_guid.append(ref)

    def entry_topic(self):
        n = len(self.topics) if len(self.topics) <= 5 else randint(5, len(self.topics))
        self.gen_logs(n, 'entry topic')

        self.server_response += [1] * n
        anonymous = randint(0, n - 1)
        self.user_guid += [None] * anonymous + choices(self.users, k=(n - anonymous))
        topic_ref = choices(list(self.topics.keys()), k=n)
        self.log_date += [self.random_date(self.topics[i].date_created) for i in topic_ref]
        self.topic_guid += topic_ref
        self.log_message += [ENTRY_TOPIC_LOG.format(i) for i in topic_ref]

        self.message_guid += [None] * n

    def delete_topic(self):
        n = randint(5, 10)

        self.gen_logs(n, 'delete topic')
        errors = n if self.topic_cnt <= n else randint(2, 4)
        success = n - errors

        topic_ref = choices(list(self.topics.keys()), k=errors)
        self.topic_guid += topic_ref
        self.user_guid += [self.topics[i].user_guid for i in topic_ref]
        self.server_response += [0] * errors
        self.log_message += [SERVER_ERROR for i in topic_ref]
        self.log_date += [self.random_date(self.topics[i].date_created) for i in topic_ref]
        self.message_guid += [None] * n

        self.topic_cnt -= success
        self.topic_guid += [None] * success
        topic_ref = sample(list(self.topics.keys()), k=success)
        self.user_guid += [self.topics[i].user_guid for i in topic_ref]
        self.server_response += [1] * success
        self.log_message += [DELETE_TOPIC_LOG.format(i) for i in topic_ref]
        self.log_date += [self.random_date(self.topics[i].date_created) for i in topic_ref]

        for i in topic_ref:
            while i in self.topic_guid:
                idx = self.topic_guid.index(i)
                self.topic_guid[idx] = None
            ref = self.topics.pop(i)
            self.msg_cnt -= len(ref.msg)
            for j in ref.msg:
                self.messages.pop(j)
                idx = self.message_guid.index(j)
                self.message_guid[idx] = None

    def write_message(self):
        n = randint(5, 500)

        auth = choices([0, 1], k=n, weights=[1, 1])
        self.msg_cnt += n

        self.gen_logs(n, 'write message')
        self.server_response += [1] * n

        user_ref = [choice(self.users) if i else None for i in auth]
        topic_ref = choices(list(self.topics.keys()), k=n)
        msg_ref = [uuid.uuid4() for _ in range(n)]

        self.user_guid += user_ref
        self.log_message += [WRITE_MESSAGE_LOG.format(i) for i in msg_ref]

        self.message_guid += msg_ref
        self.topic_guid += topic_ref
        self.log_date += [self.random_date(self.topics[i].date_created) for i in topic_ref]
        for k, i in enumerate(msg_ref):
            self.messages[i] = Message(
                user_ref[k],
                topic_ref[k],
                self.log_date[self.log_cnt - n + k])
            self.topics[topic_ref[k]].msg.append(i)

    def gen_data(self):
        while self.start <= self.end:
            self.first_visited()
            self.registration()
            self.login()
            self.logout()
            self.topic_creation()
            self.entry_topic()
            self.delete_topic()
            self.write_message()
            self.start += timedelta(days=1)

        self.username = [self.fake.unique.user_name() for _ in range(self.user_cnt)]
        self.user_email = [self.fake.unique.email() for _ in range(self.user_cnt)]

        self.topic_title = [self.fake.paragraph(nb_sentences=3) for _ in range(self.topic_cnt)]
        self.topic_content = [self.fake.paragraph(nb_sentences=5) for _ in range(self.topic_cnt)]

        self.message_body = [self.fake.paragraph(nb_sentences=randint(3, 5)) for _ in range(self.msg_cnt)]
