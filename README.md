# WIP

## Tests
```bash
python3 ./manage.py test
```

## OpenAPI Schema and TypeScript Equivalent
```bash
python3 ./manage.py spectacular --color --file schema.yml
npx openapi-typescript schema.yml -o schema.d.ts
```