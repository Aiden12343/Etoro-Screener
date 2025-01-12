import csv
import json
import os
import requests

#---- Proxies and Headers ----#
def get_proxies():
    # Define your proxy settings here
    return {
    }

def get_headers():
    # Define your headers here
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.etoro.com/',
        'Origin': 'https://www.etoro.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers',
    }

#---- Fetching Data ----#
def fetch_user_data(username):
    headers = get_headers()
    proxies = get_proxies()

    ##get realcid
    print("Fetching user data for:", username)
    endpoint_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
    response = requests.get(endpoint_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    cid_data = response.json() 
    real_cid = cid_data['realCID']   
    
    ##Risk score data and rankings
    print("Fetching risk score data and rankings")
    rankings_url = f"https://www.etoro.com/sapi/rankings/cid/{cid_data['realCID']}/rankings/?Period=OneYearAgo"
    response = requests.get(rankings_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    rankings_data = response.json()

    ##Portfolio data
    print("Fetching portfolio data")
    portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={cid_data['realCID']}"
    response = requests.get(portfolio_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    portfolio_data = response.json()

    return rankings_data['Data'], portfolio_data['AggregatedPositions'], real_cid

import json

###Mapping path
def load_instrument_map(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
## Mapping Portfolio Data
def map_portfolio_data(aggregated_positions, instrument_map):
    mapped_portfolio_data = []
    for position in aggregated_positions:
            mapped_position = {
                'ticker_name': position.get(instrument_map.get(str(position['InstrumentID']), 'Unknown')),
                'direction': position.get('Direction', 'Unknown'),
                'invested': position.get('Invested', 0.0),
                'net_profit': position.get('NetProfit', 0.0),
                'value': position.get('Value', 0.0)
            }
            mapped_portfolio_data.append(mapped_position)
    return mapped_portfolio_data

def get_risk_score_data(username, real_cid):
    headers = headers = {
    "accept": "application/json, text/plain, */*",
    "authorization": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiNDI2NzgiLCJ0eXAiOiJKV1QiLCJjdHkiOiJKV1QifQ..ogRP4V0KuU5d9SbbX8XYlA.vExhjpPKI_HBd18-HvJeMeWozDUogToYeKicRc2o7zqCQwVRIdyzp72ZDLiUghJ_cx3IIrN6EJ_8gPEKy8lVfeHKysEXS-lQ-6gi5MmkkXRYcqaVaRtSN9X2xA-j7lfaN3hpSirpTLSF-M_1PxCJZq2I7oOIj00GiGVvJc4Xcqw-JjLTsQFYHuQOloLb1l6R6e54B0_63mE21iw8cWSAhZib2IgQJ8Hv2fWJ-JAusSbtculQv9-x2OuqXBFqeR-SN4O8-diJwaqyZUoVgzpeBDL6xO1aVAqKZSthkccL8g8YJtwGQRlqncjyixrUAmeE3EvwEHPBfq_0Wqt0cU_EzR1B8FqPzBtMXmc0ta8vLYX3YmwzS1R7v_HYxex_mJpnwQuGMtJPx5I6gYUYMSKpoplg7PpbtjqSBHx1evGfoL6ZPUuuCklXCqHvTOWzj2tYjsRZuYZplouT6HbIxbzWuWkC4EYD6LdWdXspkOYSSXWH5qYQ9hQccnXJZ1XtWJ1KOEVL-ez11SrPOcaUnY1lADfNgeaM8xI0RPcDte2vLiQhNVx2Gc-A1uaatsS6Pnivm3EYOGaElEZXnYZy-MByd6kbL7ocFCmXzliQmYdvpmGKevyO7PpDc1iAlv4hIzWKjDpbkurJzQvvcI7M5ugLwcB8PVA_OvzuZvVJbZu-cP1D5ktUK39kmwLL_jRZ-p6HBg9S-vkTlPKGcAA-5po8v9keugdFBZQRqJciYY2ZIH5YhQ1VPDL2uVDSG_Nh3yQYjX3reaRwK5zUAQDRRqh39TY8UsK62NOvsNDHk-lR5KxzqJAc35hnjO6Em-jsji9kTBZ1A5etXCag17zNMBPsVQoQD4ojvZy8e42Njpv00Z2uOie5vt9-K3BSjHalnM2VqyrW-vVZQGpl1rz0LoyOP6O382n-BuixS9-nOpceSxQGpSXRgtTr6Jwe7Ug08y7KC_2TLuPnwbMqC8_deeK3yP0668S6-x-hzQNuFFT17zNuIasIixtYtaSe1Ijjn0mEg1dbmkNIV7N2syx270Jn5s8HZAYI49VxKO4PLbv8WZpbS02EaIN59pXq4wIPkqffAIBDy78Y2TNWhwS1UM-ELHLXmQa8At6dPsWCfLL_rvdcA0cw79P_WWc_aAJEeHLZ5bhkHUuKDpkysMfc9d078I7t_IAg0uY0jVHenpx3ljeE1aGQum1j_pKlDzW2KiavzJz2lZHRD9SUFF_o5oFsAetM9TqAdmTijuX4-eTT3qneKZj_5RTw_dBITKgzXJmhxtMtJxwcpSDutjJirjokXWUfWAuPP4pKjev8guaVhg1SpZgxeaIt2SawZhgaSswroMCPIC8d1b85ahuS_SorbeBGevIT1mi4tuNXh1JeyiSTAyH-zOCoUFMQ4rr5hf0IFj6P_ApP89xVpeWdIgv-GGty3_uX-TCL4M32n7tozlTDQYiAK0b8qf61Z7hcIKt4.5wK2C2PDeVYixgJs2Mm8cJSwfcO80oYZ3kBmRT7DyPM",  # Replace <TOKEN> with your valid token
    "cookie" : "__adal_ca=so%3DGoogle%26me%3Dorganic%26ca%3D%28not%2520set%29%26co%3D%28not%2520set%29%26ke%3D%28not%2520set%29; RAF=26415018; RafAttr=eyJSYWZDaWQiOjI2NDE1MDE4LCJBZmZpbGlhdGVJZCI6NTU3MTQsIkJhbm5lcklkIjowLCJDYW1wYWlnbiI6IlNvY2lhbFNoYXJlUG9zdGNvcHlMaW5rXzI2NDE1MDE4IiwiQ2xpY2tUaW1lIjoiMjAyNC0xMi0xNlQyMTowNDoyMS4wNTM0MjY5WiIsIlVzZXJVbmlxdWVJZGVudGlmaWVyIjoiNDU1ODE4ZWItMGQxNi00MTE5LWFiYTMtN2YzZmU5MzI2ZjY5In0; AffiliateWizAffiliateID=AffiliateID=114807&ClickBannerID=12087&SubAffiliateID=PaPu_Win_8252867&Custom=&ClickDateTime=2025-01-02T19%3A13%3A01.1640666Z&UserUniqueIdentifier=828cb8ed-1048-4d72-a65a-081a62e8f82d; AffAttr=eyJBZmZpbGlhdGVJZCI6MTE0ODA3LCJCYW5uZXJJZCI6MTIwODcsIkNhbXBhaWduIjoiUGFQdV9XaW5fODI1Mjg2NyIsIkNsaWNrVGltZSI6IjIwMjUtMDEtMDJUMTk6MTM6MDEuMTY0MDc2M1oiLCJVc2VyVW5pcXVlSWRlbnRpZmllciI6IjgyOGNiOGVkLTEwNDgtNGQ3Mi1hNjVhLTA4MWE2MmU4ZjgyZCJ9; etoroHPRedirect=1; _gcl_au=1.1.1611639318.1735860492; intercom-device-id-x8o64ufr=62f0cbaa-895d-48c2-b1a7-013d91b146da; _fbp=fb.1.1735860501432.244972837785957738; _hjSessionUser_1871831=eyJpZCI6ImFiZmFhMDAxLTkzZWUtNWFlYi1hYTMwLWM3ZTExYzZkOTU5YiIsImNyZWF0ZWQiOjE3MzU4NjA0OTM0OTUsImV4aXN0aW5nIjp0cnVlfQ==; OptanonAlertBoxClosed=2025-01-07T14:17:01.930Z; _gid=GA1.2.1265311923.1736375920; __adal_cw=1736429666839; __adal_id=b882e829-bf2e-4e5a-ac43-41e063053340.1720971426.626.1736429705.1734512743.60f73073-3385-44f3-b394-0d4f942a472f; eToroLocale=en-gb; __cflb=0BswgK6NoHjhKuYuoBgEgnjf2n97zxfjLtGVrZZNyUVQJMsqVnavrnrMBYKEQzp6gHdAT6rLdfxQj51yGaTFsJf3aamu74a1BPwpSsxzcYYgYCcTgftZhrEGj6gYRYe2JDduN2dD5dWUWRTZPRH8YnLzEZeQtKQnGziy1pJEwbRZiVm7kgMqcXk38VZGVFdSig9SLn7ytVXvU5Q5PNhhH8Npk2NBQWq9ih62qoUk62n69YNQEFzWKdWmMFzGShUAtREhweD53RPfi5e7zCnF9kmfPpZXkekjTuoVDFAvXnjQjNHb6afek4z8H26fmbNPqRHKoGtp4sNoc6268gjEBRf26PcA8gL743DxuyL22XWiwCXeVq2rB1GSEMHN5GCHs4PNqodaju7irWM2to3QUxk1QAx3qi5xpCek3FcSYgDhnu6rxDQaGSs9qYtGzXEbhpMB5sBg4LNWQyi3yzmQc9s18BYYZ2fUQqGMwZ4LgWySgUYfuRatjfWPLTq8CVFkv4jfqvzzug4LAfyoMJvYmY15vJQye3QKzTzJeqRmadFwWm9CAFZJzMSSoj1QATFxA5Jw4zmsj8GPysYNWAvHen9mr1NPiukgPsM2kQ9qzFbvgJBqLMbskM23JB5tayuhRoPY5WJGruWgBY1HBr5UGGxJdUJtH6rp1hw5kdLsvp2NNWRqAe612L2R3gvWv7Z2L4twwi4MMeC99eUX2TjfqBcgnToDEazYZ22rKXrq8dzWCm7noe6ZUZwYbJqzwM4p3PM2UM6QcxnsCWtTa3eWqFGCAoD7pNRpP5S4oyaW5Vb7c8VeTEDvsoGwXFfvnY5QC382mMkx3fjGwH8nY4djed15PvBSj3zReHQZJukriTgZSUqqomKJtxpipfLgSvyKRMf8EZxXL8eiLAxyoNo4MuQySuuyCDLm5aasSCrX5B4UdjXZNfL9gurLDUzQRPRALDNzvNeM8gNzEXevopHMcuuLv31VXbFdXuA1JGnG6MBJ8oA92tYi5BMswEtYeL8H3fkTRNx3XqQjnqghn3xmVDTq9QftiNj1oYAzftfRTehRYksVU2ZnF65iWmxz5vMMQD1Ucoyep8PgLBQiP1tNE5PFsBpDxEqKoxaMpsxrQAx4tSNawWesMQGB6hXNWVE4g5zuo6xPCxpPaAjj9p1M8qdDpPSn5C8nEoa6xxwKsfxLRyYpQPyGQF22HUriho4hFTBW9icUerS5aKs7yyRyYPztsAMtbeNKTJG8ktdyJN8GjW44Y7pR4n4CVGyYkcJ6ewSHdgHcbYYmrGC2TpmhZt2xn6w47t9jJDjjhifyYJUNYMxAg69smhv52JRBJgJfDvwVZoKBhxLYeRgau9HPfduxXAadgnTLZwoAh16js6t26Qc; _hjSession_1871831=eyJpZCI6IjVmZTJhZDg4LTM0ZDQtNDBiNS04YTBlLTBhMjc4MWRhMTE5NiIsImMiOjE3MzY2MzAyMjI4ODIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; __cf_bm=hX8ZT0J9Hlb0qHgipOel9uVWUeJ53uGhdFaJbUiSpy8-1736630373-1.0.1.1-59uuyLyYVxz.JSt1fPDxX4bVbBqB8dAA6mQOkH69aqXbhC32o5BqoOIfdcQV3GKE8fPwwQ83u9fT5MVgkM8I5iEZaJ4DzThtKlwbnV3mhtY; _gat=1; cf_clearance=1FF63oY80QQDMpx8Mjn392dIDgHV49LtOPVueB_.xN0-1736631512-1.2.1.1-HlM2mMEkFyFjbSlXBH_LFac6uFZNiFFcEJAdmwXBcQK5z2lKrXvDolGMwxc8MiDxdjSNE9EohPl._GLwBl3S4g3Ugw6_FSIKxmHXV4jqCnEjCKwfaW1JpmeP1fbxCU_Q72uB_np8iIyyCVxSg5n48hrHg.6YavrM6EDvMfFHBlcNiY8QaK820iqSe5fxEMy77vSdBhn_svcyRZGKs1Z8pcp8Sj6PlEZBaKogwH6SG.jp4Az9DJUOgU9QSir5KxnUoQrucyVkuZETE4fua3WUVb_iTzSHPxhQxepaY4mkxOg; _ga_B0NS054E7V=GS1.1.1736626433.588.1.1736631517.46.0.0; _ga=GA1.1.1572765161.1723066101; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Jan+11+2025+21%3A38%3A38+GMT%2B0000+(Greenwich+Mean+Time)&version=202410.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=bd00165e-8cdb-496d-91c1-02e8579cbae8&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=GB%3BENG&AwaitingReconsent=false; _uetsid=4c268520ce1111efaf52ed749f81b343; _uetvid=f824d180550311ef808cdfd78abe2812; datadome=4vhfX~6GOSYa6Hy4_~~L7lxM_Es8fRKs4YJfwxNKnE4VVUH70u_oKGYjzNgXwmQPbZu_vkezAA0RQoaQR4VXgjAkQYriZ_LrOMeivaEHx9i1GPwLGSWzKPz8EX50yycN; intercom-session-x8o64ufr=bUNzdzRCNkQrdXNFcWNnYVBWOWxrMjE1aVlLL2VCN1JOUU01S21WQVFZY3FWYVFxSkFhYmxrWmZZclJXbXJDbC0tZDVnc2R1Y3lOZGIrMG9hUnN6TEtrUT09--5b3d5145d5034a55b173083a3ff8064280c14627",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0",
    "referer": "https://www.etoro.com/people/ukjoehk/stats",
    "origin": "https://www.etoro.com",
}
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
    proxies = get_proxies()

    ##Risk score data
    print("Fetching risk score data")
    risk_score_url = f"https://www.etoro.com/api/userpagestats/v1/user/{real_cid}/stats/components"
    response = requests.post(risk_score_url, headers=headers, proxies=proxies, json = payload)
    response.raise_for_status()
    risk_score_data = response.json()

    return risk_score_data