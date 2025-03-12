import psycopg2

# start_date  = '2025-02-10'
# end_date  = '2025-03-11'

host = 'localhost'
port = '5432'
user = 'admin'
database_name = 'logsdb'
password = 'admin'

start_date  = input('start date (YYYY-MM-DD):')
end_date  = input('end date (YYYY-MM-DD):')

s = f'''
with log_by_date as (
select log_date, user_guid, event_name
from logs
inner join log_event lg on lg.guid = logs.event_guid
where log_date >= '{start_date}' and  log_date <= '{end_date}' and
      response_status_code = 1
),
new_accounts as (
select log_date::date, count(*) as new_users
from log_by_date
where event_name = 'registration'
group by log_date::date
),
message_count as (
select log_date::date,
       sum(case when user_guid is null
           then 1
           else 0 end
       )*100 / count(*) as anon_pcnt,
       count(*) as msg_cnt
from log_by_date
where event_name = 'write message'
group by log_date::date
),
topic_count_by_day as (
select log_date::date,
       sum(case when event_name ='create topic'
            then 1
            else -1 end)  as topic_cnt
from log_by_date
where event_name in ('create topic', 'delete topic')
group by log_date :: date
),
preffix_sum  as (
select log_date,
topic_cnt,
sum(topic_cnt) over (order by log_date) as topic_sum
from topic_count_by_day
)
select ps.log_date,
       new_users,
       anon_pcnt,
       msg_cnt,
       round(topic_cnt*100*lag(1/topic_sum, 1, 0) over (order by ps.log_date), 1) as new_topic_pcnt
from preffix_sum ps
inner join new_accounts na on na.log_date = ps.log_date
inner join message_count mc on mc.log_date = ps.log_date
'''

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=database_name,
    user=user,
    password=password
)
cur = conn.cursor()

SQL_for_file_output = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(s)

with open('data.csv', 'w') as f_output:
    cur.copy_expert(SQL_for_file_output, f_output)

conn.close()