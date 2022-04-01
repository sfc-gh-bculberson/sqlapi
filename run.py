from locust import FastHttpUser, task
import uuid, os, time, random

AUTHTOKEN = os.environ['AUTHTOKEN']
ACCOUNT = os.environ['ACCOUNT']
HEADERS = {
    "Authorization": "Bearer " + AUTHTOKEN,
    "Content-Type": "application/json",
    "Snowflake-Account": ACCOUNT,
    "Accept": "application/json",
    "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT"
}


def sql2body(sql):
    return {
        "statement": sql,
        "timeout": 60,
        "resultSetMetaData": {
            "format": "json"
        },
        "database": "CITIBIKE",
        "schema": "DEMO",
        "warehouse": f"LOAD_WH_{random.randint(0,9)}"
        }


class CachedQueries(FastHttpUser):
    @task(1000)
    def get_count(self):
        jsonBody = sql2body("SELECT COUNT(*) FROM TRIPS")
        r = self.client.post(f"/api/v2/statements?requestId={str(uuid.uuid4())}&retry=true", json=jsonBody, headers=HEADERS)
        if r.status_code == 200:
            return
        elif r.status_code == 202:
            statementStatusUrl = r.json()['statementStatusUrl']
            while r.status_code == 202:
                r = self.client.get(statementStatusUrl, json=jsonBody, headers=HEADERS)
                time.sleep(100)

        
class Queries(FastHttpUser):
    @task(1000)
    def get_random_count(self):
        start = time.mktime(time.strptime("2016-06-01", "%Y-%m-%d"))
        end = time.mktime(time.strptime("2020-11-30", "%Y-%m-%d"))
        p1time = start + random.random() * (end - start)
        p2time = p1time + random.random() * (end - p1time)

        p1 = time.strftime("%Y-%m-%d", time.localtime(p1time))
        p2 = time.strftime("%Y-%m-%d", time.localtime(p2time))
        sql = f"select count(*) from demo.TRIPS where starttime between '{p1}' and '{p2}';"
        jsonBody = sql2body(sql)
        r = self.client.post(f"/api/v2/statements?requestId={str(uuid.uuid4())}&retry=true", json=jsonBody, headers=HEADERS)
        if r.status_code == 200:
            return
        elif r.status_code == 202:
            statementStatusUrl = r.json()['statementStatusUrl']
            while r.status_code == 202:
                r = self.client.get(statementStatusUrl, json=jsonBody, headers=HEADERS)
                time.sleep(100)


class PaginationNext(FastHttpUser):
    @task
    def get_trips(self):
        jsonBody = sql2body("SELECT * FROM TRIPS")
        r = self.client.post(f"/api/v2/statements?requestId={str(uuid.uuid4())}&retry=true", json=jsonBody, headers=HEADERS)
        if r.status_code == 200:
            return
        elif r.status_code == 202:
            statementStatusUrl = r.json()['statementStatusUrl']
            while r.status_code == 202:
                r = self.client.get(statementStatusUrl, json=jsonBody, headers=HEADERS)
                if r.status_code == 200 and r.json()['partitionInfo']:
                    for x in range(1, len(r.json()['partitionInfo'])+1):
                        url = f"{statementStatusUrl}?partition={x}"
                        r = self.client.get(url, json=jsonBody, headers=HEADERS)
                        return
                time.sleep(100)
            