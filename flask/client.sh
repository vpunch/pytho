curl --header 'content-type: application/json' \
     --request POST \
     --data '{"content": "foobar"}' \
     http://localhost:5000/api/mail/send

curl --header 'content-type: application/json' \
     --header 'authorization: Bearer 123' \
     --request PUT \
     http://localhost:5000/api/login
