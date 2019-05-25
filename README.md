# AzLegApiClient

This is a client library for the Arizona Legislature's web service. It uses zeep to work with the soap endpoint. You can request your own credentials at https://www.azleg.gov.

Example Usage

```
    from AzLegApiClient import AzLegApiClient

    api = AzLegApiClient(username='username',password='password')

    sessions = api.sessions()

    session_id = sessions[1]

    members = api.members_by_session_id(session_id)
```