import requests
import json

# Define the target URL
url = "https://www.etoro.com/api/userpagestats/v1/user/149/stats/components"

# Query parameters
params = {"client_request_id": "49f65935-9c76-424d-aae6-18d2265d8a2f"}

# Headers
headers = {
    "accept": "application/json, text/plain, */*",
    "authorization": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiNDI2NzgiLCJ0eXAiOiJKV1QiLCJjdHkiOiJKV1QifQ..dMeGLEaxnwbCdE_dcJ2bmQ.onBHgm_C4ncRRnitBz96NEjENhYotbtAT2tI9UmGJNI6bMyu_mIXTNjcj4DmTu5QDJBQ4ke_gRRuxlTTP_exfzP-ESpwoQJQIEkURmOz1LsWj0TtjgoHmHLPB3hgp9d0KnD0PfuzZzRVmHAozgpQ2IOKemhidKB_X2I8T16XH76GS7VSegXSjTmtsLqiL8MJKs1NQ1szwgt2MURjiGt-_0X-5BIp0ayTOn4CCNIwrHI5-WcwJVZJvQB_d0SpWJ5L8BToXKHa3NO7vlVva5sLa1osn0z02ryFamq4UYwMCc6hP68eEYXvwTkoif4nMsXtZU9kCwe4hhfKDryP2vhyTNjhYHtjb08qdZEn7dT7i5gFuJsojGz8OsCDMt5lyzCE8oUZPE6ETJRjVKmKfE92hPiqf00owJj9ALJtaWr4IduzEk-TxedyGYMISBJURpcb1XH7d-l3htrORvNzt-CzvKk6Gusn7NJ1b-6ShaIufKDFF59VIPDDPPR1cKzwhJLTZRPSdbSh1jnwXyfXYtlo1wE51tZ24TymqDzXZPecNXjrqh_DEJFpQtawRzHezTqF9w9h5scfn5YJvgTaZcRgb2vt1k4PZ2NvpGtvwUOTByEHpkM0TqK0ZDI7Nfx8pbGPAPc-9hgRsi1ZuCNqxZ-MKXN5Zij8_PC-0D7jaxbybiv65-vfZBRgeVGxsu8wm-wLZnnqfarzjUuHE2V2dzXoOobKmBOSBKJ5vKWx2ys5xVGdjd_OjISGlu8i4CdslKgRGRUx7YvV_pO9ZdamSDxf-LOBpKv0FXi8Xzed8ZwSBdB2dT6jwudOSvs9TS-YmJJ4l9MlhrI1lq0PMNisGxw9xGMtYb5ZjfAZLWcZFcMy8IoDy78ebvzLWmgC27_qlJyd4bTp870Z5327NxaxGk1WDdeiR3anvgS6RdvzmLNqxguaaaK7yGRh4GcxwW4o1_cBaMb9zC1fxP9bdpuq2-n-kvwp2DjWrKbKPviK6I0In22_GGMn8s9drVl62qSGqmhKhW1_7x5O2pzfnZRdub-GwAnyT43R5dc6OmIVjoBplOTFbzkhUt3uT0_DFnKP4WElFPcxeVDvTZZrT2e7MuCmkGQqv_rlE3omJQfLbA7sXFm5PHPZafKuFNAYWzKU3GBRCQp0DmxNAhC3y2-sTDWAS5pNsgxc0tx5vIT_anepkYeeL3JpIMNgJeOSzxl8_-jevH_sImJywOO--XMX1rNoeJjFgl158ZsE4hQNzM2f_cg-Aukfn8MuBWMoBxu7ed5q4eQ_0om-eCZhzLSSQgx2Qq8Z9hWnKqPQYciRdAhM796zsMh2fdxZMEWITEOZoFpg_-9XI6mXld5IH7vbUTRErFIHYfrd4yzM9AfpnO_WLkyFL5Q87DGSZ6JuOh-LL7oaUFyYNwdf2dDOqhy-XlobY4IWLx1Fcy_AeL3_98xa3azocEuL5tJYzKdpdlPaFUuI.vsweFVNRsC_Ml9iJl-hYkA9-Ua35wdpWLSrKgYGkJYU",  # Replace <TOKEN> with your valid token
    "cookie" : "__adal_ca=so%3DGoogle%26me%3Dorganic%26ca%3D%28not%2520set%29%26co%3D%28not%2520set%29%26ke%3D%28not%2520set%29; RAF=26415018; RafAttr=eyJSYWZDaWQiOjI2NDE1MDE4LCJBZmZpbGlhdGVJZCI6NTU3MTQsIkJhbm5lcklkIjowLCJDYW1wYWlnbiI6IlNvY2lhbFNoYXJlUG9zdGNvcHlMaW5rXzI2NDE1MDE4IiwiQ2xpY2tUaW1lIjoiMjAyNC0xMi0xNlQyMTowNDoyMS4wNTM0MjY5WiIsIlVzZXJVbmlxdWVJZGVudGlmaWVyIjoiNDU1ODE4ZWItMGQxNi00MTE5LWFiYTMtN2YzZmU5MzI2ZjY5In0; AffiliateWizAffiliateID=AffiliateID=114807&ClickBannerID=12087&SubAffiliateID=PaPu_Win_8252867&Custom=&ClickDateTime=2025-01-02T19%3A13%3A01.1640666Z&UserUniqueIdentifier=828cb8ed-1048-4d72-a65a-081a62e8f82d; AffAttr=eyJBZmZpbGlhdGVJZCI6MTE0ODA3LCJCYW5uZXJJZCI6MTIwODcsIkNhbXBhaWduIjoiUGFQdV9XaW5fODI1Mjg2NyIsIkNsaWNrVGltZSI6IjIwMjUtMDEtMDJUMTk6MTM6MDEuMTY0MDc2M1oiLCJVc2VyVW5pcXVlSWRlbnRpZmllciI6IjgyOGNiOGVkLTEwNDgtNGQ3Mi1hNjVhLTA4MWE2MmU4ZjgyZCJ9; etoroHPRedirect=1; _gcl_au=1.1.1611639318.1735860492; intercom-device-id-x8o64ufr=62f0cbaa-895d-48c2-b1a7-013d91b146da; _fbp=fb.1.1735860501432.244972837785957738; _hjSessionUser_1871831=eyJpZCI6ImFiZmFhMDAxLTkzZWUtNWFlYi1hYTMwLWM3ZTExYzZkOTU5YiIsImNyZWF0ZWQiOjE3MzU4NjA0OTM0OTUsImV4aXN0aW5nIjp0cnVlfQ==; OptanonAlertBoxClosed=2025-01-07T14:17:01.930Z; _gid=GA1.2.1265311923.1736375920; __adal_cw=1736429666839; __adal_id=b882e829-bf2e-4e5a-ac43-41e063053340.1720971426.626.1736429705.1734512743.60f73073-3385-44f3-b394-0d4f942a472f; eToroLocale=en-gb; __cf_bm=5yo46TsCzY.F1h5Qx1k8yZOLiFl5y2nm9.9YDeO0IqQ-1736706482-1.0.1.1-EaSKr9KDLca9pOmo8tzmJ2bm3ISc_BPYIdkq6REZX2KeHcl9i_FMNO6bXKovfyuYrpF.DCT1Q.dcVccyoFHI.WtqWpuaIcSDfbDIgPvOu34; cf_clearance=mP_6.XWlhi1Beq8AqcAp7k8bgOmufZfI9Lq.02O52yo-1736706483-1.2.1.1-WdASxNNDVGwaG3wiCrS27b2k76KHIkVU3TFo1H9tL2t6OKpijpxdR35zWsZYyYNP.y0JFQ.CgQr0Qons0c8XErC2OpY0Z9HXywGoC52nBoPB.iXwwjmhiS2idX5Oh33E.qqpi8TScR.6dbpbDKSBM3cMWJFspVl8QZNQIZoDPMDVJW9RpYMbzfCLjMnE3md_jpmOL5w3keHx3S5B3pX8Y.dDf_zwHRN8GlSWe9vN2EDnkU8Ysy3hSbYJGvxTteVvWMOxnMkQm7NVrzfTFJVbqWoMJmHb_vHFMQHDUitJCEw; _hjSession_1871831=eyJpZCI6Ijg1M2M5YjMyLTYwYzMtNDFiMi1iYTkxLWM2ZjM4ZjY5N2VhOCIsImMiOjE3MzY3MDY0OTE2MDksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _gat=1; __cflb=0R6EA6uCenbWRSDji6ssKLaxm9Ld5FK8pdmWw75pd2VNPNwm2rWnWodp8TJEzvkuy6AcuEXsmRAcmwXguy7CPt7D6KnJ6MQmYXKyBAQXUwJcnCrSF7UNqzUa7oJA4N4E4XfGLrFzb2xhdrJzejvYJuiJEDsUq5FQfWpnvuDSKv6wZ3FTVRbTRiGohv7nEMwPUwD1dGV1umZcUejc92TFnzG7V87AzdUm6orQWVhiN1UFMWKN7xTwaxbBAUBRmpVtchUUnuYnwU1KkyBqotWsehR82Y8Ya8LS34NZmYV1J4LDhxRdFqHVLTRGQh96pYCDKhC8sXq5HmxV3iURCHVmKtm9EX1zyk33vzZ5NgLxqwPkGrpzLnMGfMuJR5ZdQSPAYCpA6kVWEwgmXo3x8CpNDMqKTTYhoPYDWNvRDCyYSH2HqUabZqTfvYvdeyF1cKkVNVKV5uXRDceuSQa82DHDxJmMLtLYb7UZsZCdXxkhCb1iccyqQ8vCxmK3ijWMkxpCaLVdTWcX4bGQo9qQXsFKvUw3ucxU2dd95nAJMc87qqtuq7LVsLhB85n5ZNvcS8PjdefoziUWVMjH1U39TuJmzTRGYX8cccLsZQjG26YHoBqPjcgWDeP2XSr1So6N89rBReeSAKAVJxr4DSg29qoiPWfALv4pSQAJ4jo6zyuynWE68GNAzwHsvkYszdWhGVxhTsbqH79raa2TwrUxEKtMq5GHDhbtRxF4uLtuprQBczvDYLiLYVKis7HDz4dCkLVFbtUChkWbtYRqwqcC4FNZvot7tsKAs98RVAGh3Hs4yy2Ndqy1L32TN3Cjy1Expcm63rvMzu66A4yAmX8wf5tM4eM3oFuoFR2Ga4WMZinBcYfoB8jtYhp33WjJjxQrMtakPfBJNi4sgQ1rLRMxhfksfvWxTLyj2G9ZZZ7xZTnsQRS9xDbgU7kSrrwjT8xvLyVqrgp9FTs9Mkx7WEedodA2ZWEVcHut1ZcMqtvNcxv3GpctpodtnpJCnbeqBhhabt1BYDiQXt5oGzCMJ3vDYJc7oQt98xCEEFmZiUP2vxvgrvFJt1yqmpsZev9zLDZZ1hB9HNzEZeoMLaG2EBR9hadZN9YiLxiULsud6GuRnue2xzC2SqMnA9zaifWhpjQP9QGWqTamc4mxzfYjaXXtDkc7EC8ky4yXMkMw14SQnuXF8hXkamaRsBrzAVy6ktLhBspg; _ga=GA1.1.1572765161.1723066101; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Jan+12+2025+18%3A39%3A27+GMT%2B0000+(Greenwich+Mean+Time)&version=202410.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=bd00165e-8cdb-496d-91c1-02e8579cbae8&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=GB%3BENG&AwaitingReconsent=false; intercom-session-x8o64ufr=OG9jcjRFdyt4WXFFWm9JSFhxc1ZrMGN3SUR6R09nQndQNXdBL3dQM1F0SXhGL0FwR1g5Ky9CNFpiVGI5SEd1Mi0tL0VyNVRUQnpvdUh5U1RiOFNLZDBLQT09--9d63eada03754111778a97907ce8abe7b4e3d6d4; _uetsid=4c268520ce1111efaf52ed749f81b343; _uetvid=f824d180550311ef808cdfd78abe2812; datadome=fvQNuxvqHGzQOhkan6YhdQSG5Ualm8V~gLZ_5Xjiskhv7TPtd24P8bKVy02WUTIMmg4_u1lrQe4EzVEcBhUOIwVqA4iPMcwXW1_3UMy6534hlv8Qjx7dIzam2szlZTc4; _ga_B0NS054E7V=GS1.1.1736706490.591.1.1736707168.43.0.0",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0",
    "referer": "https://www.etoro.com/people/ukjoehk/stats",
    "origin": "https://www.etoro.com",
}

# JSON payload
payload = {
    "groups": [
        {
            "groupId": 0,
            "dataComponents": [{"type": "Performance"}],
            "minRequiredItems": 2,
            "isMandatory": True,
        },
        {
            "groupId": 1,
            "dataComponents": [
                {"type": "PortfolioRisk"},
                {
                    "type": "ExpectedDividends",
                    "params": {
                        "totalAmount": 0,
                        "assetsPercentages": {
                        },
                    },
                },
                {"type": "TradingStats"},
                {"type": "AdditionalStats"},
            ],
            "minRequiredItems": 1,
            "isMandatory": True,
        },
        {
            "groupId": 2,
            "dataComponents": [
                {
                    "type": "ComparePortfolio",
                    "params": {
                        "itemsToCompare": [
                        ]
                    },
                },
                {"type": "CopiersStats"},
            ],
            "minRequiredItems": 2,
            "isMandatory": True,
        },
    ]
}

# Make the POST request
try:
    response = requests.post(url, headers=headers, params=params, json=payload)
    with open("testoutput.json", "w") as file:
        if response.status_code == 200:
            data = response.json()
            json.dump(data, file, indent = 1)
        else:
                file.write(f"Error: Received status code {response.status_code}\n")
                file.write(response.text)
    # Print response details
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Here's the response data:")
        print(response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
