# Creating the mga-app-secrets Secret

Secrets are NEVER committed to git. Apply them manually before deploying.

## Generate values

```fish
set DB_PW (openssl rand -base64 32)
set JWT_SECRET (openssl rand -hex 64)
```

## Create the secret

```fish
oc create secret generic mga-app-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://soap_user:$DB_PW@mga-postgresql:5432/soap_calculator" \
  --from-literal=DATABASE_URL_SYNC="postgresql://soap_user:$DB_PW@mga-postgresql:5432/soap_calculator" \
  --from-literal=DATABASE_HOST="mga-postgresql" \
  --from-literal=DATABASE_PORT="5432" \
  --from-literal=DATABASE_USER="soap_user" \
  --from-literal=SECRET_KEY="$JWT_SECRET" \
  --from-literal=ENVIRONMENT="production" \
  --from-literal=ALLOWED_ORIGINS="https://mga-soap-calculator.apps.sno.greysson.com" \
  -n mga-soap-calculator
```

Also create the PostgreSQL password secret separately (used by the StatefulSet):

```fish
oc create secret generic mga-postgresql-secret \
  --from-literal=POSTGRES_PASSWORD="$DB_PW" \
  --from-literal=POSTGRES_USER="soap_user" \
  --from-literal=POSTGRES_DB="soap_calculator" \
  -n mga-soap-calculator
```

## Verify

```fish
oc get secret mga-app-secrets -n mga-soap-calculator -o jsonpath='{.data}' | python3 -c "import sys,json,base64; d=json.load(sys.stdin); [print(k,'=',base64.b64decode(v).decode()[:8]+'...') for k,v in d.items()]"
```
