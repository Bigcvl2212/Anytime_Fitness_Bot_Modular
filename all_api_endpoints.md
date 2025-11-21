# ALL API Endpoints

## GET /api/staff/{id}/leads
**Path:** `/api/staff/{id}/leads`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/staff/187032782/leads?&_=1752550744858",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/staff/187032782/leads?&_=1752550744858"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg3MDMyNzgyLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiI0M0Y1QzZFQkFBMUIzRkNFMUI1QzZEREIyOTkyMjU2QiJ9.jniCa5w-qxiKEw4J-iUU56Ov6E4WZt4SOYzVL7IlrSo"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjE2MjVmMDk4YTdkY2IyNmEiLCJ0ciI6IjRhNjUyNDZkODJkZTM5Yjc4NTRhYTI5MTUzNDRiZTRiIiwidGkiOjE3NTI1NTA3NDQ4NTh9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-4a65246d82de39b7854aa2915344be4b-1625f098a7dcb26a-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-1625f098a7dcb26a----1752550744858"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/Dashboard/view"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=43F5C6EBAA1B3FCE1B5C6DDB2992256B"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6IjA2MDQzYzhlLTdjMDItNDRjMy04ODczLTJmZDI4MWRhZmFkNyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1NTA3NDAsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU1NDM0MCwiaWF0IjoxNzUyNTUwNzQwLCJqdGkiOiJiZTI3ZGQ5My05OWZkLTQ2ZDEtYTI1YS05NjRmODc5MTc4MzkiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.dTJfvtthThkaLEnSuJg5XWzMw4jz69Wdg3HEO5TDcpUPQdA8DQnoBLZmkgtG8A1B5KBq_-9WRJzj0AYAy2hk62WyAvAMV8neTJRgMq8evAfR9nfr2UzQxGcqUDt88bcJEGWvAgG8PBI0FM255O3b5vMXghcPoknYzwyvHyc8PT2QfGL_VIhtNsbcsxI_RoPw5lijLMzYnBS9aEBCzBW0nLghn71CbGaWhDu-bT1LJ_Ln7cuHSK9KIfDFvDWDhpyUZmdP3alVWROCmpqMcdUP_HkLgHQHCYa_a2oxI6fdO0lhB8zhKuAOPuGNUcvNCBz8RPBcbnv-kHfCfUcoMkqG4Q"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiMDYwNDNjOGUtN2MwMi00NGMzLTg4NzMtMmZkMjgxZGFmYWQ3IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1NTA3NDAsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NTQzNDAsImlhdCI6MTc1MjU1MDc0MH0.LMMjqfLMWaT2xMI8sU3_FaS3wCqUIiRyr5gEfuNAGDF1WAHsRkKDe25oftgod-CsnCaTz2-8XhbbNtXTJsabsgelb9VNW9JDz_ou2uUXD6c_gY8Nbhw13xs9usALS9PWG2vpjPv9ZnmK9fL0DNzM-f7p-1Qxek5wYJs-rpo32k4AJwp2pOA4xpDOJKtLH2knkI2qF1MEth_t6wz5pDRmNAcK8lWWOKxzNy3uhObsVohQCLDO6OdF-3j1cg7FONKPI8pJGhhK9h7YwDkwd3FSqSIIOITy6JE4laQIgNI0kbSjLz7pJ5aWEPb0EV_x8TZq1HFPmAl7-Mdl-dYAkAiL9A"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.Cjj8JjvK7sGz3fRO1fYnSRnjViHbACXqARK4E9BPZAke4v5wUgpgSC2rTVEt61O-1RguMdWs5pnM9jelN_HTW17VUHa8LcQUfSb7aZUKp9QjNnif64BJf3oE5XKs_noiekrkSqJ3bkmYDvrbPKMe4J4Ir0v7obJIsiF9wL-xf_Y3fHYYq-RVP1iozKlX62CXipZWteg0Av0VORpYqiIYYGBqfYdpLycY7kwA7txI-MTwAcYcaBCCBhH82ZJ1ojCi9rMLp6oHBJ1kjNDbV-XeEUfa65jlJuukhgYB2aiABT-WQKSDjY6taIdJeSz75FXWsBjSVeVFHTIy1qS0fknbJw.VdQG7xUzdJAUxvX6.hghOR-QbzaKRJakl9B9GeOdlg45SGoJTt919lqUmNBmuWZ3bQLWZ0O7uPQs1-C_V8Gi8z49wc4Dmux717B_tJvCoESBR8EpxCBVy3XrN_Z7p9U1bccpNcrYr7Vi2OJ5PRIvA0aDzveIA7Zz90SMFFokSAtfcE5eCcl1feunFaolstCWS1hJ0aAopMOmkUD6jwtRi4P_L-MEiXM-z-4j-2bKfe_EnrvpyDhDt59UDkw7Vvhu4fPkGl4UW25W9sgrf3IsoFqtDQ6tKo-7sQ-btqlVB6cG6JMbEBljM4SA5e38vnhWzU8NAAkUPXyYIC1afEDPX94FVQb9F0l1mL3UIoMfdsy4sYTM89YSp_hx3e-q6aWFrgLrY7ZCK2eUeUZu02ZHrzmpCPnXJeHuyPk2C6uKLG7eLf6jbLG_ZLfIii_QcGUMZzbSPMmGscoqbm_88GL6GIj5GpUjBnvvQWGTybHAoxg8obHvIAQcgVf65U63SsUWaOItnwgWJpCUZeIrEMIj0MoXcxjAHs6dt2c4aP3i0G7sAnqxot95xEyhkjfdpTh-GaV52X-c5FMbZCmJbK3k6MUCVhenHzZTXxOR9htUALe2LfW6w4NkhPzgbApjYVvf07c4-jsoKOxcWaPaVZVkcHUrmUkBCsJnhKeBptqKvdJiHTmrYAMeN3Xp615xNJ_rtZ6K01zZ9gH0AIKIWcV3OvFAmxc-N943Hy3j8Ec-kiMVGWVishlZomaH9Es4zAoX0WUo393lGKFgiBqWHoR17FNoo46vigoLL1WfOTJl067oSgsB79p6r3cUWRtINMsBJCWx0Kg1DkEaJkYaSsx_EOgMjjXpLoog4Bvi_X8C28P9yBbdUjxaYtSqtGpPRG4cuwCi_L5c9lOoyD9QedxGIpOuXkuw46dkwFzSDStri4-FcHtpFABm7ZX94WkFGIYcKJbfSJloo6U2Sa_RTDeoMV3pugmWEWt2bkGZ2LKBJaBs-dxSfUC-DXuo7zQkgmSl5HYc1JJvqFiP0sBCakoqyktptESEuN2V-o8GGLGbCZJTSrN14JFnObWZIt6jv-ICJZp60JPthp6Emb7Vm3bLmKPupNP1nuzNTbx7WG90tXjxDm7yVR41VR8fAFq9KlhMwjR9JmpoEe9NMBaEYM6E75twJRq4k4gBcEpoxoBrlikK-zAwu5jkWotFVTFWYJ_C_P2-gekWm9wXB1DQp5_f90cWeQgF6eRlvbvheUx-P1Vd_ueftjYZuGE-ufLhjRpXlz6dKUcgUKdIOha3rDH03B66ZgW0.F_wzSpx62Q9bfd3HZ25knA"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId=187032782"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "_",
      "value": "1752550744858"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/members
**Path:** `/api/clubs/{id}/members`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1657/members?page=1&pageSize=50",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "50"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/usages
**Path:** `/api/clubs/{id}/usages`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1657/usages?page=1&pageSize=50",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "50"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/usages
**Path:** `/api/members/{id}/usages`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/60081504/usages?page=1&pageSize=200",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "200"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/DoorStatus
**Path:** `/api/clubs/{id}/DoorStatus`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1657/DoorStatus",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/1657
**Path:** `/api/clubs/1657`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1657",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/settings
**Path:** `/api/clubs/{id}/settings`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1657/settings",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/members/all
**Path:** `/api/clubs/{id}/members/all`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1657/members/all",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_205_434694=bz7uc6JFvFxttlLJvU7YAr/CdWgAAAAAVyWoCavFutYbVRZBEONJsw==; incap_ses_69_434694=XgnrLBXqtX89lEmXhiP1AOqxdWgAAAAAoXmfvFbjsMTdzLlibmJvLw==; dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJ6U1hvODRaal8tM3lQdmVzRmF3WlJGS0lSME9YUi03QWpfbnpoQjdoNGNxdEY1MFhCakc5ck1wc29ZdG92aTR5elZXY3k4YnBIX0JxanNzemZvREpQajdzaFZWMjR5VWRxRlFYX29SV1M0X3BPQWttbk1RZmpUUnhua1FNeDFiamNlNUd4eEZNSlk2UEFCUzdTX2tZa0JoNGNnY0pTUGllbnliR2NTYklSaDY1RE5RQWxpV0dPZXl0YlZmaDdfbWtyZEJIaDc3SjJ0ZER0eFRROEFsN3pWTXV4WFNrRzF2eWJNR3d1U0xhVkh5cmNkcExPY3htZFdrUS1rQzYtY0k4UFJZUnBVbmNyM3p4bHVkd0x1RkhQcXE1MzUzQWFnckpnUDVfb0U0WlhjNk1Pblh3Y0tZb2NqdnNOWHM5X1ZnOGZ0ZkVVZyIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDQ5MjYsImV4cCI6MTc1MjYzMTMyNiwiaWF0IjoxNzUyNTQ0OTI2LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.S1UMdx9aZuYMffO97pL5V8no6mno1Tu5zQYpRiJUw0A"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/features
**Path:** `/api/clubs/{id}/features`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/features",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/digital-key-status
**Path:** `/api/members/{id}/digital-key-status`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/digital-key-status",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/66735385
**Path:** `/api/members/66735385`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/agreement
**Path:** `/api/members/{id}/agreement`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/agreement",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/Doors
**Path:** `/api/clubs/{id}/Doors`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/Doors?page=1&pageSize=100",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "100"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/activities
**Path:** `/api/members/{id}/activities`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/activities?page=1&pageSize=25",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "25"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/bans
**Path:** `/api/members/{id}/bans`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/bans",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/tanning
**Path:** `/api/members/{id}/tanning`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/tanning?clubId=1156",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "clubId",
      "value": "1156"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/TopicTypes
**Path:** `/api/clubs/{id}/TopicTypes`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/TopicTypes?page=1&pageSize=50",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "50"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## POST /api/members/{id}/usages
**Path:** `/api/members/{id}/usages`

**Method:** `POST`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/usages",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Content-Type",
      "value": "application/json"
    },
    {
      "name": "Content-Length",
      "value": "87"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; dtCookie=v_4_srv_8_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": "application/json",
    "text": "{\"date\":\"2025-07-14T20:34:03-05:00\",\"door\":{\"id\":772},\"club\":{\"id\":1156},\"manual\":true}"
  }
}
````

**Example Response:** None

## GET /api/members/{id}/pendingActions
**Path:** `/api/members/{id}/pendingActions`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/pendingActions",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/agreementHistory
**Path:** `/api/members/{id}/agreementHistory`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/agreementHistory",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/agreementTokenQuery
**Path:** `/api/members/{id}/agreementTokenQuery`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/66735385/agreementTokenQuery",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/prospects
**Path:** `/api/clubs/{id}/prospects`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/prospects?days=1&page=1&pageSize=50",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "days",
      "value": "1"
    },
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "50"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/schedule
**Path:** `/api/clubs/{id}/schedule`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/schedule?endDate=2025-07-20T05%3A00%3A00Z&page=1&pageSize=200&startDate=2025-07-13T05%3A00%3A00Z",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_69_434694=PB7ofImPOV4fxkOXhiP1AK2vdWgAAAAA6qalvZK55+cxkp/wQB0/TA==; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "endDate",
      "value": "2025-07-20T05:00:00Z"
    },
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "200"
    },
    {
      "name": "startDate",
      "value": "2025-07-13T05:00:00Z"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## POST /api/clubs/{id}/opendoors
**Path:** `/api/clubs/{id}/opendoors`

**Method:** `POST`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/opendoors",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Content-Length",
      "value": "0"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": null,
    "text": ""
  }
}
````

**Example Response:** None

## GET /api/clubs/{id}/Bans
**Path:** `/api/clubs/{id}/Bans`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/Bans?page=1&pageSize=50",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "50"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/65157278
**Path:** `/api/members/65157278`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/65157278?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/56793239
**Path:** `/api/members/56793239`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/56793239?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/62933542
**Path:** `/api/members/62933542`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/62933542?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/58331913
**Path:** `/api/members/58331913`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/58331913?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/57173275
**Path:** `/api/members/57173275`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/57173275?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/48076211
**Path:** `/api/members/48076211`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/48076211?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/51861859
**Path:** `/api/members/51861859`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/51861859?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/32927988
**Path:** `/api/members/32927988`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/32927988?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/55030530
**Path:** `/api/members/55030530`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/55030530?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/55404826
**Path:** `/api/members/55404826`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/55404826?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/49295679
**Path:** `/api/members/49295679`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/49295679?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/49827381
**Path:** `/api/members/49827381`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/49827381?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/36071624
**Path:** `/api/members/36071624`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/36071624?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/46062828
**Path:** `/api/members/46062828`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/46062828?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/48065366
**Path:** `/api/members/48065366`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/48065366?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/50936874
**Path:** `/api/members/50936874`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/50936874?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/49525408
**Path:** `/api/members/49525408`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/49525408?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/44724243
**Path:** `/api/members/44724243`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/44724243?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/41650175
**Path:** `/api/members/41650175`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/41650175?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/32390811
**Path:** `/api/members/32390811`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/32390811?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/9713566
**Path:** `/api/members/9713566`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/9713566?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/23029439
**Path:** `/api/members/23029439`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/23029439?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/44102933
**Path:** `/api/members/44102933`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/44102933?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/17768116
**Path:** `/api/members/17768116`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/17768116?includeLastActivity=false",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "incap_ses_69_434694=M9PZOFYUkhIJ0EWXhiP1AHWwdWgAAAAAa3OYtBbH+kNNVoo3c+3Q8g==; dtCookie=v_4_srv_9_sn_6ABE292FDA902A0B9479140B93E10F7B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; incap_ses_132_434694=01WsXJh4439fIQlVVvXUAYKLdWgAAAAAxGD+IS00tgrkyjzDyD/Jkw==; incap_ses_1167_434694=vKiNItPkVTAUCS2jqQQyEI/5c2gAAAAABzfSywXPNWp/SWhLoMWTDw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJUNlZXS3FnRzNIUEpXdmpETXRKQjdkdmJmZGVacGJKMjZvRGdsRzFwdWRGUFN0c2RWQnZaVHZQc0R1LUJ2aFl1X2JiWkVkSkxRRDhDd0dCTFRsMkhPMEJKc0RUN0p6dHg5aEZnU0dDR2hqMlZCc0Q4a3Z6Rm1SUWU2UDFNVmJhOUhKRU0tWlNTcTZfVVRFRDJwd3h5S3lzbEN2LVRwR3ZEcEQybWk1SW01VnNHZ1Z3THVHZ183R0Qwcm5RVUg3eG1qWDM5SU50NklZV0xJeEY2MEtaN2ZEbHlSWjVRZVdPdnd2MzVSNTlhQkw0dW4zOFlPd1NGYjltREVpcGlkZWJmWG5wR1JwZGhRbWtNd2o5X25kc2RfRjNtWFo3Rm5OZm0wRG5IVmRMOHNCOFdVTjd0Mko0SXFHWk5YbENlemY1UWR6Q3huUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1MDA2MDEsImV4cCI6MTc1MjU4NzAwMSwiaWF0IjoxNzUyNTAwNjAxLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.c802Z5b6GlmPvqi-wONJB0PUsJLc606w90sCKk_C2I8"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "includeLastActivity",
      "value": "false"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## POST /api/login
**Path:** `/api/login`

**Method:** `POST`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/login",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Content-Type",
      "value": "application/json"
    },
    {
      "name": "Cookie",
      "value": "visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    },
    {
      "name": "Content-Length",
      "value": "69"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": "application/json",
    "text": "{\"username\":\"mayo.jeremy2212@gmail.com\",\"password\":\"_-gYpkzQRWrX5k-\"}"
  }
}
````

**Example Response:** None

## GET /api/users/30820449
**Path:** `/api/users/30820449`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/users/30820449",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/users/{id}/clubs
**Path:** `/api/users/{id}/clubs`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/users/30820449/clubs?page=1&pageSize=250",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "250"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/1156
**Path:** `/api/clubs/1156`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/clubs/{id}/Sources
**Path:** `/api/clubs/{id}/Sources`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/Sources?page=1&pageSize=100",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "page",
      "value": "1"
    },
    {
      "name": "pageSize",
      "value": "100"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## PUT /api/clubs/{id}/members/{id}/bans
**Path:** `/api/clubs/{id}/members/{id}/bans`

**Method:** `PUT`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members/47641439/bans",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Content-Length",
      "value": "0"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": null,
    "text": ""
  }
}
````

**Example Response:** None

## POST /api/clubs/{id}/notes
**Path:** `/api/clubs/{id}/notes`

**Method:** `POST`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/notes",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Content-Type",
      "value": "application/json"
    },
    {
      "name": "Content-Length",
      "value": "95"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": "application/json",
    "text": "{\"member\":{\"id\":47641439},\"note\":\"Banned by: mayo.jeremy2212@gmail.com\\nReason: Payment Issue\"}"
  }
}
````

**Example Response:** None

## DELETE /api/clubs/{id}/members/{id}/bans
**Path:** `/api/clubs/{id}/members/{id}/bans`

**Method:** `DELETE`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members/47641439/bans",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Content-Length",
      "value": "0"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": null,
    "text": ""
  }
}
````

**Example Response:** None

## GET /api/v1/google.json
**Path:** `/api/v1/google.json`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://token.safebrowsing.apple/api/v1/google.json",
  "headers": [
    {
      "name": "Host",
      "value": "token.safebrowsing.apple"
    },
    {
      "name": "Accept",
      "value": "*/*"
    },
    {
      "name": "Accept-Language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "Accept-Encoding",
      "value": "gzip, deflate, br"
    },
    {
      "name": "User-Agent",
      "value": "SafariSafeBrowsing/8621.2.5.10.10 CFNetwork/3826.500.131 Darwin/24.5.0"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/members/{id}/usages/by-date-range
**Path:** `/api/members/{id}/usages/by-date-range`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://clubhub-ios-api.anytimefitness.com/api/members/47641439/usages/by-date-range?endDate=2025-07-15T02%3A11%3A57Z&startDate=2025-04-16T02%3A11%3A57Z",
  "headers": [
    {
      "name": "Host",
      "value": "clubhub-ios-api.anytimefitness.com"
    },
    {
      "name": "Cookie",
      "value": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_69_434694=7w3ndItTUGav8kaXhiP1AOawdWgAAAAAG25RDJCvNu9dUHN9R0Q23A==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
    },
    {
      "name": "Connection",
      "value": "keep-alive"
    },
    {
      "name": "API-version",
      "value": "1"
    },
    {
      "name": "Accept",
      "value": "application/json"
    },
    {
      "name": "User-Agent",
      "value": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4"
    },
    {
      "name": "Authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeTdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"
    },
    {
      "name": "Accept-Language",
      "value": "en-US"
    },
    {
      "name": "Accept-Encoding",
      "value": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
  ],
  "queryString": [
    {
      "name": "endDate",
      "value": "2025-07-15T02:11:57Z"
    },
    {
      "name": "startDate",
      "value": "2025-04-16T02:11:57Z"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/list
**Path:** `/api/agreements/package_agreements/list`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/list",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/list"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjFlNzUzNDEzZGI0NDU4ZWQiLCJ0ciI6IjdkZjI0Njk4YTk1NjYxNzc1ZjgwZGY4MzNiNGFkZTkzIiwidGkiOjE3NTI1NDEyNTU3MTl9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-7df24698a95661775f80df833b4ade93-1e753413db4458ed-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-1e753413db4458ed----1752541255719"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/ClubServicesNew"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/inventory/detailed
**Path:** `/api/inventory/detailed`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/inventory/detailed",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/inventory/detailed"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImZkYThiYjMwN2YxZDcwYjciLCJ0ciI6Ijc2OGFjZTJhNmZhZDFmNWFmOTM1MjM1YWZhZmQxMWFlIiwidGkiOjE3NTI1NDEyNTU4NDd9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-768ace2a6fad1f5af935235afafd11ae-fda8bb307f1d70b7-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-fda8bb307f1d70b7----1752541255847"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/ClubServicesNew"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/packages/package/active/3586
**Path:** `/api/packages/package/active/3586`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/packages/package/active/3586",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/packages/package/active/3586"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjU1NWQzZmQ4YzBlMmEwZmEiLCJ0ciI6IjBhOWJjNDlmYzVkZWNhMWM3YjI3ZmU4Y2FmODZhN2QxIiwidGkiOjE3NTI1NDEyNTk3MzB9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-0a9bc49fc5deca1c7b27fe8caf86a7d1-555d3fd8c0e2a0fa-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-555d3fd8c0e2a0fa----1752541259730"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## POST /api/agreements/package_agreements/invoices
**Path:** `/api/agreements/package_agreements/invoices`

**Method:** `POST`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/invoices",
  "headers": [
    {
      "name": ":method",
      "value": "POST"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/invoices"
    },
    {
      "name": "content-length",
      "value": "1157"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjJmYTI1ZDhjNDRiZTBlNjYiLCJ0ciI6ImNhZmM4OTM4OTY3NTQ4OGJjNWU3NDdkY2JmY2I4OGRlIiwidGkiOjE3NTI1NDEyNjAwNzR9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-cafc89389675488bc5e747dcbfcb88de-2fa25d8c44be0e66-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "content-type",
      "value": "application/json;charset=UTF-8"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-2fa25d8c44be0e66----1752541260074"
    },
    {
      "name": "origin",
      "value": "https://anytime.club-os.com"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": "application/json;charset=UTF-8",
    "text": "{\"packageId\":74379,\"locationId\":3586,\"name\":\"6 Week Challenge Payments\",\"description\":\"Weekly Payments\",\"agreementStatus\":1,\"duration\":6,\"durationType\":6,\"billingDuration\":1,\"billingDurationType\":6,\"renewType\":0,\"defaultRenewType\":0,\"packageAgreementFees\":[{\"packageFeeId\":110396,\"description\":\"6 Week Challenge Weekly  Payments\",\"unitPrice\":99.99,\"billingDuration\":1,\"billingDurationType\":6,\"feeType\":2,\"salesTaxTypes\":[]}],\"packageAgreementCancellationFees\":[],\"packageAgreementMemberServices\":[{\"packageMemberServiceId\":97012,\"regions\":[3880],\"name\":\"Small Group Training\",\"description\":\"Small Group Training\",\"calendarEventType\":{\"name\":\"Small Group Training\",\"id\":8,\"icon\":\"icon_smallgrouptraining.png\",\"consumable\":true,\"privateOnly\":false,\"meeting\":false,\"groupClass\":false,\"ptEventType\":true},\"salesTaxTypes\":[],\"unitPrice\":0,\"expirationDuration\":31,\"expirationDurationType\":7,\"billingDuration\":1,\"billingDurationType\":6,\"isActiveInPackage\":null,\"parentIds\":null,\"unitsPerBillingDuration\":3}],\"memberId\":184027841,\"downPaymentBillingDurations\":1,\"startDate\":\"2025-07-14\",\"agreementBillingStatusChanges\":[{\"eventDate\":\"2025-07-14\",\"billingState\":1}]}"
  }
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/undefined
**Path:** `/api/agreements/package_agreements/undefined`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/undefined",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/undefined"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImYyYzgzMDEzZTFiMzRlMWMiLCJ0ciI6ImEzZGE2YTMwMTUzY2Y5NWZlN2VjODIzYWJiM2I0ODVlIiwidGkiOjE3NTI1NDEyNjc1NjF9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-a3da6a30153cf95fe7ec823abb3b485e-f2c83013e1b34e1c-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-f2c83013e1b34e1c----1752541267561"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/undefined/billing_status
**Path:** `/api/agreements/package_agreements/undefined/billing_status`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/undefined/billing_status",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/undefined/billing_status"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjcwZWZhMzQ1NTZkM2Q2NzQiLCJ0ciI6IjMwNjM2ZmQ1ODcxNmM4Y2I3M2Q2MzIzZDFhOTNiN2FlIiwidGkiOjE3NTI1NDEyNjc1NjZ9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-30636fd58716c8cb73d6323d1a93b7ae-70efa34556d3d674-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-70efa34556d3d674----1752541267566"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/users/employee
**Path:** `/api/users/employee`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/users/employee?locationId=3586",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/users/employee?locationId=3586"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImM5MTY0ODRjMzkwYjI3NGUiLCJ0ciI6ImRhM2JmOGFhOWM2MDA3MTljZWIyODZlYjMzMTM5MDE1IiwidGkiOjE3NTI1NDEyNjc1Njh9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-da3bf8aa9c600719ceb286eb33139015-c916484c390b274e-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-c916484c390b274e----1752541267568"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "locationId",
      "value": "3586"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/users/employee/trainers
**Path:** `/api/users/employee/trainers`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/users/employee/trainers?locationId=3586",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/users/employee/trainers?locationId=3586"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjJiMmIyNmU2YzFhMzE0YjciLCJ0ciI6ImY1ZTM5ZTVhZGU2ODA1ZjFiY2I5OWY1ZDM0YzZiNmFhIiwidGkiOjE3NTI1NDEyNjc1Njl9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-f5e39e5ade6805f1bcb99f5d34c6b6aa-2b2b26e6c1a314b7-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-2b2b26e6c1a314b7----1752541267569"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "locationId",
      "value": "3586"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/member_payment_profiles
**Path:** `/api/member_payment_profiles`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/member_payment_profiles",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/member_payment_profiles"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImZiZTdiODUwYmJjYzgwOTQiLCJ0ciI6ImUyNDg2NjIyZmIxYTc0NTk0ZWRlMWZjOGRlYTg0ZWQ2IiwidGkiOjE3NTI1NDEyNjc1NzB9fQ=="
    },
    {
      "name": "traceparent",
      "value": "00-e2486622fb1a74594ede1fc8dea84ed6-fbe7b850bbcc8094-01"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "application/json, text/plain, */*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-fbe7b850bbcc8094----1752541267570"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {}
}
````

**Example Response:** None

## GET /api/package-agreement-proposals
**Path:** `/api/package-agreement-proposals`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/package-agreement-proposals?locationId=3586&packageId=98255&rewriteDraft=false&_=1752541267960",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/package-agreement-proposals?locationId=3586&packageId=98255&rewriteDraft=false&_=1752541267960"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImExNjBmODA5NDYwNjczOGQiLCJ0ciI6IjcxODFjZTJjZjgwMGE4ZDMyYzQxMGUxYzg0MTdiNTYwIiwidGkiOjE3NTI1NDEyNjc5NjB9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-7181ce2cf800a8d32c410e1c8417b560-a160f8094606738d-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-a160f8094606738d----1752541267960"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "locationId",
      "value": "3586"
    },
    {
      "name": "packageId",
      "value": "98255"
    },
    {
      "name": "rewriteDraft",
      "value": "false"
    },
    {
      "name": "_",
      "value": "1752541267960"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/sales-tax/{id}/effectiveTaxes
**Path:** `/api/sales-tax/{id}/effectiveTaxes`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/sales-tax/3586/effectiveTaxes?effectiveDate=2025-07-14&_=1752541267961",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/sales-tax/3586/effectiveTaxes?effectiveDate=2025-07-14&_=1752541267961"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjZjN2Y1NjU4YzljMjc1YWUiLCJ0ciI6ImZhOGExOGUxNzk0MjUxMjVlYTQxMjJkYmE2ZDkyMmQ2IiwidGkiOjE3NTI1NDEyNjc5NjF9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-fa8a18e179425125ea4122dba6d922d6-6c7f5658c9c275ae-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-6c7f5658c9c275ae----1752541267961"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "effectiveDate",
      "value": "2025-07-14"
    },
    {
      "name": "_",
      "value": "1752541267961"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/package-agreement-proposals/proposal-discount
**Path:** `/api/package-agreement-proposals/proposal-discount`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/package-agreement-proposals/proposal-discount?packageId=98255&_=1752541268128",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/package-agreement-proposals/proposal-discount?packageId=98255&_=1752541268128"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjY1Y2M3NTg1MDFlMzdhMDciLCJ0ciI6IjMzMzQyNDQ0MDUyNDA4MmNiODlmNDM0ODRkYjNjMDNkIiwidGkiOjE3NTI1NDEyNjgxMjh9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-333424440524082cb89f43484db3c03d-65cc758501e37a07-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-65cc758501e37a07----1752541268128"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "packageId",
      "value": "98255"
    },
    {
      "name": "_",
      "value": "1752541268128"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/regions
**Path:** `/api/regions`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/regions?_=1752541268247",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/regions?_=1752541268247"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImIzMmYyOTNhNWVhYzQwODMiLCJ0ciI6ImEyZmRjNGMwOWVjMTUxZGMzNDg0NjZiZGM5YWQ1ZGZjIiwidGkiOjE3NTI1NDEyNjgyNDh9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-a2fdc4c09ec151dc348466bdc9ad5dfc-b32f293a5eac4083-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-b32f293a5eac4083----1752541268248"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "_",
      "value": "1752541268247"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## POST /api/package-agreement-proposals/calculate
**Path:** `/api/package-agreement-proposals/calculate`

**Method:** `POST`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/package-agreement-proposals/calculate",
  "headers": [
    {
      "name": ":method",
      "value": "POST"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/package-agreement-proposals/calculate"
    },
    {
      "name": "content-length",
      "value": "800"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg0MDI3ODQxLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.wuudSAy8nsktoRgclpijPjEbTQHRUBuf2VVOkhyGIGI"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImRhMzIxYzY0YTlmOWUxNzEiLCJ0ciI6ImRiYWVlYjMxMTJjOWI1YjAxM2NkOTk3OWI1ZmJkYzQ0IiwidGkiOjE3NTI1NDEyNjkyNjN9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-dbaeeb3112c9b5b013cd9979b5fbdc44-da321c64a9f9e171-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "content-type",
      "value": "application/json"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-da321c64a9f9e171----1752541269263"
    },
    {
      "name": "origin",
      "value": "https://anytime.club-os.com"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=184027841"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [],
  "postData": {
    "mimeType": "application/json",
    "text": "{\"billingDuration\":2,\"billingDurationType\":6,\"downPaymentBillingDurations\":1,\"duration\":12,\"durationType\":5,\"locationId\":3586,\"memberServices\":[{\"packageAgreementId\":null,\"packageAgreementMemberServiceId\":null,\"packageMemberServiceId\":127862,\"name\":\"PT-30\",\"description\":null,\"calendarEventType\":{\"name\":\"Personal Training\",\"id\":2,\"icon\":\"icon_trainer.png\",\"consumable\":true,\"privateOnly\":false,\"meeting\":false,\"groupClass\":false,\"ptEventType\":true},\"salesTaxTypes\":[],\"unitPrice\":25,\"unitPriceMin\":25,\"expirationDuration\":30,\"expirationDurationType\":7,\"billingDuration\":2,\"billingDurationType\":6,\"unitsPerDuration\":4,\"unitsPerDurationMin\":4,\"unitsPerDurationMax\":4,\"unitDuration\":30,\"unitDurationType\":10,\"activeInPackage\":null}],\"packageAgreementFees\":[],\"startDate\":\"2025-07-14\",\"discountId\":null}"
  }
}
````

**Example Response:** None

## GET /api/calendar/events
**Path:** `/api/calendar/events`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/calendar/events?eventIds=152241606&eventIds=152241619&eventIds=152313709&eventIds=152330854&eventIds=152307818&eventIds=150073576&eventIds=152251071&eventIds=152331703&eventIds=152323134&eventIds=150468903&eventIds=150850294&eventIds=152068118&eventIds=152339247&eventIds=152330036&eventIds=149648946&eventIds=152335380&eventIds=150636019&eventIds=152334766&fields=fundingStatus&_=1752541547652",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/calendar/events?eventIds=152241606&eventIds=152241619&eventIds=152313709&eventIds=152330854&eventIds=152307818&eventIds=150073576&eventIds=152251071&eventIds=152331703&eventIds=152323134&eventIds=150468903&eventIds=150850294&eventIds=152068118&eventIds=152339247&eventIds=152330036&eventIds=149648946&eventIds=152335380&eventIds=150636019&eventIds=152334766&fields=fundingStatus&_=1752541547652"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg3MDMyNzgyLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.Udx2u6d2RMpaPB4Bzh3O4AXL9-mgEaB9JJIGRxgz1Do"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6Ijc1ZmFmYWNhNWMxNzc1OGIiLCJ0ciI6ImI5MTA3ZWEyMzQ3MGE0NzcxMzY0Mzk2ZTdkN2Y1NjIwIiwidGkiOjE3NTI1NDE1NDc2NTN9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-b9107ea23470a4771364396e7d7f5620-75fafaca5c17758b-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-75fafaca5c17758b----1752541547653"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/Calendar"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjU0NDYzMiwiaWF0IjoxNzUyNTQxMDMyLCJqdGkiOiJkODc5NDM4Zi1mNjY0LTQ1OWEtYTU4Ni01NjgxY2RjNTI4YTgiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.XUIVp5nBJpXpBoQ4j2OFzUdf-2CT-1WPKNktoXjrUl_p7U8KJixO_jtE2e5fjXlYZyhCzaAriU7ujCTuG3Cc2C8Zkow953MCSgnKvDaXJcCt47bs4hsHQLMrlCyu0vWSbb8xmLZtjcrJY6skTAFpw9PJjofRyhoLI5zG4ns6QrBxqt-2T_N3DDGr68S0k8VqbOPsEZRH0oY886CQYK2sLsNwjriF8lPsO2OX5X0uV-L_Wrf6DOmzYvFv41TWJE70t8TCvRPyqBtjSvAQ8dUZtQAWeOmuHTeqONdE_CLV7F_DmbYYVmRJBJB_-40812KvxzqyXEo-lPRiXkZZbooA5g"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1NDQ2MzIsImlhdCI6MTc1MjU0MTAzMn0.zIB7WHtddYZgVLHnnyoR6M_mW2Sm-pxhuF2OkOE6hPDxDfPI30XHwXrZ9rvXbLyr5m7rJ2mvFFhHsrPy4kH70UAGRVA5KoLRRSUOr_IFj52Uvwcve3K83nTFJozP8dZ9H84PytVpK2tjdNPc7YCZ3xbvIr0Qbng9o1_iTMdBx8LlxM2wv_5r43YYtYnL_pqE7dkGRcDaz0mDni_BvUVcuuLzv7AWyYfKZg378-kWLof4UeihGQvqREsp9NVRN5EITRyn_6K6yecon6vLyEgDUxcGUN1kaE0W7y-EMqYdb-Esd4rwp7Vr-euckH6xAGWPDZ0B7ZIUmfdzbuWBEQgn9Q"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId=187032782"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "eventIds",
      "value": "152241606"
    },
    {
      "name": "eventIds",
      "value": "152241619"
    },
    {
      "name": "eventIds",
      "value": "152313709"
    },
    {
      "name": "eventIds",
      "value": "152330854"
    },
    {
      "name": "eventIds",
      "value": "152307818"
    },
    {
      "name": "eventIds",
      "value": "150073576"
    },
    {
      "name": "eventIds",
      "value": "152251071"
    },
    {
      "name": "eventIds",
      "value": "152331703"
    },
    {
      "name": "eventIds",
      "value": "152323134"
    },
    {
      "name": "eventIds",
      "value": "150468903"
    },
    {
      "name": "eventIds",
      "value": "150850294"
    },
    {
      "name": "eventIds",
      "value": "152068118"
    },
    {
      "name": "eventIds",
      "value": "152339247"
    },
    {
      "name": "eventIds",
      "value": "152330036"
    },
    {
      "name": "eventIds",
      "value": "149648946"
    },
    {
      "name": "eventIds",
      "value": "152335380"
    },
    {
      "name": "eventIds",
      "value": "150636019"
    },
    {
      "name": "eventIds",
      "value": "152334766"
    },
    {
      "name": "fields",
      "value": "fundingStatus"
    },
    {
      "name": "_",
      "value": "1752541547652"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/{id}/billing_status
**Path:** `/api/agreements/package_agreements/{id}/billing_status`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/1522516/billing_status?_=1752529076326",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/1522516/billing_status?_=1752529076326"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.sU4bUawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6ImY4YWU0MjRhNjdiMDdhMDIiLCJ0ciI6ImYxOTBmMDJjZGRmZGVlMzdhZWM0MzY2NWEzYzAwNDUzIiwidGkiOjE3NTI1MjkwNzYzMjZ9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-f190f02cddfdee37aec43665a3c00453-f8ae424a67b07a02-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-f8ae424a67b07a02----1752529076326"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjUzMDU5NCwiaWF0IjoxNzUyNTI2OTk0LCJqdGkiOiJmZDRmZjJiNy0yMTM3LTQzOTMtYWJkNS1jNDM3M2FjNTliMDUiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.ONntA6_kUMSjhPX2nCQhgVorCKS0Bwq68Z_d5tqaushpvRcPQNbiPIP5toDx8CVaNq8l0dI9wBKttINT8YlK6s603XZRpH_oPwKGTFt6qCbazG4d3hlEX-S0W8OGbCHki76rCuTMeeMSjqQm6CrR7i9vEV4uO1SRUlD6XNxtB4aLvyv5Em17SyrBrKc4sogZWXerrC79Xz3wCKWYVXbRUVmtRRwEJgfa-_nbDrr0Z9mbzX_Wthj0q3psqotB3GN0CGlUhVSs2BDOcRYmj3G-eXERhvjMYcxyxyu2oVy36blOuZy8oD0cC18Q8gS_rXTxnRRGa9XRPmz1-wHVbFHUsA"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1MzA1OTQsImlhdCI6MTc1MjUyNjk5NH0.RLbygRMiEl__BgDUfC-e8czoM3fML7wjZkMnIu8DP2c0GAhrEhFAjBpz1RppXRTAxuBxmr0eb2u0uAtVepcUBtT-N2b2d1Kj9YwT_981bOMyU00Rq2ygOeFCCp4m0FurJYsAT6FcgFOiAIlmNiZvbPO6Jp0X1lEMBEiwvp1ARuKwApMBzWbogxYyScxxyzz_tMISyoMHGozIe7Zj7aM-H8SGsesaFO5sIrNoJen976SyhC8v5rfjLfBGWl2hhH39unVQ8IJQuEsWeTAbYVzVFM1o0xvTWsHCKNz00Hq0JtEKLwF8-eriYkUeuSuh9s4jKgpuK271L_PvwF78-qTtfA"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=185777276"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "_",
      "value": "1752529076326"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/V2/1522516
**Path:** `/api/agreements/package_agreements/V2/1522516`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/V2/1522516?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_=1752529076328",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/V2/1522516?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_=1752529076328"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.sU4bUawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjllZjFhZDcyYmU3OGIxYWYiLCJ0ciI6ImJlMDRhYzRhYWU0NGM3NjM5MzczYTM2NTZiNTE4NTlhIiwidGkiOjE3NTI1MjkwNzYzMjl9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-be04ac4aae44c7639373a3656b51859a-9ef1ad72be78b1af-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-9ef1ad72be78b1af----1752529076329"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjUzMDU5NCwiaWF0IjoxNzUyNTI2OTk0LCJqdGkiOiJmZDRmZjJiNy0yMTM3LTQzOTMtYWJkNS1jNDM3M2FjNTliMDUiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.ONntA6_kUMSjhPX2nCQhgVorCKS0Bwq68Z_d5tqaushpvRcPQNbiPIP5toDx8CVaNq8l0dI9wBKttINT8YlK6s603XZRpH_oPwKGTFt6qCbazG4d3hlEX-S0W8OGbCHki76rCuTMeeMSjqQm6CrR7i9vEV4uO1SRUlD6XNxtB4aLvyv5Em17SyrBrKc4sogZWXerrC79Xz3wCKWYVXbRUVmtRRwEJgfa-_nbDrr0Z9mbzX_Wthj0q3psqotB3GN0CGlUhVSs2BDOcRYmj3G-eXERhvjMYcxyxyu2oVy36blOuZy8oD0cC18Q8gS_rXTxnRRGa9XRPmz1-wHVbFHUsA"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1MzA1OTQsImlhdCI6MTc1MjUyNjk5NH0.RLbygRMiEl__BgDUfC-e8czoM3fML7wjZkMnIu8DP2c0GAhrEhFAjBpz1RppXRTAxuBxmr0eb2u0uAtVepcUBtT-N2b2d1Kj9YwT_981bOMyU00Rq2ygOeFCCp4m0FurJYsAT6FcgFOiAIlmNiZvbPO6Jp0X1lEMBEiwvp1ARuKwApMBzWbogxYyScxxyzz_tMISyoMHGozIe7Zj7aM-H8SGsesaFO5sIrNoJen976SyhC8v5rfjLfBGWl2hhH39unVQ8IJQuEsWeTAbYVzVFM1o0xvTWsHCKNz00Hq0JtEKLwF8-eriYkUeuSuh9s4jKgpuK271L_PvwF78-qTtfA"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=185777276"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "include",
      "value": "invoices"
    },
    {
      "name": "include",
      "value": "scheduledPayments"
    },
    {
      "name": "include",
      "value": "prohibitChangeTypes"
    },
    {
      "name": "_",
      "value": "1752529076328"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/agreementTotalValue
**Path:** `/api/agreements/package_agreements/agreementTotalValue`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/agreementTotalValue?agreementId=1522516&_=1752529076330",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/agreementTotalValue?agreementId=1522516&_=1752529076330"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.sU4bUawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjY0MjU5ZDYwNTA5MGI4NmUiLCJ0ciI6ImQ3NTVlZWNhYjdhZjcwZDA0ZDJhODY2ODdkNzc3YzEzIiwidGkiOjE3NTI1MjkwNzYzMzB9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-d755eecab7af70d04d2a86687d777c13-64259d605090b86e-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-64259d605090b86e----1752529076330"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjUzMDU5NCwiaWF0IjoxNzUyNTI2OTk0LCJqdGkiOiJmZDRmZjJiNy0yMTM3LTQzOTMtYWJkNS1jNDM3M2FjNTliMDUiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.ONntA6_kUMSjhPX2nCQhgVorCKS0Bwq68Z_d5tqaushpvRcPQNbiPIP5toDx8CVaNq8l0dI9wBKttINT8YlK6s603XZRpH_oPwKGTFt6qCbazG4d3hlEX-S0W8OGbCHki76rCuTMeeMSjqQm6CrR7i9vEV4uO1SRUlD6XNxtB4aLvyv5Em17SyrBrKc4sogZWXerrC79Xz3wCKWYVXbRUVmtRRwEJgfa-_nbDrr0Z9mbzX_Wthj0q3psqotB3GN0CGlUhVSs2BDOcRYmj3G-eXERhvjMYcxyxyu2oVy36blOuZy8oD0cC18Q8gS_rXTxnRRGa9XRPmz1-wHVbFHUsA"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1MzA1OTQsImlhdCI6MTc1MjUyNjk5NH0.RLbygRMiEl__BgDUfC-e8czoM3fML7wjZkMnIu8DP2c0GAhrEhFAjBpz1RppXRTAxuBxmr0eb2u0uAtVepcUBtT-N2b2d1Kj9YwT_981bOMyU00Rq2ygOeFCCp4m0FurJYsAT6FcgFOiAIlmNiZvbPO6Jp0X1lEMBEiwvp1ARuKwApMBzWbogxYyScxxyzz_tMISyoMHGozIe7Zj7aM-H8SGsesaFO5sIrNoJen976SyhC8v5rfjLfBGWl2hhH39unVQ8IJQuEsWeTAbYVzVFM1o0xvTWsHCKNz00Hq0JtEKLwF8-eriYkUeuSuh9s4jKgpuK271L_PvwF78-qTtfA"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=185777276"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "agreementId",
      "value": "1522516"
    },
    {
      "name": "_",
      "value": "1752529076330"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/{id}/salespeople
**Path:** `/api/agreements/package_agreements/{id}/salespeople`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/1522516/salespeople?_=1752529076331",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/1522516/salespeople?_=1752529076331"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.sU4bUawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjkwMmY0MDhkOGMzNDA4ZjMiLCJ0ciI6ImRlZGUzY2U4NGJlNDM3Mjk5Yzk1MWQ5OTJkYTNjYmNhIiwidGkiOjE3NTI1MjkwNzYzMzF9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-dede3ce84be437299c951d992da3cbca-902f408d8c3408f3-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-902f408d8c3408f3----1752529076331"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjUzMDU5NCwiaWF0IjoxNzUyNTI2OTk0LCJqdGkiOiJmZDRmZjJiNy0yMTM3LTQzOTMtYWJkNS1jNDM3M2FjNTliMDUiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.ONntA6_kUMSjhPX2nCQhgVorCKS0Bwq68Z_d5tqaushpvRcPQNbiPIP5toDx8CVaNq8l0dI9wBKttINT8YlK6s603XZRpH_oPwKGTFt6qCbazG4d3hlEX-S0W8OGbCHki76rCuTMeeMSjqQm6CrR7i9vEV4uO1SRUlD6XNxtB4aLvyv5Em17SyrBrKc4sogZWXerrC79Xz3wCKWYVXbRUVmtRRwEJgfa-_nbDrr0Z9mbzX_Wthj0q3psqotB3GN0CGlUhVSs2BDOcRYmj3G-eXERhvjMYcxyxyu2oVy36blOuZy8oD0cC18Q8gS_rXTxnRRGa9XRPmz1-wHVbFHUsA"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1MzA1OTQsImlhdCI6MTc1MjUyNjk5NH0.RLbygRMiEl__BgDUfC-e8czoM3fML7wjZkMnIu8DP2c0GAhrEhFAjBpz1RppXRTAxuBxmr0eb2u0uAtVepcUBtT-N2b2d1Kj9YwT_981bOMyU00Rq2ygOeFCCp4m0FurJYsAT6FcgFOiAIlmNiZvbPO6Jp0X1lEMBEiwvp1ARuKwApMBzWbogxYyScxxyzz_tMISyoMHGozIe7Zj7aM-H8SGsesaFO5sIrNoJen976SyhC8v5rfjLfBGWl2hhH39unVQ8IJQuEsWeTAbYVzVFM1o0xvTWsHCKNz00Hq0JtEKLwF8-eriYkUeuSuh9s4jKgpuK271L_PvwF78-qTtfA"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=185777276"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "_",
      "value": "1752529076331"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/package-agreement-proposals/scheduled-payments-count
**Path:** `/api/package-agreement-proposals/scheduled-payments-count`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/package-agreement-proposals/scheduled-payments-count?duration=12&durationType=5&billingDuration=2&billingDurationType=6&startDate=2024-09-13&_=1752529077962",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/package-agreement-proposals/scheduled-payments-count?duration=12&durationType=5&billingDuration=2&billingDurationType=6&startDate=2024-09-13&_=1752529077962"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.sU4bUawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjNmZTU3MTdmN2Y4MjE0OTciLCJ0ciI6IjY4OTg5NDAxN2MxYTUzNTE1NWZjYzAyNzU4YTYyYzU4IiwidGkiOjE3NTI1MjkwNzc5NjN9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-689894017c1a535155fcc02758a62c58-3fe5717f7f821497-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-3fe5717f7f821497----1752529077963"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjUzMDU5NCwiaWF0IjoxNzUyNTI2OTk0LCJqdGkiOiJmZDRmZjJiNy0yMTM3LTQzOTMtYWJkNS1jNDM3M2FjNTliMDUiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.ONntA6_kUMSjhPX2nCQhgVorCKS0Bwq68Z_d5tqaushpvRcPQNbiPIP5toDx8CVaNq8l0dI9wBKttINT8YlK6s603XZRpH_oPwKGTFt6qCbazG4d3hlEX-S0W8OGbCHki76rCuTMeeMSjqQm6CrR7i9vEV4uO1SRUlD6XNxtB4aLvyv5Em17SyrBrKc4sogZWXerrC79Xz3wCKWYVXbRUVmtRRwEJgfa-_nbDrr0Z9mbzX_Wthj0q3psqotB3GN0CGlUhVSs2BDOcRYmj3G-eXERhvjMYcxyxyu2oVy36blOuZy8oD0cC18Q8gS_rXTxnRRGa9XRPmz1-wHVbFHUsA"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1MzA1OTQsImlhdCI6MTc1MjUyNjk5NH0.RLbygRMiEl__BgDUfC-e8czoM3fML7wjZkMnIu8DP2c0GAhrEhFAjBpz1RppXRTAxuBxmr0eb2u0uAtVepcUBtT-N2b2d1Kj9YwT_981bOMyU00Rq2ygOeFCCp4m0FurJYsAT6FcgFOiAIlmNiZvbPO6Jp0X1lEMBEiwvp1ARuKwApMBzWbogxYyScxxyzz_tMISyoMHGozIe7Zj7aM-H8SGsesaFO5sIrNoJen976SyhC8v5rfjLfBGWl2hhH39unVQ8IJQuEsWeTAbYVzVFM1o0xvTWsHCKNz00Hq0JtEKLwF8-eriYkUeuSuh9s4jKgpuK271L_PvwF78-qTtfA"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=185777276"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "duration",
      "value": "12"
    },
    {
      "name": "durationType",
      "value": "5"
    },
    {
      "name": "billingDuration",
      "value": "2"
    },
    {
      "name": "billingDurationType",
      "value": "6"
    },
    {
      "name": "startDate",
      "value": "2024-09-13"
    },
    {
      "name": "_",
      "value": "1752529077962"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/V2/1617934
**Path:** `/api/agreements/package_agreements/V2/1617934`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/V2/1617934?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_=1752529095047",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/V2/1617934?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_=1752529095047"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9.sU4bUawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjQ1YjA2MmY3YmIzYTFjZWQiLCJ0ciI6IjZiZjlhMjA2MDA3YjRkYzEwYTJkNDQ1YjcwMjJkODdkIiwidGkiOjE3NTI1MjkwOTUwNDh9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-6bf9a206007b4dc10a2d445b7022d87d-45b062f7bb3a1ced-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-45b062f7bb3a1ced----1752529095048"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_fbp=fb.1.1750181614288.28580080925040380"
    },
    {
      "name": "cookie",
      "value": "__ecatft={\"utm_campaign\":\"\",\"utm_source\":\"\",\"utm_medium\":\"\",\"utm_content\":\"\",\"utm_term\":\"\",\"utm_device\":\"\",\"referrer\":\"https://www.bing.com/\",\"gclid\":\"\",\"lp\":\"www.club-os.com/\"}"
    },
    {
      "name": "cookie",
      "value": "_gcl_au=1.1.1983975127.1750181615"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28"
    },
    {
      "name": "cookie",
      "value": "osano_consentmanager=pUQdj9lXwNz8G0r5wg8XEpcNpzH-L1ou8e0iwwSBlyChK-6AZCLQmpYmFjG69PvKoD3k_33vDX274aQLwD6OFYigCckQYlqdOy6WZfsR41ygA1SiH0fF5nPbmvjgp6btck0GxLageQFhsKYXm58G4yL-C4YXEVBoOoTn_NxeoVk8vus5y8LMJ_yXrgtAqh7yq01FJ7GlBuRETYKtnj9BU6JnfRLJke553R9xj7NBM23IrjNFA4c6NWp-o-7zX-LiSnJWZGR41LgLBJTgjivcnlp3pjSf9Dv3R8zsXw=="
    },
    {
      "name": "cookie",
      "value": "_clck=47khr4%7C2%7Cfwu%7C0%7C1994"
    },
    {
      "name": "cookie",
      "value": "messagesUtk=45ced08d977d42f1b5360b0701dcdadc"
    },
    {
      "name": "cookie",
      "value": "__hstc=130365392.da9547cf2e866b0ea5a811ae2d00f8e3.1750195292681.1750195292681.1750195292681.1"
    },
    {
      "name": "cookie",
      "value": "hubspotutk=da9547cf2e866b0ea5a811ae2d00f8e3"
    },
    {
      "name": "cookie",
      "value": "_hp2_id.2794995124=%7B%22userId%22%3A%2254936772480015%22%2C%22pageviewId%22%3A%223416648379715226%22%2C%22sessionId%22%3A%228662001472485713%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    },
    {
      "name": "cookie",
      "value": "_ga_KNW7VZ6GNY=GS2.1.s1750198517$o3$g0$t1750198517$j60$l0$h1657069555"
    },
    {
      "name": "cookie",
      "value": "_uetvid=31d786004ba111f0b8df757d82f1b34b"
    },
    {
      "name": "cookie",
      "value": "_ga_0NH3ZBDBNZ=GS2.1.s1752337346$o1$g1$t1752337499$j6$l0$h0"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.1684127573.1750181615"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.75957065.1752508973"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=B3467A4162F3FB3126FA6C2E4558FCB9"
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6ImNlZWQ1NmRiLWM0NWQtNGVlZS05YjI2LWE0OThmZjRjY2ViYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MjUzMDU5NCwiaWF0IjoxNzUyNTI2OTk0LCJqdGkiOiJmZDRmZjJiNy0yMTM3LTQzOTMtYWJkNS1jNDM3M2FjNTliMDUiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.ONntA6_kUMSjhPX2nCQhgVorCKS0Bwq68Z_d5tqaushpvRcPQNbiPIP5toDx8CVaNq8l0dI9wBKttINT8YlK6s603XZRpH_oPwKGTFt6qCbazG4d3hlEX-S0W8OGbCHki76rCuTMeeMSjqQm6CrR7i9vEV4uO1SRUlD6XNxtB4aLvyv5Em17SyrBrKc4sogZWXerrC79Xz3wCKWYVXbRUVmtRRwEJgfa-_nbDrr0Z9mbzX_Wthj0q3psqotB3GN0CGlUhVSs2BDOcRYmj3G-eXERhvjMYcxyxyu2oVy36blOuZy8oD0cC18Q8gS_rXTxnRRGa9XRPmz1-wHVbFHUsA"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiY2VlZDU2ZGItYzQ1ZC00ZWVlLTliMjYtYTQ5OGZmNGNjZWJhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTI1MjY5OTQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTI1MzA1OTQsImlhdCI6MTc1MjUyNjk5NH0.RLbygRMiEl__BgDUfC-e8czoM3fML7wjZkMnIu8DP2c0GAhrEhFAjBpz1RppXRTAxuBxmr0eb2u0uAtVepcUBtT-N2b2d1Kj9YwT_981bOMyU00Rq2ygOeFCCp4m0FurJYsAT6FcgFOiAIlmNiZvbPO6Jp0X1lEMBEiwvp1ARuKwApMBzWbogxYyScxxyzz_tMISyoMHGozIe7Zj7aM-H8SGsesaFO5sIrNoJen976SyhC8v5rfjLfBGWl2hhH39unVQ8IJQuEsWeTAbYVzVFM1o0xvTWsHCKNz00Hq0JtEKLwF8-eriYkUeuSuh9s4jKgpuK271L_PvwF78-qTtfA"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.TONPFo86Kk2nPWzZHh_JIoMA_pAl1BHTUd7aQObyGUND2jrhtwqr9GJBRpM2o1J8_lu_bPH_Ogm8IES5igrw5JFArD2ueLYS2AH8a8LMgo_SXCY98kIGbugK-RrPt1oOl3yezCNYwPQr--REYdeSthbdXzVYU4-lxdx1XyeLHo7VZMZgZWFY4DMfNJgVGxqVbvrJv04MWKhLgEim1b7UgiHBrZfoc64Cdh_n6WNqnShH1WG4BzxbiIV7eA93jen7D43MVHEFrBSGSY_GBqAoSMjYHFwhT2Xaa_LO57vk3jdOb9Dex_hRYTkCl3IMLCV0YxlVlf7cuQLBJkDnuHgWIg.hAVUzIdDUJ6KbAZh.DgBCa_Hrwn5PcKD3mNeQuIOUMB1W3_6alu-7vFYw-PDBOCossK3CIS_Ld6so-_Bk-O9RZwPF0W90BcwrAhxarZjUFBKIqCPzfDEtRDae_VOiDjslkW-RegDV02pxqU4LbVGze1UajddQQHSi3z0cYCBvVL0f-JB2nzxmfGRZqqjJKfxEwCkc_jHggPuodNIKdoSADejRFVGdBQ2bFTolCRRmrJLsElVcyLsILRWpeRAUow0caGPJHMLDTktrztH46Pf-zCNB3vS2uWeHIn0paK074wNY4FeRUiqdpnZ8ygbdqLeV4EtJ2VPFbkPtnihdnaYuh-EhWkvy3Vtg0MGCxm0DKVRD6soUattRvHZSUDb5UveCmEvf6UAq6v0_xGCyddxt0n1lVnRWNYMSCj2LVPcQThwHSqcNIbRIcYQEtMaI-30znbXkHMBRLdiLAR4rQnoiq2kpI0wtb48qk6_EQGFwtJ7a1_J2tCqpYcwi7jiIQ92i5NdWO-onpWEPYh2mE0xZRbJ9YQ_ROvwit2DiCT_VGQuM2ZM-tMfJpis5kaQmVTa8KFe4-KnaS6e62hYsy7pr7lVacvAxtxaU5S0yCT1X-jpABFpISCzdkXMnIpbAcv4S_XX3fPPlOvi3ZkN4j0xYFIbyTxXs7m1KgG04v0H1MYiZMXXNtDe8lylKyPWc4w9t-Jz7hxd2FDTZVhe7QqVHO7QQzmGwPZ40XF0nSRK8koNejGTs6fSTGiLArSU9XCkeuPxHDpEx1Jb_w9u9HxkJZClrdCK7hFRpCllIROkYrBEAxOZ0vW_8r8N1mlSBr9QlBfMKD-cdknmYYN2o5DzyhgdPY3suwFamGbvXbk2N9mCsjMTsMel0nojaV4Uq2eZUCTXyuTxJ8lVNhRx5JX6FBzYa37EmgfeapcXRr96NGLznsADgvcYF8fE8HAg2gWUaIGf5zOrq5uI7W4pqy1suXyqh0DHX4aQmVzmDSfQKV_ErW0y8qjBusYaIqZSwKr-C2ENGsMJTERE6FnmN1XE-kZr18L9GKNDoPXal9aV7ESEMfbQoD2bXHCRQ5SWLFzTBqUH2RuJcd8weDiKNGEkIIT1noZZPJieRepk84oKBayWJYsmwaEvNOnw2CPv7dWWwl8hWdRC6emTtIkodXaMAJ9CedgQhJ0x2bjFf5GdNs95gyXOCSOkTUYk0G1kk9KMsVaa-9myhjekG33mcaOywYaJL2Y0C75jHwrCkrEVWy0zwIpzysUK9lwuWZ5cYXT2RQGEYuVsyn987lPdYdB6rWmQDpJE.OFOi8I2jSl1zVjwFahqJJQ"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=185777276"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "include",
      "value": "invoices"
    },
    {
      "name": "include",
      "value": "scheduledPayments"
    },
    {
      "name": "include",
      "value": "prohibitChangeTypes"
    },
    {
      "name": "_",
      "value": "1752529095047"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

## GET /api/agreements/package_agreements/V2/1616463
**Path:** `/api/agreements/package_agreements/V2/1616463`

**Method:** `GET`

**Keyword Fields:** None

**Example Request:**
````json
{
  "url": "https://anytime.club-os.com/api/agreements/package_agreements/V2/1616463?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_=1753892905870",
  "headers": [
    {
      "name": ":method",
      "value": "GET"
    },
    {
      "name": ":authority",
      "value": "anytime.club-os.com"
    },
    {
      "name": ":scheme",
      "value": "https"
    },
    {
      "name": ":path",
      "value": "/api/agreements/package_agreements/V2/1616463?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_=1753892905870"
    },
    {
      "name": "x-newrelic-id",
      "value": "VgYBWFdXCRABVVFTBgUBVVQJ"
    },
    {
      "name": "sec-ch-ua-platform",
      "value": "\"Windows\""
    },
    {
      "name": "authorization",
      "value": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTc1NTYwMTU3LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiI0RDIwRjhBMjZCOTM5MTE1QUY4RDQ1NDcxMTc4RUMzNCJ9.gWCg1NwTtSsn-jJMgl_eHYl6h0MtH6BLXyVheGXbvu8"
    },
    {
      "name": "sec-ch-ua",
      "value": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\""
    },
    {
      "name": "newrelic",
      "value": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6IjAxZTMwNGY1NGJlOWE5MTUiLCJ0ciI6IjJjNzI3MzY4OWJlMjE1ZjY3Y2YwNmVjYWYwYjc3MzE5IiwidGkiOjE3NTM4OTI5MDU4NzB9fQ=="
    },
    {
      "name": "sec-ch-ua-mobile",
      "value": "?0"
    },
    {
      "name": "traceparent",
      "value": "00-2c7273689be215f67cf06ecaf0b77319-01e304f54be9a915-01"
    },
    {
      "name": "x-requested-with",
      "value": "XMLHttpRequest"
    },
    {
      "name": "user-agent",
      "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    },
    {
      "name": "accept",
      "value": "*/*"
    },
    {
      "name": "dnt",
      "value": "1"
    },
    {
      "name": "tracestate",
      "value": "2069141@nr=0-1-2069141-1103255579-01e304f54be9a915----1753892905870"
    },
    {
      "name": "sec-fetch-site",
      "value": "same-origin"
    },
    {
      "name": "sec-fetch-mode",
      "value": "cors"
    },
    {
      "name": "sec-fetch-dest",
      "value": "empty"
    },
    {
      "name": "referer",
      "value": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    },
    {
      "name": "accept-encoding",
      "value": "gzip, deflate, br, zstd"
    },
    {
      "name": "accept-language",
      "value": "en-US,en;q=0.9"
    },
    {
      "name": "cookie",
      "value": "_ga=GA1.2.498331350.1750176996"
    },
    {
      "name": "cookie",
      "value": "loggedInUserId=187032782"
    },
    {
      "name": "cookie",
      "value": "_gid=GA1.2.1534567408.1753738880"
    },
    {
      "name": "cookie",
      "value": "JSESSIONID=4D20F8A26B939115AF8D45471178EC34"
    },
    {
      "name": "cookie",
      "value": "apiV3RefreshToken=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.ZUL4q04TLYudHtiLdyoSNV-8jokuelJKC_RyH4BvykLvsYxvEIGewGkGVwWnjPr9iN5JcWdynZTFhboh10SGwMZ5j7PypfpaFV_G36qGbkGROh2UdLUmq1bQWKjAcjYkloeY9jBxr8a3kE03OeKY5vZbWDGbIpBgNOea_euXnbueTFl-gLn6JhpCUZHnZTvfKPV29DL4zT7GraTvD_x8nnJKXVhasoLSRlxIvBGRLAU1pB1QbUwlhMb8sDIgVPoWF1SpIUDOwWwFjSdrcNxeBVRNtEDUS0Eje5p_m9qkPEdD8HumiL96rLiOTw-5J-8-1nRudKPTIrYcoP0B1l3wzw.erIFdruHzepXMgsj.wVp6XAR6jAjDQp2ZdaovvF1QlGhM95OEYvuUTnXpo7tbPFIFYCZOhbLh2yNvPXNAt2Y4-KSMK72dVfmCSi9-sXHCyaMlrB0pD_x9VSg224zkkRseRZo8SU5FyRizc1oS8L4AsoUKZsyOdyjsYP3ervDu-n1NuJrqOJVlDJYHGhMtTZRApLgPPhooOlvCwYhNRk9Ls_Jq0t74A62tefu2HaLcUUqOL3sPF005kk9BgACRmCfCw2r8mnHKwVHfiLH0UTf_o3gEAyza1QaHP9JAggUVzX-OIzPAQhRuAga7h9QwxZshBBrvdQosCt38Cn71aMlHsD_X91cPpPWjeCuhBhqpz_1PGV7nnL34FOzLWSGsXsKo3VzyY1MNDYSRFn5ggCz6UJfUxpPbtPzWkAicyL37YS3HmUCVSc3KRF13Kpa6O2UAraDSwEr_Pt3z8_mL1tR_JbVn6gP10BmJubRJsDgPHEwbLD2a40l7bu7v74y7SNUCFas6Pb7J90B32BBcxXfPMczlGHqYtIbLwNOcZVz0IMSQPWZK65OroFatPjKWPQXpbSxZGpqbWI1wHtNbOEgp-ZplR7oyFUhIG6KyeEJeI-hMNB3dmkQZP0rljfrfu9LTn7_c7xdu9pmZkCxdBsMVA6iLmus0aKffys1UkfYUw-GbbOE3Aucyludnr2PAGd8QhoHMTCOWXnafgkF59OLYaTSI8s0eAbRlplgStMjnrnyk4PmCnrS9N-QGmbWB2HQkzWb2wClLXFoqyosP0E0DLQKFZgAjFi7M_0Il9Nc5FZL86PwoyCON2eebBVggVzGY3x3QrfCjClksLpXlCMLSvW_POGFfZCLzpmYreGTry2uL5MH7sZ_mcVZu5GsKXODnhOCwECvau8-FCrFPL03JqXPOPMuubwfcSnwOesFtYvWCTbvmR7bf-DKMeJ3BZ-uBFucQd-Dfya7mdoc50seFtAvXXPW7Q8vlCo-MnjnqNIDGjDY47bilvCkuQWPL7b0pasrO_qa9k4QND5AQ-9D86pfpQ1WJcZosm0tUAGMVwfKY24VGVAaFu96lIMmWUneUFMfX-ZvazD4QZaLGPP6xn5GMLbIi-mldpL8KUKU4Jcjb5UjIvQNmJkDpYwaWbdbyL0JE86TjvnPf-xGNFVw3wEmvhOdHsFelQCrMlZcPt2n5cUs41ODKjsNGmCjIL8PWsufzovK2YdwZs3d2-UdVue4ycEy9uUMogqluqUrhA-UYfb5M39AIej_myFAAbh68fZWZaA6flnxuNRCl0QWdqGcJTaM.8YX0yG7b0h8wyS1gwKlElQ"
    },
    {
      "name": "cookie",
      "value": "staffDelegatedUserId="
    },
    {
      "name": "cookie",
      "value": "apiV3AccessToken=eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6IjUzODE5NjFlLTc2ZWUtNGY1NC04Y2U4LTA4NmM4NjQ0OTA1ZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTM4ODM3OTEsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1Mzg5NjM4NywiaWF0IjoxNzUzODkyNzg3LCJqdGkiOiI5YTU3NDVjNy1kMDM4LTQxY2YtOTZhZS1jNzA3MDEwM2MxMzMiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.PVMmATp3Xae7bmcKmPAVJN96RWdhww8P9uvzqspoCxcYfXp4nSo60aW9v-z21guRUQumrONoDIZRmJroiUWocA7v7pnoeFv3XD-QmGHZfRCM-wkezxavdqhna9YpKK7a4cwLQTL554oomYpkKOFqTYn3Aceuu1uZxpBZchKk31VkB-V-1GYP7A2hmygBRvOGyNzqHVpiss6lSVK0L9Fs9Y7fdSyS__laZZUBzrFDDHKtiUYi8LQr0-XPRAxUGTyyr8aNitx64AZ6nOjBvhDX5Ox7mKNIdgFenAnIljO3xPhLDQG0hY1gGM1DvYmiJcbwMRlnK1YG8bqcjEspiMMriw"
    },
    {
      "name": "cookie",
      "value": "apiV3IdToken=eyJraWQiOiJibWtxY1lkWGVqT25LUkQ1T2VxcW1sdFlORnA0cVVzV3FNN3dCSDg2WE9VPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJhdWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsImV2ZW50X2lkIjoiNTM4MTk2MWUtNzZlZS00ZjU0LThjZTgtMDg2Yzg2NDQ5MDVmIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTM4ODM3OTEsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImNvZ25pdG86dXNlcm5hbWUiOiIxODcwMzI3ODIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqLm1heW8iLCJleHAiOjE3NTM4OTYzODcsImlhdCI6MTc1Mzg5Mjc4N30.Xixzs7bBjfyZl8MIIZZOX0JJdsm89D9lyabOISXipzH4kewK_6uPjJbBFY7inht7wbl77iKtKPgTq6s77NBRH2poeS4wplT9riAU60riVXR7u_lyq9_glOgVyS7_TTMmOekjmtsc1kUMa739a-pEPJ-225ZmR7Todyne4AhS8SUss0ATB2hOTkmko0ISOpOEUoOBxus1k9Q-xE_vxlRwRRXO42xc4bs2oS14zsy9NC_nQWFsvmJYblwaRqwNewkU1tQGdvC636mkyk5NOtquIKOQ71pifEdOsGG2EibR9WxOZRpVkuTrGr9eGgvu3kGE-Fel6Y0kCUwEt3SAELCrsg"
    },
    {
      "name": "cookie",
      "value": "delegatedUserId=175560157"
    },
    {
      "name": "cookie",
      "value": "_gat_UA-24447344-1=1"
    },
    {
      "name": "priority",
      "value": "u=1, i"
    }
  ],
  "queryString": [
    {
      "name": "include",
      "value": "invoices"
    },
    {
      "name": "include",
      "value": "scheduledPayments"
    },
    {
      "name": "include",
      "value": "prohibitChangeTypes"
    },
    {
      "name": "_",
      "value": "1753892905870"
    }
  ],
  "postData": {}
}
````

**Example Response:** None

