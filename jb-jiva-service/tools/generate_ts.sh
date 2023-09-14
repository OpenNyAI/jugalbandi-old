#!/bin/bash


SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1  || exit; pwd -P )"

PROJECT_DIR="$(dirname "$SCRIPT_DIR")"


create_package_json() {
cat <<EOF > "$1"
{
  "name": "@opennyai/$2",
  "version": "$3",
  "description": "",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "artifactregistry-login": "npx google-artifactregistry-auth",
    "compile": "tsc"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "@types/node": "^18.15.11",
    "typescript": "^5.0.3"
  }
}
EOF
}

VERSION="${1?Please enter the version}" 


cd "$PROJECT_DIR" || exit
rm -rf out
poetry run python tools/generate_schema.py


npx openapi-typescript-codegen \
  --input ./out/user/openapi.json \
  --output ./out/user \
  --exportSchemas true --name JivaUserService

npx openapi-typescript-codegen \
  --input ./out/admin/openapi.json \
  --output ./out/admin \
  --exportSchemas true --name JivaAdminService

create_package_json "out/user/package.json" "jiva-user-api" "$VERSION"
create_package_json "out/admin/package.json" "jiva-admin-api" "$VERSION"


cp tools/.npmrc out/user/
cp tools/.npmrc out/admin/

cp tools/tsconfig.json out/user
cp tools/tsconfig.json out/admin

cd "$PROJECT_DIR/out/user"
npm install
npm run compile

cd "$PROJECT_DIR/out/admin"
npm install
npm run compile

